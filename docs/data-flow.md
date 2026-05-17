# Data Flow

## Upload Workflow

1. User signs in with dummy credentials.
2. User uploads an `.xlsx` workbook or loads the generated sample file.
3. The web app stores the file under `storage/jobs/<job_key>/`.
4. A database row is created with status `Waiting Queue`.

## Job Lifecycle

1. Worker scans for waiting jobs.
2. Selected job is marked `Processing`.
3. Workbook is staged and cleaned.
4. Validation rules run against AC and SR sheets.
5. Partner-level workbooks and log files are written to the job output folder.
6. All outputs are compressed into a ZIP archive.
7. Job is marked `Completed` or `Failed`.

## Background Worker Flow

`scripts/run_worker.py` starts a polling loop that repeatedly calls `process_pending_jobs_once()`. This keeps the web app simple and demonstrates a decoupled processing pattern typical of internal automation systems, without introducing Redis, Celery, or cloud queues.

## Output ZIP Process

The processor writes:

- one workbook per partner/agent
- `LOGERROR.txt`
- `LOGERROR_AGENT.txt`
- `LOGERROR_JOURNAL.txt`

Then the archive service compresses the output directory into a single downloadable ZIP file.

## Sanitized Public Version

The public demo is intentionally conservative:

- local-only execution
- dummy workbook schema
- fictional partner list
- synthetic transaction values
- generic validation outcomes
