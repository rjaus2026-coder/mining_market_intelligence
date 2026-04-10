import unittest

from scripts.send_report import _empty_daily_email_markdown, _report_is_effectively_empty


class SendReportTests(unittest.TestCase):
    def test_detects_empty_daily_report(self) -> None:
        content = "\n".join(
            [
                "**New signals today:** 0",
                "No SEC filing items surfaced today.",
                "None above threshold today; review top signals manually.",
                "No company briefs cleared the account-work threshold today.",
            ]
        )
        self.assertTrue(_report_is_effectively_empty("daily", content))

    def test_keeps_nonempty_daily_report(self) -> None:
        content = "\n".join(
            [
                "**New signals today:** 3",
                "- **Signal**",
            ]
        )
        self.assertFalse(_report_is_effectively_empty("daily", content))

    def test_builds_empty_daily_email_summary(self) -> None:
        content = _empty_daily_email_markdown("2026-04-10")
        self.assertIn("# Daily Mining Market Intelligence - 2026-04-10", content)
        self.assertIn("No actionable U.S.-relevant signals cleared the daily thresholds today.", content)
        self.assertIn("No outreach action is recommended from today's run.", content)


if __name__ == "__main__":
    unittest.main()
