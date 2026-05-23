"""Chapter model for storing book chapters."""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base

if TYPE_CHECKING:
    from src.models.book import Book


class Chapter(Base):
    """Chapter entity representing a book chapter.

    Attributes:
        id: Unique identifier (UUID).
        book_id: Foreign key to the parent book.
        title: Chapter title.
        order: Chapter order number.
        highlight_count: Number of highlights in this chapter.
        created_at: Record creation timestamp.
    """

    __tablename__ = "chapters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)
    highlight_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped = mapped_column(
        server_default=func.now(),
    )

    # Relationships
    book: Mapped["Book"] = relationship("Book", back_populates="chapters")

    def __repr__(self) -> str:
        return f"<Chapter(id={self.id}, title={self.title!r}, order={self.order})>"
