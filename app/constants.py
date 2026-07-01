"""Shared constants module for field names, error messages, and default values."""

import os

# ============================================================================
# FIELD NAMES - Common field names used across routes
# ============================================================================

# Cartoes (Credit Cards) fields
FIELD_DESCRICAO = "descricao"
FIELD_VALOR = "valor"
FIELD_BANDEIRA = "bandeira"
FIELD_VENCIMENTO = "vencimento"

# Categorias fields
FIELD_NOME = "nome"
FIELD_CATEGORIAS = "categorias"

# Gastos Casa (Household Expenses) fields
FIELD_CATEGORIA_ID = "categoriaId"
FIELD_DATA = "data"

# Dashboard/Salarios fields
FIELD_MES = "mes"
FIELD_ANO = "ano"
FIELD_SALARIO = "salario"

# Parse/Import fields
FIELD_ITENS = "itens"
FIELD_TEXT = "text"
FIELD_FILE = "file"

# ============================================================================
# ERROR MESSAGES - Standard error messages for API responses
# ============================================================================

ERROR_NOT_FOUND = "not found"
ERROR_DESCRICAO_VALOR_REQUIRED = "descricao and positive valor required"
ERROR_NOME_REQUIRED = "nome is required"
ERROR_MES_ANO_REQUIRED = "mes and ano required"
ERROR_CATEGORIAS_REQUIRED = "categorias is required"

# ============================================================================
# RESPONSE KEYS - Common keys in JSON responses
# ============================================================================

RESPONSE_ERROR = "error"
RESPONSE_SUCCESS = "success"

# ============================================================================
# DEFAULT VALUES - Default configuration values
# ============================================================================

DEFAULT_DATA_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "data"
)

# ============================================================================
# DATA FILE NAMES - JSON store file names
# ============================================================================

FILE_CARTOES = "cartoes.json"
FILE_CATEGORIAS = "categorias.json"
FILE_GASTOS_CASA = "gastos_casa.json"
FILE_SALARIOS = "salarios.json"
FILE_RELATORIOS = "relatorios.json"

# ============================================================================
# HTTP RESPONSE CODES - Standard HTTP status codes as constants
# ============================================================================

HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
