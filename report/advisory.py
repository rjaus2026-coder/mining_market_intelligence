from __future__ import annotations

from collections import Counter
import re
from typing import Iterable

from classify.rules import confidence, posture, score_dimensions
from extract import extract_company


_POSTURE_THRESHOLDS = (
    (70, "Proactive outreach"),
    (55, "Target accounts"),
    (40, "Prepare POV"),
)

_MOVE_RANK = {
    "Track only": 0,
    "Track target account": 1,
    "Warm research": 2,
    "Prepare outreach": 3,
    "Contact now": 4,
}

_SEC_MOVE_RANK = {
    "Low": 0,
    "Medium": 1,
    "High": 2,
}

_PRESSURE_POINT_TO_FUNCTION = {
    "Procurement": "Procurement",
    "Inventory": "SCM",
    "Supply Chain": "SCM",
    "Planning": "Planning",
    "Operations": "Ops",
    "Logistics": "Logistics",
}

_FUNCTION_TO_ROLE = {
    "Ops": "COO or VP Operations",
    "SCM": "VP Supply Chain or Supply Chain Director",
    "Procurement": "CPO or Procurement Director",
    "Planning": "VP Operations or Planning Director",
    "Logistics": "Logistics Director or Supply Chain Director",
}

_FUNCTION_TO_ENTRY_ANGLE = {
    "Ops": "Offer a startup and execution-readiness diagnostic.",
    "SCM": "Offer a material-flow and supplier-coordination diagnostic.",
    "Procurement": "Offer a rapid sourcing-risk and supplier-continuity review.",
    "Planning": "Offer a ramp-readiness and scenario-planning review.",
    "Logistics": "Offer an inbound reliability and logistics-risk review.",
}

_FUNCTION_TO_LANGUAGE_USE = {
    "Ops": "startup readiness, execution stability, and cross-functional handoffs",
    "SCM": "material flow, supplier coordination, and lead-time visibility",
    "Procurement": "supplier continuity, sourcing discipline, and purchase execution",
    "Planning": "capacity confidence, ramp assumptions, and planning visibility",
    "Logistics": "inbound reliability, route risk, and delivery visibility",
}

_FUNCTION_TO_LANGUAGE_AVOID = {
    "Ops": "generic transformation language or a broad system-overhaul pitch",
    "SCM": "abstract strategy language without a near-term operating problem",
    "Procurement": "cost-cutting language before supplier risk is understood",
    "Planning": "ERP-first language before the planning bottleneck is clear",
    "Logistics": "network-redesign language before immediate delivery risk is proven",
}

_FUNCTION_TO_INITIAL_SCOPE = {
    "Ops": "Assess startup/ramp handoffs, material availability, and the first execution bottlenecks.",
    "SCM": "Map critical material flows, supplier dependencies, and likely failure points.",
    "Procurement": "Review active sourcing, supplier risk, and short-list mitigation actions.",
    "Planning": "Pressure-test ramp assumptions, schedule dependencies, and near-term scenarios.",
    "Logistics": "Review inbound routes, carrier dependencies, and schedule-exposure points.",
}


def normalize_posture(posture: str, total_score: int | None = None) -> str:
    normalized = (posture or "").strip().lower()
    aliases = {
        "monitor": "Monitor",
        "prepare pov": "Prepare POV",
        "target account": "Target accounts",
        "target accounts": "Target accounts",
        "proactive outreach": "Proactive outreach",
        "immediate outreach / priority": "Proactive outreach",
    }
    if normalized in aliases:
        canonical = aliases[normalized]
        if total_score is None:
            return canonical

    if total_score is not None:
        for threshold, label in _POSTURE_THRESHOLDS:
            if total_score >= threshold:
                return label
    return aliases.get(normalized, "Monitor")


def move_rank(move: str) -> int:
    return _MOVE_RANK.get((move or "").strip(), -1)


def is_sec_signal(signal: dict) -> bool:
    return (signal.get("source_name") or "").strip() == "SEC EDGAR"


