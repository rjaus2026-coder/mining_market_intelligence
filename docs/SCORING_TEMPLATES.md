# Steelpoint Operations Opportunity Score – Report template reference

Templates are implemented in `report/markdown.py` (daily) and `report/weekly.py` (weekly). Below: full template markdown for both.

---

## 1) Daily report template (full)

```markdown
# Mining Market Intelligence – {report_date}

**New signals today:** {new_count}

**How to read** — Each signal line shows: **Segment** | **Category** | **Posture** | **Score** | Link.
- **Segment:** Type of player (Operator, EPCM, Contractor, OEM, Supplier, Startup/Platform).
- **Category:** Type of development (Growth, Entry, Change, Risk, Transition).
- **Posture:** Recommended BD stance: Monitor → Prepare POV → Target accounts → Proactive outreach (higher score = more urgency).
- **Score:** Heuristic 0–100 from impact, time-to-strain, fit, and access.

## Steelpoint Operations Opportunity Score (0–100)

**What it represents**
A heuristic measure of how likely a company-level change will create near- to mid-term business operations or supply chain pain where Steelpoint Operations services are relevant. Directional, not predictive.

**Scoring dimensions**
- Operational impact (0–30): effect on sourcing, procurement, inventory, planning, material flow
- Time-to-strain (0–30): how quickly operational/SCM pressure is likely to surface
- Steelpoint Operations service fit (0–25): alignment with Steelpoint Operations business ops + SCM offerings
- Engagement feasibility (0–15): practical likelihood to engage (visibility, buyer, timing)

**Score brackets and posture**
- 0–24: Informational signal → Monitor
- 25–39: Early indicator → Monitor / Prepare POV
- 40–54: Emerging risk → Prepare POV
- 55–69: High-likelihood future pain (3–12 months) → Target accounts
- 70–84: Near-term strain → Proactive outreach
- 85–100: Active/imminent breakdown → Immediate outreach / priority

**Scoring rules (governance)**
- Scores must decay if no follow-on signals appear (reduce confidence over time).
- A single uncorroborated item cannot jump from <30 to >70 without additional evidence.
- Repeated signals across different sources compound; they do not replace prior signals.
- New entrants with limited operating detail receive a higher Time-to-strain bias until execution clarity improves.
- Technical/geological items cap Operational impact at 10 unless downstream operational/SCM implications are explicit.
- If evidence is incomplete, keep score conservative and mark key unknowns as TBD.

---

## Top signals by score

- **{signal_summary}** [{company}]
  - {segment} | {category} | {posture} | Score: {total_score} | [Link]({link})
  - Score rationale: TBD   _(only for signals with Score >= 40)_

  **Time-to-pain:**
  - Horizon: TBD
  - Reason: TBD

  **Buyer trigger mapping:**
  - Likely role: TBD
  - Function: TBD
  - Trigger moment: TBD

  **Steelpoint Operations first move:**
  - Entry angle: TBD
  - Language to use: TBD
  - Language to avoid: TBD
  - Initial scope (2–4 weeks): TBD

---

## Sell-ahead shortlist (Next 90–180 days)

- **{signal_summary}** [{company}] — {posture} | Score: {total_score} | [Link]({link})
(If none: "None above threshold today; review top signals manually.")

---

## By segment

- **{segment}:** {cnt}

---

## Companies to target

- **{company}** – {segment} | {posture} (score {total_score}) – {signal_summary}... [Link]({link})
```

---

## 2) Weekly report template (full)

```markdown
# Steelpoint Operations Insight Brief (Weekly)

**Period:** {start_str} – {end_str}
**Signals in period:** {count}

## Steelpoint Operations Opportunity Score (0–100)

**Meaning**
A heuristic indicator of likely near- to mid-term business operations and supply chain strain where Steelpoint Operations services apply. Directional, not predictive.

**Score brackets**
- 0–24 Monitor
- 25–39 Monitor / Prepare POV
- 40–54 Prepare POV
- 55–69 Target accounts
- 70–84 Proactive outreach
- 85–100 Immediate outreach / priority

## Scoring rules (governance)

- Scores must decay if no follow-on signals appear.
- No single uncorroborated item jumps from <30 to >70 without additional evidence.
- Repeated signals across sources compound.
- New entrants with limited operating detail bias Time-to-strain upward until clarified.
- Technical/geological items cap Operational impact at 10 unless downstream ops/SCM impacts are explicit.
- Keep scores conservative when evidence is incomplete; mark unknowns TBD.

---

## Synthesized insights

### 1. {Category}

**What changed**
{what}

**Why it matters operationally**
{why}

**What typically fails next**
{fails}

**Commercial angle:**
- Likely buyer: TBD
- Best entry point: TBD

---

## Sell-Ahead Watchlist (Next 90–180 Days)

- **Company:** {name or TBD}
  - Why now: TBD
  - Who feels it first: TBD
  - Recommended posture: {posture}
  - Suggested Steelpoint Operations first move: TBD

---

*Factual, plain-spoken. Treat as signal inputs, not conclusions. Where evidence is incomplete, watch for follow-on announcements.*
```

