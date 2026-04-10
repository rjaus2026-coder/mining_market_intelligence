import unittest

from report.advisory import build_sec_company_briefs, dedupe_sec_signals, enrich_signal, sec_focus, sec_materiality


class SecReportingTests(unittest.TestCase):
    def test_dedupes_repeated_sec_filing_variants(self) -> None:
        signals = [
            {
                "source_name": "SEC EDGAR",
                "company": "USA Rare Earth",
                "signal_summary": "USA Rare Earth: SEC 424B3 filing",
                "notes": "SEC 424B3 filed 2026-03-12. PROSPECTUS SUPPLEMENT.",
                "tags": "424B3",
                "link": "https://example.com/1",
                "watchlist_us_relevance_basis": "US asset",
            },
            {
                "source_name": "SEC EDGAR",
                "company": "USA Rare Earth",
                "signal_summary": "USA Rare Earth: SEC 424B3 filing",
                "notes": "SEC 424B3 filed 2026-03-12. PROSPECTUS SUPPLEMENT.",
                "tags": "424B3",
                "link": "https://example.com/2",
                "watchlist_us_relevance_basis": "US asset",
            },
        ]

        deduped = dedupe_sec_signals(signals, max_per_company=2)
        self.assertEqual(len(deduped), 1)

    def test_classifies_8k_items_above_routine_filings(self) -> None:
        material = enrich_signal(
            {
                "source_name": "SEC EDGAR",
                "company": "Atlas Lithium",
                "signal_summary": "Atlas Lithium: SEC 8-K filing",
                "notes": "SEC 8-K filed 2026-04-07. FORM 8-K - ITEM 2.02.",
                "tags": "8-K",
                "watchlist_us_relevance_basis": "US asset",
            }
        )
        routine = enrich_signal(
            {
                "source_name": "SEC EDGAR",
                "company": "USA Rare Earth",
                "signal_summary": "USA Rare Earth: SEC 10-K filing",
                "notes": "SEC 10-K filed 2026-03-30. FY2025 FORM 10-K.",
                "tags": "10-K",
                "watchlist_us_relevance_basis": "US asset",
            }
        )

        self.assertEqual(sec_materiality(material), "Medium")
        self.assertEqual(sec_materiality(routine), "Low")

    def test_extracts_sec_focus_and_groups_one_row_per_company(self) -> None:
        signals = [
            {
                "source_name": "SEC EDGAR",
                "company": "Uranium Energy",
                "signal_summary": "Uranium Energy: SEC 8-K - material agreement",
                "notes": "SEC 8-K filed 2026-04-08. Current report filing (Items 1.01 and 9.01).",
                "tags": "8-K,1.01,9.01",
                "link": "https://example.com/a",
                "watchlist_us_relevance_basis": "US asset",
            },
            {
                "source_name": "SEC EDGAR",
                "company": "Uranium Energy",
                "signal_summary": "Uranium Energy: SEC 10-K - annual filing",
                "notes": "SEC 10-K filed 2026-03-30. Annual report.",
                "tags": "10-K",
                "link": "https://example.com/b",
                "watchlist_us_relevance_basis": "US asset",
            },
        ]

        high = enrich_signal(signals[0])
        self.assertEqual(sec_focus(high), "material agreement")
        self.assertEqual(sec_materiality(high), "High")

        briefs = build_sec_company_briefs(signals, limit=8)
        self.assertEqual(len(briefs), 1)
        self.assertEqual(briefs[0]["company"], "Uranium Energy")
        self.assertEqual(briefs[0]["top_focus"], "material agreement")
        self.assertEqual(briefs[0]["materiality"], "High")

    def test_sec_focus_uses_backfilled_item_tags(self) -> None:
        signal = enrich_signal(
            {
                "source_name": "SEC EDGAR",
                "company": "USA Rare Earth",
                "signal_summary": "USA Rare Earth: SEC 8-K",
                "notes": "SEC 8-K filed 2026-04-09.",
                "tags": "8-K,5.02,9.01",
                "watchlist_us_relevance_basis": "US asset",
            }
        )
        self.assertEqual(sec_focus(signal), "leadership change")
        self.assertEqual(sec_materiality(signal), "High")


if __name__ == "__main__":
    unittest.main()
