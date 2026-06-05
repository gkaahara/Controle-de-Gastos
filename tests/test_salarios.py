import pytest
import tempfile
import os
from app import create_app
from app.json_store import JsonStore


@pytest.fixture
def store():
    tmp = tempfile.mkdtemp()
    filepath = os.path.join(tmp, "salarios.json")
    s = JsonStore(filepath)
    yield s
    if os.path.exists(filepath):
        os.remove(filepath)
    os.rmdir(tmp)


@pytest.fixture
def client():
    tmp = tempfile.mkdtemp()
    app = create_app({"TESTING": True, "DATA_DIR": tmp})
    with app.test_client() as c:
        yield c
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)


class TestSalariosRoutes:
    def test_get_salarios_empty(self, client):
        resp = client.get("/salarios")
        assert resp.status_code == 200
        assert resp.is_json
        assert resp.get_json() == []

    def test_create_salario(self, client):
        resp = client.post("/salarios", json={
            "membroId": "mem1", "valor": 5000.00, "mes": 6, "ano": 2026
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["membroId"] == "mem1"
        assert data["valor"] == 5000.00
        assert data["mes"] == 6
        assert data["ano"] == 2026

    def test_create_salario_validation(self, client):
        resp = client.post("/salarios", json={"membroId": "", "valor": -1, "mes": 13, "ano": 1800})
        assert resp.status_code == 400

    def test_get_salario_by_id(self, client):
        created = client.post("/salarios", json={
            "membroId": "mem1", "valor": 3000, "mes": 6, "ano": 2026
        }).get_json()
        resp = client.get(f"/salarios/{created['id']}")
        assert resp.status_code == 200
        assert resp.get_json()["valor"] == 3000.0

    def test_get_salario_not_found(self, client):
        resp = client.get("/salarios/nonexistent")
        assert resp.status_code == 404

    def test_update_salario(self, client):
        created = client.post("/salarios", json={
            "membroId": "mem1", "valor": 2000, "mes": 6, "ano": 2026
        }).get_json()
        resp = client.post(f"/salarios/{created['id']}/update", json={"valor": 2500})
        assert resp.status_code == 200
        assert resp.get_json()["valor"] == 2500.0

    def test_update_salario_not_found(self, client):
        resp = client.post("/salarios/nonexistent/update", json={"valor": 1000})
        assert resp.status_code == 404

    def test_delete_salario(self, client):
        created = client.post("/salarios", json={
            "membroId": "mem1", "valor": 4000, "mes": 6, "ano": 2026
        }).get_json()
        resp = client.post(f"/salarios/{created['id']}/delete")
        assert resp.status_code == 200
        get_resp = client.get(f"/salarios/{created['id']}")
        assert get_resp.status_code == 404

    def test_delete_salario_not_found(self, client):
        resp = client.post("/salarios/nonexistent/delete")
        assert resp.status_code == 404

    def test_list_filter_by_mes_ano(self, client):
        client.post("/salarios", json={"membroId": "mem1", "valor": 3000, "mes": 6, "ano": 2026})
        client.post("/salarios", json={"membroId": "mem2", "valor": 2000, "mes": 6, "ano": 2026})
        client.post("/salarios", json={"membroId": "mem1", "valor": 3000, "mes": 7, "ano": 2026})
        resp = client.get("/salarios?mes=6&ano=2026")
        assert len(resp.get_json()) == 2
