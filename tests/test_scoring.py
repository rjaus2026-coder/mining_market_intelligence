import unittest

from classify.rules import score_dimensions


class ScoringTests(unittest.TestCase):
    def test_scores_actionable_mining_events_higher_than_macro_commentary(self) -> None:
        actionable = "Uranium Energy begins production at its Texas ISR project after restart work."
        macro = "Gold price climbs as traders weigh war and ceasefire comments."

        actionable_total = sum(score_dimensions(actionable))
        macro_total = sum(score_dimensions(macro))

        self.assertGreater(actionable_total, macro_total)
        self.assertGreaterEqual(actionable_total, 50)

    def test_penalizes_off_domain_energy_projects(self) -> None:
        off_domain = "Heelstone Renewable starts construction on 206MW US solar projects."
        total = sum(score_dimensions(off_domain))

        self.assertLess(total, 30)


if __name__ == "__main__":
    unittest.main()
