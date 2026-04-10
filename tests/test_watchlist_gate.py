import unittest

from classify.us_relevance import filter_signals_by_us_gate


class WatchlistGateTests(unittest.TestCase):
    def test_accepts_manual_watchlist_basis_for_sec_item(self) -> None:
        signals = [
            {
                "source_name": "SEC EDGAR",
                "signal_summary": "Uranium Energy: SEC 8-K filing",
                "notes": "SEC 8-K filed 2026-04-09.",
                "company": "Uranium Energy",
                "pressure_point": "Operations",
                "total_score": 50,
                "posture": "Prepare POV",
                "link": "https://www.sec.gov/example",
                "watchlist_us_relevance_basis": "US asset",
            }
        ]

        filtered = filter_signals_by_us_gate(signals, secondary_whitelist=["SEC EDGAR"])
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["us_relevance_basis"], "US asset")


if __name__ == "__main__":
    unittest.main()
