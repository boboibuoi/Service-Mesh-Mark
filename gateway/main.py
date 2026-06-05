import os
from json import JSONDecodeError

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Gateway Service", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("FRONTEND_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8004")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8001")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8002")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8003")


@app.get("/health")
async def health():
    return {"service": "gateway", "status": "ok"}


@app.get("/products")
async def list_products():
    return await _forward("GET", PRODUCT_SERVICE_URL, "/products")


@app.get("/products/{product_id}")
async def get_product(product_id: str):
    return await _forward("GET", PRODUCT_SERVICE_URL, f"/products/{product_id}")


@app.get("/products/{product_id}/reviews")
async def list_product_reviews(product_id: str):
    return await _forward("GET", PRODUCT_SERVICE_URL, f"/products/{product_id}/reviews")


@app.post("/products/{product_id}/reviews")
async def create_product_review(product_id: str, request: Request):
    payload = await _read_json(request)
    return await _forward("POST", PRODUCT_SERVICE_URL, f"/products/{product_id}/reviews", request=request, payload=payload)


@app.post("/orders")
async def create_order(request: Request):
    payload = await _read_json(request)
    return await _forward("POST", ORDER_SERVICE_URL, "/orders", request=request, payload=payload)


@app.get("/orders")
async def list_orders(request: Request):
    return await _forward("GET", ORDER_SERVICE_URL, "/orders", request=request, query=request.url.query)


@app.get("/orders/{order_id}")
async def get_order(order_id: str, request: Request):
    return await _forward("GET", ORDER_SERVICE_URL, f"/orders/{order_id}", request=request)


@app.post("/payments")
async def create_payment(request: Request):
    payload = await _read_json(request)
    return await _forward("POST", PAYMENT_SERVICE_URL, "/payments", payload)


@app.post("/notifications")
async def create_notification(request: Request):
    payload = await _read_json(request)
    return await _forward("POST", NOTIFICATION_SERVICE_URL, "/notifications", payload)


async def _read_json(request: Request) -> dict:
    content_type = request.headers.get("content-type", "")
    if "application/json" not in content_type:
        return {}

    try:
        return await request.json()
    except JSONDecodeError:
        return {}


async def _forward(
    method: str,
    base_url: str,
    path: str,
    request: Request | None = None,
    payload: dict | None = None,
    query: str | None = None,
):
    target_url = f"{base_url}{path}"
    if query:
        target_url = f"{target_url}?{query}"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.request(method, target_url, json=payload, headers=_forward_headers(request))
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=_safe_json(exc.response)) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail={"message": f"{base_url} is unavailable", "error": str(exc)},
        ) from exc


def _safe_json(response: httpx.Response):
    try:
        return response.json()
    except ValueError:
        return {"message": response.text}


def _forward_headers(request: Request | None) -> dict[str, str]:
    if request is None:
        return {}

    header_names = [
        "idempotency-key",
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
        for name in header_names
        if (value := request.headers.get(name)) is not None
    }
