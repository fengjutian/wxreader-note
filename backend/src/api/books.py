"""Books API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas import BookListResponse, BookResponse
from src.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=BookListResponse)
async def list_books(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    db: Session = Depends(get_db),
) -> BookListResponse:
    """List all books with pagination.

    Args:
        page: Page number (starting from 1).
        page_size: Number of items per page.
        category: Optional category filter.
        db: Database session.

    Returns:
        Paginated list of books.
    """
    logger.info("List books: page=%d, page_size=%d, category=%s", page, page_size, category)

    # TODO: Implement actual database query
    return BookListResponse(
        items=[],
        total=0,
        page=page,
        page_size=page_size,
    )


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: UUID,
    db: Session = Depends(get_db),
) -> BookResponse:
    """Get a specific book by ID.

    Args:
        book_id: Book UUID.
        db: Database session.

    Returns:
        Book details.
    """
    logger.info("Get book: %s", book_id)

    # TODO: Implement actual database query
    raise NotImplementedError("Book retrieval not yet implemented")
