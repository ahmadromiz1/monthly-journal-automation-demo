from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.job import Job, JobStatus, STATUS_LABELS


def ensure_storage() -> None:
    settings = get_settings()
    for path in [settings.upload_dir, settings.archive_dir, settings.sample_input_dir, settings.sample_output_dir]:
        path.mkdir(parents=True, exist_ok=True)


def serialize_list(items: list[str]) -> str:
    return json.dumps(items, ensure_ascii=True)


def deserialize_list(raw_value: str | None) -> list[str]:
    if not raw_value:
        return []
    return list(json.loads(raw_value))


def job_display_status(job: Job) -> str:
    notes = deserialize_list(job.validation_notes_json)
    if job.status == JobStatus.COMPLETED.value and notes:
        return "Completed with Review Notes"
    return job.status_label


def list_jobs(db: Session) -> list[Job]:
    return list(db.scalars(select(Job).order_by(Job.created_at.desc(), Job.id.desc())))


def get_job(db: Session, job_id: int) -> Job | None:
    return db.get(Job, job_id)


def get_job_by_key(db: Session, job_key: str) -> Job | None:
    return db.scalar(select(Job).where(Job.job_key == job_key))


async def create_job(db: Session, file: UploadFile, created_by: str) -> Job:
    ensure_storage()
    job_key = uuid4().hex[:12]
    input_dir = get_settings().upload_dir / job_key
    input_dir.mkdir(parents=True, exist_ok=True)
    input_path = input_dir / file.filename

    with input_path.open("wb") as target:
        shutil.copyfileobj(file.file, target)

    job = Job(
        job_key=job_key,
        original_filename=file.filename or "monthly_reconciliation.xlsx",
        stored_input_path=str(input_path),
        output_dir=str(input_dir / "output"),
        archive_path=None,
        status=JobStatus.WAITING.value,
        status_label=STATUS_LABELS[JobStatus.WAITING],
        created_by=created_by,
        validation_notes_json="[]",
        output_files_json="[]",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def mark_job_processing(job: Job, db: Session) -> None:
    job.status = JobStatus.PROCESSING.value
    job.status_label = STATUS_LABELS[JobStatus.PROCESSING]
    job.started_at = datetime.utcnow()
    job.error_message = None
    db.add(job)
    db.commit()


def mark_job_completed(job: Job, db: Session, output_files: list[Path], notes: list[str], archive_path: Path) -> None:
    job.status = JobStatus.COMPLETED.value
    job.status_label = STATUS_LABELS[JobStatus.COMPLETED]
    job.completed_at = datetime.utcnow()
    job.archive_path = str(archive_path)
    job.output_files_json = serialize_list([path.name for path in output_files])
    job.validation_notes_json = serialize_list(notes)
    job.error_message = None
    db.add(job)
    db.commit()


def mark_job_failed(job: Job, db: Session, error_message: str) -> None:
    job.status = JobStatus.FAILED.value
    job.status_label = STATUS_LABELS[JobStatus.FAILED]
    job.completed_at = datetime.utcnow()
    job.error_message = error_message
    db.add(job)
    db.commit()


def retry_job(job: Job, db: Session) -> None:
    job.status = JobStatus.WAITING.value
    job.status_label = STATUS_LABELS[JobStatus.WAITING]
    job.completed_at = None
    job.started_at = None
    job.error_message = None
    job.retry_count += 1
    job.validation_notes_json = "[]"
    job.output_files_json = "[]"
    if job.output_dir:
        output_dir = Path(job.output_dir)
        if output_dir.exists():
            shutil.rmtree(output_dir, ignore_errors=True)
    if job.archive_path:
        archive_path = Path(job.archive_path)
        if archive_path.exists():
            archive_path.unlink()
        job.archive_path = None
    db.add(job)
    db.commit()
