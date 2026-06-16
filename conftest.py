import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from main import app
from database import Base, get_db
from models import Produto

# URL do banco de testes (variável de ambiente ou padrão)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5433/produtos_test"
)

test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def client():
    """
    Fixture principal:
    (a) Cria as tabelas com Base.metadata.create_all
    (b) Usa app.dependency_overrides para substituir get_db
    (c) Usa yield do TestClient
    (d) Destrói tudo com Base.metadata.drop_all no teardown
    """
    # (a) Cria tabelas no banco de testes
    Base.metadata.create_all(bind=test_engine)

    # (b) Substitui a dependência get_db pelo banco de testes
    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # (c) yield do TestClient — testes rodam aqui
    with TestClient(app) as test_client:
        yield test_client

    # (d) Teardown: remove todas as tabelas para isolar entre execuções
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def produto_existente(client):
    """
    Fixture auxiliar que depende de client e já cria um produto no banco.
    Útil para testes que precisam de um produto pré-existente.
    """
    payload = {"nome": "Produto Inicial", "preco": 49.90, "estoque": 10, "ativo": True}
    response = client.post("/produtos", json=payload)
    assert response.status_code == 201
    return response.json()
