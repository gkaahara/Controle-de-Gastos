import os
from flask import Flask, jsonify

DEFAULT_CATEGORIES = [
    {"nome": "Moradia", "cor": "#e74c3c"},
    {"nome": "Alimentação", "cor": "#f39c12"},
    {"nome": "Transporte", "cor": "#3498db"},
    {"nome": "Saúde", "cor": "#2ecc71"},
    {"nome": "Lazer", "cor": "#9b59b6"},
    {"nome": "Educação", "cor": "#1abc9c"},
    {"nome": "Assinaturas", "cor": "#e67e22"},
    {"nome": "Outros", "cor": "#95a5a6"},
]


def seed_default_categories(app):
    from app.store_factory import get_store
    store = get_store("categorias.json")
    existing = store.get_all()
    if existing:
        return
    for cat in DEFAULT_CATEGORIES:
        store.create(cat)


def create_app(test_config=None, data_dir=None):
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), "templates"),
                static_folder=os.path.join(os.path.dirname(__file__), "static"))

    if test_config:
        app.config.update(test_config)
    else:
        app.config.from_pyfile("config.py", silent=True)
    if data_dir:
        app.config["DATA_DIR"] = data_dir

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.routes.categorias import categorias_bp
    app.register_blueprint(categorias_bp)

    from app.routes.salarios import salarios_bp
    app.register_blueprint(salarios_bp)

    from app.routes.gastos_casa import gastos_casa_bp
    app.register_blueprint(gastos_casa_bp)

    from app.routes.cartoes import cartoes_bp
    app.register_blueprint(cartoes_bp)

    from app.routes.relatorios import relatorios_bp
    app.register_blueprint(relatorios_bp)

    from app.routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    if not test_config:
        with app.app_context():
            seed_default_categories(app)

    return app

