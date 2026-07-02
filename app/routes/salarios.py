from flask import Blueprint, jsonify, request
from app.store_factory import get_store
from app.constants import (
    FIELD_NOME,
    FIELD_MES,
    FIELD_ANO,
    FIELD_VALOR,
    ERROR_NOT_FOUND,
    RESPONSE_ERROR,
    RESPONSE_SUCCESS,
    FILE_SALARIOS,
    HTTP_OK,
    HTTP_CREATED,
    HTTP_BAD_REQUEST,
    HTTP_NOT_FOUND,
)

salarios_bp = Blueprint("salarios", __name__)


@salarios_bp.route("/salarios", methods=["GET"])
def listar():
    store = get_store(FILE_SALARIOS)
    items = store.get_all()
    mes = request.args.get(FIELD_MES)
    ano = request.args.get(FIELD_ANO)
    if mes and ano:
        items = [i for i in items if str(i.get(FIELD_MES)) == mes and str(i.get(FIELD_ANO)) == ano]
    return jsonify(items)


@salarios_bp.route("/salarios", methods=["POST"])
def criar():
    data = request.get_json()
    if not data:
        return jsonify({RESPONSE_ERROR: "invalid data"}), HTTP_BAD_REQUEST
    membro_id = data.get("membroId") or data.get(FIELD_NOME, "")
    valor = data.get(FIELD_VALOR, 0)
    mes = data.get(FIELD_MES, 0)
    ano = data.get(FIELD_ANO, 0)
    if not membro_id or float(valor) <= 0 or int(mes) < 1 or int(mes) > 12 or int(ano) < 1900:
        return jsonify({RESPONSE_ERROR: "invalid fields"}), HTTP_BAD_REQUEST
    store = get_store(FILE_SALARIOS)
    item = store.create(data)
    return jsonify(item), HTTP_CREATED


@salarios_bp.route("/salarios/<id>", methods=["GET"])
def obter(id):
    store = get_store(FILE_SALARIOS)
    item = store.get_by_id(id)
    if item is None:
        return jsonify({RESPONSE_ERROR: ERROR_NOT_FOUND}), HTTP_NOT_FOUND
    return jsonify(item)


@salarios_bp.route("/salarios/<id>", methods=["PUT"])
def atualizar(id):
    store = get_store(FILE_SALARIOS)
    item = store.get_by_id(id)
    if item is None:
        return jsonify({RESPONSE_ERROR: ERROR_NOT_FOUND}), HTTP_NOT_FOUND
    data = request.get_json()
    updated = store.update(id, data)
    return jsonify(updated), HTTP_OK


@salarios_bp.route("/salarios/<id>", methods=["DELETE"])
def deletar(id):
    store = get_store(FILE_SALARIOS)
    item = store.get_by_id(id)
    if item is None:
        return jsonify({RESPONSE_ERROR: ERROR_NOT_FOUND}), HTTP_NOT_FOUND
    store.delete(id)
    return jsonify({RESPONSE_SUCCESS: True}), HTTP_OK
