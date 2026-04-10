import unittest

from report.advisory import enrich_signal, normalize_posture


class AdvisoryTests(unittest.TestCase):
    def test_normalize_posture_uses_score_thresholds(self) -> None:
        self.assertEqual(normalize_posture("Target Account", 60), "Target accounts")
        self.assertEqual(normalize_posture("Proactive Outreach", 75), "Proactive outreach")
        self.assertEqual(normalize_posture("", 42), "Prepare POV")

    def test_enrich_signal_populates_lead_gen_fields(self) -> None:
        signal = {
            "segment": "Operator",
            "category": "Growth",
            "pressure_point": "Procurement",
            "impact": 20,
            "time_to_strain": 18,
            "fit": 18,
            "access": 9,
            "total_score": 65,
            "posture": "Target Account",
            "signal_summary": "Mine expansion moves into contractor mobilization",
        }

        enriched = enrich_signal(signal)

        self.assertEqual(enriched["posture"], "Prepare POV")
        self.assertEqual(enriched["buyer_function"], "Procurement")
        self.assertEqual(enriched["likely_role"], "CPO or Procurement Director")
        self.assertEqual(enriched["time_to_pain_horizon"], "Latent (post-commissioning or scale)")
        self.assertTrue(enriched["time_to_pain_reason"])
        self.assertIn("supplier continuity", enriched["language_to_use"].lower())
        self.assertNotIn("TBD", enriched["initial_scope"])
        self.assertEqual(enriched["recommended_move"], "Warm research")


if __name__ == "__main__":
    unittest.main()
