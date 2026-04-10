import unittest

from classify.us_relevance import filter_signals_by_us_gate


class FilterSignalsByUsGateTests(unittest.TestCase):
    def test_keeps_primary_mining_dot_com_rows_without_page_metadata(self) -> None:
        signals = [
            {
                "source_name": "MINING.com",
                "signal_summary": "Rare earth recycling plant to open in Nevada",
                "notes": "The company will build a plant in Nevada.",
                "company": "Cyclic Materials",
                "pressure_point": "Supply Chain",
                "total_score": 52,
                "posture": "Prepare POV",
                "link": "https://example.com/mining",
                "mining_com_source_page": "",
            }
        ]

        filtered = filter_signals_by_us_gate(signals, secondary_whitelist=["Mining Technology"])

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["source_tier"], "primary_global")
        self.assertEqual(filtered[0]["mining_com_source_page"], "Primary page unspecified")

    def test_keeps_explicitly_whitelisted_secondary_rows(self) -> None:
        signals = [
            {
                "source_name": "Mining Technology",
                "signal_summary": "US-based miner expands Nevada processing facility",
                "notes": "The US-based company is expanding its Nevada processing facility.",
                "company": "Example Mining",
                "pressure_point": "Operations",
                "total_score": 61,
                "posture": "Target accounts",
                "link": "https://example.com/secondary",
            }
        ]

        filtered = filter_signals_by_us_gate(signals, secondary_whitelist=["Mining Technology"])

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["source_tier"], "secondary_whitelisted")
        self.assertEqual(filtered[0]["execution_angle"], "Ops")
        self.assertEqual(filtered[0]["total_score"], 55)


if __name__ == "__main__":
    unittest.main()
