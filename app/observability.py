"""Request-scoped telemetry; never log questions, answers, or credentials."""

import json
import logging
from contextvars import ContextVar
from dataclasses import dataclass
from time import perf_counter
from uuid import uuid4

from starlette.responses import JSONResponse

MAX_BODY_BYTES = 16_384
logger = logging.getLogger("fastapiguide.requests")
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)
logger.propagate = False


@dataclass
class RequestMetrics:
    llm_calls: int = 0
    unknown_usage: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cache: str = "bypass"

    def usage(self):
        known = self.unknown_usage == 0
        return {
            "prompt_tokens": self.prompt_tokens if known else None,
            "completion_tokens": self.completion_tokens if known else None,
            "total_tokens": self.total_tokens if known else None,
            "usage_known": known,
        }


current_metrics: ContextVar[RequestMetrics | None] = ContextVar("request_metrics", default=None)


def tracked_completion(client, **kwargs):
    """Account for actual provider usage, including calls made by the agent."""
    metrics = current_metrics.get()
    if metrics is not None:
        metrics.llm_calls += 1
        metrics.unknown_usage += 1
    completion = client.chat.completions.create(**kwargs)
    usage = getattr(completion, "usage", None)
    counts = [getattr(usage, key, None) for key in
              ("prompt_tokens", "completion_tokens", "total_tokens")]
    if metrics is not None and all(isinstance(n, int) and n >= 0 for n in counts):
        metrics.prompt_tokens += counts[0]
        metrics.completion_tokens += counts[1]
        metrics.total_tokens += counts[2]
        metrics.unknown_usage -= 1
    return completion


class RequestTelemetryMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        start = perf_counter()
        request_id = uuid4().hex
        metrics = RequestMetrics()
        token = current_metrics.set(metrics)
        status = 500

        async def measured_send(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                usage = metrics.usage()
                message = {**message, "headers": [*message.get("headers", []),
                    (b"x-request-id", request_id.encode()),
                    (b"x-process-time-ms", f"{(perf_counter() - start) * 1000:.3f}".encode()),
                    (b"x-cache", metrics.cache.encode()),
                    (b"x-total-tokens", str(usage["total_tokens"]).encode() if usage["usage_known"] else b"unknown"),
                ]}
            await send(message)

        async def too_large():
            response = JSONResponse(
                {"detail": f"Request body exceeds {MAX_BODY_BYTES} bytes"}, status_code=413,
            )
            await response(scope, receive, measured_send)

        try:
            headers = dict(scope.get("headers", []))
            length = headers.get(b"content-length", b"0")
            if length.isdigit() and int(length) > MAX_BODY_BYTES:
                return await too_large()
            body = bytearray()
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    status = 499
                    return
                body.extend(message.get("body", b""))
                if len(body) > MAX_BODY_BYTES:
                    return await too_large()
                if not message.get("more_body", False):
                    break
            consumed = False

            async def replay_receive():
                nonlocal consumed
                if consumed:
                    return await receive()
                consumed = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}

            await self.app(scope, replay_receive, measured_send)
        finally:
            route = scope.get("route")
            logger.info(json.dumps({
                "event": "request", "request_id": request_id,
                "method": scope["method"],
                "route": getattr(route, "path", "unmatched"),
                "status": status,
                "latency_ms": round((perf_counter() - start) * 1000, 3),
                "llm_calls": metrics.llm_calls, "cache": metrics.cache,
                **metrics.usage(),
            }))
            current_metrics.reset(token)
