from decimal import Decimal
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum, String, Numeric, DateTime, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import UUIDPKMixin, CreatedAtMixin
from .enums import PaymentStatus, CurrencyType

if TYPE_CHECKING:
    from .outbox import OutboxEventOrm


class PaymentOrm(Base, UUIDPKMixin, CreatedAtMixin):
    __tablename__ = "payments"

    amount: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    currency: Mapped[CurrencyType] = mapped_column(
        Enum(CurrencyType, name="currency_type_enum"),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=False,
        default=None,
    )
    meta_info: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
    )
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status_enum"),
        nullable=False,
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False
    )
    webhook_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    processing_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    outbox_events: Mapped[list["OutboxEventOrm"]] = relationship(
        "OutboxEventOrm", back_populates="payment"
    )

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_payment_amount_positive"),
        Index("ix_payments_status_created_at", "status", "created_at"),
    )
