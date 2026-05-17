# Architecture

## Overview

Monthly Journal Automation Demo is a sanitized internal-tool simulation built with FastAPI, Jinja2, SQLAlchemy, pandas, and openpyxl. The application uses SQLite for local demo persistence and filesystem storage for uploads, processing outputs, logs, and ZIP archives.

## Main Components

- `app/main.py`
  Hosts the web application, session-based dummy login, dashboard, upload endpoint, job detail page, retry action, and ZIP download.
- `app/models/job.py`
  Stores job metadata, status, validation notes, output file names, retry count, and archive references.
- `app/services/jobs.py`
  Creates queued jobs, manages storage directories, serializes notes, and updates lifecycle states.
- `app/services/worker.py`
  Polls queued jobs and executes the processor in a simple background loop.
- `app/services/processor.py`
  Orchestrates Excel reading, staging cleanup, validation, partner-level export, log generation, and ZIP packaging.
- `app/services/validator.py`
  Applies generic validation rules such as required columns, missing key fields, amount mismatch checks, partner-level reconciliation mismatch, and threshold warnings.
- `app/services/exporter.py`
  Builds per-partner output workbooks with AC, SR, and `JOURNAL_RECONCILIATION` sheets.
- `storage/jobs/`
  Local job folders for uploaded inputs and generated output files.
- `storage/archive/`
  Reserved archive folder for local demo use.

## Why SQLite + Filesystem

The public portfolio version avoids production dependencies and infrastructure assumptions. SQLite and local filesystem storage make the demo reproducible and safe for recruiters and interviewers who want to run it quickly.

## Sanitization Design

- No real partner names, company names, endpoints, or business formulas.
- No external credentials, tokens, or database dumps.
- Journal stages are illustrative and intentionally generic.
- Validation thresholds and mismatch rules are representative, not production-derived.
