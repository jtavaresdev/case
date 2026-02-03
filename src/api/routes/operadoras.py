import math
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..config import get_settings
from ..database import execute_one, execute_query
from ..models.operadora import (
    DespesaItem,
    OperadoraComDespesas,
    OperadoraDetail,
    OperadoraList,
    PaginatedResponse,
)

router = APIRouter(prefix="/api/operadoras", tags=["Operadoras"])
settings = get_settings()


## @brief Lista operadoras com paginação e busca
#  @param page Número da página (começa em 1)
#  @param limit Quantidade de itens por página (máximo: 100)
#  @param search Busca por razão social ou CNPJ (opcional)
#  @return PaginatedResponse com dados paginados de operadoras
@router.get("", response_model=PaginatedResponse)
async def listar_operadoras(
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(20, ge=1, le=100, description="Itens por página"),
    search: Optional[str] = Query(None, description="Busca por razão social ou CNPJ"),
):
    offset = (page - 1) * limit

    where_clause = ""
    params = []

    if search:
        where_clause = "WHERE o.razao_social ILIKE %s OR o.cnpj LIKE %s"
        search_param = f"%{search}%"
        params = [search_param, search_param]

    count_query = f"""
        SELECT COUNT(DISTINCT o.cnpj) as total
        FROM operadoras o
        {where_clause}
    """

    total_result = execute_one(count_query, tuple(params))

    if not total_result:
        total = 0
    else:
        total = (
            total_result.get("total", 0)
            if isinstance(total_result, dict)
            else total_result[0]
            if total_result
            else 0
        )

    data_query = f"""
        SELECT
            o.cnpj,
            o.razao_social,
            o.modalidade,
            o.uf,
            COUNT(d.id) as qtd_registros,
            COALESCE(SUM(d.valor_despesas), 0) as total_despesas
        FROM operadoras o
        LEFT JOIN despesas d ON o.cnpj = d.cnpj
        {where_clause}
        GROUP BY o.cnpj, o.razao_social, o.modalidade, o.uf
        ORDER BY o.razao_social
        LIMIT %s OFFSET %s
    """

    params_with_pagination = params + [limit, offset]
    resultados = execute_query(data_query, tuple(params_with_pagination))

    return {
        "data": resultados,
        "total": total,
        "page": page,
        "page_size": limit,
        "total_pages": math.ceil(total / limit),
    }


## @brief Retorna detalhes de uma operadora específica
#  @param cnpj CNPJ da operadora (14 dígitos, apenas números)
#  @return OperadoraDetail com informações detalhadas da operadora
@router.get("/{cnpj}", response_model=OperadoraDetail)
async def obter_operadora(cnpj: str):
    cnpj_limpo = "".join(filter(str.isdigit, cnpj))

    if len(cnpj_limpo) != 14:
        raise HTTPException(status_code=400, detail="CNPJ deve ter 14 dígitos")

    query = """
        SELECT
            cnpj,
            registro_ans,
            razao_social,
            modalidade,
            uf,
            created_at::text
        FROM operadoras
        WHERE cnpj = %s
    """

    resultado = execute_one(query, (cnpj_limpo,))

    if not resultado:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")

    return resultado


## @brief Retorna histórico completo de despesas de uma operadora
#  @param cnpj CNPJ da operadora (14 dígitos)
#  @return OperadoraComDespesas com dados da operadora e suas despesas
@router.get("/{cnpj}/despesas", response_model=OperadoraComDespesas)
async def obter_despesas_operadora(cnpj: str):
    cnpj_limpo = "".join(filter(str.isdigit, cnpj))

    if len(cnpj_limpo) != 14:
        raise HTTPException(status_code=400, detail="CNPJ deve ter 14 dígitos")

    operadora = execute_one(
        """
        SELECT
            cnpj,
            registro_ans,
            razao_social,
            modalidade,
            uf,
            created_at::text
        FROM operadoras
        WHERE cnpj = %s
    """,
        (cnpj_limpo,),
    )

    if not operadora:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")

    despesas = execute_query(
        """
        SELECT
            ano,
            trimestre,
            valor_despesas,
            descricao
        FROM despesas
        WHERE cnpj = %s
        ORDER BY ano DESC, trimestre DESC
    """,
        (cnpj_limpo,),
    )

    return {**operadora, "despesas": despesas}
