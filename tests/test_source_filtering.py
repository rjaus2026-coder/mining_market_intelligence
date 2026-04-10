import unittest

from classify.source_tier import is_mining_domain_signal
from classify.us_relevance import filter_signals_by_us_gate


class SourceFilteringTests(unittest.TestCase):
    def test_rejects_off_domain_secondary_energy_story(self) -> None:
        signals = [
            {
                "source_name": "NS Energy",
                "signal_summary": "Heelstone Renewable starts construction on 206MW US solar projects",
                "notes": "The developer starts solar construction in the United States.",
                "company": "Heelstone Renewable",
                "pressure_point": "Planning",
                "total_score": 72,
                "posture": "Proactive outreach",
                "link": "https://example.com/solar",
            }
        ]

        self.assertFalse(is_mining_domain_signal(signals[0]))
        self.assertEqual(filter_signals_by_us_gate(signals, secondary_whitelist=["NS Energy"]), [])

    def test_keeps_mining_secondary_story(self) -> None:
        signals = [
            {
                "source_name": "Mining Technology",
                "signal_summary": "Uranium Energy begins production at Texas ISR mine",
                "notes": "The United States project begins production after restart work.",
                "company": "Uranium Energy",
                "pressure_point": "Operations",
                "total_score": 61,
                "posture": "Target accounts",
                "link": "https://example.com/uranium",
            }
        ]

        filtered = filter_signals_by_us_gate(signals, secondary_whitelist=["Mining Technology"])
        self.assertEqual(len(filtered), 1)


if __name__ == "__main__":
    unittest.main()
