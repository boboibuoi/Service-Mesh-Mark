import asyncio
import json
import logging
import os
from copy import deepcopy
from datetime import datetime, timezone
from time import monotonic, perf_counter
from typing import Any, Literal
from uuid import NAMESPACE_URL, uuid4, uuid5

import httpx
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    make_asgi_app,
    CONTENT_TYPE_LATEST,
    generate_latest,
    REGISTRY,
)
from pydantic import BaseModel, Field


SERVICE_NAME = "order-service"

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

app = FastAPI(title="Order Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("FRONTEND_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Prometheus metrics ───────────────────────────────────────────────────────
ORDER_COUNTER = Counter(
    "meshmart_orders_total",
    "Total number of orders created, labelled by outcome and payment mode",
    ["status", "payment_mode"],
)
ORDER_DURATION_HISTOGRAM = Histogram(
    "meshmart_order_duration_seconds",
    "End-to-end order processing latency in seconds",
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 15.0],
)
ORDER_AMOUNT_HISTOGRAM = Histogram(
    "meshmart_order_amount_usd",
    "Checkout cart value in USD",
    buckets=[10, 50, 100, 250, 500, 1000, 2000, 5000],
)
IDEMPOTENCY_HIT_COUNTER = Counter(
    "meshmart_idempotency_hits_total",
    "Number of duplicate order requests rejected or served from idempotency cache",
    ["outcome"],  # cached | conflict | in_progress
)
IN_FLIGHT_GAUGE = Gauge(
    "meshmart_order_in_flight",
    "Number of order requests currently being processed",
)
ORDER_ITEMS_HISTOGRAM = Histogram(
    "meshmart_order_items_total",
    "Number of line items (distinct products) per order",
    buckets=[1, 2, 3, 5, 10],
)

# Expose /metrics for Prometheus scraping
app.mount("/metrics", make_asgi_app())

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8004")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8002")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8003")
IDEMPOTENCY_TTL_SECONDS = int(os.getenv("IDEMPOTENCY_TTL_SECONDS", "600"))

_idempotency_lock = asyncio.Lock()
_idempotency_store: dict[str, dict] = {}
_orders_lock = asyncio.Lock()
_orders_store: dict[str, dict[str, Any]] = {}

PaymentMode = Literal["success", "failed", "delayed", "process", "fail", "delay", "slow"]


class OrderItem(BaseModel):
    product_id: str = Field(min_length=1)
    quantity: int = Field(default=1, gt=0)


class OrderRequest(BaseModel):
    user_id: str = Field(min_length=1)
    product_id: str | None = Field(default=None, min_length=1)
    quantity: int = Field(default=1, gt=0)
    items: list[OrderItem] | None = None
    payment_mode: PaymentMode = "success"


class PaymentRequest(BaseModel):
    order_id: str
    amount: float = Field(gt=0)
    mode: Literal["success", "failed", "delayed"] = "success"


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
    return {"service": "order-service", "status": "ok", "stored_orders": len(_orders_store)}


@app.get("/health/live")
async def liveness():
    return {"status": "alive", "service": SERVICE_NAME}


@app.get("/health/ready")
async def readiness():
    checks = {}
    overall = "ready"
    
    async with httpx.AsyncClient(timeout=1.5) as client:
        # Check Product Service
        try:
            r = await client.get(f"{PRODUCT_SERVICE_URL}/health", timeout=1.5)
            checks["product-service"] = "ok" if r.status_code == 200 else f"status_{r.status_code}"
            if r.status_code != 200:
                overall = "degraded"
        except Exception as e:
            checks["product-service"] = f"error: {str(e)}"
            overall = "not_ready"

        # Check Payment Service
        try:
            r = await client.get(f"{PAYMENT_SERVICE_URL}/health", timeout=1.5)
            checks["payment-service"] = "ok" if r.status_code == 200 else f"status_{r.status_code}"
            if r.status_code != 200:
                overall = "degraded"
        except Exception as e:
            checks["payment-service"] = f"error: {str(e)}"
            overall = "not_ready"

        # Check Notification Service
        try:
            r = await client.get(f"{NOTIFICATION_SERVICE_URL}/health", timeout=1.5)
            checks["notification-service"] = "ok" if r.status_code == 200 else f"status_{r.status_code}"
            if r.status_code != 200:
                overall = "degraded"
        except Exception as e:
            checks["notification-service"] = f"error: {str(e)}"
            overall = "not_ready"

    if overall == "not_ready":
        raise HTTPException(
            status_code=503,
            detail={"status": "not_ready", "service": SERVICE_NAME, "dependencies": checks}
        )
    
    return {"status": overall, "service": SERVICE_NAME, "dependencies": checks}


