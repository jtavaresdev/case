import zipfile
from pathlib import Path
from typing import List, Optional

import pandas as pd

from validator import DataValidator


class DataProcessor:
    ## @brief Construtor da classe DataProcessor
    def __init__(self, separator=";"):
        self.separator = separator
        self.relatorio_cadop_path = Path("dados/raw/Relatorio_cadop")
        # Preciso de mais contexto para saber melhor keywords
        self.keywords = ["EVENTOS", "SINISTROS", "SINISTRO"]
        self.validador = DataValidator()

    ## @brief Lê arquivo .csv
    #  @param file_path Path do arquivo
    #  @return Optional de DataFrame
    def read_csv(self, file_path: Path) -> Optional[pd.DataFrame]:
        try:
            df = pd.read_csv(file_path, sep=self.separator)
            return df
        except Exception as e:
            print(f"Erro ao ler {file_path.name}: {e}")
            return None

    ## @brief Filtra linhas relacionadas self.keywords
    #  @param file_path Path do arquivo há ser filtrado
    #  @return Optional de DataFrame
    def filter_csv(self, file_path: Path) -> Optional[pd.DataFrame]:
        df = self.read_csv(file_path)
        if df is None:
            return None

        print(f"  → {len(df)} linhas lidas")

        if "DESCRICAO" not in df.columns:
            print("Sem coluna DESCRICAO")
            return None

        mask = pd.Series([False] * len(df))
        for keyword in self.keywords:
            mask |= df["DESCRICAO"].str.upper().str.contains(keyword, na=False)

        df_filtrado = df.loc[mask].copy()

        if df_filtrado.empty:
            print(f"Nenhum sinistro em {file_path.name}")
            return None

        print(f"{len(df_filtrado)} sinistros")
        return df_filtrado

    ## @brief Processa todos CSV recursivamentes.
    #  @param diretorio Path do diretorio raiz para busca recursiva
    def processar_diretorio(self, diretorio: Path) -> List[pd.DataFrame]:
        dataframes = []

        for arquivo in diretorio.rglob("*.csv"):
            df = self.filter_csv(arquivo)
            if df is not None:
                dataframes.append(df)

        print(f"Total: {len(dataframes)} arquivos processados com sucesso")
        return dataframes

    ## @brief Processa trimestre e ano
    #  @param data_frama Arquivo para ser processado
    def trimestre_ano(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        if "DATA" not in data_frame.columns:
            print("Nenhuma coluna chamada _DATA")
            return data_frame

        data_frame["DATA"] = pd.to_datetime(data_frame["DATA"], errors="coerce")

        data_frame["Ano"] = data_frame["DATA"].dt.year
        data_frame["Trimestre"] = data_frame["DATA"].dt.quarter

        return data_frame

    ## @brief Conversor de coluna para monetario.
    #  @param data_frame Arquivo para ser modificado.
    #  @param collum Nome da coluna para ser modificado.
    def converter_monetario(
        self, data_frame: pd.DataFrame, collum: str
    ) -> pd.DataFrame:
        if collum not in data_frame.columns:
            print(f"Aviso: Coluna '{collum}' não encontrada no DataFrame")
            return data_frame

        data_frame[collum] = (
            data_frame[collum].astype(str).str.replace(".", "", regex=False)
        )
        data_frame[collum] = data_frame[collum].str.replace(",", ".", regex=False)
        data_frame[collum] = pd.to_numeric(data_frame[collum], errors="coerce")

        return data_frame

    ## @brief Faz Join entre dois arquivos .csv
    #  @param df_principal Arquivo para ser persistido
    #  @param df_secundaria Arquivo para extrair informações
    #  @param collum_left Nome da coluna com a condição de junção
    #  @param collum_right Nome da coluna com a condição de junção
    #  @param columns_add Colunas para ser adicionados ao df_principal
    def join_registro_ans(
        self,
        df_principal: pd.DataFrame,
        df_secundaria: pd.DataFrame,
        collum_left: str,
        collum_right: str,
        columns_add: List[str],
    ) -> pd.DataFrame:
        colunas_selecionar = [collum_right] + columns_add
        df_registro_filtrado = df_secundaria[colunas_selecionar]

        df = df_principal.merge(
            df_registro_filtrado, left_on=collum_left, right_on=collum_right, how="left"
        )
        if collum_left != collum_right and collum_right in df.columns:
            df = df.drop(columns=[collum_right])

        if "CNPJ" in df.columns:
            df["CNPJ"] = df["CNPJ"].apply(
                lambda x: str(int(float(x)))
                if pd.notna(x) and str(x) != "nan"
                else "PENDENTE"
            )
        else:
            df["CNPJ"] = "PENDENTE"
        return df

    ## @brief Função para agregar dados
    #  @param data_frame Arquivo para ser agregado
    #  @param keys List[str] Lista de colunas para serem agrupados
    def agregar_csv(self, data_frame: pd.DataFrame, keys: List[str]):
        if not isinstance(keys, list):
            print(f"{keys} não é uma instância de List")
            return pd.DataFrame()
        if not keys:
            return data_frame

        df_agrupado = data_frame.groupby(keys, as_index=False).agg(
            Soma_Despesas=("ValorDespesas", "sum"),
            Desvio_Padrao_Despesas=("ValorDespesas", "std"),
        )

        return df_agrupado

    ## @brief Função para zipar arquivos da pasta output
    #  @param file_path Path para pasta com arquivos .csv
    #  @param file_name Nome para o arquivo zipado
    def zip_csv(self, file_path: Path, file_name: str):
        pasta = file_path

        with zipfile.ZipFile(file_name, "w", zipfile.ZIP_DEFLATED) as zipf:
            for arquivo in pasta.rglob("*.csv"):
                zipf.write(arquivo, arquivo.relative_to(pasta))
                print(f"Adicionado: {arquivo.name}")

    ## @brief Função para consolidar e exportar o .csv final
    #  @param dataframes List com Dataframes
    #  @param output_path Path para onde o .csv final vai ser salvado + nome do arquivo
    def consolidar_e_exportar(self, dataframes: List[pd.DataFrame], output_path: Path):
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

        df_consolidado = df_consolidado.rename(columns={"REG_ANS": "RegistroANS"})

        if "CD_CONTA_CONTABIL" in df_consolidado.columns:
            df_consolidado.drop("CD_CONTA_CONTABIL", axis=1, inplace=True)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        df_relatorio = self.read_csv(self.relatorio_cadop_path)
        if df_relatorio is None:
            print("Relatório CADOP não encontrado")
            return None

        df_consolidado = self.join_registro_ans(
            df_consolidado,
            df_relatorio,
            "RegistroANS",
            "REGISTRO_OPERADORA",
            ["CNPJ", "Razao_Social", "Modalidade", "UF"],
        )
        df_consolidado = self.validador.valid_collum_not_null(
            df_consolidado, "Razao_Social"
        )

        df_validos, df_invalidos = self.validador.validade_cnpjs(df_consolidado, "CNPJ")

        if len(df_invalidos) > 0:
            invalidos_path = output_path.parent / "cnpjs_invalidos.csv"
            df_invalidos, df_pendentes = self.validador.validate_collum_str(
                df_invalidos
            )

            if len(df_pendentes) > 0:
                pendentes_path = output_path.parent / "razao_social_pendentes.csv"

                colunas_pendentes = [
                    "RegistroANS",
                    "CNPJ",
                    "Razao_Social",
                    "Trimestre",
                    "Ano",
                    "ValorDespesas",
                ]

                df_pendentes[colunas_pendentes].to_csv(
                    pendentes_path,
                    index=False,
                    sep=";",
                    encoding="utf-8-sig",
                    decimal=".",
                )

            colunas_invalidos = [
                "RegistroANS",
                "CNPJ",
                "Razao_Social",
                "Trimestre",
                "Ano",
                "ValorDespesas",
            ]

            df_invalidos[colunas_invalidos].to_csv(
                invalidos_path,
                index=False,
                sep=";",
                encoding="utf-8-sig",
                decimal=".",
            )

        # df_consolidado = df_validos

        df_numeros_validos, df_numeros_invalidos = self.validador.validade_number(
            df_validos
        )
        if len(df_numeros_invalidos) > 0:
            numeros_invalidos_path = output_path.parent / "numeros_invalidos.csv"
            colunas_num = [
                "RegistroANS",
                "CNPJ",
                "Razao_Social",
                "Trimestre",
                "Ano",
                "ValorDespesas",
            ]
            df_numeros_invalidos[colunas_num].to_csv(
                numeros_invalidos_path,
                index=False,
                sep=";",
                encoding="utf-8-sig",
                decimal=".",
            )

        df_consolidado = df_numeros_validos

        df_consolidado = df_consolidado[
            [
                "RegistroANS",
                "CNPJ",
                "Razao_Social",
                "Trimestre",
                "Ano",
                "ValorDespesas",
                "Modalidade",
                "UF",
                "DESCRICAO",
            ]
        ]
        df_agrupado = self.agregar_csv(df_numeros_validos, ["UF", "Razao_Social"])
        df_agrupado.to_csv(
            output_path.parent / "despesas_agregadas.csv",
            index=False,
            sep=";",
            encoding="utf-8-sig",
            decimal=".",
        )

        df_consolidado.to_csv(
            output_path,
            index=False,
            sep=";",
            encoding="utf-8-sig",
            decimal=".",
        )
        self.zip_csv(output_path.parent, "Teste_{JoaoVictorTavares}.zip")


if __name__ == "__main__":
    processor = DataProcessor()

    diretorio = Path("dados/extracted")

    dataframes = processor.processar_diretorio(diretorio)

    output = Path("dados/output/consolidado_despesas.csv")
    processor.consolidar_e_exportar(dataframes, output)
