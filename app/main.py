from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import BASE_DIR, get_settings
from app.core.security import authenticate, get_current_user, login_user, logout_user, template_context
from app.db.database import get_db, init_db
from app.services.jobs import (
    create_job,
    deserialize_list,
    ensure_storage,
    get_job,
    job_display_status,
    list_jobs,
    retry_job,
)
from app.services.worker import process_pending_jobs_once


settings = get_settings()
app = FastAPI(title=settings.app_name)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


def build_job_file_manifest(job: object) -> list[dict[str, str]]:
    output_dir = Path(job.output_dir)
    manifest: list[dict[str, str]] = []
    for file_name in deserialize_list(job.output_files_json):
        file_path = output_dir / file_name
        manifest.append(
            {
                "name": file_name,
                "download_url": f"/jobs/{job.id}/files/{quote(file_name)}",
                "kind": "log" if file_name.lower().endswith(".txt") else "workbook",
                "exists": "true" if file_path.exists() else "false",
            }
        )
    return manifest


def read_log_lines(job: object, file_name: str) -> list[str]:
    log_path = Path(job.output_dir) / file_name
    if not log_path.exists():
        return []
    return [
        line.strip()
        for line in log_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and line.strip() != "No issues detected."
    ]


def build_input_file_manifest(job: object) -> dict[str, str]:
    input_path = Path(job.stored_input_path)
    return {
        "name": input_path.name,
        "download_url": f"/jobs/{job.id}/input",
        "exists": "true" if input_path.exists() else "false",
    }


@app.on_event("startup")
def on_startup() -> None:
    ensure_storage()
    init_db()


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/login")
def login_page(request: Request) -> object:
    return templates.TemplateResponse("login.html", template_context(request, error=None))


@app.post("/login")
async def login_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
) -> object:
    if not authenticate(username, password):
        return templates.TemplateResponse(
            "login.html",
            template_context(request, error="Invalid demo username or password."),
            status_code=400,
        )
    login_user(request, username)
    return RedirectResponse(url="/dashboard", status_code=303)


@app.post("/logout")
def logout_action(request: Request) -> RedirectResponse:
    logout_user(request)
    return RedirectResponse(url="/login", status_code=303)


@app.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)) -> object:
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    jobs = list_jobs(db)
    cards = [
        {
            "id": job.id,
            "job_key": job.job_key,
            "filename": job.original_filename,
            "created_by": job.created_by,
            "created_at": job.created_at,
            "status_label": job_display_status(job),
            "status": job.status,
            "retry_count": job.retry_count,
            "input_file": build_input_file_manifest(job),
        }
        for job in jobs
    ]
    sample_input_path = settings.sample_input_dir / "monthly_reconciliation_sample.xlsx"
    return templates.TemplateResponse(
        "dashboard.html",
        template_context(
            request,
            current_user=user,
            jobs=cards,
            sample_file=sample_input_path.exists(),
            sample_input_name=sample_input_path.name,
            sample_input_download_url="/sample-data/input" if sample_input_path.exists() else None,
            worker_required=True,
        ),
    )


@app.post("/jobs/upload")
async def upload_job(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported.")
    job = await create_job(db, file, user)
    return RedirectResponse(url=f"/jobs/{job.id}", status_code=303)


@app.post("/jobs/upload-sample")
async def upload_sample_job(request: Request, db: Session = Depends(get_db)) -> RedirectResponse:
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    sample_path = settings.sample_input_dir / "monthly_reconciliation_sample.xlsx"
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail="Sample input file not found.")
    upload = UploadFile(filename=sample_path.name, file=sample_path.open("rb"))
    try:
        job = await create_job(db, upload, user)
    finally:
        upload.file.close()
    return RedirectResponse(url=f"/jobs/{job.id}", status_code=303)


@app.get("/jobs/{job_id}")
def job_detail(request: Request, job_id: int, db: Session = Depends(get_db)) -> object:
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    job = get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    notes = deserialize_list(job.validation_notes_json)
    output_files = build_job_file_manifest(job)
    download_ready = bool(job.archive_path and Path(job.archive_path).exists())
    row_logs = read_log_lines(job, "LOGERROR.txt")
    agent_logs = read_log_lines(job, "LOGERROR_AGENT.txt")
    journal_logs = read_log_lines(job, "LOGERROR_JOURNAL.txt")
    return templates.TemplateResponse(
        "job_detail.html",
        template_context(
            request,
            current_user=user,
            job=job,
            input_file=build_input_file_manifest(job),
            display_status=job_display_status(job),
            notes=notes,
            output_files=output_files,
            download_ready=download_ready,
            row_logs=row_logs,
            agent_logs=agent_logs,
            journal_logs=journal_logs,
            is_pending=job.status in {"waiting", "processing"},
        ),
    )


@app.post("/jobs/{job_id}/retry")
def retry_job_action(request: Request, job_id: int, db: Session = Depends(get_db)) -> RedirectResponse:
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    job = get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    retry_job(job, db)
    return RedirectResponse(url=f"/jobs/{job_id}", status_code=303)


@app.post("/jobs/process-now")
def process_jobs_now(request: Request) -> RedirectResponse:
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    process_pending_jobs_once()
    return RedirectResponse(url="/dashboard", status_code=303)


@app.post("/jobs/{job_id}/process-now")
def process_job_now(request: Request, job_id: int, db: Session = Depends(get_db)) -> RedirectResponse:
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    job = get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    process_pending_jobs_once()
    return RedirectResponse(url=f"/jobs/{job_id}", status_code=303)


@app.get("/jobs/{job_id}/download")
def download_archive(request: Request, job_id: int, db: Session = Depends(get_db)) -> FileResponse:
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required.")
    job = get_job(db, job_id)
    if not job or not job.archive_path:
        raise HTTPException(status_code=404, detail="Archive not available.")
    archive_path = Path(job.archive_path)
    if not archive_path.exists():
        raise HTTPException(status_code=404, detail="Archive file not found.")
    return FileResponse(path=archive_path, filename=archive_path.name, media_type="application/zip")


@app.get("/sample-data/input")
def download_sample_input(request: Request) -> FileResponse:
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required.")
    sample_path = settings.sample_input_dir / "monthly_reconciliation_sample.xlsx"
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail="Sample input file not found.")
    return FileResponse(path=sample_path, filename=sample_path.name)


@app.get("/jobs/{job_id}/input")
def download_job_input(request: Request, job_id: int, db: Session = Depends(get_db)) -> FileResponse:
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required.")
    job = get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    input_path = Path(job.stored_input_path)
    if not input_path.exists():
        raise HTTPException(status_code=404, detail="Input file not found.")
    return FileResponse(path=input_path, filename=input_path.name)


@app.get("/jobs/{job_id}/files/{file_name:path}")
def download_output_file(request: Request, job_id: int, file_name: str, db: Session = Depends(get_db)) -> FileResponse:
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required.")
    job = get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    output_dir = Path(job.output_dir).resolve()
    target_path = (output_dir / file_name).resolve()
    if output_dir not in target_path.parents and target_path != output_dir:
        raise HTTPException(status_code=400, detail="Invalid file path.")
    if not target_path.exists() or not target_path.is_file():
        raise HTTPException(status_code=404, detail="Output file not found.")

    media_type = "text/plain" if target_path.suffix.lower() == ".txt" else None
    return FileResponse(path=target_path, filename=target_path.name, media_type=media_type)
