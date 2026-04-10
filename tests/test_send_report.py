import unittest

from scripts.send_report import _report_is_effectively_empty


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


if __name__ == "__main__":
    unittest.main()
