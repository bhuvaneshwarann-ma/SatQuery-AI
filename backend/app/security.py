"""Small deployment security boundary for the single-tenant public gateway."""
import hashlib
import hmac
from fastapi import Header, HTTPException, Request
from .config import PUBLIC_API_KEY, PUBLIC_DEPLOYMENT


def client_id(request: Request, api_key: str | None = None) -> str:
    raw = api_key or request.client.host if request.client else "anonymous"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def require_public_key(request: Request, x_api_key: str | None = Header(default=None)) -> str:
    if not PUBLIC_DEPLOYMENT:
        return client_id(request, x_api_key)
    if not x_api_key or not hmac.compare_digest(x_api_key, PUBLIC_API_KEY):
        raise HTTPException(status_code=401, detail="A valid X-API-Key is required.")
    return client_id(request, x_api_key)
