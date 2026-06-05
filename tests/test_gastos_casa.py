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


class TestGastosCasaRoutes:
    def test_get_empty(self, client):
        resp = client.get("/gastos-casa")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_create_gasto(self, client):
        resp = client.post("/gastos-casa", json={
            "descricao": "Mercado", "valor": 250.50,
            "categoriaId": "cat1", "data": "2026-06-01", "membroId": "mem1"
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["descricao"] == "Mercado"
        assert data["valor"] == 250.50

    def test_create_validation(self, client):
        resp = client.post("/gastos-casa", json={"descricao": "", "valor": -1})
        assert resp.status_code == 400

    def test_get_by_id(self, client):
        created = client.post("/gastos-casa", json={
            "descricao": "Farmácia", "valor": 80,
            "categoriaId": "cat1", "data": "2026-06-05", "membroId": "mem1"
        }).get_json()
        resp = client.get(f"/gastos-casa/{created['id']}")
        assert resp.status_code == 200
        assert resp.get_json()["descricao"] == "Farmácia"

    def test_not_found(self, client):
        assert client.get("/gastos-casa/nonexistent").status_code == 404

    def test_update(self, client):
        created = client.post("/gastos-casa", json={
            "descricao": "Old", "valor": 100,
            "categoriaId": "cat1", "data": "2026-06-01", "membroId": "mem1"
        }).get_json()
        resp = client.post(f"/gastos-casa/{created['id']}/update", json={"valor": 150})
        assert resp.status_code == 200
        assert resp.get_json()["valor"] == 150.0

    def test_delete(self, client):
        created = client.post("/gastos-casa", json={
            "descricao": "Delete", "valor": 50,
            "categoriaId": "cat1", "data": "2026-06-01", "membroId": "mem1"
        }).get_json()
        assert client.post(f"/gastos-casa/{created['id']}/delete").status_code == 200
        assert client.get(f"/gastos-casa/{created['id']}").status_code == 404

    def test_filter_by_mes(self, client):
        client.post("/gastos-casa", json={"descricao": "Jun", "valor": 100, "categoriaId": "cat1", "data": "2026-06-15", "membroId": "mem1"})
        client.post("/gastos-casa", json={"descricao": "Jul", "valor": 200, "categoriaId": "cat1", "data": "2026-07-01", "membroId": "mem1"})
        resp = client.get("/gastos-casa?mes=6&ano=2026")
        assert len(resp.get_json()) == 1
