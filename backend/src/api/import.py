"""File import API endpoints."""

from fastapi import APIRouter, UploadFile, File, HTTPException

from src.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/")
async def import_file(
    file: UploadFile = File(...),
) -> dict:
    """Import a markdown file from WeChat Reading.

    Args:
        file: The markdown file to import.

    Returns:
        Import result with book information.
    """
    logger.info("Import request received: %s", file.filename)

    # Validate file type
    if not file.filename.endswith(".md"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Expected .md file, got: {file.filename}",
        )

    # TODO: Implement actual file processing
    return {
        "status": "success",
        "message": "File import endpoint ready",
        "file_name": file.filename,
    }


@router.post("/batch")
async def import_batch(
    files: list[UploadFile] = File(...),
) -> dict:
    """Import multiple markdown files.

    Args:
        files: List of markdown files to import.

    Returns:
        Batch import results.
    """
    logger.info("Batch import request: %d files", len(files))

    # TODO: Implement batch processing
    return {
        "status": "success",
        "message": "Batch import endpoint ready",
        "file_count": len(files),
    }
