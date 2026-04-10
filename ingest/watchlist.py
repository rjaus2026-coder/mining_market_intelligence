from __future__ import annotations

from typing import Any

from ingest.rss import fetch_feed


def fetch_watchlist_press_releases(company_watchlist: list[dict[str, Any]], user_agent: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for entry in company_watchlist:
        feed_url = str(entry.get("press_release_feed") or "").strip()
        company_name = str(entry.get("name") or "").strip()
        if not feed_url or not company_name:
            continue
        try:
            feed_items = fetch_feed(feed_url, "Company IR", user_agent)
        except Exception:
            continue
        for item in feed_items:
            item = dict(item)
            item["source_name"] = "Company IR"
            item["source_url"] = feed_url
            item["watchlist_company"] = company_name
            item["watchlist_us_relevance_basis"] = str(entry.get("us_relevance_basis") or "").strip()
            if company_name.lower() not in (item.get("summary") or "").lower():
                item["summary"] = f"{company_name}. {(item.get('summary') or '').strip()}".strip()
            items.append(item)
    return items
