# Report templates and example snippets

Templates are implemented in `report/markdown.py` (daily) and `report/weekly.py` (weekly). Below: template structure and placeholder-only examples.

---

## A) Daily template (structure)

```markdown
# Mining Market Intelligence – {report_date}

**New signals today:** {new_count}

**How to read** — Each signal line shows: **Segment** | **Category** | **Posture** | **Score** | Link.
- **Segment:** Type of player (Operator, EPCM, Contractor, OEM, Supplier, Startup/Platform).
- **Category:** Type of development (Growth, Entry, Change, Risk, Transition).
- **Posture:** Recommended BD stance: Monitor → Prepare POV → Target accounts → Proactive outreach (higher score = more urgency).
- **Score:** Heuristic 0–100 from impact, time-to-strain, fit, and access.

---

## Top signals by score

- **{signal_summary}** [{company}]
  - {segment} | {category} | {posture} | Score: {total_score} | [Link]({link})

  **Time-to-pain:**
  - Horizon: [Immediate (0–90 days) | Near-term (3–9 months) | Mid-term (9–18 months) | Latent (post-commissioning/scale) | TBD]
  - Reason: [1 short sentence, or TBD]

  **Buyer trigger mapping:**
  - Likely role: [e.g., COO | VP Supply Chain | Head of Procurement | Plant Manager | TBD]
  - Function: [Ops | SCM | Procurement | Planning | Logistics | TBD]
  - Trigger moment: [1 short sentence describing what causes urgency, or TBD]

  **FP360 first move:**
  - Entry angle: [1 short phrase, or TBD]
  - Language to use: [short phrase, or TBD]
  - Language to avoid: [short phrase, or TBD]
  - Initial scope (2–4 weeks): [short phrase, or TBD]

---

## Sell-ahead shortlist (Next 90–180 days)

- **{signal_summary}** [{company}] — {posture} | Score: {total_score} | [Link]({link})
(If none qualify: "None above threshold today; review top signals manually.")

---

## By segment

- **{segment}:** {cnt}

---

## Companies to target

- **{company}** – {segment} | {posture} (score {total_score}) – {signal_summary}... [Link]({link})
```

---

## B) Weekly template (structure)

```markdown
# FP360 Insight Brief (Weekly)

**Period:** {start_str} – {end_str}
**Signals in period:** {count}

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
- Likely buyer: [role/function or TBD]
- Best entry point: [1 short phrase or TBD]

---

## Sell-Ahead Watchlist (Next 90–180 Days)

- **Company:** [name or TBD]
  - Why now: [1 sentence]
  - Who feels it first: [role/function]
  - Recommended posture: [Monitor | Prepare POV | Target accounts | Proactive outreach]
  - Suggested FP360 first move: [1 short phrase]

---

*Factual, plain-spoken. Treat as signal inputs, not conclusions. Where evidence is incomplete, watch for follow-on announcements.*
```

---

## C) Example daily signal (placeholders only)

```markdown
- **Example Mining Co. announces expansion at Nevada site**
  - Operator | Change | Prepare POV | Score: 52 | [Link](https://example.com/signal)

  **Time-to-pain:**
  - Horizon: TBD
  - Reason: TBD

  **Buyer trigger mapping:**
  - Likely role: TBD
  - Function: TBD
  - Trigger moment: TBD

  **FP360 first move:**
  - Entry angle: TBD
  - Language to use: TBD
  - Language to avoid: TBD
  - Initial scope (2–4 weeks): TBD
```

---

## D) Example weekly watchlist entry (placeholders only)

```markdown
- **Company:** TBD
  - Why now: TBD
  - Who feels it first: TBD
  - Recommended posture: Prepare POV
  - Suggested FP360 first move: TBD
```
