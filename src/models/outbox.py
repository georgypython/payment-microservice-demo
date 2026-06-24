from uuid import UUID
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .base import Base
    from .mixins import CreatedAtMixin, UUIDPKMixin
    from .payment import PaymentOrm


class OutboxEventOrm(Base, UUIDPKMixin, CreatedAtMixin):
    __tablename__ = "outbox_events"
    payment_id: Mapped[UUID] = mapped_column(
        ForeignKey("payments.id", ondelete="CASCADE"), nullable=False
    )
    exchange: Mapped[str] = mapped_column(String(255), nullable=False)
    routing_key: Mapped[str] = mapped_column(String(255), nullable=False)
    is_processed: Mapped[bool] = mapped_column(
        default=False, index=True, nullable=False
    )

    payment: Mapped["PaymentOrm"] = relationship(
        "PaymentOrm", back_populates="outbox_events"
    )

    __table_args__ = ( 
        Index(
            "ix_outbox_unprocessed_created_at",
            "created_at",
            postgresql_where="is_processed = FALSE",
        )
    )
