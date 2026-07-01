"""Tests for shared constants module."""

import pytest
from app.constants import (
    # Field names
    FIELD_DESCRICAO,
    FIELD_VALOR,
    FIELD_NOME,
    FIELD_CATEGORIAS,
    FIELD_CATEGORIA_ID,
    FIELD_DATA,
    FIELD_MES,
    FIELD_ANO,
    FIELD_VENCIMENTO,
    FIELD_BANDEIRA,
    FIELD_SALARIO,
    FIELD_ITENS,
    FIELD_TEXT,
    FIELD_FILE,
    # Error messages
    ERROR_NOT_FOUND,
    ERROR_DESCRICAO_VALOR_REQUIRED,
    ERROR_NOME_REQUIRED,
    ERROR_MES_ANO_REQUIRED,
    # Response keys
    RESPONSE_ERROR,
    RESPONSE_SUCCESS,
    # Default values
    DEFAULT_DATA_DIR,
)


class TestConstants:
    """Test that all required constants are defined."""

    def test_field_names_defined(self):
        """Test field name constants are defined."""
        assert FIELD_DESCRICAO == "descricao"
        assert FIELD_VALOR == "valor"
        assert FIELD_NOME == "nome"
        assert FIELD_CATEGORIAS == "categorias"
        assert FIELD_CATEGORIA_ID == "categoriaId"
        assert FIELD_DATA == "data"
        assert FIELD_MES == "mes"
        assert FIELD_ANO == "ano"
        assert FIELD_VENCIMENTO == "vencimento"
        assert FIELD_BANDEIRA == "bandeira"
        assert FIELD_SALARIO == "salario"
        assert FIELD_ITENS == "itens"
        assert FIELD_TEXT == "text"
        assert FIELD_FILE == "file"

    def test_error_messages_defined(self):
        """Test error message constants are defined."""
        assert isinstance(ERROR_NOT_FOUND, str)
        assert "not found" in ERROR_NOT_FOUND.lower()
        assert isinstance(ERROR_DESCRICAO_VALOR_REQUIRED, str)
        assert isinstance(ERROR_NOME_REQUIRED, str)
        assert isinstance(ERROR_MES_ANO_REQUIRED, str)

    def test_response_keys_defined(self):
        """Test response key constants are defined."""
        assert RESPONSE_ERROR == "error"
        assert RESPONSE_SUCCESS == "success"

    def test_default_values_defined(self):
        """Test default value constants are defined."""
        assert DEFAULT_DATA_DIR is not None

    def test_constants_are_strings(self):
        """Test that field name and key constants are strings."""
        for const in [
            FIELD_DESCRICAO,
            FIELD_VALOR,
            FIELD_NOME,
            RESPONSE_ERROR,
            RESPONSE_SUCCESS,
        ]:
            assert isinstance(const, str)

    def test_no_duplicate_field_values(self):
        """Test that field constants don't have unintended duplicates."""
        field_values = {
            FIELD_DESCRICAO,
            FIELD_VALOR,
            FIELD_NOME,
            FIELD_DATA,
            FIELD_MES,
            FIELD_ANO,
        }
        # Each should be unique
        assert len(field_values) == 6


class TestConstantsUsage:
    """Test that constants can be used in typical scenarios."""

    def test_field_constant_for_dict_access(self):
        """Test field constants work for dict.get() access."""
        test_data = {
            FIELD_DESCRICAO: "Test Item",
            FIELD_VALOR: 100.50,
        }
        assert test_data.get(FIELD_DESCRICAO) == "Test Item"
        assert test_data.get(FIELD_VALOR) == 100.50

    def test_error_constant_for_json_response(self):
        """Test error constants work in JSON response construction."""
        response = {RESPONSE_ERROR: ERROR_NOT_FOUND}
        assert response == {"error": "not found"}

    def test_success_constant_for_json_response(self):
        """Test success constants work in JSON response construction."""
        response = {RESPONSE_SUCCESS: True}
        assert response == {"success": True}

    def test_all_constants_are_accessible(self):
        """Test that all constants can be imported and used."""
        constants = {
            "FIELD_DESCRICAO": FIELD_DESCRICAO,
            "FIELD_VALOR": FIELD_VALOR,
            "FIELD_NOME": FIELD_NOME,
            "ERROR_NOT_FOUND": ERROR_NOT_FOUND,
            "RESPONSE_ERROR": RESPONSE_ERROR,
            "RESPONSE_SUCCESS": RESPONSE_SUCCESS,
        }
        # All should exist and have values
        for name, const in constants.items():
            assert const is not None, f"{name} should not be None"
