"""Concept model for storing extracted concepts."""

import uuid
from typing import Optional

from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class Concept(Base):
    """Concept entity representing an extracted concept from highlights.

    Attributes:
        id: Unique identifier (UUID).
        name: Concept name/label.
        domain: Subject domain (e.g., philosophy, management).
        frequency: Number of times this concept appears.
        last_mentioned: Last time this concept was mentioned.
        description: Optional description.
        created_at: Record creation timestamp.
    """

    __tablename__ = "concepts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    domain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    frequency: Mapped[int] = mapped_column(Integer, default=0)
    last_mentioned: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped = mapped_column(
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Concept(id={self.id}, name={self.name!r}, domain={self.domain!r})>"
