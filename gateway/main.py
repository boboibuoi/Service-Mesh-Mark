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


@app.post("/orders")
async def create_order(request: Request):
    payload = await _read_json(request)
    return await _forward("POST", ORDER_SERVICE_URL, "/orders", payload)


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


async def _forward(method: str, base_url: str, path: str, payload: dict | None = None):
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.request(method, f"{base_url}{path}", json=payload)
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
