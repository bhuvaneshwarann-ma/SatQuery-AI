"""Limit multipart bodies before Starlette can spool unlimited uploads."""
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse


class BodyLimitMiddleware:
    def __init__(self, app, max_bytes: int = 61 * 1024 * 1024):
        self.app, self.max_bytes = app, max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = dict(scope.get("headers", []))
        try:
            length = int(headers.get(b"content-length", b"0"))
        except ValueError:
            length = self.max_bytes + 1
        if length > self.max_bytes:
            return await JSONResponse({"detail": "Request exceeds upload limit."}, 413)(scope, receive, send)
        consumed = 0

        async def limited_receive():
            nonlocal consumed
            message = await receive()
            consumed += len(message.get("body", b""))
            if consumed > self.max_bytes:
                raise HTTPException(413, "Request exceeds upload limit.")
            return message

        await self.app(scope, limited_receive, send)