@app.get("/orders")
async def list_orders(user_id: str | None = None, limit: int = Query(default=20, ge=1, le=100)):
    async with _orders_lock:
        orders = list(_orders_store.values())

    if user_id:
        orders = [order for order in orders if order["user_id"] == user_id]

    orders.sort(key=lambda order: order["created_at"], reverse=True)
    return {"orders": orders[:limit]}


@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    async with _orders_lock:
        order = _orders_store.get(order_id)

    if order is None:
        raise HTTPException(status_code=404, detail={"message": "Order not found", "order_id": order_id})

    return order


@app.post("/orders")
async def create_order(order: OrderRequest, request: Request):
    idempotency_key = request.headers.get("Idempotency-Key")
    request_fingerprint = _order_fingerprint(order)

    if idempotency_key:
        cached_response = await _begin_idempotent_request(idempotency_key, request_fingerprint)
        if cached_response is not None:
            IDEMPOTENCY_HIT_COUNTER.labels(outcome="cached").inc()
            return cached_response

    IN_FLIGHT_GAUGE.inc()
    try:
        response = await _create_order(order, request, idempotency_key)
    except Exception:
        if idempotency_key:
            await _remove_idempotency_record(idempotency_key)
        raise
    finally:
        IN_FLIGHT_GAUGE.dec()

    if idempotency_key:
        await _complete_idempotent_request(idempotency_key, response)

    return response


async def _create_order(order: OrderRequest, request: Request, idempotency_key: str | None = None):
    order_id = _new_order_id(idempotency_key)
    created_at = datetime.now(timezone.utc).isoformat()
    trace_headers = _trace_headers(request)
    items = _normalized_order_items(order)

    events = []
    
    def add_event(name: str, detail: str = ""):
        events.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": name,
            "detail": detail
        })

    add_event("order_created", f"order_id={order_id}")

    timings: dict[str, float] = {}
    reservation_id = order_id
    inventory_status = "not_started"
    inventory_compensated = False
    reserved_items: list[dict[str, Any]] = []

    _order_start = perf_counter()  # for duration metric

    try:
        inventory_started = perf_counter()
        reservation = await _reserve_inventory(reservation_id, items, trace_headers)
        timings["inventory_reserve_ms"] = _elapsed_ms(inventory_started)
        inventory_status = reservation["inventory_status"]
        reserved_items = reservation["items"]
        add_event("inventory_reserved", f"reservation_id={reservation_id}, status={inventory_status}, items_count={len(reserved_items)}")

        amount = round(sum(item["line_total"] for item in reserved_items), 2)
        payment_started = perf_counter()
        payment = await _call_payment_service(
            PaymentRequest(
                order_id=order_id,
                amount=amount,
                mode=_normalize_payment_mode(order.payment_mode),
            ).model_dump(),
            trace_headers,
        )
        timings["payment_service_ms"] = _elapsed_ms(payment_started)

        payment_status = payment["payment_status"]
        add_event("payment_processed", f"payment_status={payment_status}, mode={_normalize_payment_mode(order.payment_mode)}")

        if payment_status == "success":
            commit_started = perf_counter()
            commit = await _commit_inventory(reservation_id, items, trace_headers)
            timings["inventory_commit_ms"] = _elapsed_ms(commit_started)
            inventory_status = commit["inventory_status"]
            add_event("inventory_committed", f"inventory_status={inventory_status}")
        else:
            release_started = perf_counter()
            release = await _release_inventory(reservation_id, items, trace_headers, "payment_failed")
            timings["inventory_release_ms"] = _elapsed_ms(release_started)
            inventory_status = release["inventory_status"]
            inventory_compensated = True
            add_event("inventory_released", f"inventory_status={inventory_status} (payment_failed)")
    except Exception as err:
        add_event("transaction_failed", f"error={str(err)}")
        if reserved_items:
            try:
                release_started = perf_counter()
                await _release_inventory(reservation_id, items, trace_headers, "order_failed")
                timings["inventory_release_ms"] = _elapsed_ms(release_started)
                inventory_compensated = True
                add_event("inventory_released", "inventory_compensated=true (exception_rollback)")
            except Exception as release_error:
                logger.warning(
                    "Inventory release error",
                    extra={
                        "order_id": order_id,
                        "inventory_release_error": str(release_error)
                    }
                )
        raise

    notification_started = perf_counter()
    notification_warning = None
    try:
        notification_status = await _call_notification_service(
            NotificationRequest(
                order_id=order_id,
                user_id=order.user_id,
                payment_status=payment_status,
            ).model_dump(),
            trace_headers,
        )
        add_event("notification_sent", f"notification_status={notification_status}")
    except HTTPException as exc:
        notification_status = "queued"
        notification_warning = exc.detail
        add_event("notification_failed_queued", f"warning={str(notification_warning)}")
    timings["notification_service_ms"] = _elapsed_ms(notification_started)

    order_status = "confirmed" if payment_status == "success" else "payment_failed"
    normalized_mode = _normalize_payment_mode(order.payment_mode)

    # ── Record Prometheus metrics ──────────────────────────────────────────────
    _order_duration = perf_counter() - _order_start
    ORDER_COUNTER.labels(status=order_status, payment_mode=normalized_mode).inc()
    ORDER_DURATION_HISTOGRAM.observe(_order_duration)
    ORDER_AMOUNT_HISTOGRAM.observe(amount)
    ORDER_ITEMS_HISTOGRAM.observe(len(reserved_items))
    # ──────────────────────────────────────────────────────────────────────────

    response = {
        "order_id": order_id,
        "created_at": created_at,
        "order_status": order_status,
        "user_id": order.user_id,
        "product": reserved_items[0],
        "items": reserved_items,
        "amount": amount,
        "payment": payment,
        "notification": notification_status,
        "inventory": {
            "reservation_id": reservation_id,
            "inventory_status": inventory_status,
            "compensated": inventory_compensated,
        },
        "service_timings_ms": timings,
        "events": events,
        "resilience": {
            "idempotency_key": idempotency_key,
            "retry_safe": idempotency_key is not None,
            "notification_degraded": notification_status != "sent",
            "inventory_compensated": inventory_compensated,
        },
    }
    if notification_warning is not None:
        response["notification_warning"] = notification_warning

    await _record_order(response)
    return response


