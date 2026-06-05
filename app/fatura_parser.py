import re


VALOR_REGEX = re.compile(r'(\d{1,3}(?:\.\d{3})*,\d{2})\s*$')
DATA_REGEX = re.compile(r'^(\d{2}/\d{2})\s*')


def _parse_valor(raw):
    return float(raw.replace(".", "").replace(",", "."))


def parse_fatura_linha(linha):
    linha = linha.strip()
    if not linha:
        return None

    m_data = DATA_REGEX.match(linha)
    if not m_data:
        return None
    data_compra = m_data.group(1)
    restante = linha[m_data.end():]

    m_valor = VALOR_REGEX.search(restante)
    if not m_valor:
        return None
    valor = _parse_valor(m_valor.group(1))
    restante = restante[:m_valor.start()].strip()

    parcela_match = None
    for m in re.finditer(r'(\d{2})/(\d{2})', restante):
        parcela_match = m

    if parcela_match:
        parcela_atual = int(parcela_match.group(1))
        total_parcelas = int(parcela_match.group(2))
        descricao_raw = restante[:parcela_match.start()].strip()
        suffix = restante[parcela_match.end():].strip()

        if descricao_raw and descricao_raw[-1].isdigit() and len(parcela_match.group(1)) == 2:
            m2 = re.search(r'(\d{1})/(\d{2})$', restante)
            if m2 and m2.start() > parcela_match.start():
                descricao_raw = restante[:m2.start()].strip()
                suffix = restante[m2.end():].strip()
                parcela_atual = int(m2.group(1))
                total_parcelas = int(m2.group(2))

        descricao = descricao_raw
        if suffix:
            descricao = f"{descricao} {suffix}"
    else:
        parcela_atual = 1
        total_parcelas = 1
        descricao = restante

    return {
        "dataCompra": data_compra,
        "descricao": descricao,
        "valor": valor,
        "parcelaAtual": parcela_atual,
        "totalParcelas": total_parcelas,
    }


def parse_fatura_text(texto):
    linhas = texto.strip().split("\n")
    resultados = []
    for linha in linhas:
        resultado = parse_fatura_linha(linha)
        if resultado is not None:
            resultados.append(resultado)
    return resultados
