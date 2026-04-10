import unittest

from ingest.sec import _filing_focus, _normalize_items, _sec_dedupe_key, resolve_watchlist_company


class SecIngestTests(unittest.TestCase):
    def test_resolves_watchlist_company_by_ticker_or_name(self) -> None:
        ticker_data = {
            "0": {"cik_str": 1334933, "ticker": "UEC", "title": "Uranium Energy Corp"},
            "1": {"cik_str": 1320461, "ticker": "UAMY", "title": "United States Antimony Corp."},
        }

        resolved_by_ticker = resolve_watchlist_company({"name": "Uranium Energy", "ticker": "UEC"}, ticker_data)
        resolved_by_name = resolve_watchlist_company({"name": "United States Antimony"}, ticker_data)

        self.assertEqual(resolved_by_ticker["sec_cik"], "0001334933")
        self.assertEqual(resolved_by_name["sec_cik"], "0001320461")

    def test_extracts_useful_focus_from_8k_description(self) -> None:
        focus = _filing_focus("8-K", "Current report filing (Items 1.01, 2.03 and 9.01)")
        self.assertEqual(focus, "material agreement")

    def test_prefers_items_field_when_present(self) -> None:
        items = _normalize_items("5.02, 9.01")
        focus = _filing_focus("8-K", "Current report filing", items)
        self.assertEqual(items, ["5.02", "9.01"])
        self.assertEqual(focus, "leadership change")

    def test_sec_dedupe_key_is_stable_when_title_changes(self) -> None:
        first = _sec_dedupe_key("https://example.com/filing.htm", "0001-0001", "8-K")
        second = _sec_dedupe_key("https://example.com/filing.htm", "0001-0001", "8-K")
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
