from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


AC_REQUIRED_COLUMNS = [
    "partner_code",
    "partner_name",
    "transaction_date",
    "ticket_number",
    "route",
    "base_fare",
    "tax",
    "commission",
    "total_fare",
    "net_amount",
]

SR_REQUIRED_COLUMNS = [
    "partner_code",
    "partner_name",
    "statement_date",
    "ticket_number",
    "sales_amount",
    "refund_amount",
    "commission_amount",
    "balance_amount",
]


@dataclass
class ValidationResult:
    row_logs: list[str]
    agent_logs: list[str]
    journal_logs: list[str]
    review_notes: list[str]


def validate_required_columns(ac_frame: pd.DataFrame, sr_frame: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    missing_ac = [column for column in AC_REQUIRED_COLUMNS if column not in ac_frame.columns]
    missing_sr = [column for column in SR_REQUIRED_COLUMNS if column not in sr_frame.columns]
    if missing_ac:
        errors.append(f"Missing AC columns: {', '.join(missing_ac)}")
    if missing_sr:
        errors.append(f"Missing SR columns: {', '.join(missing_sr)}")
    return errors


def run_validations(ac_frame: pd.DataFrame, sr_frame: pd.DataFrame, warning_threshold: float) -> ValidationResult:
    row_logs: list[str] = []
    agent_logs: list[str] = []
    journal_logs: list[str] = []

    for index, row in ac_frame.iterrows():
        ticket = row.get("ticket_number") or f"AC-ROW-{index + 1}"
        if not row.get("partner_code"):
            row_logs.append(f"Missing partner_code on AC row {index + 2} / ticket {ticket}")
        if not row.get("ticket_number"):
            row_logs.append(f"Missing ticket_number on AC row {index + 2}")

        expected_total = round(float(row.get("base_fare", 0.0)) + float(row.get("tax", 0.0)), 2)
        total_fare = round(float(row.get("total_fare", 0.0)), 2)
        if abs(expected_total - total_fare) > 0.01:
            row_logs.append(f"Row validation mismatch on ticket {ticket}: total_fare mismatch")

        expected_net = round(total_fare - float(row.get("commission", 0.0)), 2)
        net_amount = round(float(row.get("net_amount", 0.0)), 2)
        if abs(expected_net - net_amount) > 0.01:
            row_logs.append(f"Row validation mismatch on ticket {ticket}: net_amount mismatch")

    for index, row in sr_frame.iterrows():
        ticket = row.get("ticket_number") or f"SR-ROW-{index + 1}"
        if not row.get("partner_code"):
            row_logs.append(f"Missing partner_code on SR row {index + 2} / ticket {ticket}")
        if not row.get("ticket_number"):
            row_logs.append(f"Missing ticket_number on SR row {index + 2}")

    ac_totals = ac_frame.groupby("partner_code", dropna=False)["net_amount"].sum().round(2)
    sr_totals = (
        sr_frame.assign(
            sr_net=(sr_frame["sales_amount"] - sr_frame["refund_amount"] - sr_frame["commission_amount"]).round(2)
        )
        .groupby("partner_code", dropna=False)["sr_net"]
        .sum()
        .round(2)
    )
    partner_codes = sorted(set(ac_totals.index.tolist()) | set(sr_totals.index.tolist()))
    for partner_code in partner_codes:
        ac_value = float(ac_totals.get(partner_code, 0.0))
        sr_value = float(sr_totals.get(partner_code, 0.0))
        diff = round(ac_value - sr_value, 2)
        label = partner_code or "UNKNOWN_PARTNER"
        if abs(diff) > 0.01:
            agent_logs.append(f"Partner {label} total amount not balanced: difference {diff:.2f}")
        if abs(diff) >= warning_threshold:
            journal_logs.append(
                f"Journal Stage 2 warning for {label}: reconciliation difference {diff:.2f} exceeds threshold"
            )
        ac_partner = ac_frame.loc[ac_frame["partner_code"] == partner_code]
        gross_total = round(float(ac_partner["total_fare"].sum()), 2)
        rebuilt_total = round(float(ac_partner["net_amount"].sum() + ac_partner["commission"].sum()), 2)
        imbalance = round(gross_total - rebuilt_total, 2)
        if abs(imbalance) > 0.01:
            journal_logs.append(f"Journal Stage 1 imbalance for {label}: debit/credit difference {imbalance:.2f}")

    review_notes = [*row_logs, *agent_logs, *journal_logs]
    return ValidationResult(
        row_logs=row_logs,
        agent_logs=agent_logs,
        journal_logs=journal_logs,
        review_notes=review_notes,
    )
