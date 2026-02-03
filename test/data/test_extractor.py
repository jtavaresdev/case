from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.data.extractor import DataExtractor


class TestDataExtractor:
    @pytest.fixture
    def extractor(self, temp_dir):
        return DataExtractor(
            base_url="https://example.com",
            raw_dir=str(temp_dir / "raw"),
            output_dir=str(temp_dir / "output"),
            extract_dir=str(temp_dir / "extracted"),
        )

    def test_diretorios_criados(self, extractor):
        assert extractor.raw_dir.exists()
        assert extractor.output_dir.exists()
        assert extractor.extract_dir.exists()

    @patch("requests.get")
    def test_baixar_arquivo_sucesso(self, mock_get, extractor):
        # Mock da resposta HTTP
        mock_response = Mock()
        mock_response.content = b"conteudo_teste"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        resultado = extractor.baixar_arquivo(
            "https://example.com/arquivo.zip", "arquivo.zip"
        )

        assert resultado is not None
        assert resultado.exists()
        assert resultado.name == "arquivo.zip"

    def test_extrair_zip_sucesso(self, extractor, temp_dir):
        import zipfile

        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("arquivo.txt", "conteudo")

        resultado = extractor.extrair_zip(zip_path)

        assert resultado is not None
        assert len(resultado) == 1
        assert resultado[0].name == "arquivo.txt"
