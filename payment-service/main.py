import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from time import perf_counter
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, Request
from prometheus_client import Counter, Histogram, make_asgi_app
from pydantic import BaseModel, Field


SERVICE_NAME = "payment-service"

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

app = FastAPI(title="Payment Service")

# ─── Prometheus metrics ───────────────────────────────────────────────────────
PAYMENT_COUNTER = Counter(
    "meshmart_payments_total",
    "Total payment requests processed, labelled by outcome and mode",
    ["status", "mode"],
)
PAYMENT_DURATION_HISTOGRAM = Histogram(
    "meshmart_payment_duration_seconds",
    "Payment processing latency in seconds (includes simulated delay)",
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)
PAYMENT_AMOUNT_HISTOGRAM = Histogram(
    "meshmart_payment_amount_usd",
    "Payment amount in USD",
    buckets=[10, 50, 100, 250, 500, 1000, 2000, 5000],
)

# Expose /metrics endpoint
app.mount("/metrics", make_asgi_app())


class PaymentRequest(BaseModel):
    order_id: str = Field(min_length=1)
    amount: float = Field(gt=0)
    mode: Literal["success", "failed", "delayed", "fail", "slow"] = "success"


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
    return {"service": "payment-service", "status": "ok"}


@app.get("/health/live")
async def liveness():
    return {"status": "alive", "service": SERVICE_NAME}


@app.get("/health/ready")
async def readiness():
    return {"status": "ready", "service": SERVICE_NAME}


@app.get("/payment")
async def payment_probe(
    mode: Literal["success", "fail", "slow"] = Query(default="success"),
    order_id: str | None = Query(default=None),
    amount: float = Query(default=100.0, gt=0),
):
    request = PaymentRequest(order_id=order_id or _temporary_order_id(), amount=amount, mode=mode)
    return await create_payment(request)


@app.post("/payments")
async def create_payment(payment: PaymentRequest):
    mode = _normalize_payment_mode(payment.mode)
    _start = perf_counter()

    if mode == "failed":
        PAYMENT_COUNTER.labels(status="failed", mode=mode).inc()
        PAYMENT_AMOUNT_HISTOGRAM.observe(payment.amount)
        PAYMENT_DURATION_HISTOGRAM.observe(perf_counter() - _start)
        raise HTTPException(
            status_code=402,
            detail={
                "order_id": payment.order_id,
                "payment_status": "failed",
                "reason": "Simulated payment failure",
            },
        )

    if mode == "delayed":
        await asyncio.sleep(5)
        _duration = perf_counter() - _start
        PAYMENT_COUNTER.labels(status="success", mode=mode).inc()
        PAYMENT_AMOUNT_HISTOGRAM.observe(payment.amount)
        PAYMENT_DURATION_HISTOGRAM.observe(_duration)
        return {
            "order_id": payment.order_id,
            "amount": payment.amount,
            "payment_status": "success",
            "mode": mode,
            "delay_seconds": 5,
        }

    _duration = perf_counter() - _start
    PAYMENT_COUNTER.labels(status="success", mode=mode).inc()
    PAYMENT_AMOUNT_HISTOGRAM.observe(payment.amount)
    PAYMENT_DURATION_HISTOGRAM.observe(_duration)
    return {
        "order_id": payment.order_id,
        "amount": payment.amount,
        "payment_status": "success",
        "mode": mode,
    }


def _normalize_payment_mode(mode: str) -> Literal["success", "failed", "delayed"]:
    aliases = {
        "fail": "failed",
        "slow": "delayed",
    }
    return aliases.get(mode, mode)


def _temporary_order_id() -> str:
    return f"PAY-TMP-{uuid4().hex[:8].upper()}"


@app.post("/payment/process")
async def process_payment(payment: PaymentRequest):
    return {
        "order_id": payment.order_id,
        "amount": payment.amount,
        "payment_status": "success",
    }


@app.post("/payment/fail")
async def fail_payment(payment: PaymentRequest):
    raise HTTPException(
        status_code=402,
        detail={
            "order_id": payment.order_id,
            "payment_status": "failed",
            "reason": "Simulated payment failure",
        },
    )


@app.post("/payment/delay")
async def delay_payment(payment: PaymentRequest):
    await asyncio.sleep(5)
    return {
        "order_id": payment.order_id,
        "amount": payment.amount,
        "payment_status": "success",
        "delay_seconds": 5,
    }
