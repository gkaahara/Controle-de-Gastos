import os


SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
