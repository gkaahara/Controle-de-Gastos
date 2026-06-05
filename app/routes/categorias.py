import os
from flask import Blueprint, jsonify, request, current_app
from app.json_store import JsonStore


categorias_bp = Blueprint("categorias", __name__)


def _get_store():
    data_dir = current_app.config.get("DATA_DIR",
                                      os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    return JsonStore(os.path.join(data_dir, "categorias.json"))


@categorias_bp.route("/categorias", methods=["GET"])
def listar():
    store = _get_store()
    return jsonify(store.get_all())


@categorias_bp.route("/categorias", methods=["POST"])
def criar():
    data = request.get_json()
    if not data or not data.get("nome"):
        return jsonify({"error": "nome is required"}), 400
    store = _get_store()
    item = store.create(data)
    return jsonify(item), 201


@categorias_bp.route("/categorias/<id>", methods=["GET"])
def obter(id):
    store = _get_store()
    item = store.get_by_id(id)
    if item is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(item)


@categorias_bp.route("/categorias/<id>/update", methods=["POST"])
def atualizar(id):
    store = _get_store()
    item = store.get_by_id(id)
    if item is None:
        return jsonify({"error": "not found"}), 404
    data = request.get_json()
    updated = store.update(id, data)
    return jsonify(updated)


@categorias_bp.route("/categorias/<id>/delete", methods=["POST"])
def deletar(id):
    store = _get_store()
    item = store.get_by_id(id)
    if item is None:
        return jsonify({"error": "not found"}), 404
    store.delete(id)
    return jsonify({"success": True})
