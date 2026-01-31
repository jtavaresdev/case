from calendar import month_abbr
from pathlib import Path
from typing import List, Optional

import pandas as pd


class DataProcessor:
    """
    Processa e normaliza arquivos CSV
    """

    def __init__(self, separator=";"):
        self.separator = separator
        # Preciso de mais contexto para saber melhor keywords
        self.keywords_sinistro = ["EVENTOS", "SINISTROS", "SINISTRO"]
        self.inconsistencias = {
            "cnpjs_duplicados": [],
            "valores_zerados": 0,
            "valores_negativos": 0,
        }

    def processar_arquivo(self, file_path: Path) -> Optional[pd.DataFrame]:
        try:
            df = pd.read_csv(file_path, sep=self.separator)

            if "DESCRICAO" not in df.columns:
                print("Arquivo sem coluna 'DESCRICAO'")
                return None

            # Cria a máscara
            mask = pd.Series([False] * len(df))
            for keyword in self.keywords_sinistro:
                mask |= df["DESCRICAO"].str.upper().str.contains(keyword, na=False)

            # Usa .loc para garantir que retorna DataFrame
            df_filtrado = df.loc[mask].copy()

            if df_filtrado.empty:
                print(f"Nenhum sinistro encontrado no arquivo {file_path.name}")
                return None

            print(f"Sinistros/Eventos encontrados = {len(df_filtrado)}")
            return df_filtrado

        except Exception as e:
            print(f"Erro ao processar arquivo {file_path.name}: {e}")
            return None

    def processar_diretorio(self, diretorio: Path) -> List[pd.DataFrame]:
        """Processa todos os CSVs de um diretório recursivamente"""
        dataframes = []

        for arquivo in diretorio.rglob("*.csv"):
            df = self.processar_arquivo(arquivo)
            if df is not None:
                dataframes.append(df)

        print(f"\n Total: {len(dataframes)} arquivos processados com sucesso")
        return dataframes

    def get_inconsistencias(self, data_frame: pd.DataFrame):
        # CNPJ TODO
        # ZEROS
        zerados = (data_frame["ValorDespesas"] == 0).sum()
        self.inconsistencias["valores_zerados"] += zerados
        # NEGATIVOS
        negativos = (data_frame["ValorDespesas"] < 0).sum()
        self.inconsistencias["valores_negativos"] += negativos

        return

    def trimestre_ano(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        if "DATA" not in data_frame.columns:
            print("Nenhuma coluna chamada _DATA")
            return data_frame

        data_frame["DATA"] = pd.to_datetime(data_frame["DATA"], errors="coerce")

        data_frame["Ano"] = data_frame["DATA"].dt.year
        data_frame["Trimestre"] = data_frame["DATA"].dt.quarter

        return data_frame

    def converter_monetario(
        self, data_frame: pd.DataFrame, collum: str
    ) -> pd.DataFrame:
        """
        @brief Converte coluna para valor monetário
        @param data_frame Dados que vão ser modificados
        @param collum Nome da coluna a ser modificada
        @return DataFrame modificado
        """
        if collum not in data_frame.columns:
            print(f"Aviso: Coluna '{collum}' não encontrada no DataFrame")
            return data_frame

        data_frame[collum] = (
            data_frame[collum].astype(str).str.replace(".", "", regex=False)
        )
        data_frame[collum] = data_frame[collum].str.replace(",", ".", regex=False)
        data_frame[collum] = pd.to_numeric(data_frame[collum], errors="coerce")

        return data_frame

    def consolidar_e_exportar(self, dataframes: List[pd.DataFrame], output_path: Path):
        """Consolida DataFrames e exporta para CSV"""
        if not dataframes:
            print("Nenhum dado para consolidar")
            return

        df_consolidado = pd.concat(dataframes, ignore_index=True)

        if "VL_SALDO_INICIAL" in df_consolidado.columns:
            df_consolidado = self.converter_monetario(
                df_consolidado, "VL_SALDO_INICIAL"
            )

        if "VL_SALDO_FINAL" in df_consolidado.columns:
            df_consolidado = self.converter_monetario(df_consolidado, "VL_SALDO_FINAL")

        df_consolidado = self.trimestre_ano(df_consolidado)
        if "DATA" in df_consolidado.columns:
            df_consolidado.drop("DATA", axis=1, inplace=True)

        df_consolidado["ValorDespesas"] = (
            df_consolidado["VL_SALDO_FINAL"] - df_consolidado["VL_SALDO_INICIAL"]
        )

        df_consolidado.drop("VL_SALDO_INICIAL", axis=1, inplace=True)
        df_consolidado.drop("VL_SALDO_FINAL", axis=1, inplace=True)

        df_consolidado.insert(0, "CNPJ", "PENDENTE")

        df_consolidado = df_consolidado.rename(
            columns={"REG_ANS": "RegistroANS", "DESCRICAO": "RazaoSocial"}
        )

        if "CD_CONTA_CONTABIL" in df_consolidado.columns:
            df_consolidado.drop("CD_CONTA_CONTABIL", axis=1, inplace=True)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.get_inconsistencias(df_consolidado)

        df_consolidado.to_csv(
            output_path,
            index=False,
            sep=";",
            encoding="utf-8-sig",
            decimal=".",
        )


if __name__ == "__main__":
    processor = DataProcessor()

    diretorio = Path("dados/extracted")

    dataframes = processor.processar_diretorio(diretorio)

    output = Path("dados/output/consolidado_despesas.csv")
    processor.consolidar_e_exportar(dataframes, output)
