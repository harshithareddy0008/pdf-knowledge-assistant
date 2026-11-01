"""Shared API token and opaque per-browser workspace IDs for a portfolio demo."""
import hmac
from uuid import UUID

from fastapi import Header, HTTPException

from backend.config import get_settings


def require_token(x_app_token: str | None = Header(default=None, alias="X-App-Token")) -> None:
    expected = get_settings().app_access_token
    if not expected:
        raise HTTPException(status_code=503, detail="APP_ACCESS_TOKEN is not configured on API.")
    if not x_app_token or not hmac.compare_digest(x_app_token, expected):
        raise HTTPException(status_code=401, detail="Invalid app access token.")


def get_workspace(x_workspace_id: str | None = Header(default=None, alias="X-Workspace-ID")) -> str:
    if not x_workspace_id:
        raise HTTPException(status_code=400, detail="X-Workspace-ID header is required.")
    try:
        workspace = UUID(x_workspace_id)
    except (ValueError, AttributeError) as exc:
        raise HTTPException(status_code=400, detail="Invalid workspace ID.") from exc
    if workspace.version != 4:
        raise HTTPException(status_code=400, detail="Workspace must be a UUID4.")
    return workspace.hex
