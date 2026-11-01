"""FastAPI routes with mocked storage: no cloud keys or network access."""
from uuid import uuid4

from fastapi.testclient import TestClient

from backend import main, security
from backend.config import Settings


def test_health_does_not_need_credentials():
    response = TestClient(main.app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_docs_endpoint_requires_secret(monkeypatch, tmp_path):
    settings = Settings(app_access_token="test-token", gemini_api_key="dummy", data_dir=tmp_path)
    monkeypatch.setattr(security, "get_settings", lambda: settings)
    monkeypatch.setattr(main, "get_settings", lambda: settings)
    monkeypatch.setattr(main, "make_store", lambda *args: object())
    monkeypatch.setattr(main, "list_documents", lambda store: [])
    client = TestClient(main.app)
    workspace = str(uuid4())
    assert client.get("/documents", headers={"X-Workspace-ID": workspace}).status_code == 401
    response = client.get("/documents", headers={"X-Workspace-ID": workspace, "X-App-Token": "test-token"})
    assert response.status_code == 200
    assert response.json() == {"documents": []}
