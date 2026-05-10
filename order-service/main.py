import asyncio
import os
from copy import deepcopy
from time import monotonic
from typing import Literal
from uuid import NAMESPACE_URL, uuid4, uuid5

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


app = FastAPI(title="Order Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("FRONTEND_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8004")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8002")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8003")
IDEMPOTENCY_TTL_SECONDS = int(os.getenv("IDEMPOTENCY_TTL_SECONDS", "600"))

_idempotency_lock = asyncio.Lock()
_idempotency_store: dict[str, dict] = {}

PaymentMode = Literal["success", "failed", "delayed", "process", "fail", "delay", "slow"]


class OrderRequest(BaseModel):
    user_id: str = Field(min_length=1)
    product_id: str = Field(min_length=1)
    quantity: int = Field(default=1, gt=0)
    payment_mode: PaymentMode = "success"


class PaymentRequest(BaseModel):
    order_id: str
    amount: float = Field(gt=0)
    mode: Literal["success", "failed", "delayed"] = "success"


class NotificationRequest(BaseModel):
    order_id: str
    user_id: str
    payment_status: str


@app.get("/health")
async def health():
    return {"service": "order-service", "status": "ok"}


@app.post("/orders")
async def create_order(order: OrderRequest, request: Request):
    idempotency_key = request.headers.get("Idempotency-Key")
    request_fingerprint = _order_fingerprint(order)

    if idempotency_key:
        cached_response = await _begin_idempotent_request(idempotency_key, request_fingerprint)
        if cached_response is not None:
            return cached_response

    try:
        response = await _create_order(order, request, idempotency_key)
    except Exception:
        if idempotency_key:
            await _remove_idempotency_record(idempotency_key)
        raise

    if idempotency_key:
        await _complete_idempotent_request(idempotency_key, response)

    return response


async def _create_order(order: OrderRequest, request: Request, idempotency_key: str | None = None):
    order_id = _new_order_id(idempotency_key)
    trace_headers = _trace_headers(request)
    product = await _call_product_service(order.product_id, trace_headers)

    if order.quantity > product["stock"]:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Not enough product stock",
                "product_id": order.product_id,
                "requested_quantity": order.quantity,
                "available_stock": product["stock"],
            },
        )

    amount = round(product["price"] * order.quantity, 2)
    payment = await _call_payment_service(
        PaymentRequest(
            order_id=order_id,
            amount=amount,
            mode=_normalize_payment_mode(order.payment_mode),
        ).model_dump(),
        trace_headers,
    )
    payment_status = payment["payment_status"]
    notification_status = await _call_notification_service(
        NotificationRequest(
            order_id=order_id,
            user_id=order.user_id,
            payment_status=payment_status,
        ).model_dump(),
        trace_headers,
    )

    return {
        "order_id": order_id,
        "order_status": "confirmed" if payment_status == "success" else "payment_failed",
        "user_id": order.user_id,
        "product": {
            "id": product["id"],
            "name": product["name"],
            "unit_price": product["price"],
            "quantity": order.quantity,
        },
        "amount": amount,
        "payment": payment,
        "notification": notification_status,
    }


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
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Idempotency-Key was already used with a different order request",
                    "idempotency_key": idempotency_key,
                },
            )

        if existing["response"] is None:
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
    return "|".join(
        [
            order.user_id,
            order.product_id,
            str(order.quantity),
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
