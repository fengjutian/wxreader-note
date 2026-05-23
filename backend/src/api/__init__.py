"""API routes for Cognitive Reading Graph."""

from fastapi import APIRouter

# Import routers
from src.api import import_router, books_router, analyze_router
from src.api import graph_router, profile_router, search_router, timeline_router

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include sub-routers
api_router.include_router(import_router, prefix="/import", tags=["Import"])
api_router.include_router(books_router, prefix="/books", tags=["Books"])
api_router.include_router(analyze_router, prefix="/analyze", tags=["Analysis"])
api_router.include_router(graph_router, prefix="/graph", tags=["Graph"])
api_router.include_router(profile_router, prefix="/profile", tags=["Profile"])
api_router.include_router(search_router, prefix="/search", tags=["Search"])
api_router.include_router(timeline_router, prefix="/timeline", tags=["Timeline"])

__all__ = ["api_router"]
