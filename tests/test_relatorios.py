import pytest
import tempfile
from app import create_app


@pytest.fixture
def client():
    tmp = tempfile.mkdtemp()
    app = create_app({"TESTING": True, "DATA_DIR": tmp})
    client = app.test_client()

    # seed data: gastos da casa
    client.post("/gastos-casa", json={"descricao": "Mercado", "valor": 300, "categoriaId": "cat1", "data": "2026-06-05", "membroId": "mem1"})
    client.post("/gastos-casa", json={"descricao": "Farmácia", "valor": 100, "categoriaId": "cat2", "data": "2026-06-10", "membroId": "mem1"})
    client.post("/gastos-casa", json={"descricao": "Uber", "valor": 50, "categoriaId": "cat1", "data": "2026-06-15", "membroId": "mem1"})
    # cartoes in same month
    client.post("/cartoes", json={"descricao": "Amazon", "valor": 200, "categoriaId": "cat1", "parcela": 1, "totalParcelas": 1, "bandeira": "Visa", "vencimento": "2026-06-20"})
    # another month
    client.post("/gastos-casa", json={"descricao": "Mercado Jul", "valor": 200, "categoriaId": "cat1", "data": "2026-07-01", "membroId": "mem1"})

    yield client
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)


class TestRelatorioCategoria:
    def test_relatorio_returns_json(self, client):
        resp = client.get("/relatorios/categoria?mes=6&ano=2026")
        assert resp.status_code == 200
        assert resp.is_json

    def test_relatorio_groups_by_categoria(self, client):
        resp = client.get("/relatorios/categoria?mes=6&ano=2026")
        data = resp.get_json()
        assert len(data) == 2
        cat1 = [c for c in data if c["categoriaId"] == "cat1"][0]
        assert cat1["total"] == 550.0  # 300 casa + 50 casa + 200 cartao
        assert cat1["gastosCasa"] == 350.0
        assert cat1["cartoes"] == 200.0
        assert cat1["percentual"] == 84.62
        assert cat1["nome"] != ""
        cat2 = [c for c in data if c["categoriaId"] == "cat2"][0]
        assert cat2["total"] == 100.0
        assert cat2["gastosCasa"] == 100.0
        assert cat2["cartoes"] == 0.0

    def test_relatorio_ordered_by_valor_desc(self, client):
        resp = client.get("/relatorios/categoria?mes=6&ano=2026")
        data = resp.get_json()
        assert data[0]["total"] >= data[1]["total"]

    def test_relatorio_respects_mes_filter(self, client):
        resp = client.get("/relatorios/categoria?mes=7&ano=2026")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["total"] == 200.0

    def test_relatorio_empty_month(self, client):
        resp = client.get("/relatorios/categoria?mes=8&ano=2026")
        assert resp.get_json() == []
