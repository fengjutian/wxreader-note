     """AI Analyzer service for batch processing highlights.

Coordinates concept extraction, progress tracking, and error handling.
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from src.services.llm_provider import LLMProvider
from src.services.concept_extractor import ConceptExtractor, ExtractedConcepts
from src.utils.logging import get_logger

logger = get_logger(__name__)


class JobStatus(str, Enum):
    """Analysis job status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AnalysisJob:
    """Represents an analysis job.

    Attributes:
        job_id: Unique job identifier.
        status: Current job status.
        total: Total number of highlights to process.
        completed: Number of processed highlights.
        errors: Number of errors encountered.
        results: Extracted concepts results.
        created_at: Job creation time.
        updated_at: Last update time.
    """

    job_id: str
    status: JobStatus
    total: int
    completed: int = 0
    errors: int = 0
    results: list[ExtractedConcepts] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @property
    def progress_percent(self) -> float:
        """Calculate progress percentage."""
        if self.total == 0:
            return 100.0
        return (self.completed / self.total) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "total": self.total,
            "completed": self.completed,
            "errors": self.errors,
            "progress_percent": self.progress_percent,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class AIAnalyzer:
    """AI analyzer for batch processing highlights.

    Manages analysis jobs, coordinates with LLM provider,
    tracks progress, and handles errors.
    """

    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        concept_extractor: Optional[ConceptExtractor] = None,
        batch_size: int = 10,
        max_retries: int = 3,
    ) -> None:
        """Initialize AI analyzer.

        Args:
            llm_provider: LLM provider instance.
            concept_extractor: Concept extractor instance.
            batch_size: Number of highlights per batch.
            max_retries: Maximum retries per highlight.
        """
        self.llm_provider = llm_provider or LLMProvider()
        self.extractor = concept_extractor or ConceptExtractor(
            llm_provider=self.llm_provider
        )
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.logger = get_logger(self.__class__.__name__)

        # Job storage
        self._jobs: dict[str, AnalysisJob] = {}

    def create_job(
        self,
        highlights: list[dict[str, Any]],
        book_id: Optional[str] = None,
    ) -> str:
        """Create a new analysis job.

        Args:
            highlights: List of highlight dicts with 'id' and 'content'.
            book_id: Optional book ID for context.

        Returns:
            Job ID.
        """
        job_id = str(uuid.uuid4())

        job = AnalysisJob(
            job_id=job_id,
            status=JobStatus.PENDING,
            total=len(highlights),
        )

        self._jobs[job_id] = job
        self.logger.info(
            "Created analysis job %s with %d highlights (book_id: %s)",
            job_id,
            len(highlights),
            book_id,
        )

        return job_id

    def get_job_status(self, job_id: str) -> AnalysisJob:
        """Get job status and results.

        Args:
            job_id: Job ID.

        Returns:
            AnalysisJob with current status.

        Raises:
            ValueError: If job not found.
        """
        if job_id not in self._jobs:
            raise ValueError(f"Job not found: {job_id}")
        return self._jobs[job_id]

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job.

        Args:
            job_id: Job ID.

        Returns:
            True if cancelled successfully.
        """
        job = self.get_job_status(job_id)

        if job.status in (JobStatus.COMPLETED, JobStatus.FAILED):
            return False

        job.status = JobStatus.CANCELLED
        job.updated_at = datetime.now()
        self.logger.info("Cancelled job %s", job_id)
        return True

    def _divide_into_batches(
        self,
        highlights: list[dict[str, Any]],
    ) -> list[list[dict[str, Any]]]:
        """Divide highlights into batches.

        Args:
            highlights: List of highlights.

        Returns:
            List of highlight batches.
        """
        batches = []
        for i in range(0, len(highlights), self.batch_size):
            batches.append(highlights[i : i + self.batch_size])
        return batches

    def _update_job_progress(
        self,
        job_id: str,
        completed_count: int,
        error_count: int = 0,
    ) -> None:
        """Update job progress.

        Args:
            job_id: Job ID.
            completed_count: Number of newly completed items.
            error_count: Number of newly encountered errors.
        """
        job = self._jobs[job_id]
        job.completed += completed_count
        job.errors += error_count
        job.updated_at = datetime.now()

        # Check if completed
        if job.completed >= job.total:
            job.status = JobStatus.COMPLETED if job.errors == 0 else JobStatus.FAILED

    async def analyze_highlight(
        self,
        highlight: dict[str, Any],
        retries: int = 0,
    ) -> ExtractedConcepts:
        """Analyze a single highlight.

        Args:
            highlight: Highlight dict with 'content'.
            retries: Current retry count.

        Returns:
            ExtractedConcepts.

        Raises:
            Exception: If analysis fails after max retries.
        """
        content = highlight.get("content", "")

        if not content:
            return ExtractedConcepts(
                concepts=[],
                domain=None,
                emotion="neutral",
            )

        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.extractor.extract,
                content,
            )
            return result

        except Exception as e:
            if retries < self.max_retries:
                self.logger.warning(
                    "Analysis failed for highlight, retrying (%d/%d): %s",
                    retries + 1,
                    self.max_retries,
                    str(e),
                )
                await asyncio.sleep(2 ** retries)  # Exponential backoff
                return await self.analyze_highlight(highlight, retries + 1)

            self.logger.error(
                "Analysis failed after %d retries: %s",
                self.max_retries,
                str(e),
            )
            raise

    async def process_job(
        self,
        job_id: str,
        highlights: list[dict[str, Any]],
    ) -> AnalysisJob:
        """Process all highlights in a job.

        Args:
            job_id: Job ID.
            highlights: List of highlight dicts.

        Returns:
            Completed AnalysisJob.
        """
        job = self.get_job_status(job_id)
        job.status = JobStatus.PROCESSING
        job.updated_at = datetime.now()

        self.logger.info(
            "Starting job %s: %d highlights in batches of %d",
            job_id,
            len(highlights),
            self.batch_size,
        )

        batches = self._divide_into_batches(highlights)
        total_processed = 0
        total_errors = 0

        for batch_idx, batch in enumerate(batches):
            # Check for cancellation
            if job.status == JobStatus.CANCELLED:
                self.logger.info("Job %s cancelled, stopping", job_id)
                break

            self.logger.debug(
                "Processing batch %d/%d",
                batch_idx + 1,
                len(batches),
            )

            # Process batch
            batch_results = []
            batch_errors = 0

            for highlight in batch:
                try:
                    result = await self.analyze_highlight(highlight)
                    batch_results.append(result)
                except Exception as e:
                    self.logger.error(
                        "Failed to analyze highlight %s: %s",
                        highlight.get("id", "unknown"),
                        str(e),
                    )
                    batch_results.append(
                        ExtractedConcepts(
                            concepts=[],
                            domain=None,
                            emotion="neutral",
                        )
                    )
                    batch_errors += 1

            # Update job with batch results
            job.results.extend(batch_results)
            total_processed += len(batch_results)
            total_errors += batch_errors

            # Update progress
            self._update_job_progress(
                job_id,
                completed_count=len(batch_results),
                error_count=batch_errors,
            )

            self.logger.info(
                "Job %s progress: %d/%d (%.1f%%)",
                job_id,
                job.completed,
                job.total,
                job.progress_percent,
            )

        # Final status update
        job.updated_at = datetime.now()
        if job.completed >= job.total:
            job.status = JobStatus.COMPLETED if total_errors == 0 else JobStatus.FAILED

        self.logger.info(
            "Job %s completed: %d/%d processed, %d errors",
            job_id,
            total_processed,
            len(highlights),
            total_errors,
        )

        return job

    def run_job_sync(
        self,
        highlights: list[dict[str, Any]],
    ) -> str:
        """Run analysis synchronously (blocking).

        Args:
            highlights: List of highlight dicts.

        Returns:
            Job ID.
        """
        job_id = self.create_job(highlights)

        # Run in executor to avoid blocking
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.process_job(job_id, highlights))
        finally:
            loop.close()

        return job_id

    def get_all_jobs(self) -> list[AnalysisJob]:
        """Get all jobs.

        Returns:
            List of all analysis jobs.
        """
        return list(self._jobs.values())

    def cleanup_completed_jobs(self, older_than_hours: int = 24) -> int:
        """Clean up old completed jobs.

        Args:
            older_than_hours: Remove jobs older than this many hours.

        Returns:
            Number of jobs removed.
        """
        cutoff = datetime.now().timestamp() - (older_than_hours * 3600)
        to_remove = []

        for job_id, job in self._jobs.items():
            if job.status in (JobStatus.COMPLETED, JobStatus.FAILED):
                if job.updated_at.timestamp() < cutoff:
                    to_remove.append(job_id)

        for job_id in to_remove:
            del self._jobs[job_id]

        self.logger.info("Cleaned up %d old jobs", len(to_remove))
        return len(to_remove)


# Singleton instance
ai_analyzer = AIAnalyzer()
