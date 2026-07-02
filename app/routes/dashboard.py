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
    FILE_CARTOES,
    FILE_SALARIOS,
    FILE_CATEGORIAS,
    HTTP_BAD_REQUEST,
)

dashboard_bp = Blueprint("dashboard", __name__)


def _prefix_filter(entries, ano, mes):
    prefix = f"{ano}-{int(mes):02d}"
    return [e for e in entries if e.get(FIELD_DATA, "").startswith(prefix)]


@dashboard_bp.route("/dashboard", methods=["GET"])
def resumo():
    mes = request.args.get(FIELD_MES)
    ano = request.args.get(FIELD_ANO)
    if not mes or not ano:
        return jsonify({RESPONSE_ERROR: ERROR_MES_ANO_REQUIRED}), HTTP_BAD_REQUEST

    gastos_casa = _prefix_filter(get_store(FILE_GASTOS_CASA).get_all(), ano, mes)
    cartoes_raw = get_store(FILE_CARTOES).get_all()
    cartoes = [c for c in cartoes_raw if c.get("vencimento", "").startswith(f"{ano}-{int(mes):02d}")]
    salarios = get_store(FILE_SALARIOS).get_all()
    categorias = get_store(FILE_CATEGORIAS).get_all()

    membros_mes = [s for s in salarios if s.get("mes") == int(mes) and s.get("ano") == int(ano)]
    total_gastos_casa = round(sum(g["valor"] for g in gastos_casa), 2)
    total_cartoes = round(sum(c["valor"] for c in cartoes), 2)
    total_salarios = round(sum(s["valor"] for s in membros_mes), 2)
    saldo = round(total_salarios - total_gastos_casa - total_cartoes, 2)

    cat_map = {c.get("id", ""): c.get("nome", "unknown") for c in categorias}
    cat_agg = {}
    for g in gastos_casa:
        cat = g.get("categoriaId", "")
        cat_agg.setdefault(cat, {"casa": 0, "cartao": 0})
        cat_agg[cat]["casa"] += g["valor"]

    for c in cartoes:
        cat = c.get("categoriaId", "")
        cat_agg.setdefault(cat, {"casa": 0, "cartao": 0})
        cat_agg[cat]["cartao"] += c["valor"]

    total_geral = sum(v["casa"] + v["cartao"] for v in cat_agg.values())
    por_categoria = []
    for cat_id, valores in cat_agg.items():
        total = round(valores["casa"] + valores["cartao"], 2)
        if total == 0:
            continue
        por_categoria.append({
            "categoriaId": cat_id,
            "nome": cat_map.get(cat_id, "Sem categoria"),
            "gastosCasa": round(valores["casa"], 2),
            "cartoes": round(valores["cartao"], 2),
            "total": total,
            "percentual": round(total / total_geral * 100, 2) if total_geral > 0 else 0,
        })
    por_categoria.sort(key=lambda x: x["total"], reverse=True)

    cartoes_casal = [c for c in cartoes if c.get("responsavel", "Casal") == "Casal"]
    cartoes_gabriel = [c for c in cartoes if c.get("responsavel") == "Gabriel"]
    cartoes_helena = [c for c in cartoes if c.get("responsavel") == "Helena"]
    cartoes_ambos = [c for c in cartoes if c.get("responsavel") == "Ambos"]

    total_cartoes_casal = round(sum(c["valor"] for c in cartoes_casal), 2)
    total_proporcional = total_gastos_casa + total_cartoes_casal
    total_ambos = round(sum(c["valor"] for c in cartoes_ambos), 2)
    metade_ambos = round(total_ambos / 2, 2)
    total_individual_gabriel = round(sum(c["valor"] for c in cartoes_gabriel), 2)
    total_individual_helena = round(sum(c["valor"] for c in cartoes_helena), 2)
    total_despesas = total_proporcional + total_ambos + total_individual_gabriel + total_individual_helena

    divisao = []
    if membros_mes and total_proporcional > 0:
        soma_salarios = sum(s["valor"] for s in membros_mes)
        d_soma = Decimal(str(soma_salarios))
        d_total_prop = Decimal(str(total_proporcional))
        for s in membros_mes:
            nome = s.get("nome", "")
            d_salario = Decimal(str(s["valor"]))
            valor_proporcional = float((d_total_prop * d_salario / d_soma).quantize(Decimal('0.01'), rounding=ROUND_DOWN))
            if total_proporcional > 0:
                gastos_casa_share = round(valor_proporcional * total_gastos_casa / total_proporcional, 2)
                cartoes_casal_share = round(valor_proporcional * total_cartoes_casal / total_proporcional, 2)
                diff = round(valor_proporcional - gastos_casa_share - cartoes_casal_share, 2)
                if diff != 0:
                    if gastos_casa_share >= cartoes_casal_share:
                        gastos_casa_share += diff
                    else:
                        cartoes_casal_share += diff
            else:
                gastos_casa_share = 0
                cartoes_casal_share = 0
            extras = {"Gabriel": total_individual_gabriel + metade_ambos, "Helena": total_individual_helena + metade_ambos}
            cartoes_total = cartoes_casal_share + extras.get(nome, 0)
            valor_pagar = round(gastos_casa_share + cartoes_total, 2)
            divisao.append({
                "membroId": s.get("membroId") or nome,
                "nome": nome,
                "salario": s["valor"],
                "percentual": round(s["valor"] / soma_salarios * 100, 2),
                "gastosCasa": gastos_casa_share,
                "cartoes": cartoes_total,
                "valorPagar": valor_pagar,
            })
        soma_pago = sum(r["valorPagar"] for r in divisao)
        residual = round(total_despesas - soma_pago, 2)
        if residual > 0:
            maior = max(divisao, key=lambda r: r["salario"])
            maior["valorPagar"] = round(maior["valorPagar"] + residual, 2)
    elif membros_mes and total_proporcional == 0 and total_ambos + total_individual_gabriel + total_individual_helena > 0:
        for s in membros_mes:
            nome = s.get("nome", "")
            extras = {"Gabriel": total_individual_gabriel + metade_ambos, "Helena": total_individual_helena + metade_ambos}
            cartoes_total = extras.get(nome, 0)
            divisao.append({
                "membroId": s.get("membroId") or nome,
                "nome": nome,
                "salario": s["valor"],
                "percentual": 0,
                "gastosCasa": 0,
                "cartoes": cartoes_total,
                "valorPagar": cartoes_total,
            })

    return jsonify({
        "mes": int(mes),
        "ano": int(ano),
        "totalGastosCasa": total_gastos_casa,
        "totalCartoes": total_cartoes,
        "totalSalarios": total_salarios,
        "saldo": saldo,
        "porCategoria": por_categoria,
        "divisao": divisao,
    })


