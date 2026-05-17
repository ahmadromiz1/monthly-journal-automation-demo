# Validation Rules

## Required Column Validation

The processor requires two sheets:

- `AC`
- `SR`

Each sheet is checked for the expected demo columns before processing starts.

## Row-Level Validation

The demo raises row log entries for:

- missing `partner_code`
- missing `ticket_number`
- `total_fare` not equal to `base_fare + tax`
- `net_amount` not equal to `total_fare - commission`

## Partner-Level Validation

AC net totals are compared with a derived SR net calculation:

`sales_amount - refund_amount - commission_amount`

If the partner totals differ, the processor writes a partner summary validation note.

## Journal Validation

If the partner-level difference exceeds a warning threshold, the processor writes a journal review note that simulates a debit/credit imbalance or reconciliation warning.

## Journal Notes Parsing

All generated log messages are collected into a note list and stored with the job record. The job detail page displays them as Journal Notes, and completed jobs with notes are labeled `Completed with Review Notes`.
