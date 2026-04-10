import unittest

from extract import extract_company


class ExtractCompanyTests(unittest.TestCase):
    def test_extracts_subject_company_from_action_headlines(self) -> None:
        self.assertEqual(
            extract_company("USA Rare Earth considers building French magnet plant", ""),
            "USA Rare Earth",
        )
        self.assertEqual(
            extract_company("United States Antimony restarts mining in Montana", ""),
            "United States Antimony",
        )
        self.assertEqual(
            extract_company("White House taps Highland Copper in local supply push", ""),
            "Highland Copper",
        )

    def test_filters_bad_geography_or_generic_entities(self) -> None:
        self.assertIsNone(extract_company("South Korea sets 20% renewable power goal for 2030", ""))
        self.assertIsNone(extract_company("Trump to reduce steel, aluminum tariff rates for derivative products", ""))


if __name__ == "__main__":
    unittest.main()
