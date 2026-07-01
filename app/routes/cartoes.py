from flask import Blueprint, jsonify, request
from app.store_factory import get_store
from app.fatura_parser import parse_fatura_text
from app.constants import (
    FIELD_DESCRICAO,
    FIELD_VALOR,
    FIELD_BANDEIRA,
    FIELD_VENCIMENTO,
    FIELD_CATEGORIA_ID,
    FIELD_ITENS,
    FIELD_TEXT,
    FIELD_FILE,
    ERROR_NOT_FOUND,
    ERROR_DESCRICAO_VALOR_REQUIRED,
    RESPONSE_ERROR,
    RESPONSE_SUCCESS,
    FILE_CARTOES,
    HTTP_OK,
    HTTP_BAD_REQUEST,
    HTTP_NOT_FOUND,
    HTTP_CREATED,
)


cartoes_bp = Blueprint("cartoes", __name__)


@cartoes_bp.route("/cartoes", methods=["GET"])
def listar():
    store = get_store(FILE_CARTOES)
    return jsonify(store.get_all())


@cartoes_bp.route("/cartoes", methods=["POST"])
def criar():
    data = request.get_json()
    if not data or not data.get(FIELD_DESCRICAO) or float(data.get(FIELD_VALOR, 0)) <= 0:
        return jsonify({RESPONSE_ERROR: ERROR_DESCRICAO_VALOR_REQUIRED}), HTTP_BAD_REQUEST
    store = get_store(FILE_CARTOES)
    item = store.create(data)
    return jsonify(item), HTTP_CREATED


@cartoes_bp.route("/cartoes/<id>", methods=["GET"])
def obter(id):
    store = get_store(FILE_CARTOES)
    item = store.get_by_id(id)
    if item is None:
        return jsonify({RESPONSE_ERROR: ERROR_NOT_FOUND}), HTTP_NOT_FOUND
    return jsonify(item)


@cartoes_bp.route("/cartoes/<id>", methods=["PUT"])
def atualizar(id):
    store = get_store(FILE_CARTOES)
    item = store.get_by_id(id)
    if item is None:
        return jsonify({RESPONSE_ERROR: ERROR_NOT_FOUND}), HTTP_NOT_FOUND
    updated = store.update(id, request.get_json())
    return jsonify(updated), HTTP_OK


@cartoes_bp.route("/cartoes/<id>", methods=["DELETE"])
def deletar(id):
    store = get_store(FILE_CARTOES)
    item = store.get_by_id(id)
    if item is None:
        return jsonify({RESPONSE_ERROR: ERROR_NOT_FOUND}), HTTP_NOT_FOUND
    store.delete(id)
    return jsonify({RESPONSE_SUCCESS: True}), HTTP_OK


@cartoes_bp.route("/cartoes/parse", methods=["POST"])
def parse_fatura():
    texto = None
    if request.is_json:
        texto = request.get_json().get(FIELD_TEXT, "")
    elif request.files:
        f = request.files.get(FIELD_FILE)
        if f:
            texto = f.read().decode("utf-8")
    if not texto or not texto.strip():
        return jsonify([])
    return jsonify(parse_fatura_text(texto))


@cartoes_bp.route("/cartoes/import", methods=["POST"])
def importar_fatura():
    data = request.get_json()
    if not data or FIELD_ITENS not in data:
        return jsonify({RESPONSE_ERROR: "itens required"}), HTTP_BAD_REQUEST
    bandeira = data.get(FIELD_BANDEIRA, "Elo")
    vencimento = data.get(FIELD_VENCIMENTO, "")
    categoria_id = data.get(FIELD_CATEGORIA_ID, "")
    store = get_store(FILE_CARTOES)
    criados = []
    for item in data[FIELD_ITENS]:
        if not item.get(FIELD_DESCRICAO) or float(item.get(FIELD_VALOR, 0)) <= 0:
            continue
        novo = {
            FIELD_DESCRICAO: item[FIELD_DESCRICAO],
            FIELD_VALOR: round(float(item[FIELD_VALOR]), 2),
            FIELD_BANDEIRA: bandeira,
            FIELD_VENCIMENTO: vencimento,
            FIELD_CATEGORIA_ID: categoria_id or item.get(FIELD_CATEGORIA_ID, ""),
            "responsavel": item.get("responsavel", "Ambos"),
            "parcelaAtual": int(item.get("parcelaAtual", 1)),
            "totalParcelas": int(item.get("totalParcelas", 1)),
            "dataCompra": item.get("dataCompra", ""),
        }
        criados.append(store.create(novo))
    return jsonify(criados), 201
