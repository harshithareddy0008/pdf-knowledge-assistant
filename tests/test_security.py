"""Authentication and workspace format tests without a live server."""
from uuid import uuid4

from fastapi import HTTPException
import pytest

from backend.config import Settings
from backend import security


def test_shared_token_accepts_only_matching_secret(monkeypatch):
    monkeypatch.setattr(security, "get_settings", lambda: Settings(app_access_token="long-secret"))
    assert security.require_token("long-secret") is None
    with pytest.raises(HTTPException) as exc:
        security.require_token("wrong")
    assert exc.value.status_code == 401


def test_workspace_must_be_uuid4():
    workspace = uuid4()
    assert security.get_workspace(str(workspace)) == workspace.hex
    with pytest.raises(HTTPException) as exc:
        security.get_workspace("../../another-user")
    assert exc.value.status_code == 400
