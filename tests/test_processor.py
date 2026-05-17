from __future__ import annotations

from pathlib import Path

from app.services.processor import process_workbook
from scripts.generate_sample_data import build_frames


def test_process_workbook_generates_outputs(tmp_path: Path) -> None:
    input_path = tmp_path / "sample.xlsx"
    output_dir = tmp_path / "output"
    archive_path = tmp_path / "result.zip"

    ac_frame, sr_frame = build_frames(seed=101)
    with __import__("pandas").ExcelWriter(input_path, engine="openpyxl") as writer:
        ac_frame.to_excel(writer, index=False, sheet_name="AC")
        sr_frame.to_excel(writer, index=False, sheet_name="SR")

    output_files, review_notes, archive = process_workbook(input_path, output_dir, archive_path)

    assert archive.exists()
    assert any(path.name == "LOGERROR.txt" for path in output_files)
    assert any(path.name.endswith("_journal_pack.xlsx") for path in output_files)
    assert review_notes