async def _begin_idempotent_request(idempotency_key: str, request_fingerprint: str) -> dict | None:
    async with _idempotency_lock:
        _prune_idempotency_store()
        existing = _idempotency_store.get(idempotency_key)

        if existing is None:
            _idempotency_store[idempotency_key] = {
                "fingerprint": request_fingerprint,
                "created_at": monotonic(),
                "response": None,
            }
            return None

        if existing["fingerprint"] != request_fingerprint:
            IDEMPOTENCY_HIT_COUNTER.labels(outcome="conflict").inc()
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Idempotency-Key was already used with a different order request",
                    "idempotency_key": idempotency_key,
                },
            )

        if existing["response"] is None:
            IDEMPOTENCY_HIT_COUNTER.labels(outcome="in_progress").inc()
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Order with this Idempotency-Key is still being processed",
                    "idempotency_key": idempotency_key,
                },
            )

        return deepcopy(existing["response"])


async def _complete_idempotent_request(idempotency_key: str, response: dict) -> None:
    async with _idempotency_lock:
        if idempotency_key in _idempotency_store:
            _idempotency_store[idempotency_key]["response"] = deepcopy(response)


async def _remove_idempotency_record(idempotency_key: str) -> None:
    async with _idempotency_lock:
        _idempotency_store.pop(idempotency_key, None)


def _order_fingerprint(order: OrderRequest) -> str:
    items = sorted(_normalized_order_items(order), key=lambda item: item.product_id)
    item_fingerprint = ",".join(f"{item.product_id}:{item.quantity}" for item in items)
    return "|".join(
        [
            order.user_id,
            item_fingerprint,
            _normalize_payment_mode(order.payment_mode),
        ]
    )


def _prune_idempotency_store() -> None:
    now = monotonic()
    expired_keys = [
        key
        for key, value in _idempotency_store.items()
        if now - value["created_at"] > IDEMPOTENCY_TTL_SECONDS
    ]
    for key in expired_keys:
        _idempotency_store.pop(key, None)


def _new_order_id(idempotency_key: str | None) -> str:
    if idempotency_key:
        return f"ORD-{uuid5(NAMESPACE_URL, idempotency_key).hex[:8].upper()}"
    return f"ORD-{uuid4().hex[:8].upper()}"


def _normalized_order_items(order: OrderRequest) -> list[OrderItem]:
    raw_items = order.items
    if not raw_items:
        if not order.product_id:
            raise HTTPException(
                status_code=422,
                detail={"message": "Either product_id or items must be provided"},
            )
        raw_items = [OrderItem(product_id=order.product_id, quantity=order.quantity)]

    grouped: dict[str, int] = {}
    for item in raw_items:
        grouped[item.product_id] = grouped.get(item.product_id, 0) + item.quantity

    return [OrderItem(product_id=product_id, quantity=quantity) for product_id, quantity in grouped.items()]


async def _record_order(order: dict[str, Any]) -> None:
    async with _orders_lock:
        _orders_store[order["order_id"]] = deepcopy(order)


def _elapsed_ms(start: float) -> float:
    return round((perf_counter() - start) * 1000, 2)


async def _reserve_inventory(reservation_id: str, items: list[OrderItem], headers: dict[str, str]) -> dict:
    payload = _inventory_payload(reservation_id, items)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{PRODUCT_SERVICE_URL}/inventory/reserve", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        status_code = 409 if exc.response.status_code == 409 else 502
        raise HTTPException(
            status_code=status_code,
            detail={"message": "Inventory reservation failed", "inventory_error": _safe_json(exc.response)},
        ) from exc
    except (httpx.RequestError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=503,
            detail={"message": "Product Service inventory API is unavailable", "error": str(exc)},
        ) from exc


