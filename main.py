from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os

from database import Base, engine, get_db
from models import Produto
from schemas import ProdutoCreate, ProdutoResponse

app = FastAPI(title="API de Gerenciamento de Produtos")


@app.get("/produtos", response_model=List[ProdutoResponse], status_code=200)
def listar_produtos(db: Session = Depends(get_db)):
    """Retorna lista de todos os produtos."""
    produtos = db.query(Produto).all()
    return produtos


@app.post("/produtos", response_model=ProdutoResponse, status_code=201)
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    """Cria um novo produto e retorna com id gerado."""
    db_produto = Produto(
        nome=produto.nome,
        preco=produto.preco,
        estoque=produto.estoque,
        ativo=produto.ativo,
    )
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto


@app.get("/produtos/{id}", response_model=ProdutoResponse, status_code=200)
def buscar_produto(id: int, db: Session = Depends(get_db)):
    """Retorna produto pelo id ou 404 se não existir."""
    produto = db.query(Produto).filter(Produto.id == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@app.delete("/produtos/{id}", status_code=204)
def deletar_produto(id: int, db: Session = Depends(get_db)):
    """Remove o produto ou 404 se não existir."""
    produto = db.query(Produto).filter(Produto.id == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(produto)
    db.commit()
    return None
