import pytest
from app import create_app


@pytest.fixture
def app():
    app = create_app({"TESTING": True})
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class TestAppScaffold:
    def test_app_creates_successfully(self, app):
        assert app is not None
        assert app.config["TESTING"] is True

    def test_health_route_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_route_returns_json(self, client):
        resp = client.get("/health")
        assert resp.is_json
        data = resp.get_json()
        assert data["status"] == "ok"

    def test_template_folder_configured(self, app):
        assert "templates" in app.template_folder

    def test_static_folder_configured(self, app):
        assert app.static_folder is not None
        assert "static" in app.static_folder
