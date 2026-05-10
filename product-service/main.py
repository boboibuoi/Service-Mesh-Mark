import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Product Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("FRONTEND_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PRODUCTS = [
    {
        "id": "PROD-001",
        "name": "Laptop",
        "price": 899.0,
        "stock": 20,
    },
    {
        "id": "PROD-002",
        "name": "Phone",
        "price": 499.0,
        "stock": 35,
    },
    {
        "id": "PROD-003",
        "name": "Headphones",
        "price": 89.0,
        "stock": 12,
    },
]


@app.get("/health")
async def health():
    return {"service": "product-service", "status": "ok"}


@app.get("/products")
async def list_products():
    return {"products": PRODUCTS}


@app.get("/products/{product_id}")
async def get_product(product_id: str):
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product

    raise HTTPException(
        status_code=404,
        detail={"message": "Product not found", "product_id": product_id},
    )
