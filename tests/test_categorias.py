import pytest
import tempfile
import os
from app import create_app
from app.json_store import JsonStore


@pytest.fixture
def store():
    tmp = tempfile.mkdtemp()
    filepath = os.path.join(tmp, "categorias.json")
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


class TestCategoriasRoutes:
    def test_get_categorias_empty(self, client):
        resp = client.get("/categorias")
        assert resp.status_code == 200
        assert resp.is_json
        assert resp.get_json() == []

    def test_create_categoria(self, client):
        resp = client.post("/categorias", json={
            "nome": "Alimentação", "cor": "#FF5733", "icone": "food"
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["nome"] == "Alimentação"
        assert data["cor"] == "#FF5733"
        assert "id" in data

    def test_create_categoria_validation(self, client):
        resp = client.post("/categorias", json={"nome": ""})
        assert resp.status_code == 400

    def test_get_categoria_by_id(self, client):
        created = client.post("/categorias", json={"nome": "Teste"}).get_json()
        resp = client.get(f"/categorias/{created['id']}")
        assert resp.status_code == 200
        assert resp.get_json()["nome"] == "Teste"

    def test_get_categoria_not_found(self, client):
        resp = client.get("/categorias/nonexistent")
        assert resp.status_code == 404

    def test_update_categoria(self, client):
        created = client.post("/categorias", json={"nome": "Antigo"}).get_json()
        resp = client.put(f"/categorias/{created['id']}", json={"nome": "Novo"})
        assert resp.status_code == 200
        assert resp.get_json()["nome"] == "Novo"

    def test_update_categoria_not_found(self, client):
        resp = client.put("/categorias/nonexistent", json={"nome": "X"})
        assert resp.status_code == 404

    def test_delete_categoria(self, client):
        created = client.post("/categorias", json={"nome": "Remover"}).get_json()
        resp = client.delete(f"/categorias/{created['id']}")
        assert resp.status_code == 200
        get_resp = client.get(f"/categorias/{created['id']}")
        assert get_resp.status_code == 404

    def test_delete_categoria_not_found(self, client):
        resp = client.delete("/categorias/nonexistent")
        assert resp.status_code == 404


    def test_get_categorias_after_create(self, client):
        client.post("/categorias", json={"nome": "A"})
        client.post("/categorias", json={"nome": "B"})
        resp = client.get("/categorias")
        assert len(resp.get_json()) == 2