def sec_form(signal: dict) -> str:
    tags = str(signal.get("tags") or "").strip().upper()
    if tags:
        return tags.split(",")[0].strip()
    summary = str(signal.get("signal_summary") or "")
    notes = str(signal.get("notes") or "")
    for value in (summary, notes):
        for form in ("8-K", "10-Q", "10-K", "6-K", "20-F", "S-1", "S-3", "424B3"):
            if form in value.upper():
                return form
    return ""


def _sec_note_text(signal: dict) -> str:
    return f"{signal.get('signal_summary', '')} {signal.get('notes', '')}".upper()


def sec_item_codes(signal: dict) -> list[str]:
    if not is_sec_signal(signal):
        return []
    tags = str(signal.get("tags") or "").strip()
    tag_items = [part.strip() for part in tags.split(",")[1:] if re.fullmatch(r"\d+\.\d+", part.strip())]
    text = _sec_note_text(signal)
    text_items = re.findall(r"ITEMS?\s+(\d+\.\d+)", text) + re.findall(r"\bAND\s+(\d+\.\d+)", text)
    seen: set[str] = set()
    ordered: list[str] = []
    for item in tag_items + text_items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def sec_focus(signal: dict) -> str:
    items = sec_item_codes(signal)
    for item, label in (
        ("1.01", "material agreement"),
        ("1.02", "termination of agreement"),
        ("2.01", "acquisition or disposition"),
        ("2.02", "results or operating update"),
        ("2.03", "financing obligation"),
        ("2.05", "cost or impairment event"),
        ("5.01", "control change"),
        ("5.02", "leadership change"),
        ("5.03", "governance change"),
        ("8.01", "other material event"),
    ):
        if item in items:
            return label
    summary = (signal.get("signal_summary") or "").strip()
    if " - " in summary:
        return summary.split(" - ", 1)[1].strip()
    form = sec_form(signal)
    if form == "10-K":
        return "annual filing"
    if form == "10-Q":
        return "quarterly filing"
    if form == "424B3":
        return "prospectus supplement"
    return "filing"


def sec_materiality(signal: dict) -> str:
    if not is_sec_signal(signal):
        return ""
    form = sec_form(signal)
    items = set(sec_item_codes(signal))
    if form == "8-K":
        if items & {"1.01", "2.01", "2.03", "2.05", "5.01", "5.02", "8.01"}:
            return "High"
        if items & {"1.02", "2.02", "5.03", "7.01"}:
            return "Medium"
        return "Medium"
    if form in {"S-1", "S-3"}:
        return "Medium"
    if form in {"10-Q", "10-K", "20-F", "6-K"}:
        return "Low"
    if form == "424B3":
        return "Low"
    return "Low"


def sec_materiality_reason(signal: dict) -> str:
    materiality = sec_materiality(signal)
    form = sec_form(signal) or "filing"
    focus = sec_focus(signal)
    if materiality == "High":
        return f"{form} points to a likely material event around {focus}. Review the filing before outreach."
    if materiality == "Medium":
        return f"{form} may add usable context around {focus}. Review before using it in outreach."
    return f"{form} is routine monitoring unless it reinforces a stronger operating signal."


def _normalize_company(company: str) -> str:
    value = (company or "").strip()
    if value in {"Environmentalists", "South Korea", "The Journal", "Trump", "White House"}:
        return ""
    return value


def _function_for_signal(signal: dict) -> str:
    execution_angle = (signal.get("execution_angle") or "").strip()
    if execution_angle:
        return execution_angle
    pressure_point = (signal.get("pressure_point") or "").strip()
    if pressure_point in _PRESSURE_POINT_TO_FUNCTION:
        return _PRESSURE_POINT_TO_FUNCTION[pressure_point]
    category = (signal.get("category") or "").strip()
    if category in {"Growth", "Change"}:
        return "Ops"
    return "SCM"


def _role_for_signal(signal: dict, function: str) -> str:
    segment = (signal.get("segment") or "").strip()
    if segment in {"EPCM", "Contractor"} and function in {"Ops", "Planning"}:
        return "Project Director or Operations Director"
    if segment in {"OEM", "Supplier"} and function in {"SCM", "Procurement", "Logistics"}:
        return "GM, Supply Chain Director, or Procurement Lead"
    if segment == "Startup/Platform":
        return "Founder, COO, or Head of Operations"
    return _FUNCTION_TO_ROLE.get(function, "VP Operations or Supply Chain lead")


