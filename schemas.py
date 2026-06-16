from pydantic import BaseModel, field_validator
from typing import Optional


class ProdutoCreate(BaseModel):
    nome: str
    preco: float
    estoque: int = 0
    ativo: bool = True

    @field_validator("nome")
    @classmethod
    def nome_nao_vazio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("O nome não pode ser vazio")
        return v

    @field_validator("preco")
    @classmethod
    def preco_positivo(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("O preço deve ser maior que zero")
        return v


class ProdutoResponse(BaseModel):
    id: int
    nome: str
    preco: float
    estoque: int
    ativo: bool

    model_config = {"from_attributes": True}
