from pathlib import Path

import pandas as pd
import pytest

from src.data.processor import DataProcessor


class TestDataProcessor:
    @pytest.fixture
    def processor(self):
        return DataProcessor()

    def test_read_csv_sucesso(self, processor, sample_csv):
        df = processor.read_csv(sample_csv)

        assert df is not None
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "DESCRICAO" in df.columns

    def test_read_csv_arquivo_inexistente(self, processor, temp_dir):
        arquivo_falso = temp_dir / "nao_existe.csv"
        df = processor.read_csv(arquivo_falso)

        assert df is None

    def test_filter_csv_encontra_keywords(self, processor, sample_csv):
        df = processor.filter_csv(sample_csv)

        assert df is not None
        assert len(df) == 2

    def test_filter_csv_sem_coluna_descricao(self, processor, temp_dir):
        csv_path = temp_dir / "sem_descricao.csv"
        pd.DataFrame({"Outro": [1, 2]}).to_csv(csv_path, sep=";", index=False)

        df = processor.filter_csv(csv_path)
        assert df is None

    def test_converter_monetario(self, processor):
        df = pd.DataFrame({"Valor": ["1.000,50", "2.500,75", "100,00"]})

        resultado = processor.converter_monetario(df, "Valor")

        assert resultado["Valor"].iloc[0] == 1000.50
        assert resultado["Valor"].iloc[1] == 2500.75
        assert resultado["Valor"].iloc[2] == 100.00

    def test_converter_monetario_coluna_inexistente(self, processor):
        df = pd.DataFrame({"Outro": [1, 2]})
        resultado = processor.converter_monetario(df, "Valor")

        assert "Valor" not in resultado.columns

    def test_trimestre_ano_extrai_corretamente(self, processor):
        """Testa extração de trimestre e ano"""
        df = pd.DataFrame(
            {"DATA": ["2025-01-15", "2025-04-20", "2025-07-10", "2025-10-05"]}
        )

        resultado = processor.trimestre_ano(df)

        assert list(resultado["Trimestre"]) == [1, 2, 3, 4]
        assert all(resultado["Ano"] == 2025)

    def test_join_registro_ans_sucesso(self, processor):
        df_principal = pd.DataFrame(
            {"RegistroANS": ["123", "456"], "Valor": [100, 200]}
        )

        df_secundario = pd.DataFrame(
            {
                "REGISTRO_OPERADORA": ["123", "456"],
                "CNPJ": [11111111111111, 22222222222222],
                "Nome": ["Empresa A", "Empresa B"],
            }
        )

        resultado = processor.join_registro_ans(
            df_principal,
            df_secundario,
            "RegistroANS",
            "REGISTRO_OPERADORA",
            ["CNPJ", "Nome"],
        )

        assert "CNPJ" in resultado.columns
        assert "Nome" in resultado.columns
        assert len(resultado) == 2

    def test_join_registro_ans_sem_match(self, processor):
        df_principal = pd.DataFrame({"RegistroANS": ["999"], "Valor": [100]})

        df_secundario = pd.DataFrame(
            {
                "REGISTRO_OPERADORA": ["123"],
                "CNPJ": [11111111111111],
                "Nome": ["Empresa A"],
            }
        )

        resultado = processor.join_registro_ans(
            df_principal,
            df_secundario,
            "RegistroANS",
            "REGISTRO_OPERADORA",
            ["CNPJ", "Nome"],
        )

        assert resultado["CNPJ"].iloc[0] == "PENDENTE"

    def test_agregar_csv(self, processor):
        """Testa agregação de dados"""
        df = pd.DataFrame({"UF": ["SP", "SP", "RJ"], "ValorDespesas": [100, 200, 300]})

        resultado = processor.agregar_csv(df, ["UF"])

        assert len(resultado) == 2
        assert "Soma_Despesas" in resultado.columns
        assert resultado[resultado["UF"] == "SP"]["Soma_Despesas"].values[0] == 300
