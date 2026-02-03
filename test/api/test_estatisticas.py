from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


class TestEstatisticasRoutes:
    @pytest.fixture(autouse=True)
    def clear_cache(self):
        from src.api.routes.estatisticas import _get_cached_estatisticas

        _get_cached_estatisticas.cache_clear()
        yield
        _get_cached_estatisticas.cache_clear()

    @patch("src.api.routes.estatisticas.execute_one")
    @patch("src.api.routes.estatisticas.execute_query")
    def test_obter_estatisticas_sucesso(self, mock_query, mock_one):
        mock_one.return_value = {
            "total_operadoras": 100,
            "total_registros_despesas": 5000,
            "soma_total_despesas": 1000000.00,
            "media_despesas": 200.00,
        }

        mock_query.return_value = [
            {"razao_social": "Operadora A", "uf": "SP", "total_despesas": 50000.00},
            {"razao_social": "Operadora B", "uf": "RJ", "total_despesas": 40000.00},
        ]

        response = client.get("/api/estatisticas")

        assert response.status_code == 200
        data = response.json()

        assert "total_operadoras" in data
        assert "total_registros_despesas" in data
        assert "soma_total_despesas" in data
        assert "media_despesas" in data
        assert "top_5_operadoras" in data

        assert data["total_operadoras"] == 100
        assert len(data["top_5_operadoras"]) == 2

    @patch("src.api.routes.estatisticas.execute_one")
    @patch("src.api.routes.estatisticas.execute_query")
    def test_obter_estatisticas_usa_cache(self, mock_query, mock_one):
        mock_one.return_value = {
            "total_operadoras": 100,
            "total_registros_despesas": 5000,
            "soma_total_despesas": 1000000.00,
            "media_despesas": 200.00,
        }

        mock_query.return_value = []

        response1 = client.get("/api/estatisticas")
        assert response1.status_code == 200

        response2 = client.get("/api/estatisticas")
        assert response2.status_code == 200

        assert mock_one.call_count == 1
        assert mock_query.call_count == 1

    @patch("src.api.routes.estatisticas.execute_one")
    @patch("src.api.routes.estatisticas.execute_query")
    def test_obter_estatisticas_banco_vazio(self, mock_query, mock_one):
        mock_one.return_value = {
            "total_operadoras": 0,
            "total_registros_despesas": 0,
            "soma_total_despesas": 0,
            "media_despesas": 0,
        }

        mock_query.return_value = []

        response = client.get("/api/estatisticas")

        assert response.status_code == 200
        data = response.json()
        assert data["total_operadoras"] == 0
        assert len(data["top_5_operadoras"]) == 0

    # GET /api/estatisticas/refresh

    @patch("src.api.routes.estatisticas.execute_one")
    @patch("src.api.routes.estatisticas.execute_query")
    def test_refresh_estatisticas(self, mock_query, mock_one):
        mock_one.return_value = {
            "total_operadoras": 150,
            "total_registros_despesas": 7000,
            "soma_total_despesas": 1500000.00,
            "media_despesas": 214.29,
        }

        mock_query.return_value = []

        response = client.get("/api/estatisticas/refresh")

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "cached_at" in data
        assert "data" in data
        assert "sucesso" in data["message"].lower()

    @patch("src.api.routes.estatisticas.execute_one")
    @patch("src.api.routes.estatisticas.execute_query")
    def test_refresh_limpa_cache_antigo(self, mock_query, mock_one):
        mock_one.return_value = {
            "total_operadoras": 100,
            "total_registros_despesas": 5000,
            "soma_total_despesas": 1000000.00,
            "media_despesas": 200.00,
        }
        mock_query.return_value = []

        response1 = client.get("/api/estatisticas")
        assert response1.json()["total_operadoras"] == 100

        mock_one.return_value = {
            "total_operadoras": 150,
            "total_registros_despesas": 7000,
            "soma_total_despesas": 1500000.00,
            "media_despesas": 214.29,
        }

        response2 = client.get("/api/estatisticas/refresh")
        assert response2.json()["data"]["total_operadoras"] == 150

        response3 = client.get("/api/estatisticas")
        assert response3.json()["total_operadoras"] == 150

    # GET /api/estatisticas/status

    @patch("src.api.routes.estatisticas.execute_one")
    @patch("src.api.routes.estatisticas.execute_query")
    def test_status_cache_vazio(self, mock_query, mock_one):
        response = client.get("/api/estatisticas/status")

        assert response.status_code == 200
        data = response.json()

        assert "cache_hits" in data
        assert "cache_misses" in data
        assert "cache_size" in data
        assert "is_valid" in data
        assert "current_time" in data

    @patch("src.api.routes.estatisticas.execute_one")
    @patch("src.api.routes.estatisticas.execute_query")
    def test_status_cache_populado(self, mock_query, mock_one):
        mock_one.return_value = {
            "total_operadoras": 100,
            "total_registros_despesas": 5000,
            "soma_total_despesas": 1000000.00,
            "media_despesas": 200.00,
        }
        mock_query.return_value = []

        client.get("/api/estatisticas")

        response = client.get("/api/estatisticas/status")

        assert response.status_code == 200
        data = response.json()

        assert data["cache_size"] >= 1
        assert data["cached_at"] is not None
        assert data["is_valid"] == True

    @patch("src.api.routes.estatisticas.execute_one")
    @patch("src.api.routes.estatisticas.execute_query")
    def test_status_mostra_hits_e_misses(self, mock_query, mock_one):
        mock_one.return_value = {
            "total_operadoras": 100,
            "total_registros_despesas": 5000,
            "soma_total_despesas": 1000000.00,
            "media_despesas": 200.00,
        }
        mock_query.return_value = []

        client.get("/api/estatisticas")

        response1 = client.get("/api/estatisticas/status")
        data1 = response1.json()
        initial_misses = data1["cache_misses"]

        client.get("/api/estatisticas")

        response2 = client.get("/api/estatisticas/status")
        data2 = response2.json()

        assert data2["cache_hits"] > data1["cache_hits"]


class TestCacheValidity:
    @pytest.fixture(autouse=True)
    def clear_cache(self):
        """Limpa cache antes de cada teste"""
        from src.api.routes.estatisticas import _get_cached_estatisticas

        _get_cached_estatisticas.cache_clear()
        yield
        _get_cached_estatisticas.cache_clear()

    @patch("src.api.routes.estatisticas.datetime")
    @patch("src.api.routes.estatisticas.execute_one")
    @patch("src.api.routes.estatisticas.execute_query")
    def test_cache_expira_apos_30_minutos(self, mock_query, mock_one, mock_datetime):
        tempo_inicial = datetime(2025, 1, 1, 10, 0, 0)
        tempo_expirado = datetime(2025, 1, 1, 10, 31, 0)  # 31 minutos depois

        mock_datetime.now.return_value = tempo_inicial

        mock_one.return_value = {
            "total_operadoras": 100,
            "total_registros_despesas": 5000,
            "soma_total_despesas": 1000000.00,
            "media_despesas": 200.00,
        }
        mock_query.return_value = []

        client.get("/api/estatisticas")
        call_count_inicial = mock_one.call_count

        mock_datetime.now.return_value = tempo_expirado

        client.get("/api/estatisticas")

        assert mock_one.call_count > call_count_inicial
