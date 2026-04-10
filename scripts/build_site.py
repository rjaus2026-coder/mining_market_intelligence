from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config_loader import load_config
from publish import build_site


def main() -> None:
    cfg = load_config(ROOT)
    reports_dir = ROOT / cfg["paths"]["reports_dir"]
    site_dir = ROOT / cfg["paths"].get("site_dir", "site")
    build_site(reports_dir, site_dir)
    print(f"Site written: {site_dir}")


if __name__ == "__main__":
    main()
