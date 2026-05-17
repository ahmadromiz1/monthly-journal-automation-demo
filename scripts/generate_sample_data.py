from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import random

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = PROJECT_ROOT / "sample_data" / "input" / "monthly_reconciliation_sample.xlsx"

PARTNERS = [
    ("ALPHA01", "Alpha Travel Services"),
    ("BETA02", "Beta Ticketing Group"),
    ("GAMMA03", "Gamma Air Solutions"),
    ("DELTA04", "Delta Journey Partner"),
    ("NUSA05", "Nusantara Demo Agency"),
]

ROUTES = ["CGK-DPS", "CGK-SIN", "SUB-CGK", "KNO-DPS", "DPS-BPN", "CGK-UPG"]


def random_money(rng: random.Random, minimum: float, maximum: float) -> float:
    return round(rng.uniform(minimum, maximum), 2)


def build_frames(seed: int = 20260517) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = random.Random(seed)
    start_date = date(2026, 4, 1)
    ac_rows: list[dict[str, object]] = []
    sr_rows: list[dict[str, object]] = []

    for index in range(50):
        partner_code, partner_name = PARTNERS[index % len(PARTNERS)]
        transaction_date = start_date + timedelta(days=rng.randint(0, 27))
        base_fare = random_money(rng, 75.0, 420.0)
        tax = random_money(rng, 8.0, 48.0)
        commission = random_money(rng, 4.0, 32.0)
        total_fare = round(base_fare + tax, 2)
        net_amount = round(total_fare - commission, 2)
        ticket_number = f"DEMO-{index + 1:04d}"

        if index in {5, 19, 38}:
            total_fare = round(total_fare + rng.choice([-7.5, 12.0, 18.25]), 2)
        if index in {11, 31}:
            net_amount = round(net_amount + rng.choice([-9.0, 11.0]), 2)
        if index == 22:
            partner_code = ""
        if index == 27:
            ticket_number = ""

        ac_rows.append(
            {
                "partner_code": partner_code,
                "partner_name": partner_name,
                "transaction_date": transaction_date,
                "ticket_number": ticket_number,
                "route": rng.choice(ROUTES),
                "base_fare": base_fare,
                "tax": tax,
                "commission": commission,
                "total_fare": total_fare,
                "net_amount": net_amount,
            }
        )

        refund_amount = random_money(rng, 0.0, 25.0) if index % 8 == 0 else 0.0
        sales_amount = round(total_fare + rng.choice([0.0, 0.0, 0.0, 2.5, -3.25]), 2)
        commission_amount = round(commission + rng.choice([0.0, 0.0, 1.5, -1.0]), 2)
        balance_amount = round(sales_amount - refund_amount - commission_amount, 2)

        if index in {8, 33, 41}:
            balance_amount = round(balance_amount + rng.choice([125.0, -140.0, 180.0]), 2)
        if index == 36:
            partner_code = ""
        if index == 44:
            ticket_number = ""

        sr_rows.append(
            {
                "partner_code": partner_code,
                "partner_name": partner_name,
                "statement_date": transaction_date + timedelta(days=rng.randint(0, 3)),
                "ticket_number": ticket_number,
                "sales_amount": sales_amount,
                "refund_amount": refund_amount,
                "commission_amount": commission_amount,
                "balance_amount": balance_amount,
            }
        )

    return pd.DataFrame(ac_rows), pd.DataFrame(sr_rows)


def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    ac_frame, sr_frame = build_frames()
    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        ac_frame.to_excel(writer, index=False, sheet_name="AC")
        sr_frame.to_excel(writer, index=False, sheet_name="SR")
    print(f"Generated sample workbook: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
