from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from app.core.config import get_settings
from app.services.archive import build_archive
from app.services.exporter import export_partner_workbook
from app.services.staging import StagedWorkbook, clean_date_columns, clean_numeric_columns, normalize_columns
from app.services.validator import ValidationResult, validate_required_columns, run_validations


logger = logging.getLogger(__name__)


def load_workbook(input_path: Path) -> StagedWorkbook:
    ac_frame = pd.read_excel(input_path, sheet_name="AC")
    sr_frame = pd.read_excel(input_path, sheet_name="SR")

    ac_frame = normalize_columns(ac_frame)
    sr_frame = normalize_columns(sr_frame)

    ac_frame = clean_numeric_columns(ac_frame, ["base_fare", "tax", "commission", "total_fare", "net_amount"])
    sr_frame = clean_numeric_columns(sr_frame, ["sales_amount", "refund_amount", "commission_amount", "balance_amount"])
    ac_frame = clean_date_columns(ac_frame, ["transaction_date"])
    sr_frame = clean_date_columns(sr_frame, ["statement_date"])

    ac_frame["partner_code"] = ac_frame["partner_code"].fillna("").astype(str).str.upper().str.strip()
    sr_frame["partner_code"] = sr_frame["partner_code"].fillna("").astype(str).str.upper().str.strip()
    ac_frame["partner_name"] = ac_frame["partner_name"].fillna("Unknown Partner").astype(str).str.strip()
    sr_frame["partner_name"] = sr_frame["partner_name"].fillna("Unknown Partner").astype(str).str.strip()
    ac_frame["ticket_number"] = ac_frame["ticket_number"].fillna("").astype(str).str.strip()
    sr_frame["ticket_number"] = sr_frame["ticket_number"].fillna("").astype(str).str.strip()

    return StagedWorkbook(ac=ac_frame, sr=sr_frame)


def write_logs(output_dir: Path, validation: ValidationResult) -> list[Path]:
    log_files = {
        "LOGERROR.txt": validation.row_logs,
        "LOGERROR_AGENT.txt": validation.agent_logs,
        "LOGERROR_JOURNAL.txt": validation.journal_logs,
    }
    paths: list[Path] = []
    for filename, lines in log_files.items():
        log_path = output_dir / filename
        content = "\n".join(lines) if lines else "No issues detected."
        log_path.write_text(content + "\n", encoding="utf-8")
        paths.append(log_path)
    return paths


def parse_log_notes(log_paths: list[Path]) -> list[str]:
    notes: list[str] = []
    for path in log_paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            normalized = line.strip()
            if normalized and normalized != "No issues detected.":
                notes.append(normalized)
    return notes


def process_workbook(input_path: Path, output_dir: Path, archive_path: Path) -> tuple[list[Path], list[str], Path]:
    settings = get_settings()
    staged = load_workbook(input_path)
    missing_columns = validate_required_columns(staged.ac, staged.sr)
    if missing_columns:
        raise ValueError("; ".join(missing_columns))

    validation = run_validations(staged.ac, staged.sr, warning_threshold=settings.warning_threshold)

    exported_files: list[Path] = []
    for partner_code in sorted(
        set(staged.ac["partner_code"].unique().tolist()) | set(staged.sr["partner_code"].unique().tolist())
    ):
        safe_partner_code = partner_code or "UNKNOWN_PARTNER"
        ac_partner = staged.ac.loc[staged.ac["partner_code"] == partner_code].copy()
        sr_partner = staged.sr.loc[staged.sr["partner_code"] == partner_code].copy()
        if ac_partner.empty:
            ac_partner = staged.ac.iloc[0:0].copy()
        if sr_partner.empty:
            sr_partner = staged.sr.iloc[0:0].copy()
        exported_files.append(export_partner_workbook(safe_partner_code, ac_partner, sr_partner, output_dir))

    log_paths = write_logs(output_dir, validation)
    exported_files.extend(log_paths)
    parsed_notes = parse_log_notes(log_paths)
    archive = build_archive(output_dir, archive_path)
    logger.info("Processed workbook %s into %s", input_path, output_dir)
    return exported_files, parsed_notes, archive
