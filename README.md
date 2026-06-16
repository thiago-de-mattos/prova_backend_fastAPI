# API de Gerenciamento de Produtos — FastAPI + PostgreSQL + Docker

Atividade Avaliativa | Desenvolvimento de APIs com FastAPI

---

## Estrutura do Projeto

```
seu_repositorio/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── conftest.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── README.md
└── tests/
    ├── __init__.py
    └── test_produtos.py
```

---

## Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.11+ (para rodar os testes localmente, opcional)

---

## 1. Subindo o banco de testes com Docker

Antes de rodar os testes, suba o banco de testes:

```bash
docker-compose up -d db_test
```

Confirme que o container está **healthy**:

```bash
docker-compose ps
```

A coluna `Status` deve mostrar `healthy` para o serviço `db_test`.

Para subir também o banco de desenvolvimento e a API:

```bash
docker-compose up -d
```

---

## 2. Instalando dependências (ambiente local)

```bash
pip install -r requirements.txt
```

---

## 3. Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/produtos_db` | Banco de desenvolvimento |
| `TEST_DATABASE_URL` | `postgresql://postgres:postgres@localhost:5433/produtos_test` | Banco exclusivo para testes |

---

## 4. Executando os testes

### Comando padrão

```bash
pytest
```

### Com saída verbosa (recomendado para debug)

```bash
pytest -v -x
```

### Com cobertura de código

```bash
pytest --cov=main --cov-report=term-missing -v
```

### Comando de verificação final (rode antes de entregar)

```bash
docker-compose up -d db_test && pytest --cov=main -v
```

---

## 5. Saída esperada do pytest

```
tests/test_produtos.py::test_listar_produtos_banco_vazio PASSED
tests/test_produtos.py::test_criar_produto_persistencia PASSED
tests/test_produtos.py::test_criar_produto_aparece_na_listagem PASSED
tests/test_produtos.py::test_buscar_produto_por_id_sucesso PASSED
tests/test_produtos.py::test_buscar_produto_id_inexistente PASSED
tests/test_produtos.py::test_deletar_produto_sucesso PASSED
tests/test_produtos.py::test_deletar_produto_confirmar_remocao PASSED
tests/test_produtos.py::test_deletar_produto_inexistente PASSED
tests/test_produtos.py::test_criar_produto_payload_invalido[...] PASSED (x6)
tests/test_produtos.py::test_banco_isolado_entre_testes_parte1 PASSED
tests/test_produtos.py::test_banco_isolado_entre_testes_parte2 PASSED
tests/test_produtos.py::test_criar_produto_valores_padrao PASSED
tests/test_produtos.py::test_listar_multiplos_produtos PASSED

========= 18 passed in X.XXs =========
```

---

## 6. Endpoints da API

| Método | Rota | Status | Comportamento |
|---|---|---|---|
| GET | `/produtos` | 200 | Retorna lista de todos os produtos |
| POST | `/produtos` | 201 | Cria um novo produto e retorna com id gerado |
| GET | `/produtos/{id}` | 200 / 404 | Retorna produto pelo id ou 404 se não existir |
| DELETE | `/produtos/{id}` | 204 / 404 | Remove o produto ou 404 se não existir |

Documentação interativa disponível em: `http://localhost:8000/docs`

---

## 7. Como o isolamento entre testes funciona

Cada teste recebe um banco **completamente limpo**, graças à fixture `client` definida em `conftest.py`:

1. **Setup** — `Base.metadata.create_all(bind=test_engine)` cria as tabelas no banco de testes antes de cada teste.
2. **Override** — `app.dependency_overrides[get_db]` substitui a dependência de sessão para apontar ao banco de testes (`localhost:5433`), nunca ao banco de desenvolvimento.
3. **yield** — o `TestClient` é entregue ao teste; tudo que acontece dentro do teste usa o banco isolado.
4. **Teardown** — após o teste, `Base.metadata.drop_all(bind=test_engine)` destrói todas as tabelas, garantindo que nenhum dado vaze para o próximo teste.

Isso significa que a ordem dos testes **não importa** — cada um começa do zero, exatamente como acontece em produção com migrations.
