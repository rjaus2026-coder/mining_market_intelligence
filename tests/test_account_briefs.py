import unittest

from report.advisory import build_account_briefs


class AccountBriefTests(unittest.TestCase):
    def test_groups_multiple_signals_per_company(self) -> None:
        signals = [
            {
                "company": "Uranium Energy",
                "signal_summary": "UEC begins production at Burke Hollow project",
                "notes": "Texas project begins production after restart work.",
                "segment": "Operator",
                "category": "Change",
                "pressure_point": "Operations",
                "link": "https://example.com/a",
            },
            {
                "company": "Uranium Energy",
                "signal_summary": "Uranium Energy adds second ISR operation",
                "notes": "The company restarts a second US ISR operation.",
                "segment": "Operator",
                "category": "Growth",
                "pressure_point": "Operations",
                "link": "https://example.com/b",
            },
        ]

        briefs = build_account_briefs(signals, limit=5, min_move_rank=1)

        self.assertEqual(len(briefs), 1)
        self.assertEqual(briefs[0]["company"], "Uranium Energy")
        self.assertEqual(briefs[0]["signal_count"], 2)
        self.assertIn(briefs[0]["recommended_move"], {"Warm research", "Prepare outreach", "Contact now"})


if __name__ == "__main__":
    unittest.main()
