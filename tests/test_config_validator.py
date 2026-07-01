"""Tests for config validation with Pydantic schema."""

import os
import pytest
from pydantic import ValidationError

from app.config_validator import ConfigValidator, ConfigError


class TestConfigValidator:
    """Test Pydantic schema validation for Flask config."""

    def test_create_validator(self):
        """Test ConfigValidator instantiation."""
        validator = ConfigValidator()
        assert validator is not None

    def test_secret_key_not_dev_in_production(self):
        """Test that SECRET_KEY cannot be 'dev-secret-key' in production."""
        env_vars = {
            "ENVIRONMENT": "production",
            "SECRET_KEY": "dev-secret-key",
            "DEBUG": "false",
        }
        with pytest.raises(ConfigError) as exc_info:
            ConfigValidator.validate(env_vars)
        assert "SECRET_KEY" in str(exc_info.value)

    def test_secret_key_allowed_in_development(self):
        """Test that SECRET_KEY can be 'dev-secret-key' in development."""
        env_vars = {
            "ENVIRONMENT": "development",
            "SECRET_KEY": "dev-secret-key",
            "DEBUG": "true",
        }
        # Should not raise
        result = ConfigValidator.validate(env_vars)
        assert result["SECRET_KEY"] == "dev-secret-key"

    def test_debug_false_in_production(self):
        """Test that DEBUG must be False in production."""
        env_vars = {
            "ENVIRONMENT": "production",
            "SECRET_KEY": "secure-key-1234",
            "DEBUG": "true",
        }
        with pytest.raises(ConfigError) as exc_info:
            ConfigValidator.validate(env_vars)
        assert "DEBUG" in str(exc_info.value)

    def test_debug_false_in_production_strict(self):
        """Test that DEBUG=true explicitly fails in production."""
        env_vars = {
            "ENVIRONMENT": "production",
            "SECRET_KEY": "secure-key-1234",
            "DEBUG": "true",
        }
        with pytest.raises(ConfigError):
            ConfigValidator.validate(env_vars)

    def test_valid_production_config(self):
        """Test valid production configuration passes."""
        env_vars = {
            "ENVIRONMENT": "production",
            "SECRET_KEY": "secure-key-production-12345",
            "DEBUG": "false",
        }
        result = ConfigValidator.validate(env_vars)
        assert result["ENVIRONMENT"] == "production"
        assert result["SECRET_KEY"] == "secure-key-production-12345"
        assert result["DEBUG"] is False

    def test_valid_development_config(self):
        """Test valid development configuration passes."""
        env_vars = {
            "ENVIRONMENT": "development",
            "SECRET_KEY": "dev-key",
            "DEBUG": "true",
        }
        result = ConfigValidator.validate(env_vars)
        assert result["ENVIRONMENT"] == "development"
        assert result["DEBUG"] is True

    def test_validate_from_os_environ(self):
        """Test validation directly from os.environ."""
        # Save original values
        orig_env = os.environ.get("ENVIRONMENT")
        orig_secret = os.environ.get("SECRET_KEY")
        orig_debug = os.environ.get("DEBUG")

        try:
            # Set test values
            os.environ["ENVIRONMENT"] = "production"
            os.environ["SECRET_KEY"] = "test-secret-key-1234"
            os.environ["DEBUG"] = "false"

            # Should validate without error
            result = ConfigValidator.validate_from_environ()
            assert result["ENVIRONMENT"] == "production"
            assert result["DEBUG"] is False
        finally:
            # Restore original values
            if orig_env is None:
                os.environ.pop("ENVIRONMENT", None)
            else:
                os.environ["ENVIRONMENT"] = orig_env
            if orig_secret is None:
                os.environ.pop("SECRET_KEY", None)
            else:
                os.environ["SECRET_KEY"] = orig_secret
            if orig_debug is None:
                os.environ.pop("DEBUG", None)
            else:
                os.environ["DEBUG"] = orig_debug

    def test_config_error_has_helpful_message(self):
        """Test that ConfigError provides helpful error messages."""
        env_vars = {
            "ENVIRONMENT": "production",
            "SECRET_KEY": "dev-secret-key",
            "DEBUG": "true",
        }
        with pytest.raises(ConfigError) as exc_info:
            ConfigValidator.validate(env_vars)
        error_msg = str(exc_info.value)
        assert len(error_msg) > 0
        assert "validation" in error_msg.lower() or "secret_key" in error_msg.lower() or "debug" in error_msg.lower()
