from flask import Blueprint, jsonify, request
from app.store_factory import get_store
from app.constants import (
    FIELD_DESCRICAO,
    FIELD_VALOR,
    FIELD_CATEGORIA_ID,
    FIELD_DATA,
    FIELD_MES,
    FIELD_ANO,
    ERROR_NOT_FOUND,
    ERROR_DESCRICAO_VALOR_REQUIRED,
    RESPONSE_ERROR,
    RESPONSE_SUCCESS,
    FILE_GASTOS_CASA,
    HTTP_OK,
    HTTP_CREATED,
    HTTP_BAD_REQUEST,
    HTTP_NOT_FOUND,
)

gastos_casa_bp = Blueprint("gastos_casa", __name__)


@gastos_casa_bp.route("/gastos-casa", methods=["GET"])
def listar():
    store = get_store(FILE_GASTOS_CASA)
    items = store.get_all()
    mes = request.args.get(FIELD_MES)
    ano = request.args.get(FIELD_ANO)
    categoria = request.args.get("categoria")
    if mes and ano:
        items = [i for i in items if i.get(FIELD_DATA, "").startswith(f"{ano}-{int(mes):02d}")]
    if categoria:
        items = [i for i in items if i.get(FIELD_CATEGORIA_ID) == categoria]
    return jsonify(items)


@gastos_casa_bp.route("/gastos-casa", methods=["POST"])
def criar():
    data = request.get_json()
    if not data or not data.get(FIELD_DESCRICAO) or float(data.get(FIELD_VALOR, 0)) <= 0:
        return jsonify({RESPONSE_ERROR: ERROR_DESCRICAO_VALOR_REQUIRED}), HTTP_BAD_REQUEST
    store = get_store(FILE_GASTOS_CASA)
    item = store.create(data)
    return jsonify(item), HTTP_CREATED


@gastos_casa_bp.route("/gastos-casa/<id>", methods=["GET"])
def obter(id):
    store = get_store(FILE_GASTOS_CASA)
    item = store.get_by_id(id)
    if item is None:
        return jsonify({RESPONSE_ERROR: ERROR_NOT_FOUND}), HTTP_NOT_FOUND
    return jsonify(item)


@gastos_casa_bp.route("/gastos-casa/<id>", methods=["PUT"])
def atualizar(id):
    store = get_store(FILE_GASTOS_CASA)
    item = store.get_by_id(id)
    if item is None:
        return jsonify({RESPONSE_ERROR: ERROR_NOT_FOUND}), HTTP_NOT_FOUND
    updated = store.update(id, request.get_json())
    return jsonify(updated), HTTP_OK


@gastos_casa_bp.route("/gastos-casa/<id>", methods=["DELETE"])
def deletar(id):
    store = get_store(FILE_GASTOS_CASA)
    item = store.get_by_id(id)
    if item is None:
        return jsonify({RESPONSE_ERROR: ERROR_NOT_FOUND}), HTTP_NOT_FOUND
    store.delete(id)
    return jsonify({RESPONSE_SUCCESS: True}), HTTP_OK
