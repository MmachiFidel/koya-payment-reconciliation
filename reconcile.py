#!/usr/bin/env python3
"""Reconcile the latest attempt for each payment. Run: python reconcile.py."""
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path


def reconcile(lines):
    latest = {}
    for line in lines:
        try:
            event = json.loads(line, parse_float=Decimal)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict) or not event.get("txn_id"):
            continue

        txn_id = event["txn_id"]
        timestamp = datetime.fromisoformat(event["ts"].replace("Z", "+00:00"))
        if txn_id not in latest or timestamp > latest[txn_id][0]:
            latest[txn_id] = (timestamp, event)

    total = Decimal("0")
    count = 0
    for _, event in latest.values():
        if event["status"] == "success":
            total += Decimal(str(event["amount"]).replace(",", ""))
            count += 1
    return count, total


def main():
    directory = Path(__file__).resolve().parent
    with (directory / "payments.jsonl").open(encoding="utf-8") as payments:
        count, total = reconcile(payments)
    expected = int((directory / "expected.txt").read_text().strip())
    if count != expected:
        print(f"Check failed: counted {count} successful payments, expected {expected}.")
        print("Something in the data isn't being handled the way the README describes.")
    else:
        print(f"Check passed: {count} successful payments.")
        print(f"Your code: KOYA-{round(total)}")


if __name__ == "__main__":
    main()
