from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from statistics import mean
from typing import Iterable

from report.advisory import enrich_signal, is_sec_signal, move_rank


def ensure_enriched(signals: Iterable[dict]) -> list[dict]:
    items: list[dict] = []
    for signal in signals:
        if {"recommended_move", "buyer_function", "likely_role", "why_now"} <= set(signal):
            items.append(dict(signal))
        else:
            items.append(enrich_signal(signal))
    return items


def iso_window(end_date: str, days: int) -> tuple[str, str]:
    end = date.fromisoformat(end_date)
    start = end - timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()


def previous_iso_window(start_date: str, days: int) -> tuple[str, str]:
    start = date.fromisoformat(start_date)
    end = start - timedelta(days=1)
    begin = end - timedelta(days=days - 1)
    return begin.isoformat(), end.isoformat()


def durability_label(signal: dict, cohort: Iterable[dict]) -> str:
    items = ensure_enriched(cohort)
    company = (signal.get("company") or "").strip().lower()
    if not company:
        return "Single mention"

    company_items = [item for item in items if (item.get("company") or "").strip().lower() == company]
    same_category = [
        item
        for item in company_items
        if (item.get("category") or "").strip() == (signal.get("category") or "").strip()
    ]
    has_sec = any(is_sec_signal(item) for item in company_items)
    if has_sec and len(company_items) >= 2:
        return "SEC-backed and repeated"
    if has_sec:
        return "SEC-backed"
    if len(same_category) >= 2 or len(company_items) >= 3:
        return "Repeated in lookback"
    if len(company_items) == 2:
        return "Building"
    return "First mention"


def build_constraint_heatmap(signals: Iterable[dict], limit: int = 4) -> list[dict]:
    items = [item for item in ensure_enriched(signals) if not is_sec_signal(item)]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        key = (item.get("buyer_function") or item.get("pressure_point") or "SCM").strip()
        grouped[key].append(item)

    heatmap: list[dict] = []
    for function, group in grouped.items():
        avg_score = round(mean(item.get("total_score", 0) for item in group))
        companies = []
        seen = set()
        for item in sorted(group, key=lambda row: row.get("total_score", 0), reverse=True):
            company = (item.get("company") or "").strip()
            if not company or company in seen:
                continue
            seen.add(company)
            companies.append(company)
            if len(companies) == 3:
                break
        heat_level = "High" if avg_score >= 55 or len(group) >= 4 else "Medium" if avg_score >= 40 or len(group) >= 2 else "Low"
        heatmap.append(
            {
                "function": function,
                "heat": heat_level,
                "count": len(group),
                "avg_score": avg_score,
                "companies": companies,
            }
        )

    heatmap.sort(key=lambda item: (item["count"], item["avg_score"]), reverse=True)
    return heatmap[:limit]


def build_theme_momentum(current_signals: Iterable[dict], prior_signals: Iterable[dict], limit: int = 5) -> list[dict]:
    current = [item for item in ensure_enriched(current_signals) if not is_sec_signal(item)]
    prior = [item for item in ensure_enriched(prior_signals) if not is_sec_signal(item)]
    categories = {
        (item.get("category") or "").strip()
        for item in current + prior
        if (item.get("category") or "").strip()
    }

    momentum: list[dict] = []
    for category in categories:
        current_items = [item for item in current if (item.get("category") or "").strip() == category]
        prior_items = [item for item in prior if (item.get("category") or "").strip() == category]
        current_count = len(current_items)
        prior_count = len(prior_items)
        if current_count == 0 and prior_count == 0:
            continue
        delta = current_count - prior_count
        if delta > 0:
            status = "Accelerating"
        elif delta < 0:
            status = "Cooling"
        else:
            status = "Steady"
        top_companies = []
        seen = set()
        for item in sorted(current_items, key=lambda row: row.get("total_score", 0), reverse=True):
            company = (item.get("company") or "").strip()
            if not company or company in seen:
                continue
            seen.add(company)
            top_companies.append(company)
            if len(top_companies) == 3:
                break
        momentum.append(
            {
                "category": category,
                "status": status,
                "current_count": current_count,
                "prior_count": prior_count,
                "delta": delta,
                "avg_score": round(mean(item.get("total_score", 0) for item in current_items)) if current_items else 0,
                "companies": top_companies,
            }
        )

    momentum.sort(key=lambda item: (item["current_count"], item["avg_score"], item["delta"]), reverse=True)
    return momentum[:limit]


def top_active_accounts(account_briefs: Iterable[dict], limit: int = 3) -> list[dict]:
    items = [dict(brief) for brief in account_briefs if move_rank(brief.get("recommended_move", "")) >= 2]
    return items[:limit]


def top_monitor_accounts(account_briefs: Iterable[dict], limit: int = 3) -> list[dict]:
    items = [dict(brief) for brief in account_briefs if move_rank(brief.get("recommended_move", "")) <= 1]
    return items[:limit]


def build_disconfirming_evidence(
    theme_momentum: Iterable[dict],
    constraint_heatmap: Iterable[dict],
    active_accounts: Iterable[dict],
    monitor_accounts: Iterable[dict],
) -> list[str]:
    items: list[str] = []
    themes = list(theme_momentum)
    constraints = list(constraint_heatmap)
    active = list(active_accounts)
    monitor = list(monitor_accounts)

    if themes:
        top_theme = themes[0]
        companies = ", ".join(top_theme.get("companies", [])[:3]) or "the current lead names"
        if top_theme.get("status") == "Accelerating":
            items.append(
                f"The {top_theme['category']} thesis weakens if those names ({companies}) fail to produce follow-on milestones, staffing moves, contractor mobilization, or financing evidence in the next 30 days."
            )
        else:
            items.append(
                f"The {top_theme['category']} read changes if a different category overtakes it in signal count or average score over the next reporting window."
            )

    if constraints:
        top_constraint = constraints[0]
        items.append(
            f"The {top_constraint['function']} bottleneck call is overstated if new signals shift toward another function or if the current names stop showing execution strain and remain at one-off announcement stage."
        )

    if active:
        top_active = active[0]
        items.append(
            f"The push-on-{top_active['company']} recommendation should be downgraded if no corroborating signal appears and the trigger stays stuck at announcement rather than moving into delivery."
        )

    if monitor:
        top_monitor = monitor[0]
        items.append(
            f"The wait-on-{top_monitor['company']} stance should be revisited quickly if a new SEC filing, permitting decision, or operating update shifts it out of passive monitoring."
        )

    if not items:
        items.append("The current thesis is low-confidence; any cluster of repeated operating signals would materially change the read.")

    return items[:4]
