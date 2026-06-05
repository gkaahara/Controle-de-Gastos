import pytest
from datetime import datetime
from app.models import Category, HouseExpense, CreditCardBill, Salary, Member


class TestCategory:
    def test_create_valid_category(self):
        c = Category(nome="Alimentação", cor="#FF5733", icone="food")
        assert c.nome == "Alimentação"
        assert c.cor == "#FF5733"
        assert c.icone == "food"
        assert c.id is not None

    def test_category_to_dict(self):
        c = Category(nome="Transporte")
        d = c.to_dict()
        assert d["nome"] == "Transporte"
        assert "id" in d
        assert "createdAt" in d
        assert "updatedAt" in d

    def test_category_from_dict(self):
        data = {"nome": "Lazer", "cor": "#00FF00", "icone": "game"}
        c = Category.from_dict(data)
        assert c.nome == "Lazer"
        assert c.cor == "#00FF00"

    def test_category_validation_nome_required(self):
        with pytest.raises(ValueError, match="nome"):
            Category(nome="", cor="#000")


class TestHouseExpense:
    def test_create_valid_expense(self):
        e = HouseExpense(
            descricao="Mercado", valor=250.50,
            categoriaId="cat1", data="2026-06-01", membroId="mem1"
        )
        assert e.descricao == "Mercado"
        assert e.valor == 250.50

    def test_expense_valor_rounded_to_2(self):
        e = HouseExpense(
            descricao="Teste", valor=100.456,
            categoriaId="cat1", data="2026-06-01", membroId="mem1"
        )
        assert e.valor == 100.46

    def test_expense_validation_valor_positive(self):
        with pytest.raises(ValueError, match="valor"):
            HouseExpense(
                descricao="Teste", valor=-10,
                categoriaId="cat1", data="2026-06-01", membroId="mem1"
            )


class TestCreditCardBill:
    def test_create_valid_bill(self):
        b = CreditCardBill(
            descricao="Amazon", valor=150.00,
            parcela=1, totalParcelas=3,
            bandeira="Visa", vencimento="2026-07-10"
        )
        assert b.descricao == "Amazon"
        assert b.parcela == 1
        assert b.totalParcelas == 3

    def test_bill_validation_parcela_range(self):
        with pytest.raises(ValueError, match="parcela"):
            CreditCardBill(
                descricao="Teste", valor=100,
                parcela=0, totalParcelas=3,
                bandeira="Visa", vencimento="2026-07-10"
            )

    def test_bill_validation_total_parcelas_positive(self):
        with pytest.raises(ValueError, match="totalParcelas"):
            CreditCardBill(
                descricao="Teste", valor=100,
                parcela=1, totalParcelas=0,
                bandeira="Visa", vencimento="2026-07-10"
            )


class TestSalary:
    def test_create_valid_salary(self):
        s = Salary(membroId="mem1", valor=5000.00, mes=6, ano=2026)
        assert s.membroId == "mem1"
        assert s.valor == 5000.00
        assert s.mes == 6
        assert s.ano == 2026

    def test_salary_validation_mes_range(self):
        with pytest.raises(ValueError, match="mes"):
            Salary(membroId="mem1", valor=1000, mes=13, ano=2026)

    def test_salary_validation_ano(self):
        with pytest.raises(ValueError, match="ano"):
            Salary(membroId="mem1", valor=1000, mes=6, ano=1800)


class TestMember:
    def test_create_valid_member(self):
        m = Member(nome="João")
        assert m.nome == "João"
        assert m.id is not None

    def test_member_to_dict(self):
        m = Member(nome="Maria", salarioId="sal1")
        d = m.to_dict()
        assert d["nome"] == "Maria"
        assert d["salarioId"] == "sal1"
