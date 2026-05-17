from __future__ import annotations

from pathlib import Path

import pandas as pd


def build_journal_sheet(ac_partner: pd.DataFrame, sr_partner: pd.DataFrame) -> pd.DataFrame:
    ac_sales = round(float(ac_partner["total_fare"].sum()), 2)
    ac_tax = round(float(ac_partner["tax"].sum()), 2)
    ac_commission = round(float(ac_partner["commission"].sum()), 2)
    ac_net = round(float(ac_partner["net_amount"].sum()), 2)
    sr_balance = round(
        float((sr_partner["sales_amount"] - sr_partner["refund_amount"] - sr_partner["commission_amount"]).sum()),
        2,
    )
    stage_2_diff = round(ac_net - sr_balance, 2)
    stage_3_tax_invoice = round(ac_tax + ac_commission, 2)

    rows = [
        {"stage": "Stage 1: Sales Journal", "metric": "Gross Sales", "amount": ac_sales},
        {"stage": "Stage 1: Sales Journal", "metric": "Tax", "amount": ac_tax},
        {"stage": "Stage 1: Sales Journal", "metric": "Commission", "amount": ac_commission},
        {"stage": "Stage 1: Sales Journal", "metric": "Net Receivable", "amount": ac_net},
        {"stage": "Stage 2: Sales vs Statement Reconciliation", "metric": "Statement Balance", "amount": sr_balance},
        {"stage": "Stage 2: Sales vs Statement Reconciliation", "metric": "Difference", "amount": stage_2_diff},
        {
            "stage": "Stage 3: Tax / Commission Invoice Simulation",
            "metric": "Tax + Commission Invoice",
            "amount": stage_3_tax_invoice,
        },
    ]
    return pd.DataFrame(rows)


def export_partner_workbook(
    partner_code: str,
    ac_partner: pd.DataFrame,
    sr_partner: pd.DataFrame,
    output_dir: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    workbook_path = output_dir / f"{partner_code.lower()}_journal_pack.xlsx"
    journal_sheet = build_journal_sheet(ac_partner, sr_partner)

    with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
        ac_partner.to_excel(writer, index=False, sheet_name="AC")
        sr_partner.to_excel(writer, index=False, sheet_name="SR")
        journal_sheet.to_excel(writer, index=False, sheet_name="JOURNAL_RECONCILIATION")

    return workbook_path