def _horizon_for_signal(signal: dict) -> str:
    score = int(signal.get("time_to_strain") or 0)
    if score >= 20:
        return "Immediate (0-90 days)"
    if score >= 14:
        return "Near-term (3-9 months)"
    if score >= 8:
        return "Mid-term (9-18 months)"
    return "Latent (post-commissioning or scale)"


def _time_reason(signal: dict, function: str, horizon: str) -> str:
    category = (signal.get("category") or "").strip()
    if function == "Ops":
        base = "Startup, ramp, or operating-model changes usually surface execution gaps quickly once work starts moving."
    elif function == "Procurement":
        base = "Supplier decisions and contract handoffs tend to create sourcing pressure as soon as scope hardens."
    elif function == "Planning":
        base = "Capacity and schedule assumptions usually get stress-tested before steady-state operations."
    elif function == "Logistics":
        base = "Inbound logistics pressure appears once delivery dates, routes, and carrier commitments become real."
    else:
        base = "Supplier coordination and material-flow problems usually show up before the operation reaches a stable rhythm."

    if category == "Risk":
        return "The signal already points to disruption, so buyer urgency can accelerate faster than the base score suggests."
    if category == "Entry":
        return "New entrants often expose operating and supplier gaps once they move from announcement into build-out."
    if horizon.startswith("Latent"):
        return "This looks earlier in the cycle, so the strain is more likely to build during scale-up than immediately."
    return base


def _trigger_moment(signal: dict, function: str) -> str:
    category = (signal.get("category") or "").strip()
    if category == "Growth":
        return "Move when expansion turns into ramp planning, contractor mobilization, or supplier onboarding."
    if category == "Entry":
        return "Move when the company starts staffing operations or building its local supplier base."
    if category == "Change":
        return "Move when ownership, leadership, or operating-model changes begin affecting execution cadence."
    if category == "Risk":
        return "Move when delays, shortages, or replanning force reactive workarounds."
    if function == "Procurement":
        return "Move when sourcing decisions, tenders, or supplier awards start compressing timelines."
    return "Move when execution responsibility shifts from announcement to delivery."


def _score_rationale(signal: dict) -> str:
    parts = [
        ("impact", int(signal.get("impact") or 0), "meaningful operational impact"),
        ("time_to_strain", int(signal.get("time_to_strain") or 0), "a relatively near-term pain window"),
        ("fit", int(signal.get("fit") or 0), "clear fit with FP360's operating lane"),
        ("access", int(signal.get("access") or 0), "a plausible path to stakeholder access"),
    ]
    strongest = [phrase for _, _, phrase in sorted(parts, key=lambda item: item[1], reverse=True)[:2]]
    if not strongest:
        return "Low-confidence signal; monitor for follow-on operating detail."
    if len(strongest) == 1:
        return f"The score is driven mainly by {strongest[0]}."
    return f"The score is driven mainly by {strongest[0]} and {strongest[1]}."


