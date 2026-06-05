import uuid
from datetime import datetime, timezone


class BaseModel:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.createdAt = datetime.now(timezone.utc).isoformat()
        self.updatedAt = self.createdAt

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data):
        instance = cls.__new__(cls)
        for key, value in data.items():
            setattr(instance, key, value)
        return instance


class Category(BaseModel):
    def __init__(self, nome="", cor="#808080", icone="", **kwargs):
        super().__init__()
        if not nome.strip():
            raise ValueError("nome is required")
        self.nome = nome
        self.cor = cor
        self.icone = icone
        for k, v in kwargs.items():
            setattr(self, k, v)


class HouseExpense(BaseModel):
    def __init__(self, descricao="", valor=0.0, categoriaId="", data="", membroId="", **kwargs):
        super().__init__()
        if not descricao.strip():
            raise ValueError("descricao is required")
        self.descricao = descricao
        self.valor = round(float(valor), 2)
        if self.valor <= 0:
            raise ValueError("valor must be positive")
        self.categoriaId = categoriaId
        self.data = data
        self.membroId = membroId
        for k, v in kwargs.items():
            setattr(self, k, v)


class CreditCardBill(BaseModel):
    def __init__(self, descricao="", valor=0.0, parcela=1, totalParcelas=1, bandeira="", vencimento="", **kwargs):
        super().__init__()
        if not descricao.strip():
            raise ValueError("descricao is required")
        self.descricao = descricao
        self.valor = round(float(valor), 2)
        self.parcela = int(parcela)
        self.totalParcelas = int(totalParcelas)
        if self.parcela < 1 or self.parcela > self.totalParcelas:
            raise ValueError("parcela must be between 1 and totalParcelas")
        if self.totalParcelas < 1:
            raise ValueError("totalParcelas must be >= 1")
        self.bandeira = bandeira
        self.vencimento = vencimento
        for k, v in kwargs.items():
            setattr(self, k, v)


class Salary(BaseModel):
    def __init__(self, membroId="", valor=0.0, mes=1, ano=2026, **kwargs):
        super().__init__()
        self.membroId = membroId
        self.valor = round(float(valor), 2)
        self.mes = int(mes)
        self.ano = int(ano)
        if self.mes < 1 or self.mes > 12:
            raise ValueError("mes must be between 1 and 12")
        if self.ano < 1900 or self.ano > 2100:
            raise ValueError("ano must be between 1900 and 2100")
        for k, v in kwargs.items():
            setattr(self, k, v)


class Member(BaseModel):
    def __init__(self, nome="", salarioId=None, **kwargs):
        super().__init__()
        if not nome.strip():
            raise ValueError("nome is required")
        self.nome = nome
        self.salarioId = salarioId
        for k, v in kwargs.items():
            setattr(self, k, v)
