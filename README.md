# Monthly Journal Automation Demo

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Web_App-green)
![Pandas](https://img.shields.io/badge/Pandas-Data_Processing-orange)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

Monthly Journal Automation Demo is a sanitized portfolio repository that simulates a finance internal tool for monthly reconciliation processing, journal validation, partner-level Excel generation, and ZIP archive packaging.

Monthly Journal Automation Demo adalah repository portfolio yang sudah disanitasi untuk mensimulasikan internal finance tool yang memproses rekonsiliasi bulanan, validasi jurnal, generate file Excel per partner, dan packaging hasil dalam ZIP archive.

> “This repository uses anonymized/mock finance reconciliation data. No company-sensitive assets, credentials, production formulas, internal schemas, or real partner data are included.”
>
> “Repository ini menggunakan data mock/anonymized untuk rekonsiliasi finance. Tidak ada aset sensitif perusahaan, credential, formula produksi, skema internal, atau data partner asli di dalamnya.”

## Project Overview | Gambaran Proyek

This project demonstrates a backend automation workflow that accepts monthly reconciliation workbooks, creates processing jobs, runs queue-based background processing, validates AC/SR data, exports output workbooks per partner, generates validation logs, and exposes downloadable ZIP results through a web UI.

Project ini mendemonstrasikan alur backend automation yang menerima workbook rekonsiliasi bulanan, membuat processing job, menjalankan background worker berbasis queue, memvalidasi data AC/SR, mengekspor workbook output per partner, membuat log validasi, dan menyediakan hasil ZIP yang bisa diunduh lewat web UI.

## Problem Statement | Latar Belakang

Finance operations teams often work with a single large raw reconciliation file containing tens or hundreds of thousands of rows. The real process is usually more complex than this demo: data cleanup, balance checking, journal grouping, partner routing, exception handling, and distribution all need to be controlled carefully.

Tim finance operations sering bekerja dengan satu file data mentah berukuran besar yang berisi puluhan ribu sampai ratusan ribu transaksi. Proses aslinya jauh lebih kompleks daripada demo ini: pembersihan data, pengecekan balance, grouping jurnal, routing per partner, exception handling, dan distribusi hasil harus dikontrol dengan ketat.

## Real-World Context | Konteks Proses Nyata

In the real workflow that inspired this demo, most records can be processed automatically. Usually only around 1-2% of records remain unbalanced and need manual investigation. Those exceptions typically happen because some raw source data does not get captured during the earliest ingestion step, not because the whole automation fails.

Dalam proses nyata yang menginspirasi demo ini, sebagian besar data bisa diproses otomatis. Biasanya hanya sekitar 1-2% data yang masih tidak balance dan perlu pengecekan manual. Exception ini umumnya terjadi karena ada sebagian data mentah yang tidak tertarik pada proses awal, bukan karena seluruh otomasi gagal.

The real production process can transform an all-agent raw journal source into per-agent journal outputs in the original accounting format, ready to be distributed to the relevant agents. In practice, that end-to-end cycle can take around two weeks when done manually at scale, especially when the input file is very large.

Proses produksi yang sebenarnya dapat mengubah jurnal mentah gabungan semua agent menjadi jurnal per-agent dengan format jurnal asli yang siap didistribusikan ke agent terkait. Dalam praktiknya, siklus end-to-end ini bisa memakan waktu sekitar dua minggu jika dikerjakan manual dalam skala besar, apalagi saat file input sangat besar.

This demo intentionally simplifies several parts of that reality so the repository is safe to publish and easy to run locally.

Demo ini sengaja menyederhanakan beberapa bagian dari proses nyata agar aman dipublikasikan dan mudah dijalankan secara lokal.

## What This Demo Simplifies | Penyederhanaan Pada Demo

- Uses mock partner names and demo journal stages instead of real production journal formats.
- Uses a smaller workbook with 50 synthetic transactions instead of a raw file with hundreds of thousands of rows.
- Uses generic reconciliation rules instead of company-specific formulas and accounting mappings.
- Uses local filesystem storage and SQLite instead of production infrastructure and enterprise integrations.
- Uses a simple polling worker instead of a more advanced queue or orchestration stack.

- Menggunakan nama partner fiktif dan stage jurnal demo, bukan format jurnal produksi asli.
- Menggunakan workbook kecil berisi 50 transaksi sintetis, bukan file mentah ratusan ribu baris.
- Menggunakan aturan rekonsiliasi yang generic, bukan formula dan mapping akuntansi spesifik perusahaan.
- Menggunakan local filesystem dan SQLite, bukan infrastruktur produksi dan integrasi enterprise.
- Menggunakan polling worker sederhana, bukan queue/orchestration stack yang lebih maju.

## Solution Overview | Ringkasan Solusi

The repository exposes a FastAPI web app for upload and review, plus a lightweight worker for job processing. The processor stages AC and SR sheets, validates the data, writes log files, generates per-partner workbooks, and packages the result into a ZIP archive.

Repository ini menyediakan FastAPI web app untuk upload dan review, ditambah worker ringan untuk job processing. Processor melakukan staging sheet AC dan SR, memvalidasi data, menulis log file, membuat workbook per partner, lalu membungkus hasilnya menjadi ZIP archive.

## Business Flow | Alur Bisnis

1. User logs in with dummy credentials.
2. User uploads a monthly reconciliation workbook.
3. System creates a processing job with `Waiting Queue` status.
4. Worker picks the queued job and marks it `Processing`.
5. Processor reads AC and SR sheets and normalizes demo data.
6. Validator checks row-level, partner-level, and journal-level conditions.
7. Exporter creates one output workbook per partner/agent.
8. Processor writes validation logs and bundles all outputs into a ZIP archive.
9. UI shows `Completed`, `Failed`, or `Completed with Review Notes`.

1. User login menggunakan dummy credentials.
2. User upload workbook rekonsiliasi bulanan.
3. Sistem membuat processing job dengan status `Waiting Queue`.
4. Worker mengambil job queue lalu mengubah status menjadi `Processing`.
5. Processor membaca sheet AC dan SR lalu menormalkan data demo.
6. Validator mengecek kondisi row-level, partner-level, dan journal-level.
7. Exporter membuat satu output workbook per partner/agent.
8. Processor membuat validation logs dan membungkus semua output ke ZIP archive.
9. UI menampilkan `Completed`, `Failed`, atau `Completed with Review Notes`.

## Features | Fitur

- Dummy login flow
- Dashboard job list
- Upload monthly reconciliation workbook
- Job queue creation
- Background worker simulation
- Manual `Process Now` fallback from the UI
- Job status tracking
- Job detail page with direct review notes
- Download input workbook, ZIP archive, and individual output files
- Retry failed job support
- Local filesystem storage

- Dummy login
- Dashboard daftar job
- Upload workbook rekonsiliasi bulanan
- Pembuatan job queue
- Simulasi background worker
- Tombol fallback `Process Now` dari UI
- Tracking status job
- Halaman detail job dengan review notes langsung
- Download input workbook, ZIP archive, dan file output satu per satu
- Retry failed job
- Penyimpanan lokal berbasis filesystem

## Tech Stack

- Python 3.11+
- FastAPI
- Jinja2 templates
- SQLAlchemy
- SQLite for local demo persistence
- pandas
- openpyxl
- pathlib
- logging
- pytest
- Docker
- Docker Compose

## Architecture | Arsitektur

- Web layer: FastAPI routes and Jinja2 templates
- Persistence layer: SQLAlchemy + SQLite `jobs` table
- Storage layer: local folders under `storage/jobs/`
- Worker layer: polling loop in `scripts/run_worker.py`
- Processing layer: staging, validation, export, logs, archive

- Web layer: FastAPI routes dan Jinja2 templates
- Persistence layer: SQLAlchemy + SQLite `jobs` table
- Storage layer: folder lokal di `storage/jobs/`
- Worker layer: polling loop di `scripts/run_worker.py`
- Processing layer: staging, validation, export, logs, archive

See [docs/architecture.md](docs/architecture.md), [docs/data-flow.md](docs/data-flow.md), and [docs/validation-rules.md](docs/validation-rules.md).

## Folder Structure | Struktur Folder

```text
monthly-journal-automation-demo/
├─ app/
├─ docs/
├─ sample_data/
├─ scripts/
├─ storage/
├─ tests/
├─ .dockerignore
├─ .env.example
├─ .gitignore
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
├─ README.md
└─ USER_GUIDE.md
```

## Input Workbook Format | Format Workbook Input

Input workbook must contain:

- `AC` sheet
- `SR` sheet

### AC Columns

- `partner_code`
- `partner_name`
- `transaction_date`
- `ticket_number`
- `route`
- `base_fare`
- `tax`
- `commission`
- `total_fare`
- `net_amount`

### SR Columns

- `partner_code`
- `partner_name`
- `statement_date`
- `ticket_number`
- `sales_amount`
- `refund_amount`
- `commission_amount`
- `balance_amount`

## Processing Workflow | Workflow Pemrosesan

1. Upload workbook into a job folder.
2. Create a database record with queued status.
3. Worker loads the workbook and stages AC/SR sheets.
4. Required-column validation runs first.
5. Row-level and partner-level validations generate review notes.
6. Output workbook per partner is exported.
7. Log files are written:
   - `LOGERROR.txt`
   - `LOGERROR_AGENT.txt`
   - `LOGERROR_JOURNAL.txt`
8. All output files are compressed into a ZIP archive.

1. Upload workbook ke folder job.
2. Buat record database dengan status queued.
3. Worker memuat workbook dan melakukan staging sheet AC/SR.
4. Validasi kolom wajib dijalankan lebih dulu.
5. Validasi row-level dan partner-level menghasilkan review notes.
6. Output workbook per partner dibuat.
7. Log files dibuat:
   - `LOGERROR.txt`
   - `LOGERROR_AGENT.txt`
   - `LOGERROR_JOURNAL.txt`
8. Semua output dibungkus menjadi ZIP archive.

## Validation Rules | Aturan Validasi

- required columns exist
- missing `partner_code`
- missing `ticket_number`
- `total_fare` mismatch
- `net_amount` mismatch
- partner-level total mismatch
- journal debit/credit imbalance simulation
- warning when difference exceeds threshold

- kolom wajib harus ada
- `partner_code` kosong
- `ticket_number` kosong
- mismatch pada `total_fare`
- mismatch pada `net_amount`
- total partner tidak balance
- simulasi debit/credit imbalance jurnal
- warning saat selisih melewati threshold

## Output Files | File Output

Each processed job produces:

- one Excel workbook per partner
- `LOGERROR.txt`
- `LOGERROR_AGENT.txt`
- `LOGERROR_JOURNAL.txt`
- one ZIP archive

Each partner workbook contains:

- `AC`
- `SR`
- `JOURNAL_RECONCILIATION`

## Example Journal Notes | Contoh Journal Notes

- `Row validation mismatch on ticket DEMO-0001`
- `Partner ALPHA01 total amount not balanced: difference 14.25`
- `Journal Stage 2 warning for BETA02: reconciliation difference 125.00 exceeds threshold`

## Run With Docker | Menjalankan Dengan Docker

This is the recommended way for portfolio reviewers because it avoids local Python setup confusion.

Ini adalah cara yang direkomendasikan untuk reviewer portfolio karena menghindari kebingungan setup Python lokal.

```bash
docker compose up --build
```

Open:

- Web app: `http://127.0.0.1:8000`
- Username: `finance.demo`
- Password: `demo12345`

What runs in Docker:

- `web` service: generates sample data and starts FastAPI
- `worker` service: generates sample data and starts the polling worker

To stop:

```bash
docker compose down
```

## Run Locally | Menjalankan Secara Lokal

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/generate_sample_data.py
uvicorn app.main:app --reload
```

In a second terminal:

```bash
.venv\Scripts\activate
python scripts/run_worker.py
```

## How To Generate Sample Data | Cara Generate Sample Data

```bash
python scripts/generate_sample_data.py
```

This creates `sample_data/input/monthly_reconciliation_sample.xlsx` with:

- 5 fictional partners
- 50 synthetic transactions
- valid rows and intentionally mismatched rows
- review-note scenarios for row, agent, and journal validation

File ini akan membuat `sample_data/input/monthly_reconciliation_sample.xlsx` dengan:

- 5 partner fiktif
- 50 transaksi sintetis
- kombinasi data valid dan mismatch yang disengaja
- skenario review note untuk row, agent, dan journal validation

## Security & Privacy Note | Catatan Keamanan & Privasi

This demo is designed for public GitHub use:

- no secrets or tokens
- no real partner names
- no production endpoints
- no real finance formulas
- no real internal schemas
- local-only demo storage

Demo ini dirancang untuk public GitHub:

- tanpa secret atau token
- tanpa nama partner asli
- tanpa endpoint produksi
- tanpa formula finance asli
- tanpa skema internal asli
- storage demo lokal saja

## Portfolio Positioning | Posisi Portfolio

This repository is positioned as:

- backend automation project
- finance workflow automation system
- Excel processing system
- internal tools web app
- background job processing demo
- reconciliation and validation pipeline

Repository ini diposisikan sebagai:

- backend automation project
- finance workflow automation system
- Excel processing system
- internal tools web app
- demo background job processing
- pipeline rekonsiliasi dan validasi

## Portfolio Disclaimer | Disclaimer Portfolio

This repository is a simulation of a finance workflow automation system for portfolio and interview purposes. The real production workflow is more complex, handles much larger raw files, uses original journal formats, and involves stricter business rules and exception handling than what is shown here.

Repository ini adalah simulasi sistem otomasi workflow finance untuk keperluan portfolio dan interview. Workflow produksi yang sebenarnya jauh lebih kompleks, menangani file mentah yang jauh lebih besar, menggunakan format jurnal asli, dan memiliki business rules serta exception handling yang lebih ketat dibanding yang ditampilkan di sini.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Future Improvements | Pengembangan Berikutnya

- replace polling worker with queue-based orchestration
- add richer process progress tracking per stage
- add PostgreSQL profile for shared environments
- add test coverage for web routes and download flows
- add preview tables for AC/SR input sheets directly in the UI
- expand CI coverage for automated validation