def enrich_signal(signal: dict) -> dict:
    enriched = dict(signal)
    text = f"{enriched.get('signal_summary', '')} {enriched.get('notes', '')}".strip()
    impact, time_to_strain, fit, access = score_dimensions(text)
    total_score = impact + time_to_strain + fit + access

    enriched["impact"] = impact
    enriched["time_to_strain"] = time_to_strain
    enriched["fit"] = fit
    enriched["access"] = access
    enriched["total_score"] = total_score
    enriched["confidence"] = confidence(total_score)
    enriched["posture"] = normalize_posture(posture(total_score), total_score)
    company = _normalize_company(enriched.get("company", ""))
    if not company:
        company = _normalize_company(enriched.get("watchlist_company", ""))
    if not company:
        company = _normalize_company(extract_company(enriched.get("signal_summary", ""), enriched.get("notes", "")))
    enriched["company"] = company

    function = _function_for_signal(enriched)
    role = _role_for_signal(enriched, function)
    horizon = _horizon_for_signal(enriched)
    entry_angle = _FUNCTION_TO_ENTRY_ANGLE.get(function, _FUNCTION_TO_ENTRY_ANGLE["SCM"])

    enriched["buyer_function"] = function
    enriched["likely_role"] = role
    enriched["time_to_pain_horizon"] = horizon
    enriched["time_to_pain_reason"] = _time_reason(enriched, function, horizon)
    enriched["trigger_moment"] = _trigger_moment(enriched, function)
    enriched["entry_angle"] = entry_angle
    enriched["language_to_use"] = _FUNCTION_TO_LANGUAGE_USE.get(function, _FUNCTION_TO_LANGUAGE_USE["SCM"])
    enriched["language_to_avoid"] = _FUNCTION_TO_LANGUAGE_AVOID.get(function, _FUNCTION_TO_LANGUAGE_AVOID["SCM"])
    enriched["initial_scope"] = _FUNCTION_TO_INITIAL_SCOPE.get(function, _FUNCTION_TO_INITIAL_SCOPE["SCM"])
    enriched["score_rationale"] = _score_rationale(enriched)
    enriched["who_feels_it_first"] = role
    enriched["why_now"] = f"{enriched.get('category', 'This')} signal with {function} pressure; best addressed before reactive workarounds set in."
    enriched["suggested_first_move"] = entry_angle
    if total_score >= 70:
        enriched["recommended_move"] = "Contact now"
    elif total_score >= 55:
        enriched["recommended_move"] = "Prepare outreach"
    elif total_score >= 40:
        enriched["recommended_move"] = "Warm research"
    elif enriched.get("company") and total_score >= 28:
        enriched["recommended_move"] = "Track target account"
    else:
        enriched["recommended_move"] = "Track only"
    if is_sec_signal(enriched):
        enriched["sec_form"] = sec_form(enriched)
        enriched["sec_focus"] = sec_focus(enriched)
        enriched["sec_materiality"] = sec_materiality(enriched)
        enriched["sec_materiality_reason"] = sec_materiality_reason(enriched)
    return enriched


def summarize_commercial_angle(signals: Iterable[dict]) -> dict[str, str]:
    items = [enrich_signal(signal) for signal in signals]
    if not items:
        return {
            "likely_buyer": "VP Operations or Supply Chain lead",
            "best_entry_point": "Lead with the operating consequence, then offer a short diagnostic.",
        }

    function = Counter(item["buyer_function"] for item in items).most_common(1)[0][0]
    role = Counter(item["likely_role"] for item in items).most_common(1)[0][0]
    top_signal = sorted(items, key=lambda item: item.get("total_score", 0), reverse=True)[0]
    return {
        "likely_buyer": role,
        "best_entry_point": f"Lead with {function} risk visible in '{top_signal.get('signal_summary', '')[:90]}', then offer a short diagnostic.",
    }


def build_account_briefs(signals: Iterable[dict], limit: int = 10, min_move_rank: int = 1) -> list[dict]:
    grouped: dict[str, list[dict]] = {}
    for signal in signals:
        item = enrich_signal(signal)
        company = (item.get("company") or "").strip()
        if not company:
            continue
        if move_rank(item.get("recommended_move", "")) < min_move_rank:
            continue
        key = company.lower()
        grouped.setdefault(key, []).append(item)

    briefs = []
    for items in grouped.values():
        items.sort(key=lambda item: (move_rank(item.get("recommended_move", "")), item.get("total_score", 0), item.get("time_to_strain", 0)), reverse=True)
        top = items[0]
        likely_role = Counter(item.get("likely_role", "") for item in items if item.get("likely_role")).most_common(1)[0][0]
        buyer_function = Counter(item.get("buyer_function", "") for item in items if item.get("buyer_function")).most_common(1)[0][0]
        best_move = max((item.get("recommended_move", "Track only") for item in items), key=move_rank)
        best_posture = max((item.get("posture", "Monitor") for item in items), key=lambda value: ["Monitor", "Prepare POV", "Target accounts", "Proactive outreach"].index(value if value in ["Monitor", "Prepare POV", "Target accounts", "Proactive outreach"] else "Monitor"))
        recent_signal = top.get("signal_summary", "")
        briefs.append(
            {
                "company": top["company"],
                "recommended_move": best_move,
                "posture": best_posture,
                "score": top.get("total_score", 0),
                "signal_count": len(items),
                "latest_signal": recent_signal,
                "likely_role": likely_role,
                "buyer_function": buyer_function,
                "why_now": top.get("why_now", ""),
                "entry_angle": top.get("entry_angle", ""),
                "trigger_moment": top.get("trigger_moment", ""),
                "initial_scope": top.get("initial_scope", ""),
                "source_note": top.get("us_relevance_basis", ""),
                "link": top.get("link", ""),
            }
        )

    briefs.sort(key=lambda item: (move_rank(item["recommended_move"]), item["score"], item["signal_count"]), reverse=True)
    return briefs[:limit]