async def _commit_inventory(reservation_id: str, items: list[OrderItem], headers: dict[str, str]) -> dict:
    return await _inventory_transition("/inventory/commit", reservation_id, items, headers)


async def _release_inventory(
    reservation_id: str,
    items: list[OrderItem],
    headers: dict[str, str],
    reason: str,
) -> dict:
    payload = _inventory_payload(reservation_id, items)
    payload["reason"] = reason
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{PRODUCT_SERVICE_URL}/inventory/release", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail={"message": "Inventory release failed", "inventory_error": _safe_json(exc.response)},
        ) from exc
    except (httpx.RequestError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=503,
            detail={"message": "Product Service inventory API is unavailable", "error": str(exc)},
        ) from exc


async def _inventory_transition(
    path: str,
    reservation_id: str,
    items: list[OrderItem],
    headers: dict[str, str],
) -> dict:
    payload = _inventory_payload(reservation_id, items)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{PRODUCT_SERVICE_URL}{path}", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail={"message": "Inventory transition failed", "inventory_error": _safe_json(exc.response)},
        ) from exc
    except (httpx.RequestError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=503,
            detail={"message": "Product Service inventory API is unavailable", "error": str(exc)},
        ) from exc


def _inventory_payload(reservation_id: str, items: list[OrderItem]) -> dict:
    return {
        "reservation_id": reservation_id,
        "items": [item.model_dump() for item in items],
    }


async def _call_product_service(product_id: str, headers: dict[str, str]) -> dict:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}", headers=headers)
            response.raise_for_status()
            product = response.json()
            return {
                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "stock": product["stock"],
            }
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail=_safe_json(exc.response)) from exc
        raise HTTPException(
            status_code=502,
            detail={"message": "Product Service returned an error", "product_error": _safe_json(exc.response)},
        ) from exc
    except (httpx.RequestError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=503,
            detail={"message": "Product Service is unavailable or returned invalid data", "error": str(exc)},
        ) from exc


async def _call_payment_service(payload: dict, headers: dict[str, str]) -> dict:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(f"{PAYMENT_SERVICE_URL}/payments", json=payload, headers=headers)
            response.raise_for_status()
            payment = response.json()
            return {
                "order_id": payment["order_id"],
                "amount": payment["amount"],
                "payment_status": payment["payment_status"],
                "mode": payment.get("mode", payload["mode"]),
                **({"delay_seconds": payment["delay_seconds"]} if "delay_seconds" in payment else {}),
            }
    except httpx.HTTPStatusError as exc:
        payment_error = _safe_json(exc.response)
        detail = payment_error.get("detail", payment_error)
        if exc.response.status_code == 402 and isinstance(detail, dict):
            return {
                "order_id": detail.get("order_id", payload["order_id"]),
                "amount": payload["amount"],
                "payment_status": detail.get("payment_status", "failed"),
                "mode": payload["mode"],
                "reason": detail.get("reason", "Payment failed"),
            }

        raise HTTPException(
            status_code=502,
            detail={"message": "Payment Service returned an error", "payment_error": payment_error},
        ) from exc
    except (httpx.RequestError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=503,
            detail={"message": "Payment Service is unavailable or returned invalid data", "error": str(exc)},
        ) from exc


async def _call_notification_service(payload: dict, headers: dict[str, str]) -> str:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{NOTIFICATION_SERVICE_URL}/notifications", json=payload, headers=headers)
            response.raise_for_status()
            body = response.json()
            return body["notification"]
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Notification Service returned an error",
                "notification_error": _safe_json(exc.response),
            },
        ) from exc
    except (httpx.RequestError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=503,
            detail={"message": "Notification Service is unavailable or returned invalid data", "error": str(exc)},
        ) from exc


def _normalize_payment_mode(mode: PaymentMode) -> Literal["success", "failed", "delayed"]:
    aliases = {
        "process": "success",
        "fail": "failed",
        "delay": "delayed",
        "slow": "delayed",
    }
    return aliases.get(mode, mode)


def _trace_headers(request: Request) -> dict[str, str]:
    trace_header_names = [
        "x-request-id",
        "x-b3-traceid",
        "x-b3-spanid",
        "x-b3-parentspanid",
        "x-b3-sampled",
        "x-b3-flags",
        "b3",
        "traceparent",
        "tracestate",
    ]
    return {
        name: value
        for name in trace_header_names
        if (value := request.headers.get(name)) is not None
    }


def _safe_json(response: httpx.Response):
    try:
        return response.json()
    except ValueError:
        return {"message": response.text}
