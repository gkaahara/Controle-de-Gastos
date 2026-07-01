import os
from app.config_validator import ConfigValidator, ConfigError

# Validate configuration on import
try:
    validated_config = ConfigValidator.validate_from_environ()
except ConfigError as e:
    raise RuntimeError(f"Configuration error: {e}") from e

SECRET_KEY = validated_config["SECRET_KEY"]
DEBUG = validated_config["DEBUG"]
ENVIRONMENT = validated_config["ENVIRONMENT"]
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
