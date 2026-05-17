from __future__ import annotations

import logging
import time
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.core.config import get_settings
from app.models.job import Job, JobStatus
from app.services.jobs import mark_job_completed, mark_job_failed, mark_job_processing
from app.services.processor import process_workbook


logger = logging.getLogger(__name__)


def process_job(job: Job, db: Session) -> None:
    mark_job_processing(job, db)
    input_path = Path(job.stored_input_path)
    output_dir = Path(job.output_dir)
    archive_path = get_settings().archive_dir / f"{job.job_key}_results.zip"
    try:
        output_files, notes, archive = process_workbook(input_path, output_dir, archive_path)
        mark_job_completed(job, db, output_files, notes, archive)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Job %s failed", job.job_key)
        mark_job_failed(job, db, str(exc))


def process_pending_jobs_once() -> int:
    processed = 0
    with SessionLocal() as db:
        queued_jobs = list(db.scalars(select(Job).where(Job.status == JobStatus.WAITING.value).order_by(Job.id.asc())))
        for job in queued_jobs:
            process_job(job, db)
            processed += 1
    return processed


def run_worker_loop(poll_seconds: int = 5) -> None:
    logger.info("Starting worker loop with poll interval %s seconds", poll_seconds)
    while True:
        processed = process_pending_jobs_once()
        logger.info("Worker cycle complete. Processed %s queued job(s).", processed)
        time.sleep(poll_seconds)
