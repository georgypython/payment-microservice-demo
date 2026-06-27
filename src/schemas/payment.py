from datetime import datetime
from urllib.parse import urlparse
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, ConfigDict

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
        try:
            parsed_url = urlparse(value)

            host = parsed_url.hostname
            if not host:
                host = value.split(":")[0].split("/")[0]
            host = host.lower()

            if host in FORBIDDEN_HOSTS or any(
                host.startswith(fh) for fh in FORBIDDEN_HOSTS
            ):
                raise ValueError("Invalid webhook_url")
        except Exception:
            raise ValueError("Invalid webhook_url format")
        return value


class PaymentEventSchema(BaseModel):
    payment_id: str


class NewPaymentResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: PaymentStatus
    created_at: datetime


class PaymentFullResponseSchema(NewPaymentResponseSchema):
    model_config = ConfigDict(from_attributes=True)

    amount: Decimal
    currency: CurrencyType
    description: str | None = None
    meta_info: dict | None = None
    idempotency_key: str = Field(..., max_length=64)
    webhook_url: str = Field(..., max_length=2048)
    processing_at: datetime | None = None


class WebhookPayloadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_id: str
    status: PaymentStatus
    amount: str
    currency: CurrencyType
