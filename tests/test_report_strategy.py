import shutil
import unittest
from datetime import date
from pathlib import Path

from report.markdown import build_report
from report.weekly import build_weekly_brief
from scripts.send_report import _report_is_effectively_empty
from store.db import get_connection, init_db, insert_raw, insert_signal


class ReportStrategyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path("tests/.tmp_report_strategy")
        if self.root.exists():
            shutil.rmtree(self.root)
        self.root.mkdir(parents=True)
        self.db_path = str(self.root / "intelligence.db")
        init_db(self.db_path)

    def tearDown(self) -> None:
        if self.root.exists():
            shutil.rmtree(self.root)

    def _insert_signal(
        self,
        dedupe_key: str,
        detected: str,
        title: str,
        notes: str,
        company: str,
        category: str,
        pressure_point: str,
        source_name: str = "MINING.com",
        tags: str = "",
        link: str | None = None,
    ) -> None:
        conn = get_connection(self.db_path)
        raw_id = insert_raw(
            conn,
            dedupe_key=dedupe_key,
            source_url=link or f"https://example.com/{dedupe_key}",
            source_name=source_name,
            title=title,
            link=link or f"https://example.com/{dedupe_key}",
            published=detected,
            summary=notes,
            tags=tags,
            us_relevant="",
            ingested_at=detected,
        )
        insert_signal(
            conn,
            raw_id=raw_id,
            dedupe_key=dedupe_key,
            date_detected=detected,
            company=company,
            segment="Operator",
            signal_summary=title,
            category=category,
            source_name=source_name,
            impact=20,
            time_to_strain=18,
            fit=18,
            access=9,
            total_score=65,
            confidence="High",
            pressure_point=pressure_point,
            posture="Target accounts",
            tags=tags,
            notes=notes,
            link=link or f"https://example.com/{dedupe_key}",
        )
        conn.commit()
        conn.close()

    def test_daily_report_includes_strategic_sections_and_carryover_context(self) -> None:
        self._insert_signal(
            dedupe_key="uec-2026-04-10",
            detected="2026-04-10",
            title="Uranium Energy begins production at Texas ISR project",
            notes="Texas project begins production after restart work.",
            company="Uranium Energy",
            category="Change",
            pressure_point="Operations",
        )
        self._insert_signal(
            dedupe_key="uec-sec-2026-04-09",
            detected="2026-04-09",
            title="Uranium Energy 8-K cites Texas operations update",
            notes="U.S.-based miner files 8-K covering its Texas operations update.",
            company="Uranium Energy",
            category="Change",
            pressure_point="Operations",
            source_name="SEC EDGAR",
            tags="8-K,2.02",
        )
        self._insert_signal(
            dedupe_key="energyx-2026-04-08",
            detected="2026-04-08",
            title="EnergyX launches first U.S. direct lithium extraction plant in Texas",
            notes="The company launches its Texas plant and starts ramp planning.",
            company="EnergyX",
            category="Transition",
            pressure_point="Supply Chain",
        )
        self._insert_signal(
            dedupe_key="prior-2026-04-02",
            detected="2026-04-02",
            title="Example miner expands Nevada processing facility",
            notes="The U.S.-based company expands its Nevada processing facility.",
            company="Example Mining",
            category="Growth",
            pressure_point="Supply Chain",
        )

        content = build_report(self.db_path, "2026-04-10", str(self.root))

        self.assertIn("## Strategic readout", content)
        self.assertIn("## Constraint heatmap (Trailing 7 days)", content)
        self.assertIn("## What would change our mind", content)
        self.assertIn("## What remains live from the last 7 days", content)
        self.assertIn("## Park for now", content)
        self.assertIn("Durability:", content)

    def test_zero_signal_daily_with_carryover_is_not_effectively_empty(self) -> None:
        self._insert_signal(
            dedupe_key="energyx-2026-04-08",
            detected="2026-04-08",
            title="EnergyX launches first U.S. direct lithium extraction plant in Texas",
            notes="The company launches its Texas plant and starts ramp planning.",
            company="EnergyX",
            category="Transition",
            pressure_point="Supply Chain",
        )

        content = build_report(self.db_path, "2026-04-10", str(self.root))

        self.assertIn("**New signals today:** 0", content)
        self.assertIn("## What remains live from the last 7 days", content)
        self.assertFalse(_report_is_effectively_empty("daily", content))

    def test_weekly_brief_includes_thesis_momentum_and_wait_sections(self) -> None:
        self._insert_signal(
            dedupe_key="uec-2026-04-10",
            detected="2026-04-10",
            title="Uranium Energy begins production at Texas ISR project",
            notes="Texas project begins production after restart work.",
            company="Uranium Energy",
            category="Change",
            pressure_point="Operations",
        )
        self._insert_signal(
            dedupe_key="energyx-2026-04-09",
            detected="2026-04-09",
            title="EnergyX launches first U.S. direct lithium extraction plant in Texas",
            notes="The company launches its Texas plant and starts ramp planning.",
            company="EnergyX",
            category="Transition",
            pressure_point="Supply Chain",
        )
        self._insert_signal(
            dedupe_key="ioneer-2026-04-07",
            detected="2026-04-07",
            title="Ioneer faces Nevada permit appeal",
            notes="Nevada lithium project faces a permit appeal in the United States.",
            company="Ioneer",
            category="Risk",
            pressure_point="Supply Chain",
        )
        self._insert_signal(
            dedupe_key="prior-change-2026-04-03",
            detected="2026-04-03",
            title="Example miner starts Arizona mobilization",
            notes="Arizona project starts mobilization as the U.S.-based operator adds contractors.",
            company="Example Mining",
            category="Change",
            pressure_point="Operations",
        )

        content = build_weekly_brief(self.db_path, date(2026, 4, 10))

        self.assertIn("## Executive thesis", content)
        self.assertIn("## Theme momentum", content)
        self.assertIn("## Constraint heatmap", content)
        self.assertIn("## What would change our mind", content)
        self.assertIn("## Where to push now", content)
        self.assertIn("## Where to wait", content)
        self.assertIn("Durability:", content)


if __name__ == "__main__":
    unittest.main()
