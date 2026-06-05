import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Gauge, Histogram, make_asgi_app
from pydantic import BaseModel, Field


SERVICE_NAME = "product-service"

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

app = FastAPI(title="Product Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("FRONTEND_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Prometheus metrics ───────────────────────────────────────────────────────
PRODUCT_STOCK_GAUGE = Gauge(
    "meshmart_product_stock_total",
    "Current available stock level per product",
    ["product_id", "product_name"],
)
REVIEW_COUNTER = Counter(
    "meshmart_reviews_total",
    "Total product reviews submitted",
    ["product_id", "product_name"],
)
INVENTORY_OPERATION_COUNTER = Counter(
    "meshmart_inventory_operations_total",
    "Total inventory operations (reserve / commit / release)",
    ["operation", "product_id"],
)
INVENTORY_UNITS_HISTOGRAM = Histogram(
    "meshmart_inventory_units_per_operation",
    "Number of units involved per inventory operation",
    ["operation"],
    buckets=[1, 2, 3, 5, 10, 20, 50],
)

# Expose /metrics endpoint
app.mount("/metrics", make_asgi_app())


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


PRODUCTS = [
    {
        "id": "PROD-001",
        "name": "Ultrabook Pro 14",
        "category": "Computing",
        "description": "Lightweight laptop for coursework, presentations, and cloud dashboards.",
        "image_url": "/assets/ultrabook-pro.png",
        "price": 899.0,
        "stock": 20,
        "rating": 4.8,
        "review_count": 24,
        "delivery": "2-day delivery",
    },
    {
        "id": "PROD-002",
        "name": "Smartphone X1",
        "category": "Mobile",
        "description": "Reliable mobile device for checkout notifications and service alerts.",
        "image_url": "/assets/smartphone-x1.png",
        "price": 499.0,
        "stock": 35,
        "rating": 4.6,
        "review_count": 18,
        "delivery": "Next-day delivery",
    },
    {
        "id": "PROD-003",
        "name": "Audio Pods Max",
        "category": "Audio",
        "description": "Noise-canceling headphones for focused work and remote meetings.",
        "image_url": "/assets/audio-pods-max.png",
        "price": 89.0,
        "stock": 12,
        "rating": 4.7,
        "review_count": 31,
        "delivery": "Standard delivery",
    },
]

_inventory_lock = asyncio.Lock()
_reservations: dict[str, dict] = {}
_reviews: dict[str, list[dict]] = {product["id"]: [] for product in PRODUCTS}
_rating_baseline: dict[str, tuple[float, int]] = {
    product["id"]: (product["rating"], product["review_count"]) for product in PRODUCTS
}
# Tracks (user_id, order_id, product_id) combos to prevent duplicate reviews
_reviewed_combinations: set[tuple[str, str, str]] = set()

# Initialise stock gauges from seed data
for _p in PRODUCTS:
    PRODUCT_STOCK_GAUGE.labels(product_id=_p["id"], product_name=_p["name"]).set(_p["stock"])


class InventoryItem(BaseModel):
    product_id: str = Field(min_length=1)
    quantity: int = Field(gt=0)


class InventoryReservationRequest(BaseModel):
    reservation_id: str = Field(min_length=1)
    items: list[InventoryItem] = Field(min_length=1)


class InventoryReleaseRequest(InventoryReservationRequest):
    reason: str = "payment_failed"


class ProductReviewRequest(BaseModel):
    user_id: str = Field(min_length=1)
    order_id: str | None = None
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=500)
    image_url: str | None = Field(default=None, max_length=500)


@app.get("/health")
async def health():
    return {
        "service": "product-service",
        "status": "ok",
        "open_reservations": len([item for item in _reservations.values() if item["status"] == "reserved"]),
    }


@app.get("/health/live")
async def liveness():
    return {"status": "alive", "service": SERVICE_NAME}


@app.get("/health/ready")
async def readiness():
    return {"status": "ready", "service": SERVICE_NAME}


@app.get("/products")
async def list_products():
    return {"products": [_product_response(product) for product in PRODUCTS]}


@app.get("/products/{product_id}")
async def get_product(product_id: str):
    product = _find_product(product_id)
    if product:
        return _product_response(product, include_reviews=True)

    raise HTTPException(
        status_code=404,
        detail={"message": "Product not found", "product_id": product_id},
    )


