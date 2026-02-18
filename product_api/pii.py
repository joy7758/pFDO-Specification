"""PII scanning utilities for phone/email/ID18 detection."""

import json
import re
from typing import Any

PHONE_RE = re.compile(r"(?<!\d)(1[3-9]\d{9})(?!\d)")
EMAIL_RE = re.compile(r"([a-zA-Z0-9_.+\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z0-9\-.]+)")
ID18_RE = re.compile(r"(?<!\d)(\d{17}[\dXx])(?!\d)")


def _record_to_text(record: dict[str, Any]) -> str:
    """Serialize a record into scanable text."""
    try:
        return json.dumps(record, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError):
        return str(record)


def scan_text(text: str) -> dict[str, list[str]]:
    """Scan text and return unique matches grouped by PII type."""
    return {
        "phone": sorted(set(PHONE_RE.findall(text))),
        "email": sorted(set(EMAIL_RE.findall(text))),
        "id18": sorted(set(ID18_RE.findall(text))),
    }


def scan_records(records: list[dict]) -> dict:
    """Scan a list of record dictionaries and return summary + per-record results."""
    per_record: list[dict[str, Any]] = []
    phones_found = 0
    emails_found = 0
    id18_found = 0

    for record in records:
        text = _record_to_text(record)
        hits = scan_text(text)
        has_pii = any(hits.values())

        phones_found += len(hits["phone"])
        emails_found += len(hits["email"])
        id18_found += len(hits["id18"])

        per_record.append(
            {
                "record_id": record.get("record_id"),
                "source_type": record.get("source_type"),
                "hits": hits,
                "has_pii": has_pii,
            }
        )

    summary = {
        "records": len(records),
        "records_with_pii": sum(1 for item in per_record if item["has_pii"]),
        "phones_found": phones_found,
        "emails_found": emails_found,
        "id18_found": id18_found,
    }
    return {"summary": summary, "per_record": per_record}
