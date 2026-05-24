"""Reader model for storing user profile and preferences."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class Reader(Base):
    """Reader entity representing a user/reader."""

    __tablename__ = "readers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="Reader")
    reading_profile: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    interests: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    preferences: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        server_default=func.now(),
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Reader(id={self.id}, name={self.name!r})>"