@app.post("/inventory/reserve")
async def reserve_inventory(request: InventoryReservationRequest):
    async with _inventory_lock:
        existing = _reservations.get(request.reservation_id)
        if existing:
            if existing["status"] == "reserved":
                return _reservation_response(request.reservation_id, existing["items"], "reserved")
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Reservation id is already closed",
                    "reservation_id": request.reservation_id,
                    "status": existing["status"],
                },
            )

        grouped_items = _group_items(request.items)
        reserved_items = []
        for product_id, quantity in grouped_items.items():
            product = _find_product(product_id)
            if product is None:
                raise HTTPException(status_code=404, detail={"message": "Product not found", "product_id": product_id})
            if quantity > product["stock"]:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "message": "Not enough product stock",
                        "product_id": product_id,
                        "requested_quantity": quantity,
                        "available_stock": product["stock"],
                    },
                )

        for product_id, quantity in grouped_items.items():
            product = _find_product(product_id)
            product["stock"] -= quantity
            reserved_items.append(_reserved_item(product, quantity))
            # Track per-product inventory operations and update stock gauge
            INVENTORY_OPERATION_COUNTER.labels(operation="reserve", product_id=product_id).inc()
            INVENTORY_UNITS_HISTOGRAM.labels(operation="reserve").observe(quantity)
            PRODUCT_STOCK_GAUGE.labels(product_id=product_id, product_name=product["name"]).set(product["stock"])

        _reservations[request.reservation_id] = {
            "status": "reserved",
            "items": reserved_items,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return _reservation_response(request.reservation_id, reserved_items, "reserved")


@app.post("/inventory/commit")
async def commit_inventory(request: InventoryReservationRequest):
    async with _inventory_lock:
        reservation = _reservations.get(request.reservation_id)
        if reservation is None:
            raise HTTPException(
                status_code=404,
                detail={"message": "Reservation not found", "reservation_id": request.reservation_id},
            )
        if reservation["status"] == "released":
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Released inventory cannot be committed",
                    "reservation_id": request.reservation_id,
                },
            )

        reservation["status"] = "committed"
        reservation["committed_at"] = datetime.now(timezone.utc).isoformat()
        # Record commit metric per product
        for item in reservation["items"]:
            INVENTORY_OPERATION_COUNTER.labels(operation="commit", product_id=item["id"]).inc()
            INVENTORY_UNITS_HISTOGRAM.labels(operation="commit").observe(item["quantity"])
        return _reservation_response(request.reservation_id, reservation["items"], "committed")


@app.post("/inventory/release")
async def release_inventory(request: InventoryReleaseRequest):
    async with _inventory_lock:
        reservation = _reservations.get(request.reservation_id)
        if reservation is None:
            return {
                "reservation_id": request.reservation_id,
                "inventory_status": "not_found",
                "reason": request.reason,
                "items": [],
            }

        if reservation["status"] == "released":
            return _reservation_response(request.reservation_id, reservation["items"], "released", request.reason)

        if reservation["status"] == "committed":
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Committed inventory cannot be released",
                    "reservation_id": request.reservation_id,
                },
            )

        for item in reservation["items"]:
            product = _find_product(item["id"])
            if product:
                product["stock"] += item["quantity"]
                # Update stock gauge after release
                INVENTORY_OPERATION_COUNTER.labels(operation="release", product_id=item["id"]).inc()
                INVENTORY_UNITS_HISTOGRAM.labels(operation="release").observe(item["quantity"])
                PRODUCT_STOCK_GAUGE.labels(product_id=item["id"], product_name=product["name"]).set(product["stock"])

        reservation["status"] = "released"
        reservation["released_at"] = datetime.now(timezone.utc).isoformat()
        reservation["reason"] = request.reason
        return _reservation_response(request.reservation_id, reservation["items"], "released", request.reason)


@app.get("/products/{product_id}/reviews")
async def list_reviews(product_id: str):
    product = _find_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail={"message": "Product not found", "product_id": product_id})

    return {"product_id": product_id, "reviews": _reviews.get(product_id, [])}


@app.post("/products/{product_id}/reviews")
async def create_review(product_id: str, review: ProductReviewRequest):
    product = _find_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail={"message": "Product not found", "product_id": product_id})

    if not review.order_id:
        raise HTTPException(
            status_code=422,
            detail={"message": "order_id is required to submit a review"},
        )

    combo_key = (review.user_id, review.order_id, product_id)
    if combo_key in _reviewed_combinations:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "You have already reviewed this product for this order",
                "user_id": review.user_id,
                "order_id": review.order_id,
                "product_id": product_id,
            },
        )

    review_record = {
        "review_id": f"REV-{uuid4().hex[:8].upper()}",
        "product_id": product_id,
        "user_id": review.user_id,
        "order_id": review.order_id,
        "rating": review.rating,
        "comment": review.comment.strip(),
        "image_url": review.image_url,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _reviewed_combinations.add(combo_key)
    _reviews.setdefault(product_id, []).insert(0, review_record)
    _recalculate_rating(product)
    # Track review metric
    REVIEW_COUNTER.labels(product_id=product_id, product_name=product["name"]).inc()
    return {"review": review_record, "product": _product_response(product, include_reviews=True)}


def _find_product(product_id: str) -> dict | None:
    return next((product for product in PRODUCTS if product["id"] == product_id), None)


def _group_items(items: list[InventoryItem]) -> dict[str, int]:
    grouped: dict[str, int] = {}
    for item in items:
        grouped[item.product_id] = grouped.get(item.product_id, 0) + item.quantity
    return grouped


def _reserved_item(product: dict, quantity: int) -> dict:
    return {
        "id": product["id"],
        "name": product["name"],
        "unit_price": product["price"],
        "quantity": quantity,
        "line_total": round(product["price"] * quantity, 2),
        "remaining_stock": product["stock"],
    }


def _reservation_response(
    reservation_id: str,
    items: list[dict],
    status: str,
    reason: str | None = None,
) -> dict:
    response = {
        "reservation_id": reservation_id,
        "inventory_status": status,
        "items": items,
    }
    if reason:
        response["reason"] = reason
    return response


def _product_response(product: dict, include_reviews: bool = False) -> dict:
    response = dict(product)
    reviews = _reviews.get(product["id"], [])
    response["review_count"] = product.get("review_count", 0) + len(reviews)
    if include_reviews:
        response["reviews"] = reviews[:10]
    return response


def _recalculate_rating(product: dict) -> None:
    reviews = _reviews.get(product["id"], [])
    base_rating, base_count = _rating_baseline[product["id"]]
    total_count = base_count + len(reviews)
    if total_count == 0:
        return

    total_score = (base_rating * base_count) + sum(review["rating"] for review in reviews)
    product["rating"] = round(total_score / total_count, 2)
