# Mining Market Intelligence Daily Report

This project generates a daily and weekly mining market intelligence report from RSS feeds, company press releases, and SEC EDGAR filings.

The output is not a generic news roundup. It is a decision-support report designed to answer a more commercial question:

> Which mining companies are showing signals of upcoming operational or supply chain strain, and which of those accounts are worth acting on now?

If you are viewing this repository as part of my GitHub portfolio, the main thing to understand is that this project sits at the intersection of data ingestion, classification, scoring, reporting, and automation. It turns unstructured external information into a structured, repeatable business-intelligence product.

## What The Report Is

The report is built for a business development / operations intelligence use case.

Instead of summarizing commodity prices or broad macro news, it watches for company-level events such as:

- project starts and production ramp-ups
- expansions, restarts, and asset acquisitions
- leadership changes and material SEC disclosures
- new US mining or processing capacity
- permitting, execution, and transition-related signals

Those events are then translated into a practical commercial view:

- how important the signal is
- how soon pain or execution strain is likely to surface
- whether the signal is more relevant to operations or supply chain
- which companies should be monitored, researched, or contacted

In other words, this repo is closer to a signal triage engine than a traditional market research document.

## What A Reader Sees In The Report

The daily report includes:

- top signals ranked by opportunity score
- an SEC filing monitor for watched companies
- a sell-ahead shortlist for the next 90 to 180 days
- account-level recommendations on who to work today
- segment breakdowns and extracted target companies

The weekly brief rolls those signals up into a higher-level view:

- synthesized themes by category
- operational implications of those themes
- likely buyer roles and entry points
- a watchlist of accounts worth pursuing over the next few months

Representative outputs:

- Daily report: [`reports/2026-04-10.md`](reports/2026-04-10.md)
- Daily report: [`reports/2026-04-11.md`](reports/2026-04-11.md)
- Weekly brief: [`reports/weekly/insight_brief_2026-04-10.md`](reports/weekly/insight_brief_2026-04-10.md)

## How The Scoring Works

Each signal gets a heuristic score from 0 to 100 based on four dimensions:

- operational impact
- time-to-strain
- service fit
- engagement feasibility

That score is then converted into a recommended posture:

- `Monitor`
- `Prepare POV`
- `Target accounts`
- `Proactive outreach`

The intent is not to claim perfect prediction. The point is to rank noisy external signals into a usable order of commercial relevance.

## What This Project Demonstrates

From an engineering perspective, this repository showcases:

- ingestion of multiple external source types
- normalization and deduplication of noisy source data
- rule-based classification for segment, category, and pressure point
- company/entity extraction from semi-structured text
- SQLite-backed persistence for repeatable reporting
- markdown and HTML publishing for human-readable outputs
- automation with GitHub Actions, GitHub Pages, and email delivery

It is a practical example of building a vertical intelligence workflow end to end, not just a one-off script.

## Pipeline Overview

1. Ingest RSS feeds, named-account press releases, and SEC filings.
2. Filter for US-relevant companies and developments.
3. Classify each item by segment, category, and likely pressure point.
4. Score each signal using heuristic business rules.
5. Extract company names and store raw items plus scored signals in SQLite.
6. Generate daily and weekly markdown reports.
7. Publish a static archive and optionally email reports to recipients.

## Run

```bash
py -m pip install -r requirements.txt
py run_daily.py
```

Outputs:

- `reports/YYYY-MM-DD.md`
- `data/intelligence.db`

Weekly brief:

```bash
py run_weekly.py
```

Output:

- `reports/weekly/insight_brief_YYYY-MM-DD.md`

## Automation

This repo includes:

- `.github/workflows/daily-report.yml`
- `.github/workflows/weekly-report.yml`
- `scripts/build_site.py`
- `scripts/send_report.py`

Default setup:

- GitHub Actions runs the daily and weekly jobs
- GitHub Pages hosts the static report archive from `site/`
- Resend emails the generated report to configured recipients

### GitHub Setup

1. Push the repo to GitHub.
2. Enable GitHub Pages with GitHub Actions as the source.
3. Add these repository secrets:
   - `RESEND_API_KEY`
   - `RESEND_FROM_EMAIL`
   - `DAILY_REPORT_RECIPIENTS`
   - `WEEKLY_REPORT_RECIPIENTS`
4. Add this repository variable:
   - `SITE_BASE_URL`

`DAILY_REPORT_RECIPIENTS` and `WEEKLY_REPORT_RECIPIENTS` should be comma- or semicolon-separated lists.

Workflow schedule:

- Daily: `13:15 UTC` on weekdays
- Weekly: `13:30 UTC` on Mondays

These are intended to land around early morning Pacific time.

### Manual Publish Commands

```bash
py scripts/build_site.py
py scripts/send_report.py --kind daily --date 2026-04-09
py scripts/send_report.py --kind weekly --date 2026-04-09
```

If the Resend secrets are not present, the send step exits cleanly with `Email skipped`.

## Configuration

Edit `config.yaml` to control:

- `user_agent`
- `secondary_whitelist`
- `paths.db`
- `paths.reports_dir`
- `paths.reports_weekly_dir`
- `paths.site_dir`
- `report.top_n`
- `report.min_score_targets`
- `watchlist`

Source inputs:

- RSS feeds are loaded from `sources/rss_feeds.yaml`
- named-account monitoring is loaded from `sources/company_watchlist.yaml`

## Repository Layout

- `run_daily.py`: ingest, classify, score, store, and write the daily report
- `run_weekly.py`: build the weekly insight brief
- `ingest/`: RSS, SEC, and watchlist press-release ingestion
- `classify/`: segmentation, categorization, relevance, and scoring logic
- `extract/`: company extraction logic
- `store/`: SQLite schema and persistence
- `report/`: markdown report generation
- `publish/`: HTML rendering and static archive generation
- `delivery/`: Resend email delivery
- `docs/`: report templates, scoring references, and prompt materials

## Notes

- The scoring system is heuristic and intentionally conservative.
- Reports are meant to support commercial judgment, not replace it.
- Example outputs are included in the repo so the reporting format can be reviewed without running the pipeline first.
