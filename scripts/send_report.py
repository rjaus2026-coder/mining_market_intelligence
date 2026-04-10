from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from delivery.resend import send_from_env
from config_loader import load_config


def _report_path(kind: str, report_date: str, root: Path) -> Path:
    cfg = load_config(root)
    reports_dir = root / cfg["paths"]["reports_dir"]
    if kind == "weekly":
        weekly_dir = root / cfg["paths"].get("reports_weekly_dir", "reports/weekly")
        return weekly_dir / f"insight_brief_{report_date}.md"
    return reports_dir / f"{report_date}.md"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=["daily", "weekly"], required=True)
    parser.add_argument("--date", required=True, help="Report date in YYYY-MM-DD format")
    args = parser.parse_args()

    report_path = _report_path(args.kind, args.date, ROOT)
    if not report_path.exists():
        raise SystemExit(f"Report not found: {report_path}")

    sent = send_from_env(args.kind, report_path)
    print(f"Email {'sent' if sent else 'skipped'}: {report_path}")


if __name__ == "__main__":
    main()
