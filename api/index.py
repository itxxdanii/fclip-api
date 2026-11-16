import json

from app import app as fastapi_app


async def app(scope, receive, send):
    if scope["type"] == "http":
        headers = {k.decode(): v.decode() for k, v in scope.get("headers", [])}
        data = {
            "path": scope.get("path"),
            "raw_path": scope.get("raw_path", b"").decode(errors="ignore"),
            "root_path": scope.get("root_path"),
            "query_string": scope.get("query_string", b"").decode(),
            "method": scope.get("method"),
            "headers": headers,
        }
        body = json.dumps(data, indent=2).encode()
        await send({"type": "http.response.start", "status": 200, "headers": [[b"content-type", b"application/json"]]})
        await send({"type": "http.response.body", "body": body})
        return
    await fastapi_app(scope, receive, send)
