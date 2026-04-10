from __future__ import annotations

import hashlib
import json
import re
from datetime import date, timedelta
from typing import Any, Iterable, Optional
from urllib import request

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
DEFAULT_EDGAR_FORMS = ["8-K", "10-Q", "10-K", "6-K", "20-F", "S-1", "S-3", "424B3"]

_ENTITY_SUFFIXES = re.compile(r"\b(inc|corp|corporation|ltd|limited|plc|holdings?)\b\.?", re.I)
_ITEM_PATTERN = re.compile(r"ITEMS?\s+((?:\d+\.\d+(?:,\s*)?)+(?:\s+AND\s+\d+\.\d+)?)", re.I)

_EIGHT_K_ITEM_LABELS = {
    "1.01": "material agreement",
    "1.02": "termination of agreement",
    "2.01": "acquisition or disposition",
    "2.02": "results or operating update",
    "2.03": "financing obligation",
    "2.05": "cost or impairment event",
    "5.01": "control change",
    "5.02": "leadership change",
    "5.03": "governance change",
    "8.01": "other material event",
}


def _fetch_json(url: str, user_agent: str) -> dict[str, Any]:
    req = request.Request(url, headers={"User-Agent": user_agent, "Accept": "application/json"})
    with request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _normalize_company_key(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", " ", value or "").strip().lower()
    cleaned = _ENTITY_SUFFIXES.sub("", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def _build_ticker_lookup(ticker_data: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    by_ticker: dict[str, dict[str, Any]] = {}
    by_name: dict[str, dict[str, Any]] = {}
    for record in ticker_data.values():
        if not isinstance(record, dict):
            continue
        ticker = str(record.get("ticker") or "").strip().upper()
        title = str(record.get("title") or "").strip()
        if ticker:
            by_ticker[ticker] = record
        if title:
            by_name[_normalize_company_key(title)] = record
    return by_ticker, by_name


def resolve_watchlist_company(entry: dict[str, Any], ticker_data: dict[str, Any]) -> dict[str, Any]:
    resolved = dict(entry)
    if resolved.get("sec_cik"):
        resolved["sec_cik"] = str(resolved["sec_cik"]).zfill(10)
        return resolved

    by_ticker, by_name = _build_ticker_lookup(ticker_data)
    record = None
    ticker = str(resolved.get("ticker") or "").strip().upper()
    if ticker:
        record = by_ticker.get(ticker)
    if record is None:
        lookup_name = str(resolved.get("sec_lookup") or resolved.get("name") or "").strip()
        record = by_name.get(_normalize_company_key(lookup_name))
    if record is None:
        return resolved

    cik = str(record.get("cik_str") or "").strip()
    if cik:
        resolved["sec_cik"] = cik.zfill(10)
    if not resolved.get("ticker"):
        resolved["ticker"] = str(record.get("ticker") or "").strip().upper()
    return resolved


def resolve_watchlist_companies(entries: Iterable[dict[str, Any]], user_agent: str, ticker_data: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
    ticker_data = ticker_data or _fetch_json(SEC_TICKERS_URL, user_agent)
    return [resolve_watchlist_company(entry, ticker_data) for entry in entries]


def _build_filing_link(cik: str, accession_number: str, primary_document: str) -> str:
    accession_compact = accession_number.replace("-", "")
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_compact}"
    if primary_document:
        return f"{base}/{primary_document}"
    return f"{base}/{accession_number}-index.htm"


def _sec_dedupe_key(link: str, accession_number: str, form: str) -> str:
    base = f"{link.strip()}|{accession_number.strip()}|{form.strip().upper()}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]


def _normalize_description(description: str) -> str:
    text = re.sub(r"\s+", " ", str(description or "").strip())
    if not text:
        return ""
    text = re.sub(r"(?i)^FORM\s+", "", text)
    text = re.sub(r"(?i)^8-K\s*[-:]\s*", "", text)
    text = re.sub(r"(?i)^10-K\s*[-:]\s*", "", text)
    text = re.sub(r"(?i)^10-Q\s*[-:]\s*", "", text)
    text = re.sub(r"(?i)^6-K\s*[-:]\s*", "", text)
    text = re.sub(r"(?i)^20-F\s*[-:]\s*", "", text)
    return text.strip(" .")


def _normalize_items(items_value: Any) -> list[str]:
    if not items_value:
        return []
    if isinstance(items_value, list):
        raw = ",".join(str(item) for item in items_value if item)
    else:
        raw = str(items_value)
    raw = raw.replace("and", ",").replace("AND", ",")
    return [part.strip() for part in re.split(r"[\s,;]+", raw) if re.fullmatch(r"\d+\.\d+", part.strip())]


def _extract_8k_items(description: str) -> list[str]:
    match = _ITEM_PATTERN.search(description or "")
    if not match:
        return []
    raw = match.group(1).replace("AND", ",")
    items = [part.strip() for part in raw.split(",") if part.strip()]
    return items


def _filing_focus(form: str, description: str, items_value: Any = None) -> str:
    clean = _normalize_description(description)
    if form == "8-K":
        items = _normalize_items(items_value) or _extract_8k_items(clean)
        for item in items:
            if item in _EIGHT_K_ITEM_LABELS:
                return _EIGHT_K_ITEM_LABELS[item]
    if form == "10-K":
        return "annual filing"
    if form == "10-Q":
        return "quarterly filing"
    if form == "6-K":
        return "foreign issuer update"
    if form == "20-F":
        return "annual foreign issuer filing"
    if form in {"S-1", "S-3"}:
        return "capital markets filing"
    if form == "424B3":
        return "prospectus supplement"
    return clean.lower() if clean else "filing"


def fetch_sec_watchlist_items(
    company_watchlist: list[dict[str, Any]],
    user_agent: str,
    lookback_days: int = 30,
    max_items_per_company: int = 10,
) -> list[dict[str, Any]]:
    if not company_watchlist:
        return []

    resolved_watchlist = resolve_watchlist_companies(company_watchlist, user_agent)
    cutoff = date.today() - timedelta(days=lookback_days)
    items: list[dict[str, Any]] = []
    seen_signatures: set[tuple[str, str, str, str]] = set()

    for entry in resolved_watchlist:
        cik = str(entry.get("sec_cik") or "").strip()
        if not cik:
            continue
        forms = [str(form).strip().upper() for form in (entry.get("edgar_forms") or DEFAULT_EDGAR_FORMS)]
        try:
            data = _fetch_json(SEC_SUBMISSIONS_URL.format(cik=cik), user_agent)
        except Exception:
            continue

        recent = data.get("filings", {}).get("recent", {})
        filing_dates = recent.get("filingDate", []) or []
        filing_forms = recent.get("form", []) or []
        accessions = recent.get("accessionNumber", []) or []
        primary_docs = recent.get("primaryDocument", []) or []
        descriptions = recent.get("primaryDocDescription", []) or []
        filing_items = recent.get("items", []) or []
        company_name = str(entry.get("name") or data.get("name") or "").strip()

        added = 0
        for idx, filing_date in enumerate(filing_dates):
            if idx >= len(filing_forms) or idx >= len(accessions):
                continue
            form = str(filing_forms[idx] or "").strip().upper()
            if form not in forms:
                continue
            try:
                filing_day = date.fromisoformat(str(filing_date))
            except ValueError:
                continue
            if filing_day < cutoff:
                continue
            primary_doc = primary_docs[idx] if idx < len(primary_docs) else ""
            description = descriptions[idx] if idx < len(descriptions) else ""
            items_value = filing_items[idx] if idx < len(filing_items) else ""
            description_key = re.sub(r"\s+", " ", str(description or "").strip().lower())
            signature = (company_name.lower(), form, str(filing_date), description_key)
            if signature in seen_signatures:
                continue
            seen_signatures.add(signature)
            link = _build_filing_link(cik, str(accessions[idx]), str(primary_doc or ""))
            item_codes = _normalize_items(items_value) or _extract_8k_items(str(description or ""))
            focus = _filing_focus(form, str(description or ""), item_codes)
            summary = f"SEC {form} filed {filing_date}."
            if item_codes:
                summary += f" Items: {', '.join(item_codes)}."
            if description:
                summary += f" {description}."
            title = f"{company_name}: SEC {form}"
            if focus and focus != "filing":
                title += f" - {focus}"
            tag_parts = [form] + item_codes
            items.append(
                {
                    "dedupe_key": _sec_dedupe_key(link, str(accessions[idx]), form),
                    "source_url": SEC_SUBMISSIONS_URL.format(cik=cik),
                    "source_name": "SEC EDGAR",
                    "title": title,
                    "link": link,
                    "published": str(filing_date),
                    "summary": summary[:500],
                    "tags": ",".join(tag_parts),
                    "us_relevant": "Yes" if entry.get("us_relevance_basis") else "Maybe",
                    "watchlist_company": company_name,
                    "watchlist_us_relevance_basis": str(entry.get("us_relevance_basis") or "").strip(),
                }
            )
            added += 1
            if added >= max_items_per_company:
                break
    return items
