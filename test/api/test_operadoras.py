from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


class TestOperadorasRoutes:
    # GET /api/operadoras

    @patch("src.api.routes.operadoras.execute_one")
    @patch("src.api.routes.operadoras.execute_query")
    def test_listar_operadoras_sucesso(self, mock_query, mock_one):
        mock_one.return_value = {"total": 100}

        mock_query.return_value = [
            {
                "cnpj": "12345678901234",
                "razao_social": "Operadora Teste",
                "modalidade": "Seguradora",
                "uf": "SP",
                "qtd_registros": 10,
                "total_despesas": 50000.00,
            }
        ]

        response = client.get("/api/operadoras?page=1&limit=20")

        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data

        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["total"] == 100
        assert len(data["data"]) == 1

    @patch("src.api.routes.operadoras.execute_one")
    @patch("src.api.routes.operadoras.execute_query")
    def test_listar_operadoras_com_busca(self, mock_query, mock_one):
        mock_one.return_value = {"total": 1}
        mock_query.return_value = [
            {
                "cnpj": "12345678901234",
                "razao_social": "Unimed",
                "modalidade": "Cooperativa",
                "uf": "SP",
                "qtd_registros": 5,
                "total_despesas": 10000.00,
            }
        ]

        response = client.get("/api/operadoras?search=unimed")

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert "Unimed" in data["data"][0]["razao_social"]

    @patch("src.api.routes.operadoras.execute_one")
    @patch("src.api.routes.operadoras.execute_query")
    def test_listar_operadoras_vazio(self, mock_query, mock_one):
        mock_one.return_value = {"total": 0}
        mock_query.return_value = []

        response = client.get("/api/operadoras")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["data"]) == 0

    def test_listar_operadoras_parametros_invalidos(self):
        """Testa validação de parâmetros inválidos"""
        response = client.get("/api/operadoras?page=0")
        assert response.status_code == 422

        response = client.get("/api/operadoras?limit=200")
        assert response.status_code == 422

    # GET /api/operadoras/{cnpj}

    @patch("src.api.routes.operadoras.execute_one")
    def test_obter_operadora_sucesso(self, mock_one):
        mock_one.return_value = {
            "cnpj": "12345678901234",
            "registro_ans": "123456",
            "razao_social": "Operadora Teste",
            "modalidade": "Seguradora",
            "uf": "SP",
            "created_at": "2025-01-01",
        }

        response = client.get("/api/operadoras/12345678901234")

        assert response.status_code == 200
        data = response.json()
        assert data["cnpj"] == "12345678901234"
        assert data["razao_social"] == "Operadora Teste"

    @patch("src.api.routes.operadoras.execute_one")
    def test_obter_operadora_nao_encontrada(self, mock_one):
        mock_one.return_value = None

        response = client.get("/api/operadoras/99999999999999")

        assert response.status_code == 404
        assert "não encontrada" in response.json()["detail"].lower()

    def test_obter_operadora_cnpj_invalido(self):
        response = client.get("/api/operadoras/123")

        assert response.status_code == 400
        assert "14 dígitos" in response.json()["detail"].lower()

    def test_obter_operadora_cnpj_com_formatacao(self):
        """Testa CNPJ formatado (com pontos e barras)"""
        response = client.get("/api/operadoras/12.345.678/9012-34")

        assert response.status_code in [200, 404]

    # GET /api/operadoras/{cnpj}/despesas

    @patch("src.api.routes.operadoras.execute_one")
    @patch("src.api.routes.operadoras.execute_query")
    def test_obter_despesas_operadora_sucesso(self, mock_query, mock_one):
        mock_one.return_value = {
            "cnpj": "12345678901234",
            "registro_ans": "123456",
            "razao_social": "Operadora Teste",
            "modalidade": "Seguradora",
            "uf": "SP",
            "created_at": "2025-01-01",
        }

        mock_query.return_value = [
            {
                "ano": 2025,
                "trimestre": 1,
                "valor_despesas": 10000.00,
                "descricao": "EVENTOS",
            },
            {
                "ano": 2024,
                "trimestre": 4,
                "valor_despesas": 8000.00,
                "descricao": "SINISTROS",
            },
        ]

        response = client.get("/api/operadoras/12345678901234/despesas")

        assert response.status_code == 200
        data = response.json()

        assert data["cnpj"] == "12345678901234"
        assert "despesas" in data
        assert len(data["despesas"]) == 2
        assert data["despesas"][0]["ano"] == 2025

    @patch("src.api.routes.operadoras.execute_one")
    def test_obter_despesas_operadora_nao_encontrada(self, mock_one):
        mock_one.return_value = None

        response = client.get("/api/operadoras/99999999999999/despesas")

        assert response.status_code == 404

    @patch("src.api.routes.operadoras.execute_one")
    @patch("src.api.routes.operadoras.execute_query")
    def test_obter_despesas_operadora_sem_despesas(self, mock_query, mock_one):
        mock_one.return_value = {
            "cnpj": "12345678901234",
            "registro_ans": "123456",
            "razao_social": "Operadora Nova",
            "modalidade": "Seguradora",
            "uf": "SP",
            "created_at": "2025-01-01",
        }

        mock_query.return_value = []

        response = client.get("/api/operadoras/12345678901234/despesas")

        assert response.status_code == 200
        data = response.json()
        assert len(data["despesas"]) == 0
