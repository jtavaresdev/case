import pandas as pd
import pytest

from src.data.validator import DataValidator


class TestDataValidator:
    @pytest.fixture
    def validator(self):
        return DataValidator()

    def test_verify_cnpj_valido(self, validator):
        cnpj = "00000000000191"
        assert validator.verify_cnpj(cnpj) == True

    def test_verify_cnpj_invalido_tamanho(self, validator):
        cnpj = "123456789"
        assert validator.verify_cnpj(cnpj) == False

    def test_verify_cnpj_sequencia_repetida(self, validator):
        cnpj = "11111111111111"
        assert validator.verify_cnpj(cnpj) == False

    def test_verify_cnpj_com_letras(self, validator):
        cnpj = "1234567890123A"
        assert validator.verify_cnpj(cnpj) == False

    def test_valid_collum_not_null_preenche_nulos(self, validator):
        df = pd.DataFrame({"Nome": [None, "João", None]})
        resultado = validator.valid_collum_not_null(df, "Nome")

        assert resultado["Nome"].iloc[0] == "PENDENTE"
        assert resultado["Nome"].iloc[1] == "João"
        assert resultado["Nome"].iloc[2] == "PENDENTE"

    def test_valid_collum_not_null_coluna_inexistente(self, validator):
        df = pd.DataFrame({"Nome": ["João"]})
        resultado = validator.valid_collum_not_null(df, "Idade")

        assert "Idade" not in resultado.columns
        assert len(resultado) == 1

    def test_validade_cnpjs_separa_corretamente(self, validator, sample_dataframe):
        validos, invalidos = validator.validade_cnpjs(sample_dataframe, "CNPJ")

        assert len(validos) >= 0
        assert len(invalidos) >= 0
        assert len(validos) + len(invalidos) == len(sample_dataframe)

    def test_validate_collum_str_remove_pendentes(self, validator):
        df = pd.DataFrame(
            {"Razao_Social": ["Empresa A", "PENDENTE", None, "Empresa B"]}
        )

        validos, invalidos = validator.validate_collum_str(df, "Razao_Social")

        assert len(validos) == 2
        assert len(invalidos) == 2

    def test_validade_number_separa_negativos(self, validator, sample_dataframe):
        validos, invalidos = validator.validade_number(
            sample_dataframe, "ValorDespesas"
        )

        assert all(validos["ValorDespesas"] >= 0)
        assert all(invalidos["ValorDespesas"] < 0)
