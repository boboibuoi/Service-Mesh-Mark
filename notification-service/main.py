from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="Notification Service")


class NotificationRequest(BaseModel):
    order_id: str
    user_id: str
    payment_status: str


@app.get("/health")
async def health():
    return {"service": "notification-service", "status": "ok"}


@app.post("/notifications")
async def create_notification(notification: NotificationRequest):
    return {
        "order_id": notification.order_id,
        "user_id": notification.user_id,
        "payment_status": notification.payment_status,
        "notification": "sent",
        "message": f"Order {notification.order_id} payment is {notification.payment_status}",
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }
