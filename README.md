# Mining Market Intelligence Daily Report

Produces a daily mining market intelligence report from RSS, named-account company IR feeds, and SEC EDGAR filings. The pipeline ingests, classifies, scores, extracts company names, stores signals in SQLite, and writes daily and weekly report outputs.

## Run

```bash
py -m pip install -r requirements.txt
py run_daily.py
```

Output:

- `reports/YYYY-MM-DD.md`
- `data/intelligence.db`

Weekly brief:

```bash
py run_weekly.py
```

Output:

- `reports/weekly/insight_brief_YYYY-MM-DD.md`

## Automation

This repo now includes:

- [daily-report.yml](/S:/Projects/mining_market_intelligence/.github/workflows/daily-report.yml)
- [weekly-report.yml](/S:/Projects/mining_market_intelligence/.github/workflows/weekly-report.yml)
- [build_site.py](/S:/Projects/mining_market_intelligence/scripts/build_site.py)
- [send_report.py](/S:/Projects/mining_market_intelligence/scripts/send_report.py)

The default setup is:

- GitHub Actions runs the daily and weekly jobs
- GitHub Pages hosts the static report archive from `site/`
- Resend sends the generated report to configured email recipients

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

The workflows are scheduled at:

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

## Config

Edit [config.yaml](/S:/Projects/mining_market_intelligence/config.yaml):

- `user_agent`
- `secondary_whitelist`
- `paths.db`
- `paths.reports_dir`
- `paths.reports_weekly_dir`
- `paths.site_dir`
- `report.top_n`
- `report.min_score_targets`
- `watchlist`

Feed sources are loaded from [sources/rss_feeds.yaml](/S:/Projects/mining_market_intelligence/sources/rss_feeds.yaml) when present.
Named-account monitoring is loaded from [sources/company_watchlist.yaml](/S:/Projects/mining_market_intelligence/sources/company_watchlist.yaml).

## Layout

- [run_daily.py](/S:/Projects/mining_market_intelligence/run_daily.py): ingest RSS -> classify -> store -> write daily report
- [run_weekly.py](/S:/Projects/mining_market_intelligence/run_weekly.py): build the weekly insight brief
- [store/](/S:/Projects/mining_market_intelligence/store): SQLite schema and read/write
- [ingest/](/S:/Projects/mining_market_intelligence/ingest): RSS, SEC, and optional IR ingestion
- [classify/](/S:/Projects/mining_market_intelligence/classify): segment, category, pressure-point, and scoring logic
- [extract/](/S:/Projects/mining_market_intelligence/extract): company extraction
- [report/](/S:/Projects/mining_market_intelligence/report): markdown report generation
- [publish/](/S:/Projects/mining_market_intelligence/publish): HTML rendering and static archive generation
- [delivery/](/S:/Projects/mining_market_intelligence/delivery): Resend email delivery

Existing [fp360_mi_runner.py](/S:/Projects/mining_market_intelligence/fp360_mi_runner.py) and the Excel template remain unchanged.
