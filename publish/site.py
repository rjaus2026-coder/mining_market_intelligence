from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
from shutil import copy2

from .html import render_markdown_page


def _write_html(target: Path, title: str, markdown: str, subtitle: str = "") -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_markdown_page(title, markdown, subtitle=subtitle), encoding="utf-8")


def _report_title(path: Path) -> str:
    if path.parent.name == "weekly":
        return f"Steelpoint Operations Weekly Insight Brief - {path.stem.replace('insight_brief_', '')}"
    return f"Mining Market Intelligence - {path.stem}"


def _index_html(daily_pages: list[Path], weekly_pages: list[Path]) -> str:
    generated = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    def links(paths: list[Path], prefix: str) -> str:
        if not paths:
            return "<p>No reports published yet.</p>"
        items = []
        for path in paths:
            rel = f"{prefix}/{path.stem}.html"
            label = path.stem.replace("insight_brief_", "Weekly ").replace("_", " ")
            items.append(f'<li><a href="{rel}">{label}</a></li>')
        return "<ul>" + "".join(items) + "</ul>"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Steelpoint Operations Mining Market Intelligence</title>
  <style>
    body {{
      margin: 0;
      background: linear-gradient(180deg, #f4f0e7 0%, #ece4d6 100%);
      color: #1f1d18;
      font: 16px/1.6 Georgia, "Times New Roman", serif;
    }}
    main {{
      max-width: 980px;
      margin: 0 auto;
      padding: 36px 20px 64px;
    }}
    .hero {{
      background: rgba(255,255,255,0.72);
      border: 1px solid #d7ccba;
      border-radius: 20px;
      padding: 28px 30px;
      box-shadow: 0 14px 36px rgba(52, 42, 27, 0.08);
    }}
    h1, h2 {{ line-height: 1.2; }}
    section {{
      margin-top: 26px;
      background: rgba(255,255,255,0.64);
      border: 1px solid #d7ccba;
      border-radius: 18px;
      padding: 22px 24px;
    }}
    a {{ color: #8c4a21; }}
  </style>
</head>
<body>
  <main>
    <div class="hero">
      <h1>Steelpoint Operations Mining Market Intelligence</h1>
      <p>Static archive for the daily and weekly mining market intelligence reports.</p>
      <p>Generated: {generated}</p>
    </div>
    <section>
      <h2>Daily Reports</h2>
      {links(daily_pages, "daily")}
    </section>
    <section>
      <h2>Weekly Reports</h2>
      {links(weekly_pages, "weekly")}
    </section>
  </main>
</body>
</html>
"""


def build_site(reports_dir: Path, site_dir: Path) -> None:
    daily_source = reports_dir
    weekly_source = reports_dir / "weekly"
    daily_paths = sorted(daily_source.glob("????-??-??.md"), reverse=True)
    weekly_paths = sorted(weekly_source.glob("insight_brief_????-??-??.md"), reverse=True)

    (site_dir / "daily").mkdir(parents=True, exist_ok=True)
    (site_dir / "weekly").mkdir(parents=True, exist_ok=True)

    for path in daily_paths:
      markdown = path.read_text(encoding="utf-8")
      _write_html(site_dir / "daily" / f"{path.stem}.html", _report_title(path), markdown, subtitle=path.stem)
      copy2(path, site_dir / "daily" / path.name)

    for path in weekly_paths:
      markdown = path.read_text(encoding="utf-8")
      _write_html(site_dir / "weekly" / f"{path.stem}.html", _report_title(path), markdown, subtitle=path.stem.replace("insight_brief_", ""))
      copy2(path, site_dir / "weekly" / path.name)

    (site_dir / "index.html").write_text(_index_html(daily_paths, weekly_paths), encoding="utf-8")
