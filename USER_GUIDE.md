# User Guide | Panduan Pengguna

## 1. Purpose | Tujuan

This guide explains how to run the Monthly Journal Automation Demo, what to expect from the UI, and how the demo differs from a real production finance-journaling workflow.

Panduan ini menjelaskan cara menjalankan Monthly Journal Automation Demo, apa yang akan terlihat di UI, dan bagaimana demo ini berbeda dari workflow finance journaling produksi yang sebenarnya.

## 2. Recommended Startup | Cara Menjalankan Yang Direkomendasikan

### Docker

```bash
docker compose up --build
```

This starts:

- `web` service on `http://127.0.0.1:8000`
- `worker` service for background processing

Ini akan menjalankan:

- service `web` di `http://127.0.0.1:8000`
- service `worker` untuk background processing

### Local Python Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/generate_sample_data.py
uvicorn app.main:app --reload
```

In another terminal:

```bash
.venv\Scripts\activate
python scripts/run_worker.py
```

Di terminal lain:

```bash
.venv\Scripts\activate
python scripts/run_worker.py
```

## 3. Login

Use the dummy credentials below:

- Username: `finance.demo`
- Password: `demo12345`

Gunakan dummy credentials berikut:

- Username: `finance.demo`
- Password: `demo12345`

## 4. Demo Flow In The UI | Alur Demo Di UI

1. Open the dashboard.
2. Upload your own sanitized workbook or click `Use Generated Sample Workbook`.
3. A job will appear in `Job Queue`.
4. If the worker is running, the job will move from `Waiting Queue` to `Processing`.
5. If you are not running the worker, you can use the manual `Process Now` button from the UI.
6. When the process finishes, the job detail page will show:
   - review notes
   - validation logs
   - generated partner workbooks
   - downloadable ZIP archive
   - downloadable source input workbook

1. Buka dashboard.
2. Upload workbook sanitized milik Anda atau klik `Use Generated Sample Workbook`.
3. Sebuah job akan muncul di `Job Queue`.
4. Jika worker berjalan, job akan berubah dari `Waiting Queue` ke `Processing`.
5. Jika worker tidak dijalankan, Anda bisa menggunakan tombol manual `Process Now` dari UI.
6. Setelah selesai, halaman detail job akan menampilkan:
   - review notes
   - validation logs
   - generated partner workbooks
   - ZIP archive yang bisa diunduh
   - source input workbook yang bisa diunduh

## 5. Job Lifecycle | Siklus Hidup Job

- `Waiting Queue`: job has been created but not processed yet
- `Processing`: worker is running staging, validation, export, and archive steps
- `Completed`: processing finished and output files were created
- `Completed with Review Notes`: processing finished and validation notes were detected
- `Failed`: processing stopped because of an exception

- `Waiting Queue`: job sudah dibuat tetapi belum diproses
- `Processing`: worker sedang menjalankan staging, validation, export, dan archive
- `Completed`: processing selesai dan output berhasil dibuat
- `Completed with Review Notes`: processing selesai tetapi ditemukan validation notes
- `Failed`: processing berhenti karena exception

## 6. What The Worker Does | Tugas Worker

On each cycle, the worker:

1. checks queued jobs
2. marks a selected job as processing
3. reads AC and SR sheets
4. stages and cleans the input data
5. runs generic validation rules
6. generates per-partner workbooks
7. writes review logs
8. creates a ZIP archive
9. updates the final job status

Pada setiap siklus, worker:

1. mengecek job queue
2. menandai job terpilih sebagai processing
3. membaca sheet AC dan SR
4. melakukan staging dan cleaning data input
5. menjalankan aturan validasi generic
6. membuat workbook per partner
7. menulis review logs
8. membuat ZIP archive
9. memperbarui status akhir job

## 7. Real Workflow Note | Catatan Workflow Nyata

This demo comes from a real-world type of finance reconciliation problem, but the actual production workflow is more complex.

Demo ini berasal dari tipe permasalahan rekonsiliasi finance di dunia nyata, tetapi workflow produksi aslinya jauh lebih kompleks.

In real operations:

- a single raw file can contain hundreds of thousands of transactions
- most journal generation can be automated
- only around 1-2% of records usually stay unbalanced
- those exceptions are often traced manually
- the root cause is commonly missing or incomplete raw-source ingestion at an earlier stage
- the final output can be transformed from an all-agent raw journal into per-agent journal packs using the original accounting format ready for distribution

Dalam operasional nyata:

- satu file mentah bisa berisi ratusan ribu transaksi
- sebagian besar generate jurnal bisa diotomatisasi
- biasanya hanya sekitar 1-2% data yang masih tidak balance
- exception tersebut biasanya ditelusuri manual
- akar masalahnya sering berasal dari data mentah yang tidak tertarik lengkap pada tahap ingestion awal
- output akhir dapat diubah dari jurnal mentah gabungan semua agent menjadi jurnal per-agent menggunakan format akuntansi asli yang siap didistribusikan

## 8. What This Demo Simplifies | Yang Disederhanakan Oleh Demo

- the workbook size
- the accounting rules
- the journal format
- the partner mapping logic
- the validation formulas
- the distribution workflow
- the infrastructure stack

- ukuran workbook
- aturan akuntansi
- format jurnal
- logic mapping partner
- formula validasi
- workflow distribusi
- stack infrastruktur

## 9. Validation Review In The UI | Review Validasi Di UI

The Job Detail page shows:

- `Review Summary`
- `Row Validation Log`
- `Agent Summary Log`
- `Journal Validation Log`

Halaman Job Detail menampilkan:

- `Review Summary`
- `Row Validation Log`
- `Agent Summary Log`
- `Journal Validation Log`

This allows the reviewer to inspect mismatches directly without opening the ZIP file first.

Ini memungkinkan reviewer melihat mismatch langsung tanpa harus membuka ZIP lebih dulu.

## 10. Downloadable Assets | File Yang Bisa Diunduh

From the UI, you can download:

- the generated sample input workbook
- the source input workbook of each job
- each output workbook per partner
- each log file
- the final ZIP archive

Dari UI, Anda bisa mengunduh:

- generated sample input workbook
- source input workbook dari tiap job
- tiap output workbook per partner
- tiap log file
- ZIP archive final

## 11. Why The Public Version Is Sanitized | Kenapa Versi Public Ini Disanitasi

The public version excludes:

- real company data
- real partner identities
- credentials and environment secrets
- internal formulas
- proprietary schemas
- production integrations

Versi public ini tidak menyertakan:

- data perusahaan asli
- identitas partner asli
- credential dan environment secret
- formula internal
- skema proprietary
- integrasi produksi
