"""Server-side HTTP client: never send Gemini key to the browser."""
import os

import requests
from dotenv import load_dotenv

load_dotenv()


class APIError(RuntimeError):
    pass


def request_api(method: str, path: str, workspace: str, **kwargs) -> dict:
    base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    token = os.getenv("APP_ACCESS_TOKEN", "")
    if not token:
        raise APIError("APP_ACCESS_TOKEN is not configured on Streamlit.")
    try:
        response = requests.request(
            method,
            f"{base_url}{path}",
            headers={"X-App-Token": token, "X-Workspace-ID": workspace},
            timeout=(10, 180),
            **kwargs,
        )
    except requests.RequestException as exc:
        raise APIError("Cannot reach FastAPI backend. Check API_BASE_URL and service status.") from exc
    if not response.ok:
        try:
            detail = response.json().get("detail", response.text[:250])
        except ValueError:
            detail = response.text[:250]
        raise APIError(f"API error ({response.status_code}): {detail}")
    return response.json()