def dedupe_sec_signals(signals: Iterable[dict], max_per_company: int = 2) -> list[dict]:
    grouped: dict[str, list[dict]] = {}
    for signal in signals:
        item = enrich_signal(signal)
        if not is_sec_signal(item):
            continue
        company = (item.get("company") or item.get("watchlist_company") or "").strip()
        if not company:
            continue
        grouped.setdefault(company.lower(), []).append(item)

    selected: list[dict] = []
    for items in grouped.values():
        deduped: dict[tuple[str, str], dict] = {}
        for item in items:
            key = (sec_form(item), (item.get("notes") or "").strip().upper())
            existing = deduped.get(key)
            current_rank = (_SEC_MOVE_RANK.get(sec_materiality(item), 0), item.get("total_score", 0))
            if existing is None:
                deduped[key] = item
                continue
            existing_rank = (_SEC_MOVE_RANK.get(sec_materiality(existing), 0), existing.get("total_score", 0))
            if current_rank > existing_rank:
                deduped[key] = item
        company_items = sorted(
            deduped.values(),
            key=lambda item: (_SEC_MOVE_RANK.get(sec_materiality(item), 0), item.get("total_score", 0)),
            reverse=True,
        )
        selected.extend(company_items[:max_per_company])

    selected.sort(
        key=lambda item: (
            _SEC_MOVE_RANK.get(sec_materiality(item), 0),
            item.get("total_score", 0),
            item.get("company", ""),
        ),
        reverse=True,
    )
    return selected


def build_sec_company_briefs(signals: Iterable[dict], limit: int = 8) -> list[dict]:
    grouped: dict[str, list[dict]] = {}
    for signal in signals:
        item = enrich_signal(signal)
        if not is_sec_signal(item):
            continue
        company = (item.get("company") or item.get("watchlist_company") or "").strip()
        if not company:
            continue
        grouped.setdefault(company.lower(), []).append(item)

    briefs: list[dict] = []
    for items in grouped.values():
        unique_items: list[dict] = []
        seen_links: set[str] = set()
        for item in items:
            link = (item.get("link") or "").strip()
            if link and link in seen_links:
                continue
            if link:
                seen_links.add(link)
            unique_items.append(item)
        items = unique_items
        items.sort(
            key=lambda item: (
                _SEC_MOVE_RANK.get(sec_materiality(item), 0),
                item.get("total_score", 0),
                item.get("signal_summary", ""),
            ),
            reverse=True,
        )
        top = items[0]
        forms = Counter(sec_form(item) or "filing" for item in items)
        briefs.append(
            {
                "company": top.get("company") or top.get("watchlist_company") or "",
                "filing_count": len(items),
                "top_form": sec_form(top) or "SEC filing",
                "top_focus": sec_focus(top),
                "materiality": sec_materiality(top) or "Low",
                "recommended_move": top.get("recommended_move", "Track only"),
                "why_it_matters": sec_materiality_reason(top),
                "link": top.get("link", ""),
                "recent_forms": ", ".join(
                    f"{form} x{count}" if count > 1 else form
                    for form, count in forms.most_common(3)
                ),
            }
        )

    briefs.sort(
        key=lambda item: (
            _SEC_MOVE_RANK.get(item["materiality"], 0),
            move_rank(item["recommended_move"]),
            item["filing_count"],
            item["company"],
        ),
        reverse=True,
    )
    return briefs[:limit]
