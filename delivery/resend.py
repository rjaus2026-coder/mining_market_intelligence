from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable
from urllib import request

from publish import render_markdown_email

RESEND_API_URL = "https://api.resend.com/emails"


def parse_recipients(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.replace(";", ",").split(",") if item.strip()]


def _subject(kind: str, report_name: str) -> str:
    prefix = "Weekly Insight Brief" if kind == "weekly" else "Daily Mining Market Intelligence"
    return f"{prefix} - {report_name}"


def send_report_email(
    *,
    kind: str,
    report_path: Path,
    recipients: Iterable[str],
    from_email: str,
    api_key: str,
    archive_url: str = "",
) -> bool:
    recipients = [item for item in recipients if item]
    if not recipients:
        return False

    markdown = report_path.read_text(encoding="utf-8")
    report_name = report_path.stem.replace("insight_brief_", "")
    title = report_name if kind == "weekly" else report_path.stem
    payload = {
        "from": from_email,
        "to": recipients,
        "subject": _subject(kind, report_name),
        "html": render_markdown_email(title=title, markdown=markdown, archive_url=archive_url),
        "text": markdown,
    }
    req = request.Request(
        RESEND_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=30) as response:
        return 200 <= response.status < 300


def send_from_env(kind: str, report_path: Path) -> bool:
    api_key = os.getenv("RESEND_API_KEY", "").strip()
    from_email = os.getenv("RESEND_FROM_EMAIL", "").strip()
    archive_url = os.getenv("SITE_BASE_URL", "").rstrip("/")
    recipients = parse_recipients(
        os.getenv("WEEKLY_REPORT_RECIPIENTS" if kind == "weekly" else "DAILY_REPORT_RECIPIENTS")
    )
    if not api_key or not from_email or not recipients:
        return False
    report_url = ""
    if archive_url:
        if kind == "weekly":
            report_url = f"{archive_url}/weekly/{report_path.stem}.html"
        else:
            report_url = f"{archive_url}/daily/{report_path.stem}.html"
    return send_report_email(
        kind=kind,
        report_path=report_path,
        recipients=recipients,
        from_email=from_email,
        api_key=api_key,
        archive_url=report_url,
    )
