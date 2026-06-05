import pytest
import tempfile
import json
from app import create_app


@pytest.fixture
def client():
    tmp = tempfile.mkdtemp()
    app = create_app({"TESTING": True, "DATA_DIR": tmp})
    client = app.test_client()

    client.post("/categorias", json={"nome": "Alimentação", "id": "cat1"})
    client.post("/categorias", json={"nome": "Transporte", "id": "cat2"})

    client.post("/salarios", json={"membroId": "mem1", "nome": "João", "valor": 5000, "mes": 6, "ano": 2026})
    client.post("/salarios", json={"membroId": "mem2", "nome": "Maria", "valor": 3000, "mes": 6, "ano": 2026})

    client.post("/gastos-casa", json={"descricao": "Mercado", "valor": 300, "categoriaId": "cat1", "data": "2026-06-05", "membroId": "mem1"})
    client.post("/gastos-casa", json={"descricao": "Uber", "valor": 50, "categoriaId": "cat2", "data": "2026-06-10", "membroId": "mem1"})

    client.post("/cartoes", json={"descricao": "Amazon", "valor": 200, "categoriaId": "cat1", "parcela": 1, "totalParcelas": 1, "bandeira": "Visa", "vencimento": "2026-06-15", "data": "2026-06-01", "membroId": "mem1", "responsavel": "Casal"})

    yield client


class TestDashboard:
    def test_dashboard_returns_json(self, client):
        resp = client.get("/dashboard?mes=6&ano=2026")
        assert resp.status_code == 200
        assert resp.is_json

    def test_dashboard_requires_mes_ano(self, client):
        resp = client.get("/dashboard")
        assert resp.status_code == 400

    def test_dashboard_includes_all_cards(self, client):
        resp = client.get("/dashboard?mes=6&ano=2026")
        data = resp.get_json()
        assert "totalGastosCasa" in data
        assert "totalCartoes" in data
        assert "totalSalarios" in data
        assert "saldo" in data

    def test_dashboard_card_values(self, client):
        resp = client.get("/dashboard?mes=6&ano=2026")
        data = resp.get_json()
        assert data["totalGastosCasa"] == 350.0
        assert data["totalCartoes"] == 200.0
        assert data["totalSalarios"] == 8000.0
        assert data["saldo"] == 7450.0

    def test_dashboard_includes_categoria_breakdown(self, client):
        resp = client.get("/dashboard?mes=6&ano=2026")
        data = resp.get_json()
        assert "porCategoria" in data
        assert len(data["porCategoria"]) == 2
        for c in data["porCategoria"]:
            assert "gastosCasa" in c
            assert "cartoes" in c
            assert "total" in c

    def test_dashboard_categoria_merges_same_category(self, client):
        resp = client.get("/dashboard?mes=6&ano=2026")
        data = resp.get_json()
        cat1 = [c for c in data["porCategoria"] if c["categoriaId"] == "cat1"][0]
        assert cat1["gastosCasa"] == 300.0
        assert cat1["cartoes"] == 200.0
        assert cat1["total"] == 500.0

    def test_dashboard_includes_divisao(self, client):
        resp = client.get("/dashboard?mes=6&ano=2026")
        data = resp.get_json()
        assert "divisao" in data
        assert len(data["divisao"]) == 2

    def test_dashboard_divisao_includes_breakdown(self, client):
        resp = client.get("/dashboard?mes=6&ano=2026")
        data = resp.get_json()
        for m in data["divisao"]:
            assert "gastosCasa" in m
            assert "cartoes" in m
            # gastosCasa + cartoes should approximately equal valorPagar
            assert abs(m["gastosCasa"] + m["cartoes"] - m["valorPagar"]) < 0.02

    def test_dashboard_no_data_empty_month(self, client):
        resp = client.get("/dashboard?mes=7&ano=2026")
        data = resp.get_json()
        assert data["totalGastosCasa"] == 0
        assert data["totalCartoes"] == 0
        assert data["totalSalarios"] == 0
        assert data["saldo"] == 0
        assert data["porCategoria"] == []
        assert data["divisao"] == []


class TestResumoMorador:
    def test_resumo_requires_all_params(self, client):
        resp = client.get("/dashboard/resumo?pessoa=Gabriel&mes=6")
        assert resp.status_code == 400
        resp = client.get("/dashboard/resumo")
        assert resp.status_code == 400

    def test_resumo_requires_valid_pessoa(self, client):
        resp = client.get("/dashboard/resumo?pessoa=&mes=6&ano=2026")
        assert resp.status_code == 400

    def test_resumo_returns_all_keys(self, client):
        resp = client.get("/dashboard/resumo?pessoa=Jo%C3%A3o&mes=6&ano=2026")
        assert resp.status_code == 200
        d = resp.get_json()
        assert d["pessoa"] == "João"
        assert "salario" in d
        assert "individuais" in d
        assert "compartilhados" in d
        assert "totalIndividual" in d
        assert "totalCompartilhado" in d
        assert "totalGeral" in d
        assert "saldo" in d

    def test_resumo_joao_calculations(self, client):
        resp = client.get("/dashboard/resumo?pessoa=Jo%C3%A3o&mes=6&ano=2026")
        d = resp.get_json()
        assert d["salario"] == 5000
        assert d["proporcao"] == 0.625
        assert d["totalIndividual"] == 0
        esperado = round(200 * 0.625, 2) + round(300 * 0.625, 2) + round(50 * 0.625, 2)
        assert abs(d["totalCompartilhado"] - esperado) < 0.02
        assert abs(d["totalGeral"] - d["totalCompartilhado"]) < 0.02
        assert abs(d["saldo"] - round(5000 - d["totalGeral"], 2)) < 0.02
