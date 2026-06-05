import os
from flask import Blueprint, jsonify, request, current_app
from app.json_store import JsonStore


salarios_bp = Blueprint("salarios", __name__)


def _get_store():
    data_dir = current_app.config.get("DATA_DIR",
                                      os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    return JsonStore(os.path.join(data_dir, "salarios.json"))


@salarios_bp.route("/salarios", methods=["GET"])
def listar():
    store = _get_store()
    items = store.get_all()
    mes = request.args.get("mes")
    ano = request.args.get("ano")
    if mes and ano:
        items = [i for i in items if str(i.get("mes")) == mes and str(i.get("ano")) == ano]
    return jsonify(items)


@salarios_bp.route("/salarios", methods=["POST"])
def criar():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid data"}), 400
    membro_id = data.get("membroId") or data.get("nome", "")
    valor = data.get("valor", 0)
    mes = data.get("mes", 0)
    ano = data.get("ano", 0)
    if not membro_id or float(valor) <= 0 or int(mes) < 1 or int(mes) > 12 or int(ano) < 1900:
        return jsonify({"error": "invalid fields"}), 400
    store = _get_store()
    item = store.create(data)
    return jsonify(item), 201


@salarios_bp.route("/salarios/<id>", methods=["GET"])
def obter(id):
    store = _get_store()
    item = store.get_by_id(id)
    if item is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(item)


@salarios_bp.route("/salarios/<id>/update", methods=["POST"])
def atualizar(id):
    store = _get_store()
    item = store.get_by_id(id)
    if item is None:
        return jsonify({"error": "not found"}), 404
    data = request.get_json()
    updated = store.update(id, data)
    return jsonify(updated)


@salarios_bp.route("/salarios/<id>/delete", methods=["POST"])
def deletar(id):
    store = _get_store()
    item = store.get_by_id(id)
    if item is None:
        return jsonify({"error": "not found"}), 404
    store.delete(id)
    return jsonify({"success": True})
