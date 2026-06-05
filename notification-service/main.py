import json
import logging
import os
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from prometheus_client import Counter, Gauge, make_asgi_app
from pydantic import BaseModel


SERVICE_NAME = "notification-service"

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "service": SERVICE_NAME,
            "message": record.getMessage()
        }
        STANDARD_ATTRS = {
            "args", "asctime", "created", "exc_info", "exc_text", "filename", "funcName",
            "levelname", "levelno", "lineno", "message", "module", "msecs", "msg", "name",
            "pathname", "process", "processName", "relativeCreated", "stack_info", "thread",
            "threadName"
        }
        for key, val in record.__dict__.items():
            if key not in STANDARD_ATTRS:
                log_entry[key] = val
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
for h in root_logger.handlers[:]:
    root_logger.removeHandler(h)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
root_logger.addHandler(handler)

logger = logging.getLogger(SERVICE_NAME)

app = FastAPI(title="Notification Service")

# ─── Prometheus metrics ───────────────────────────────────────────────────────
NOTIFICATION_COUNTER = Counter(
    "meshmart_notifications_total",
    "Total notifications dispatched, labelled by payment outcome",
    ["payment_status"],
)
NOTIFICATIONS_SENT_GAUGE = Gauge(
    "meshmart_notifications_sent_total_gauge",
    "Running total of notifications sent (for dashboard stat panel)",
)

# Expose /metrics endpoint
app.mount("/metrics", make_asgi_app())


class NotificationRequest(BaseModel):
    order_id: str
    user_id: str
    payment_status: str


@app.middleware("http")
async def access_log(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or uuid4().hex[:12]
    start = perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (perf_counter() - start) * 1000
        logger.exception(
            "Request failed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": 500,
                "duration_ms": duration_ms
            }
        )
        raise

    duration_ms = (perf_counter() - start) * 1000
    response.headers["x-request-id"] = request_id
    logger.info(
        "Request processed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": duration_ms
        }
    )
    return response


@app.get("/health")
async def health():
    return {"service": "notification-service", "status": "ok"}


@app.get("/health/live")
async def liveness():
    return {"status": "alive", "service": SERVICE_NAME}


@app.get("/health/ready")
async def readiness():
    return {"status": "ready", "service": SERVICE_NAME}


@app.post("/notifications")
async def create_notification(notification: NotificationRequest):
    NOTIFICATION_COUNTER.labels(payment_status=notification.payment_status).inc()
    NOTIFICATIONS_SENT_GAUGE.inc()
    return {
        "order_id": notification.order_id,
        "user_id": notification.user_id,
        "payment_status": notification.payment_status,
        "notification": "sent",
        "message": f"Order {notification.order_id} payment is {notification.payment_status}",
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }
