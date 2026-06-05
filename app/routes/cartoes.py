import os
from flask import Blueprint, jsonify, request, current_app
from app.json_store import JsonStore
from app.fatura_parser import parse_fatura_text


cartoes_bp = Blueprint("cartoes", __name__)


def _get_store():
    data_dir = current_app.config.get("DATA_DIR",
                                      os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    return JsonStore(os.path.join(data_dir, "cartoes.json"))


@cartoes_bp.route("/cartoes", methods=["GET"])
def listar():
    store = _get_store()
    return jsonify(store.get_all())


@cartoes_bp.route("/cartoes", methods=["POST"])
def criar():
    data = request.get_json()
    if not data or not data.get("descricao") or float(data.get("valor", 0)) <= 0:
        return jsonify({"error": "descricao and positive valor required"}), 400
    store = _get_store()
    item = store.create(data)
    return jsonify(item), 201


@cartoes_bp.route("/cartoes/<id>", methods=["GET"])
def obter(id):
    store = _get_store()
    item = store.get_by_id(id)
    if item is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(item)


@cartoes_bp.route("/cartoes/<id>/update", methods=["POST"])
def atualizar(id):
    store = _get_store()
    item = store.get_by_id(id)
    if item is None:
        return jsonify({"error": "not found"}), 404
    updated = store.update(id, request.get_json())
    return jsonify(updated)


@cartoes_bp.route("/cartoes/<id>/delete", methods=["POST"])
def deletar(id):
    store = _get_store()
    item = store.get_by_id(id)
    if item is None:
        return jsonify({"error": "not found"}), 404
    store.delete(id)
    return jsonify({"success": True})


@cartoes_bp.route("/cartoes/parse", methods=["POST"])
def parse_fatura():
    texto = None
    if request.is_json:
        texto = request.get_json().get("text", "")
    elif request.files:
        f = request.files.get("file")
        if f:
            texto = f.read().decode("utf-8")
    if not texto or not texto.strip():
        return jsonify([])
    return jsonify(parse_fatura_text(texto))


@cartoes_bp.route("/cartoes/import", methods=["POST"])
def importar_fatura():
    data = request.get_json()
    if not data or "itens" not in data:
        return jsonify({"error": "itens required"}), 400
    bandeira = data.get("bandeira", "Elo")
    vencimento = data.get("vencimento", "")
    categoria_id = data.get("categoriaId", "")
    store = _get_store()
    criados = []
    for item in data["itens"]:
        if not item.get("descricao") or float(item.get("valor", 0)) <= 0:
            continue
        novo = {
            "descricao": item["descricao"],
            "valor": round(float(item["valor"]), 2),
            "bandeira": bandeira,
            "vencimento": vencimento,
            "categoriaId": categoria_id or item.get("categoriaId", ""),
            "responsavel": item.get("responsavel", "Ambos"),
            "parcelaAtual": int(item.get("parcelaAtual", 1)),
            "totalParcelas": int(item.get("totalParcelas", 1)),
            "dataCompra": item.get("dataCompra", ""),
        }
        criados.append(store.create(novo))
    return jsonify(criados), 201
