from sqlalchemy import String, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import CreatedAtMixin, UUIDPKMixin


class OutboxEventOrm(Base, UUIDPKMixin, CreatedAtMixin):
    __tablename__ = "outbox_events"
    idempotency_key: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False
    )
    exchange: Mapped[str] = mapped_column(String(255), nullable=False)
    queue: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[dict] = mapped_column(JSONB, nullable=False)
    attempt: Mapped[int] = mapped_column(nullable=False, default=0)

    is_processed: Mapped[bool] = mapped_column(
        default=False, index=True, nullable=False
    )

    __table_args__ = (
        Index(
            "ix_outbox_unprocessed_created_at",
            "created_at",
            postgresql_where="is_processed = FALSE",
        ),
    )