@dashboard_bp.route("/dashboard/resumo", methods=["GET"])
def resumo_morador():
    pessoa = request.args.get("pessoa", "")
    mes = request.args.get(FIELD_MES)
    ano = request.args.get(FIELD_ANO)
    if not pessoa or not mes or not ano:
        return jsonify({RESPONSE_ERROR: "pessoa, mes and ano required"}), HTTP_BAD_REQUEST
    if not pessoa.strip():
        return jsonify({RESPONSE_ERROR: "pessoa must be a valid name"}), HTTP_BAD_REQUEST

    gastos_casa = _prefix_filter(get_store(FILE_GASTOS_CASA).get_all(), ano, mes)
    cartoes_raw = get_store(FILE_CARTOES).get_all()
    cartoes = [c for c in cartoes_raw if c.get("vencimento", "").startswith(f"{ano}-{int(mes):02d}")]
    salarios = get_store(FILE_SALARIOS).get_all()
    categorias = get_store(FILE_CATEGORIAS).get_all()

    membros_mes = {s.get("nome"): s for s in salarios if s.get("mes") == int(mes) and s.get("ano") == int(ano)}
    salario_pessoa = membros_mes.get(pessoa, {}).get("valor", 0)
    soma_salarios = sum(s["valor"] for s in membros_mes.values())
    proporcao = round(salario_pessoa / soma_salarios, 4) if soma_salarios > 0 else 1.0

    cat_map = {c.get("id", ""): c.get("nome", "") for c in categorias}

    individuais = []
    for c in cartoes:
        if c.get("responsavel") == pessoa:
            individuais.append({
                "descricao": c.get("descricao", ""),
                "valor": c.get("valor", 0),
                "parcelas": f"{c.get('parcelaAtual', 1)}/{c.get('totalParcelas', 1)}",
                "categoria": cat_map.get(c.get("categoriaId", ""), ""),
            })

    compartilhados = []
    for c in cartoes:
        if c.get("responsavel") == "Ambos":
            valor = c.get("valor", 0)
            compartilhados.append({
                "descricao": c.get("descricao", ""),
                "origem": "Ambos",
                "chave": "50%",
                "valorTotal": valor,
                "suaParte": round(valor / 2, 2),
                "parcelas": f"{c.get('parcelaAtual', 1)}/{c.get('totalParcelas', 1)}",
                "categoria": cat_map.get(c.get("categoriaId", ""), ""),
            })
    for c in cartoes:
        if c.get("responsavel", "Casal") == "Casal":
            valor = c.get("valor", 0)
            compartilhados.append({
                "descricao": c.get("descricao", ""),
                "origem": "Casal",
                "chave": f"{round(proporcao * 100)}%",
                "valorTotal": valor,
                "suaParte": round(valor * proporcao, 2),
                "parcelas": f"{c.get('parcelaAtual', 1)}/{c.get('totalParcelas', 1)}",
                "categoria": cat_map.get(c.get("categoriaId", ""), ""),
            })
    for g in gastos_casa:
        valor = g.get("valor", 0)
        compartilhados.append({
            "descricao": g.get("descricao", ""),
            "origem": "Casa",
            "chave": f"{round(proporcao * 100)}%",
            "valorTotal": valor,
            "suaParte": round(valor * proporcao, 2),
            "categoria": cat_map.get(g.get("categoriaId", ""), ""),
        })

    total_individual = round(sum(i["valor"] for i in individuais), 2)
    total_compartilhado = round(sum(c["suaParte"] for c in compartilhados), 2)
    total_geral = round(total_individual + total_compartilhado, 2)
    saldo = round(salario_pessoa - total_geral, 2)

    return jsonify({
        "pessoa": pessoa,
        "mes": int(mes),
        "ano": int(ano),
        "salario": salario_pessoa,
        "proporcao": proporcao,
        "individuais": individuais,
        "compartilhados": compartilhados,
        "totalIndividual": total_individual,
        "totalCompartilhado": total_compartilhado,
        "totalGeral": total_geral,
        "saldo": saldo,
    })
