from flask import Blueprint, jsonify, request
from app.store_factory import get_store
from app.constants import (
    FIELD_NOME,
    ERROR_NOT_FOUND,
    ERROR_NOME_REQUIRED,
    RESPONSE_ERROR,
    RESPONSE_SUCCESS,
    FILE_CATEGORIAS,
    HTTP_OK,
    HTTP_CREATED,
    HTTP_BAD_REQUEST,
    HTTP_NOT_FOUND,
)

categorias_bp = Blueprint("categorias", __name__)


@categorias_bp.route("/categorias", methods=["GET"])
def listar():
    store = get_store(FILE_CATEGORIAS)
    return jsonify(store.get_all())


@categorias_bp.route("/categorias", methods=["POST"])
def criar():
    data = request.get_json()
    if not data or not data.get(FIELD_NOME):
        return jsonify({RESPONSE_ERROR: ERROR_NOME_REQUIRED}), HTTP_BAD_REQUEST
    store = get_store(FILE_CATEGORIAS)
    item = store.create(data)
    return jsonify(item), HTTP_CREATED


@categorias_bp.route("/categorias/<id>", methods=["GET"])
def obter(id):
    store = get_store(FILE_CATEGORIAS)
    item = store.get_by_id(id)
    if item is None:
        return jsonify({RESPONSE_ERROR: ERROR_NOT_FOUND}), HTTP_NOT_FOUND
    return jsonify(item)


@categorias_bp.route("/categorias/<id>", methods=["PUT"])
def atualizar(id):
    store = get_store(FILE_CATEGORIAS)
    item = store.get_by_id(id)
    if item is None:
        return jsonify({RESPONSE_ERROR: ERROR_NOT_FOUND}), HTTP_NOT_FOUND
    data = request.get_json()
    updated = store.update(id, data)
    return jsonify(updated), HTTP_OK


@categorias_bp.route("/categorias/<id>", methods=["DELETE"])
def deletar(id):
    store = get_store(FILE_CATEGORIAS)
    item = store.get_by_id(id)
    if item is None:
        return jsonify({RESPONSE_ERROR: ERROR_NOT_FOUND}), HTTP_NOT_FOUND
    store.delete(id)
    return jsonify({RESPONSE_SUCCESS: True}), HTTP_OK
