from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

from src.models.enums import CurrencyType, PaymentStatus

FORBIDDEN_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "[::1]",
    "192.168.",
    "172.16.",
    "172.17.",
    "172.18.",
    "172.19.",
    "172.20.",
    "172.30.",
    "172.31.",
    "postgres",
    "rabbitmq",
]


class CreatePaymentSchema(BaseModel):
    amount: float = Field(gt=0)
    currency: CurrencyType = Field(..., description="Currencies: usd, rub, eur")
    description: str | None = Field(None, max_length=255)
    meta_info: dict | None = None
    webhook_url: str = Field(max_length=2048)

    @field_validator("webhook_url")
    def is_valid_url(cls, value: str) -> str:
        if value.lower() in FORBIDDEN_HOSTS:
            raise ValueError("Invalid webhook_url")
        return value


class PaymentEventSchema(BaseModel):
    payment_id: UUID


class CreatedPaymentSchema(BaseModel):
    payment_id: UUID
    status: PaymentStatus
    created_at: datetime
