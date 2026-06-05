import pytest
import tempfile
from app import create_app


@pytest.fixture
def client():
    tmp = tempfile.mkdtemp()
    app = create_app({"TESTING": True, "DATA_DIR": tmp})
    client = app.test_client()

    # seed members
    client.post("/salarios", json={"membroId": "mem1", "nome": "Alice", "valor": 5000, "mes": 6, "ano": 2026})
    client.post("/salarios", json={"membroId": "mem2", "nome": "Bob", "valor": 3000, "mes": 6, "ano": 2026})
    # seed house expenses
    client.post("/gastos-casa", json={"descricao": "Mercado", "valor": 400, "categoriaId": "cat1", "data": "2026-06-05", "membroId": "mem1"})
    client.post("/gastos-casa", json={"descricao": "Luz", "valor": 200, "categoriaId": "cat2", "data": "2026-06-10", "membroId": "mem2"})
    # total = 600, proportions: Alice 600*5000/8000=375, Bob 600*3000/8000=225

    yield client
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)


class TestDivisaoProporcional:
    def test_divisao_returns_json(self, client):
        resp = client.get("/relatorios/divisao?mes=6&ano=2026")
        assert resp.status_code == 200
        assert resp.is_json

    def test_divisao_per_member(self, client):
        resp = client.get("/relatorios/divisao?mes=6&ano=2026")
        data = resp.get_json()
        assert len(data) == 2
        alice = [d for d in data if d["membroId"] == "mem1"][0]
        bob = [d for d in data if d["membroId"] == "mem2"][0]
        assert alice["valorPagar"] == 375.0
        assert bob["valorPagar"] == 225.0

    def test_divisao_includes_member_name(self, client):
        resp = client.get("/relatorios/divisao?mes=6&ano=2026")
        data = resp.get_json()
        alice = [d for d in data if d["membroId"] == "mem1"][0]
        assert alice["nome"] == "Alice"

    def test_divisao_includes_salary_and_percent(self, client):
        resp = client.get("/relatorios/divisao?mes=6&ano=2026")
        data = resp.get_json()
        alice = [d for d in data if d["membroId"] == "mem1"][0]
        assert alice["salario"] == 5000
        assert alice["percentual"] == 62.5

    def test_divisao_residual_goes_to_highest_salary(self, client):
        resp = client.get("/relatorios/divisao?mes=6&ano=2026")
        data = resp.get_json()
        alice = [d for d in data if d["membroId"] == "mem1"][0]
        bob = [d for d in data if d["membroId"] == "mem2"][0]
        assert alice["valorPagar"] + bob["valorPagar"] == 600.0

    def test_divisao_no_salaries_registered(self, client):
        tmp2 = tempfile.mkdtemp()
        app2 = create_app({"TESTING": True, "DATA_DIR": tmp2})
        c2 = app2.test_client()
        resp = c2.get("/relatorios/divisao?mes=6&ano=2026")
        assert resp.status_code == 400
        c2 = app2.test_client()
        import shutil
        shutil.rmtree(tmp2, ignore_errors=True)

    def test_divisao_com_cartoes_responsavel_individual(self, client):
        tmp2 = tempfile.mkdtemp()
        app2 = create_app({"TESTING": True, "DATA_DIR": tmp2})
        c2 = app2.test_client()
        c2.post("/salarios", json={"nome": "Gabriel", "valor": 5000, "mes": 6, "ano": 2026})
        c2.post("/salarios", json={"nome": "Helena", "valor": 3000, "mes": 6, "ano": 2026})
        c2.post("/gastos-casa", json={"descricao": "Aluguel", "valor": 1000, "categoriaId": "cat1", "data": "2026-06-01", "membroId": "mem1"})
        c2.post("/cartoes", json={"descricao": "Gabriel pessoal", "valor": 200, "parcela": 1, "totalParcelas": 1, "bandeira": "Visa", "vencimento": "2026-06-15", "responsavel": "Gabriel"})
        c2.post("/cartoes", json={"descricao": "Helena pessoal", "valor": 100, "parcela": 1, "totalParcelas": 1, "bandeira": "Master", "vencimento": "2026-06-15", "responsavel": "Helena"})
        c2.post("/cartoes", json={"descricao": "Casal", "valor": 300, "parcela": 1, "totalParcelas": 1, "bandeira": "Visa", "vencimento": "2026-06-15", "responsavel": "Casal"})
        # total_proporcional = 1000 + 300 = 1300, gabriel_share = 1300 * 5000/8000 = 812.5, helena_share = 1300 * 3000/8000 = 487.5
        # gabriel_total = 812.5 + 200 = 1012.5, helena_total = 487.5 + 100 = 587.5
        resp = c2.get("/relatorios/divisao?mes=6&ano=2026")
        data = resp.get_json()
        assert len(data) == 2
        gabriel = [d for d in data if d["nome"] == "Gabriel"][0]
        helena = [d for d in data if d["nome"] == "Helena"][0]
        assert gabriel["valorPagar"] == 1012.5
        assert helena["valorPagar"] == 587.5
        import shutil
        shutil.rmtree(tmp2, ignore_errors=True)

    def test_divisao_no_gastos(self, client):
        tmp2 = tempfile.mkdtemp()
        app2 = create_app({"TESTING": True, "DATA_DIR": tmp2})
        c2 = app2.test_client()
        c2.post("/salarios", json={"membroId": "mem1", "nome": "Alice", "valor": 5000, "mes": 6, "ano": 2026})
        resp = c2.get("/relatorios/divisao?mes=6&ano=2026")
        assert resp.get_json() == []
        import shutil
        shutil.rmtree(tmp2, ignore_errors=True)
