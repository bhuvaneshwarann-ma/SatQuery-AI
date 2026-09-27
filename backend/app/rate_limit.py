"""Process-local request limiter for the single-worker public deployment."""
import time
from collections import defaultdict, deque
from starlette.responses import JSONResponse
from .config import PUBLIC_DEPLOYMENT, RATE_LIMIT_PER_MINUTE


class RateLimitMiddleware:
    def __init__(self, app):
        self.app = app
        self.events = defaultdict(deque)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not PUBLIC_DEPLOYMENT or scope.get("path") in {"/health", "/api/health"}:
            return await self.app(scope, receive, send)
        headers = dict(scope.get("headers", []))
        client = scope.get("client")
        identity = headers.get(b"x-api-key", b"").decode() or (client[0] if client else "anonymous")
        now = time.monotonic()
        bucket = self.events[identity]
        while bucket and now - bucket[0] > 60:
            bucket.popleft()
        if len(bucket) >= RATE_LIMIT_PER_MINUTE:
            return await JSONResponse({"detail": "Rate limit exceeded. Retry shortly."}, status_code=429)(scope, receive, send)
        bucket.append(now)
        return await self.app(scope, receive, send)
