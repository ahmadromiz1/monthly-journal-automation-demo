from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class JobStatus(StrEnum):
    WAITING = "waiting"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


STATUS_LABELS = {
    JobStatus.WAITING: "Waiting Queue",
    JobStatus.PROCESSING: "Processing",
    JobStatus.COMPLETED: "Completed",
    JobStatus.FAILED: "Failed",
}


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    stored_input_path: Mapped[str] = mapped_column(String(500))
    output_dir: Mapped[str] = mapped_column(String(500))
    archive_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default=JobStatus.WAITING.value)
    status_label: Mapped[str] = mapped_column(String(64), default=STATUS_LABELS[JobStatus.WAITING])
    created_by: Mapped[str] = mapped_column(String(120))
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    validation_notes_json: Mapped[str] = mapped_column(Text, default="[]")
    output_files_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
