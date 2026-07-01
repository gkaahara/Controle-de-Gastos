"""Configuration validation with Pydantic schema."""

import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, field_validator, ValidationError


class ConfigError(Exception):
    """Raised when configuration validation fails."""
    pass


class ConfigSchema(BaseModel):
    """Pydantic schema for Flask configuration."""

    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "dev-secret-key"
    DEBUG: bool = True

    @field_validator("SECRET_KEY", mode="after")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Validate SECRET_KEY based on environment."""
        env = info.data.get("ENVIRONMENT", "development")

        if env == "production" and v == "dev-secret-key":
            raise ValueError(
                'SECRET_KEY cannot be "dev-secret-key" in production environment. '
                'Set SECRET_KEY environment variable to a secure key.'
            )
        return v

    @field_validator("DEBUG", mode="after")
    @classmethod
    def validate_debug(cls, v: bool, info) -> bool:
        """Validate DEBUG based on environment."""
        env = info.data.get("ENVIRONMENT", "development")

        if env == "production" and v is True:
            raise ValueError(
                "DEBUG cannot be True in production environment. "
                "Set DEBUG=false in environment."
            )
        return v


class ConfigValidator:
    """Validates Flask configuration against schema."""

    @staticmethod
    def validate(env_vars: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration dictionary.

        Args:
            env_vars: Dictionary with ENVIRONMENT, SECRET_KEY, DEBUG

        Returns:
            Validated config dict

        Raises:
            ConfigError: If validation fails
        """
        try:
            # Convert DEBUG string to bool if needed
            debug_val = env_vars.get("DEBUG", "true")
            if isinstance(debug_val, str):
                debug_bool = debug_val.lower() == "true"
            else:
                debug_bool = bool(debug_val)

            config_data = {
                "ENVIRONMENT": env_vars.get("ENVIRONMENT", "development"),
                "SECRET_KEY": env_vars.get("SECRET_KEY", "dev-secret-key"),
                "DEBUG": debug_bool,
            }

            # Validate with Pydantic
            validated = ConfigSchema(**config_data)

            return {
                "ENVIRONMENT": validated.ENVIRONMENT,
                "SECRET_KEY": validated.SECRET_KEY,
                "DEBUG": validated.DEBUG,
            }
        except ValidationError as e:
            raise ConfigError(f"Configuration validation failed: {e}") from e

    @staticmethod
    def validate_from_environ() -> Dict[str, Any]:
        """
        Validate configuration from os.environ.

        Returns:
            Validated config dict

        Raises:
            ConfigError: If validation fails
        """
        env_vars = {
            "ENVIRONMENT": os.environ.get("ENVIRONMENT", "development"),
            "SECRET_KEY": os.environ.get("SECRET_KEY", "dev-secret-key"),
            "DEBUG": os.environ.get("DEBUG", "true"),
        }
        return ConfigValidator.validate(env_vars)
