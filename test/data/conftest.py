import shutil
import tempfile
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def temp_dir():
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_csv(temp_dir):
    csv_path = temp_dir / "test.csv"
    data = {
        "DATA": ["2025-01-01", "2025-04-01"],
        "REG_ANS": ["123456", "789012"],
        "DESCRICAO": ["EVENTOS CONHECIDOS", "SINISTROS"],
        "VL_SALDO_INICIAL": ["1000,50", "2000,75"],
        "VL_SALDO_FINAL": ["1500,50", "2500,75"],
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_path, sep=";", index=False)
    return csv_path


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame(
        {
            "CNPJ": ["12345678901234", "98765432109876", "PENDENTE"],
            "Razao_Social": ["Operadora A", None, "Operadora C"],
            "ValorDespesas": [1000.0, -500.0, 0.0],
        }
    )
