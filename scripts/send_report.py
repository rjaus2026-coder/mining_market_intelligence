from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from delivery.resend import send_from_env, send_markdown_from_env
from config_loader import load_config


def _report_path(kind: str, report_date: str, root: Path) -> Path:
    cfg = load_config(root)
    reports_dir = root / cfg["paths"]["reports_dir"]
    if kind == "weekly":
        weekly_dir = root / cfg["paths"].get("reports_weekly_dir", "reports/weekly")
        return weekly_dir / f"insight_brief_{report_date}.md"
    return reports_dir / f"{report_date}.md"


def _report_is_effectively_empty(kind: str, content: str) -> bool:
    if kind == "daily":
        has_trailing_context = (
            "## What remains live from the last 7 days" in content
            and "No active priorities carried over from the last 7 days." not in content
        ) or (
            "## Park for now" in content
            and "No lower-urgency accounts are being carried this week." not in content
        )
        return (
            "**New signals today:** 0" in content
            and "No SEC filing items surfaced today." in content
            and "None above threshold today; review top signals manually." in content
            and "No company briefs cleared the account-work threshold today." in content
            and not has_trailing_context
        )
    return (
        "**Signals in period (US Relevance Gate applied):** 0" in content
        and "No SEC filing items surfaced this week." in content
        and "No company briefs cleared the account-work threshold this week." in content
    )


def _empty_daily_email_markdown(report_date: str) -> str:
    return "\n".join(
        [
            f"# Daily Mining Market Intelligence - {report_date}",
            "",
            "**Summary:** No actionable U.S.-relevant signals cleared the daily thresholds today.",
            "",
            "## What this means",
            "",
            "- No new daily signals reached the report's account-work threshold.",
            "- No SEC filing items surfaced today.",
            "- No company briefs cleared the account-work threshold today.",
            "",
            "## Recommended action",
            "",
            "- No outreach action is recommended from today's run.",
            "- Monitor the next daily report for follow-on signals or a change in posture.",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=["daily", "weekly"], required=True)
    parser.add_argument("--date", required=True, help="Report date in YYYY-MM-DD format")
    args = parser.parse_args()

    report_path = _report_path(args.kind, args.date, ROOT)
    if not report_path.exists():
        raise SystemExit(f"Report not found: {report_path}")

    content = report_path.read_text(encoding="utf-8")
    if _report_is_effectively_empty(args.kind, content):
        if args.kind == "daily":
            sent = send_markdown_from_env(
                kind="daily",
                report_name=args.date,
                title=args.date,
                markdown=_empty_daily_email_markdown(args.date),
                archive_path=f"daily/{report_path.stem}.html",
            )
            print(f"Email {'sent' if sent else 'skipped'}: empty daily summary for {report_path}")
            return
        print(f"Email skipped: report is empty: {report_path}")
        return

    sent = send_from_env(args.kind, report_path)
    print(f"Email {'sent' if sent else 'skipped'}: {report_path}")


if __name__ == "__main__":
    main()
