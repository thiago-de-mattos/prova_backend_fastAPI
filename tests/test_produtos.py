import pytest


# ─────────────────────────────────────────────
# 1. Listar produtos quando o banco está vazio
# ─────────────────────────────────────────────
def test_listar_produtos_banco_vazio(client):
    response = client.get("/produtos")
    assert response.status_code == 200
    assert response.json() == []


# ─────────────────────────────────────────────
# 2. Criar produto e verificar persistência no banco
# ─────────────────────────────────────────────
def test_criar_produto_persistencia(client):
    payload = {"nome": "Notebook", "preco": 3500.00, "estoque": 5, "ativo": True}
    response = client.post("/produtos", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Notebook"
    assert data["preco"] == 3500.00
    assert data["estoque"] == 5
    assert data["ativo"] is True
    assert "id" in data


# ─────────────────────────────────────────────
# 3. Criar produto e verificar que aparece na listagem
# ─────────────────────────────────────────────
def test_criar_produto_aparece_na_listagem(client):
    payload = {"nome": "Teclado Mecânico", "preco": 250.00, "estoque": 20, "ativo": True}
    client.post("/produtos", json=payload)

    response = client.get("/produtos")
    assert response.status_code == 200
    nomes = [p["nome"] for p in response.json()]
    assert "Teclado Mecânico" in nomes


# ─────────────────────────────────────────────
# 4. Buscar produto por id — caso de sucesso
# ─────────────────────────────────────────────
def test_buscar_produto_por_id_sucesso(client, produto_existente):
    produto_id = produto_existente["id"]
    response = client.get(f"/produtos/{produto_id}")

    assert response.status_code == 200
    assert response.json()["id"] == produto_id
    assert response.json()["nome"] == produto_existente["nome"]


# ─────────────────────────────────────────────
# 5. Buscar produto com id inexistente — deve retornar 404
# ─────────────────────────────────────────────
def test_buscar_produto_id_inexistente(client):
    response = client.get("/produtos/99999")
    assert response.status_code == 404


# ─────────────────────────────────────────────
# 6. Deletar produto — deve retornar 204
# ─────────────────────────────────────────────
def test_deletar_produto_sucesso(client, produto_existente):
    produto_id = produto_existente["id"]
    response = client.delete(f"/produtos/{produto_id}")
    assert response.status_code == 204


# ─────────────────────────────────────────────
# 7. Deletar produto e confirmar remoção com GET subsequente
# ─────────────────────────────────────────────
def test_deletar_produto_confirmar_remocao(client, produto_existente):
    produto_id = produto_existente["id"]

    # Deleta o produto
    delete_response = client.delete(f"/produtos/{produto_id}")
    assert delete_response.status_code == 204

    # Confirma que não existe mais
    get_response = client.get(f"/produtos/{produto_id}")
    assert get_response.status_code == 404


# ─────────────────────────────────────────────
# 8. Deletar produto inexistente — deve retornar 404
# ─────────────────────────────────────────────
def test_deletar_produto_inexistente(client):
    response = client.delete("/produtos/99999")
    assert response.status_code == 404


# ─────────────────────────────────────────────
# 9. Teste parametrizado com payloads inválidos (status 422)
# ─────────────────────────────────────────────
@pytest.mark.parametrize("payload", [
    {"nome": "",    "preco": 10.0},           # nome vazio
    {"nome": "   ", "preco": 10.0},           # nome só espaços
    {"nome": "X",   "preco": 0.0},            # preco = zero
    {"nome": "X",   "preco": -5.0},           # preco negativo
    {"nome": "X"},                            # preco ausente
    {"preco": 10.0},                          # nome ausente
])
def test_criar_produto_payload_invalido(client, payload):
    response = client.post("/produtos", json=payload)
    assert response.status_code == 422


# ─────────────────────────────────────────────
# 10. Banco isolado entre execuções de testes
# ─────────────────────────────────────────────
def test_banco_isolado_entre_testes_parte1(client):
    """Cria um produto; o próximo teste não deve vê-lo."""
    payload = {"nome": "Produto Temporário", "preco": 1.0}
    response = client.post("/produtos", json=payload)
    assert response.status_code == 201


def test_banco_isolado_entre_testes_parte2(client):
    """Banco deve estar vazio — produto do teste anterior não persiste."""
    response = client.get("/produtos")
    assert response.status_code == 200
    assert response.json() == []


# ─────────────────────────────────────────────
# 11. Criar produto com valores padrão (estoque e ativo)
# ─────────────────────────────────────────────
def test_criar_produto_valores_padrao(client):
    payload = {"nome": "Produto Simples", "preco": 9.99}
    response = client.post("/produtos", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["estoque"] == 0
    assert data["ativo"] is True


# ─────────────────────────────────────────────
# 12. Listar múltiplos produtos criados
# ─────────────────────────────────────────────
def test_listar_multiplos_produtos(client):
    produtos = [
        {"nome": "Mouse", "preco": 80.0, "estoque": 15},
        {"nome": "Monitor", "preco": 1200.0, "estoque": 3},
        {"nome": "Headset", "preco": 300.0, "estoque": 7},
    ]
    for p in produtos:
        client.post("/produtos", json=p)

    response = client.get("/produtos")
    assert response.status_code == 200
    assert len(response.json()) == 3
