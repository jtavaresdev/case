from datetime import datetime, timedelta
from functools import lru_cache

from fastapi import APIRouter

from ..database import execute_one, execute_query
from ..models.operadora import EstatisticasResponse

router = APIRouter(prefix="/api/estatisticas", tags=["Estatísticas"])


## @brief Cache em memória com LRU (Least Recently Used) que armazena as estatísticas calculadas
#  @return Dicionário contendo as estatísticas calculadas e timestamp do cache
@lru_cache(maxsize=1)
def _get_cached_estatisticas():
    stats = execute_one(
        """
        SELECT
            COUNT(DISTINCT o.cnpj) as total_operadoras,
            COUNT(d.id) as total_registros_despesas,
            COALESCE(SUM(d.valor_despesas), 0) as soma_total_despesas,
            COALESCE(AVG(d.valor_despesas), 0) as media_despesas
        FROM operadoras o
        LEFT JOIN despesas d ON o.cnpj = d.cnpj
    """,
        (),
    )

    top_5 = execute_query(
        """
        SELECT
            o.razao_social,
            o.uf,
            SUM(d.valor_despesas) as total_despesas
        FROM operadoras o
        JOIN despesas d ON o.cnpj = d.cnpj
        GROUP BY o.cnpj, o.razao_social, o.uf
        ORDER BY total_despesas DESC
        LIMIT 5
    """,
        (),
    )

    return {"data": {**stats, "top_5_operadoras": top_5}, "cached_at": datetime.now()}


## @brief Verifica se o cache ainda é válido com base no tempo decorrido
#  @param cached_data Dados retornados por _get_cached_estatisticas()
#  @param minutos_validos Tempo de validade do cache em minutos
#  @return True se o cache for válido, False caso contrário
def _is_cache_valid(cached_data, minutos_validos=30):
    if not cached_data:
        return False

    tempo_passado = datetime.now() - cached_data["cached_at"]
    limite_validade = timedelta(minutes=minutos_validos)

    return tempo_passado < limite_validade


## @brief Retorna estatísticas gerais do sistema com cache de 30 minutos
#  @return EstatísticasResponse contendo:
@router.get("", response_model=EstatisticasResponse)
async def obter_estatisticas():
    cached = _get_cached_estatisticas()

    if not _is_cache_valid(cached, minutos_validos=30):
        _get_cached_estatisticas.cache_clear()
        cached = _get_cached_estatisticas()

    return cached["data"]


## @brief Endpoint para forçar atualização do cache manualmente
#  @return Dicionário com mensagem de sucesso, timestamp e dados atualizados
@router.get("/refresh")
async def refresh_estatisticas():
    _get_cached_estatisticas.cache_clear()
    cached = _get_cached_estatisticas()

    return {
        "message": "Cache atualizado com sucesso",
        "cached_at": cached["cached_at"].isoformat(),
        "data": cached["data"],
    }


## @brief Retorna informações sobre o estado atual do cache
#  @return Dicionário com métricas do cache e status de validade
@router.get("/status")
async def status_cache():
    cached = _get_cached_estatisticas()
    cache_info = _get_cached_estatisticas.cache_info()

    return {
        "cache_hits": cache_info.hits,
        "cache_misses": cache_info.misses,
        "cache_size": cache_info.currsize,
        "cached_at": cached["cached_at"].isoformat() if cached else None,
        "is_valid": _is_cache_valid(cached) if cached else False,
        "current_time": datetime.now().isoformat(),
    }
