#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:
    yaml = None

from simple_yaml import safe_load as simple_yaml_safe_load


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    if yaml is not None:
        data = yaml.safe_load(text) or {}
    else:
        data = simple_yaml_safe_load(text) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def _merge_missing(base: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in fallback.items():
        if key not in merged:
            merged[key] = value
            continue
        if isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _merge_missing(merged[key], value)
    return merged


def _normalize_split_feeds(data: dict[str, Any]) -> list[dict[str, str]]:
    feeds = data.get("feeds") or []
    normalized = []
    for feed in feeds:
        if not isinstance(feed, dict):
            continue
        url = str(feed.get("url") or "").strip()
        if not url:
            continue
        name = str(feed.get("name") or url).strip()
        normalized.append({"name": name, "url": url})
    return normalized


def _normalize_company_watchlist(data: dict[str, Any]) -> list[dict[str, Any]]:
    companies = data.get("companies") or []
    normalized = []
    for company in companies:
        if not isinstance(company, dict):
            continue
        name = str(company.get("name") or "").strip()
        if not name:
            continue
        item = dict(company)
        item["name"] = name
        if "ticker" in item and item["ticker"] is not None:
            item["ticker"] = str(item["ticker"]).strip().upper()
        if "sec_cik" in item and item["sec_cik"] is not None:
            item["sec_cik"] = str(item["sec_cik"]).strip()
        if "press_release_feed" in item and item["press_release_feed"] is not None:
            item["press_release_feed"] = str(item["press_release_feed"]).strip()
        if "us_relevance_basis" in item and item["us_relevance_basis"] is not None:
            item["us_relevance_basis"] = str(item["us_relevance_basis"]).strip()
        forms = item.get("edgar_forms")
        if forms:
            item["edgar_forms"] = [str(form).strip().upper() for form in forms if str(form).strip()]
        normalized.append(item)
    return normalized


def load_config(root: Path) -> dict[str, Any]:
    cfg = _load_yaml(root / "config.yaml")

    split_feeds = _normalize_split_feeds(_load_yaml(root / "sources" / "rss_feeds.yaml"))
    if split_feeds:
        cfg["rss_feeds"] = split_feeds

    company_watchlist = _normalize_company_watchlist(_load_yaml(root / "sources" / "company_watchlist.yaml"))
    if company_watchlist:
        cfg["company_watchlist"] = company_watchlist

    return cfg
