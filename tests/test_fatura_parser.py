import pytest
from app.fatura_parser import parse_fatura_text, parse_fatura_linha


class TestParseFaturaLinha:
    def test_linha_simples_com_parcela(self):
        result = parse_fatura_linha("14/04 Steam 02/03 27,26")
        assert result["dataCompra"] == "14/04"
        assert result["descricao"] == "Steam"
        assert result["valor"] == 27.26
        assert result["parcelaAtual"] == 2
        assert result["totalParcelas"] == 3

    def test_linha_sem_parcela(self):
        result = parse_fatura_linha("20/04 PANIFICADORA ALADIM LT 38,93")
        assert result["dataCompra"] == "20/04"
        assert result["descricao"] == "PANIFICADORA ALADIM LT"
        assert result["valor"] == 38.93
        assert result["parcelaAtual"] == 1
        assert result["totalParcelas"] == 1

    def test_linha_texto_colado_parcela(self):
        result = parse_fatura_linha("14/04 PET LOVE Or10297649502/02 288,69")
        assert result["dataCompra"] == "14/04"
        assert result["descricao"] == "PET LOVE Or1029764950"
        assert result["valor"] == 288.69
        assert result["parcelaAtual"] == 2
        assert result["totalParcelas"] == 2

    def test_linha_texto_colado_estabelecimento(self):
        result = parse_fatura_linha("16/04 PETSUPERMARKET COMER02/02 126,61")
        assert result["dataCompra"] == "16/04"
        assert result["descricao"] == "PETSUPERMARKET COMER"
        assert result["valor"] == 126.61
        assert result["parcelaAtual"] == 2
        assert result["totalParcelas"] == 2

    def test_valor_com_milhar(self):
        result = parse_fatura_linha("10/04 NOTEBOOK LOJA 01/01 1.234,56")
        assert result["valor"] == 1234.56
        assert result["parcelaAtual"] == 1
        assert result["totalParcelas"] == 1
        assert result["descricao"] == "NOTEBOOK LOJA"

    def test_raia_drogasil(self):
        result = parse_fatura_linha("11/04 RAIA DROGASIL SA 02/02 103,42")
        assert result["dataCompra"] == "11/04"
        assert result["descricao"] == "RAIA DROGASIL SA"
        assert result["valor"] == 103.42
        assert result["parcelaAtual"] == 2
        assert result["totalParcelas"] == 2

    def test_linha_com_cidade_apos_parcela(self):
        result = parse_fatura_linha("17/05 EVENTIM COM BR 01/08 SAO PAULO 341,63")
        assert result["dataCompra"] == "17/05"
        assert result["descricao"] == "EVENTIM COM BR SAO PAULO"
        assert result["valor"] == 341.63
        assert result["parcelaAtual"] == 1
        assert result["totalParcelas"] == 8

    def test_linha_com_cidade_apos_parcela_2(self):
        result = parse_fatura_linha("26/04 CASA CHINA 01/02 CURITIBA 47,48")
        assert result["dataCompra"] == "26/04"
        assert result["descricao"] == "CASA CHINA CURITIBA"
        assert result["valor"] == 47.48
        assert result["parcelaAtual"] == 1
        assert result["totalParcelas"] == 2

    def test_linha_data_colada_sem_espaco(self):
        result = parse_fatura_linha("26/04CASA CHINA 01/02 CURITIBA 47,48")
        assert result is not None
        assert result["dataCompra"] == "26/04"
        assert result["descricao"] == "CASA CHINA CURITIBA"
        assert result["valor"] == 47.48
        assert result["parcelaAtual"] == 1
        assert result["totalParcelas"] == 2


class TestParseFaturaTexto:
    def test_multiplas_linhas(self):
        texto = """11/04 RAIA DROGASIL SA 02/02 103,42
14/04 Steam 02/03 27,26
14/04 PET LOVE Or10297649502/02 288,69
16/04 PETSUPERMARKET COMER02/02 126,61
20/04 PANIFICADORA ALADIM LT 38,93"""
        results = parse_fatura_text(texto)
        assert len(results) == 5
        assert results[0]["descricao"] == "RAIA DROGASIL SA"
        assert results[1]["descricao"] == "Steam"
        assert results[4]["descricao"] == "PANIFICADORA ALADIM LT"

    def test_texto_vazio(self):
        assert parse_fatura_text("") == []
        assert parse_fatura_text("   ") == []
        assert parse_fatura_text("\n\n") == []

    def test_linha_invalida_ignorada(self):
        texto = """14/04 Steam 02/03 27,26
texto invalido sem data nem valor
20/04 PANIFICADORA ALADIM LT 38,93"""
        results = parse_fatura_text(texto)
        assert len(results) == 2
        assert results[0]["descricao"] == "Steam"
        assert results[1]["descricao"] == "PANIFICADORA ALADIM LT"
