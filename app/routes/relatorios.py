from decimal import Decimal, ROUND_DOWN
from flask import Blueprint, jsonify, request
from app.store_factory import get_store
from app.constants import (
    FIELD_DATA,
    FIELD_MES,
    FIELD_ANO,
    ERROR_MES_ANO_REQUIRED,
    RESPONSE_ERROR,
    FILE_GASTOS_CASA,
    FILE_CATEGORIAS,
    FILE_CARTOES,
    FILE_SALARIOS,
    HTTP_BAD_REQUEST,
)

relatorios_bp = Blueprint("relatorios", __name__)


def _prefix_filter(entries, ano, mes):
    prefix = f"{ano}-{int(mes):02d}"
    return [e for e in entries if e.get(FIELD_DATA, "").startswith(prefix)]


@relatorios_bp.route("/relatorios/categoria", methods=["GET"])
def relatorio_categoria():
    mes = request.args.get(FIELD_MES)
    ano = request.args.get(FIELD_ANO)
    if not mes or not ano:
        return jsonify({RESPONSE_ERROR: ERROR_MES_ANO_REQUIRED}), HTTP_BAD_REQUEST

    store = get_store(FILE_GASTOS_CASA)
    gastos = store.get_all()
    filtrados = _prefix_filter(gastos, ano, mes)

    categorias = get_store(FILE_CATEGORIAS).get_all()
    cat_map = {c.get("id", ""): c.get("nome", "unknown") for c in categorias}

    cartoes_raw = get_store(FILE_CARTOES).get_all()
    cartoes_mes = [c for c in cartoes_raw if c.get("vencimento", "").startswith(f"{ano}-{int(mes):02d}")]

    cat_agg = {}
    for g in filtrados:
        cat = g.get("categoriaId", "")
        cat_agg.setdefault(cat, {"casa": 0, "cartao": 0})
        cat_agg[cat]["casa"] += g["valor"]

    for c in cartoes_mes:
        cat = c.get("categoriaId", "")
        cat_agg.setdefault(cat, {"casa": 0, "cartao": 0})
        cat_agg[cat]["cartao"] += c["valor"]

    total_geral = sum(v["casa"] + v["cartao"] for v in cat_agg.values())
    resultado = []
    for cat_id, valores in cat_agg.items():
        total = round(valores["casa"] + valores["cartao"], 2)
        if total == 0:
            continue
        resultado.append({
            "categoriaId": cat_id,
            "nome": cat_map.get(cat_id, "Sem categoria"),
            "gastosCasa": round(valores["casa"], 2),
            "cartoes": round(valores["cartao"], 2),
            "total": total,
            "percentual": round(total / total_geral * 100, 2) if total_geral > 0 else 0,
        })

    resultado.sort(key=lambda x: x["total"], reverse=True)
    return jsonify(resultado)


@relatorios_bp.route("/relatorios/divisao", methods=["GET"])
def divisao_proporcional():
    mes = request.args.get(FIELD_MES)
    ano = request.args.get(FIELD_ANO)
    if not mes or not ano:
        return jsonify({RESPONSE_ERROR: ERROR_MES_ANO_REQUIRED}), HTTP_BAD_REQUEST

    salarios_store = get_store(FILE_SALARIOS)
    salarios = salarios_store.get_all()
    membros_mes = [s for s in salarios if s.get(FIELD_MES) == int(mes) and s.get(FIELD_ANO) == int(ano)]
    if not membros_mes:
        return jsonify({RESPONSE_ERROR: "no salaries found for period"}), HTTP_BAD_REQUEST

    gastos = _prefix_filter(get_store(FILE_GASTOS_CASA).get_all(), ano, mes)
    cartoes_raw = get_store(FILE_CARTOES).get_all()
    cartoes = [c for c in cartoes_raw if c.get("vencimento", "").startswith(f"{ano}-{int(mes):02d}")]

    total_gastos = round(sum(g["valor"] for g in gastos), 2)
    cartoes_casal = [c for c in cartoes if c.get("responsavel", "Casal") == "Casal"]
    cartoes_gabriel = [c for c in cartoes if c.get("responsavel") == "Gabriel"]
    cartoes_helena = [c for c in cartoes if c.get("responsavel") == "Helena"]

    total_proporcional = total_gastos + round(sum(c["valor"] for c in cartoes_casal), 2)
    total_individual_gabriel = round(sum(c["valor"] for c in cartoes_gabriel), 2)
    total_individual_helena = round(sum(c["valor"] for c in cartoes_helena), 2)
    total = total_proporcional + total_individual_gabriel + total_individual_helena

    if total == 0:
        return jsonify([])

    if not membros_mes:
        return jsonify({RESPONSE_ERROR: "no salaries found for period"}), HTTP_BAD_REQUEST

    soma_salarios = sum(s["valor"] for s in membros_mes)
    d_soma = Decimal(str(soma_salarios))
    d_total_prop = Decimal(str(total_proporcional))
    resultado = []
    for s in membros_mes:
        if total_proporcional > 0:
            d_salario = Decimal(str(s["valor"]))
            valor_proporcional = float((d_total_prop * d_salario / d_soma).quantize(Decimal('0.01'), rounding=ROUND_DOWN))
        else:
            valor_proporcional = 0
        extras = {"Gabriel": total_individual_gabriel, "Helena": total_individual_helena}
        valor_pagar = round(valor_proporcional + extras.get(s.get("nome", ""), 0), 2)
        resultado.append({
            "membroId": s.get("membroId") or s.get("nome", ""),
            "nome": s.get("nome", ""),
            "salario": s["valor"],
            "percentual": round(s["valor"] / soma_salarios * 100, 2),
            "valorPagar": valor_pagar,
        })

    soma_pago = sum(r["valorPagar"] for r in resultado)
    residual = round(total - soma_pago, 2)
    if residual > 0:
        maior = max(resultado, key=lambda r: r["salario"])
        maior["valorPagar"] = round(maior["valorPagar"] + residual, 2)

    return jsonify(resultado)
