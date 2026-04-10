import shutil
import unittest
from pathlib import Path

from publish.html import render_markdown_email
from publish.site import build_site


class PublishTests(unittest.TestCase):
    def test_render_markdown_email_keeps_headings_and_links(self) -> None:
        html = render_markdown_email(
            title="Daily report",
            markdown="# Report\n\n- **Item** | [Link](https://example.com)",
            archive_url="https://reports.example.com/daily/2026-04-09.html",
        )
        self.assertIn("<h1>Daily report</h1>", html)
        self.assertIn('<a href="https://example.com">Link</a>', html)
        self.assertIn("Open report archive", html)

    def test_build_site_creates_index_and_report_pages(self) -> None:
        root = Path("tests/.tmp_publish")
        if root.exists():
            shutil.rmtree(root)
        try:
            reports = root / "reports"
            weekly = reports / "weekly"
            weekly.mkdir(parents=True)
            (reports / "2026-04-09.md").write_text("# Daily\n\n- Item", encoding="utf-8")
            (weekly / "insight_brief_2026-04-09.md").write_text("# Weekly\n\n- Item", encoding="utf-8")

            site = root / "site"
            build_site(reports, site)

            self.assertTrue((site / "index.html").exists())
            self.assertTrue((site / "daily" / "2026-04-09.html").exists())
            self.assertTrue((site / "weekly" / "insight_brief_2026-04-09.html").exists())
        finally:
            if root.exists():
                shutil.rmtree(root)


if __name__ == "__main__":
    unittest.main()
