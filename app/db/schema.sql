CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_key VARCHAR(64) NOT NULL UNIQUE,
    original_filename VARCHAR(255) NOT NULL,
    stored_input_path VARCHAR(500) NOT NULL,
    output_dir VARCHAR(500) NOT NULL,
    archive_path VARCHAR(500),
    status VARCHAR(32) NOT NULL,
    status_label VARCHAR(64) NOT NULL,
    created_by VARCHAR(120) NOT NULL,
    error_message TEXT,
    started_at DATETIME,
    completed_at DATETIME,
    retry_count INTEGER NOT NULL DEFAULT 0,
    validation_notes_json TEXT NOT NULL DEFAULT '[]',
    output_files_json TEXT NOT NULL DEFAULT '[]',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
