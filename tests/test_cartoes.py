import pytest
import tempfile
from app import create_app


@pytest.fixture
def client():
    tmp = tempfile.mkdtemp()
    app = create_app({"TESTING": True, "DATA_DIR": tmp})
    with app.test_client() as c:
        yield c
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)


class TestCartoesRoutes:
    def test_get_empty(self, client):
        assert client.get("/cartoes").get_json() == []

    def test_create_fatura(self, client):
        resp = client.post("/cartoes", json={
            "descricao": "Amazon", "valor": 150.00,
            "parcela": 1, "totalParcelas": 3,
            "bandeira": "Visa", "vencimento": "2026-07-10"
        })
        assert resp.status_code == 201
        d = resp.get_json()
        assert d["descricao"] == "Amazon"
        assert d["bandeira"] == "Visa"

    def test_create_validation(self, client):
        resp = client.post("/cartoes", json={"descricao": "", "valor": -1})
        assert resp.status_code == 400

    def test_get_by_id(self, client):
        created = client.post("/cartoes", json={
            "descricao": "Netflix", "valor": 55.90,
            "parcela": 1, "totalParcelas": 1,
            "bandeira": "Mastercard", "vencimento": "2026-07-05"
        }).get_json()
        resp = client.get(f"/cartoes/{created['id']}")
        assert resp.get_json()["descricao"] == "Netflix"

    def test_not_found(self, client):
        assert client.get("/cartoes/nonexistent").status_code == 404

    def test_update(self, client):
        created = client.post("/cartoes", json={
            "descricao": "Spotify", "valor": 21.90,
            "parcela": 1, "totalParcelas": 1,
            "bandeira": "Visa", "vencimento": "2026-07-01"
        }).get_json()
        resp = client.put(f"/cartoes/{created['id']}", json={"valor": 25.90})
        assert resp.status_code == 200
        assert resp.get_json()["valor"] == 25.90

    def test_create_with_responsavel(self, client):
        resp = client.post("/cartoes", json={
            "descricao": "Mercado", "valor": 300,
            "parcela": 1, "totalParcelas": 1,
            "bandeira": "Visa", "vencimento": "2026-07-10",
            "responsavel": "Gabriel"
        })
        assert resp.status_code == 201
        d = resp.get_json()
        assert d["responsavel"] == "Gabriel"

    def test_create_default_responsavel(self, client):
        resp = client.post("/cartoes", json={
            "descricao": "Mercado", "valor": 300,
            "parcela": 1, "totalParcelas": 1,
            "bandeira": "Visa", "vencimento": "2026-07-10"
        })
        assert resp.status_code == 201
        d = resp.get_json()
        assert d.get("responsavel") is None

    def test_delete(self, client):
        created = client.post("/cartoes", json={
            "descricao": "Delete", "valor": 100,
            "parcela": 1, "totalParcelas": 1,
            "bandeira": "Visa", "vencimento": "2026-07-01"
        }).get_json()
        resp = client.delete(f"/cartoes/{created['id']}")
        assert resp.status_code == 200
        assert client.get(f"/cartoes/{created['id']}").status_code == 404



class TestImportFatura:
    def test_parse_text(self, client):
        resp = client.post("/cartoes/parse", json={"text": "14/04 Steam 02/03 27,26"})
        assert resp.status_code == 200
        itens = resp.get_json()
        assert len(itens) == 1
        assert itens[0]["descricao"] == "Steam"
        assert itens[0]["valor"] == 27.26

    def test_parse_multiplas_linhas(self, client):
        texto = "11/04 RAIA DROGASIL SA 02/02 103,42\n20/04 PANIFICADORA ALADIM LT 38,93"
        resp = client.post("/cartoes/parse", json={"text": texto})
        assert resp.status_code == 200
        itens = resp.get_json()
        assert len(itens) == 2

    def test_parse_texto_vazio(self, client):
        resp = client.post("/cartoes/parse", json={"text": ""})
        assert resp.get_json() == []

    def test_import(self, client):
        itens = [{"descricao": "Steam", "valor": 27.26, "dataCompra": "14/04",
                  "parcelaAtual": 2, "totalParcelas": 3, "responsavel": "Gabriel"}]
        resp = client.post("/cartoes/import", json={
            "itens": itens, "bandeira": "Elo", "vencimento": "2026-07-15",
            "categoriaId": "cat1"
        })
        assert resp.status_code == 201
        dados = resp.get_json()
        assert len(dados) == 1
        assert dados[0]["descricao"] == "Steam"
        assert dados[0]["bandeira"] == "Elo"
        assert dados[0]["vencimento"] == "2026-07-15"
        assert dados[0]["responsavel"] == "Gabriel"

    def test_import_default_responsavel(self, client):
        itens = [{"descricao": "Steam", "valor": 27.26}]
        resp = client.post("/cartoes/import", json={
            "itens": itens, "bandeira": "Elo", "vencimento": "2026-07-15"
        })
        assert resp.status_code == 201
        assert resp.get_json()[0]["responsavel"] == "Ambos"

    def test_import_sem_itens(self, client):
        resp = client.post("/cartoes/import", json={})
        assert resp.status_code == 400
