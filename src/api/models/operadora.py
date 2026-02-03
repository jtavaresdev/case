from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class OperadoraBase(BaseModel):
    cnpj: str = Field(..., description="CNPJ da operadora (14 dígitos)")
    razao_social: str = Field(..., description="Razão social")
    modalidade: Optional[str] = Field(None, description="Modalidade da operadora")
    uf: Optional[str] = Field(None, description="UF da operadora")


class OperadoraList(OperadoraBase):
    qtd_registros: int = Field(0, description="Quantidade de registros de despesas")
    total_despesas: Decimal = Field(
        default=Decimal("0"), description="Total de despesas (R$)"
    )


class OperadoraDetail(OperadoraBase):
    registro_ans: str = Field(..., description="Registro ANS")
    created_at: str = Field(..., description="Data de criação no banco")


class DespesaItem(BaseModel):
    ano: int
    trimestre: int
    valor_despesas: Decimal
    descricao: Optional[str] = None


class OperadoraComDespesas(OperadoraDetail):
    despesas: list[DespesaItem] = []


class PaginatedResponse(BaseModel):
    data: list
    total: int
    page: int
    page_size: int
    total_pages: int


class EstatisticasResponse(BaseModel):
    total_operadoras: int
    total_registros_despesas: int
    soma_total_despesas: Decimal
    media_despesas: Decimal
    top_5_operadoras: list[dict]
