import asyncio
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field


app = FastAPI(title="Payment Service")


class PaymentRequest(BaseModel):
    order_id: str = Field(min_length=1)
    amount: float = Field(gt=0)
    mode: Literal["success", "failed", "delayed", "fail", "slow"] = "success"


@app.get("/health")
async def health():
    return {"service": "payment-service", "status": "ok"}


@app.get("/payment")
async def demo_payment(
    mode: Literal["success", "fail", "slow"] = Query(default="success"),
    order_id: str | None = Query(default=None),
    amount: float = Query(default=100.0, gt=0),
):
    request = PaymentRequest(order_id=order_id or _demo_order_id(), amount=amount, mode=mode)
    return await create_payment(request)


@app.post("/payments")
async def create_payment(payment: PaymentRequest):
    mode = _normalize_payment_mode(payment.mode)

    if mode == "failed":
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
        return {
            "order_id": payment.order_id,
            "amount": payment.amount,
            "payment_status": "success",
            "mode": mode,
            "delay_seconds": 5,
        }

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


def _demo_order_id() -> str:
    return f"DEMO-{uuid4().hex[:8].upper()}"


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
