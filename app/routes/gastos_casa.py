import os
from flask import Blueprint, jsonify, request, current_app
from app.json_store import JsonStore


gastos_casa_bp = Blueprint("gastos_casa", __name__)


def _get_store():
    data_dir = current_app.config.get("DATA_DIR",
                                      os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    return JsonStore(os.path.join(data_dir, "gastos_casa.json"))


@gastos_casa_bp.route("/gastos-casa", methods=["GET"])
def listar():
    store = _get_store()
    items = store.get_all()
    mes = request.args.get("mes")
    ano = request.args.get("ano")
    categoria = request.args.get("categoria")
    if mes and ano:
        items = [i for i in items if i.get("data", "").startswith(f"{ano}-{int(mes):02d}")]
    if categoria:
        items = [i for i in items if i.get("categoriaId") == categoria]
    return jsonify(items)


@gastos_casa_bp.route("/gastos-casa", methods=["POST"])
def criar():
    data = request.get_json()
    if not data or not data.get("descricao") or float(data.get("valor", 0)) <= 0:
        return jsonify({"error": "descricao and positive valor required"}), 400
    store = _get_store()
    item = store.create(data)
    return jsonify(item), 201


@gastos_casa_bp.route("/gastos-casa/<id>", methods=["GET"])
def obter(id):
    store = _get_store()
    item = store.get_by_id(id)
    if item is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(item)


@gastos_casa_bp.route("/gastos-casa/<id>/update", methods=["POST"])
def atualizar(id):
    store = _get_store()
    item = store.get_by_id(id)
    if item is None:
        return jsonify({"error": "not found"}), 404
    updated = store.update(id, request.get_json())
    return jsonify(updated)


@gastos_casa_bp.route("/gastos-casa/<id>/delete", methods=["POST"])
def deletar(id):
    store = _get_store()
    item = store.get_by_id(id)
    if item is None:
        return jsonify({"error": "not found"}), 404
    store.delete(id)
    return jsonify({"success": True})
