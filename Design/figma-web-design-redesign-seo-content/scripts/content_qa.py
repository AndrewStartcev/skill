#!/usr/bin/env python3
"""Read-only QA for SEO page-content and redesign URL-map CSV files.

Python 3.10+, standard library only. Does not access the network or modify files.
A warning is a review prompt, not a search-engine ranking rule.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


PAGE_COLUMNS = {
    "url", "page_type", "region", "intent", "primary_query",
    "secondary_queries", "title", "meta_description", "h1", "hero",
    "cta", "body_outline", "faq", "canonical", "status", "owner", "evidence",
}
REDIRECT_COLUMNS = {"old_url", "new_url", "action", "reason", "checked", "owner"}
COMMERCIAL_TYPES = {"home", "landing", "service", "category", "product"}
REDIRECT_ACTIONS = {"keep", "301", "404", "410"}


def issue(level: str, code: str, row: int, detail: str) -> dict:
    return {"level": level, "code": code, "row": row, "detail": detail}


def normalized_url(value: str) -> str | None:
    """Normalize URLs for comparisons without changing live URLs."""
    value = (value or "").strip()
    if not value:
        return None
    try:
        parts = urlsplit(value)
        if parts.scheme.lower() not in {"http", "https"} or not parts.netloc:
            return None
        if parts.username or parts.password or parts.fragment:
            return None
        hostname = parts.hostname
        if not hostname:
            return None
        host = parts.netloc.lower()
        path = (parts.path or "/").rstrip("/") or "/"
        return urlunsplit((parts.scheme.lower(), host, path, parts.query, ""))
    except ValueError:
        return None


def read_csv(path: str | Path, required_columns: set[str]) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        headers = set(reader.fieldnames or [])
        missing = sorted(required_columns - headers)
        if missing:
            raise ValueError(f"{path}: missing columns: {', '.join(missing)}")
        rows = []
        for raw in reader:
            if None in raw:
                raise ValueError(f"{path}: extra unquoted CSV columns at row {reader.line_num}")
            rows.append({key: (value or "").strip() for key, value in raw.items()})
        return rows


def validate_pages(rows: list[dict[str, str]]) -> list[dict]:
    problems: list[dict] = []
    urls: dict[str, int] = {}
    titles: dict[str, list[int]] = defaultdict(list)
    headings: dict[str, list[int]] = defaultdict(list)

    if not rows:
        return [issue("warning", "empty_pages", 0, "Page matrix has no rows")]

    for number, row in enumerate(rows, start=2):
        url = normalized_url(row.get("url", ""))
        if not url:
            problems.append(issue("error", "invalid_page_url", number, "Missing or invalid absolute page URL"))
        elif url in urls:
            problems.append(issue("error", "duplicate_page_url", number, f"Same URL as row {urls[url]}"))
        else:
            urls[url] = number

        for field in ("page_type", "intent", "title", "h1", "hero", "owner"):
            if not row.get(field, "").strip():
                problems.append(issue("error", "missing_" + field, number, f"Missing {field}"))

        if row.get("page_type", "").lower() in COMMERCIAL_TYPES and not row.get("cta", ""):
            problems.append(issue("error", "missing_cta", number, "Commercial page needs a clear primary CTA"))

        for field in ("primary_query", "meta_description", "body_outline"):
            if not row.get(field, ""):
                problems.append(issue("warning", "missing_" + field, number, f"Review missing {field}"))

        title = row.get("title", "").casefold()
        if title:
            titles[title].append(number)
        heading = row.get("h1", "").casefold()
        if heading:
            headings[heading].append(number)

        canonical_raw = row.get("canonical", "")
        if canonical_raw:
            canonical = normalized_url(canonical_raw)
            if not canonical:
                problems.append(issue("error", "invalid_canonical", number, "Invalid canonical URL"))
            elif url and canonical != url:
                problems.append(issue("warning", "cross_canonical", number, "Canonical differs from page URL: review intent"))

        if row.get("status", "").lower() == "approved" and not row.get("evidence", ""):
            problems.append(issue("warning", "missing_evidence", number, "Approved content has no source/evidence note"))

    for value, positions in titles.items():
        if len(positions) > 1:
            problems.append(issue("warning", "duplicate_title", positions[0], f"Same Title in rows {positions}: {value}"))
    for value, positions in headings.items():
        if len(positions) > 1:
            problems.append(issue("warning", "duplicate_h1", positions[0], f"Same H1 in rows {positions}: {value}"))

    return problems


def validate_redirects(rows: list[dict[str, str]]) -> list[dict]:
    problems: list[dict] = []
    seen: dict[str, int] = {}
    redirect_to: dict[str, str] = {}

    if not rows:
        return [issue("warning", "empty_redirects", 0, "URL-map has no rows")]

    for number, row in enumerate(rows, start=2):
        old_raw = row.get("old_url", "")
        new_raw = row.get("new_url", "")
        action = row.get("action", "").lower()
        old = normalized_url(old_raw)
        new = normalized_url(new_raw)

        if not old:
            problems.append(issue("error", "invalid_old_url", number, "Invalid old URL"))
        elif old in seen:
            problems.append(issue("error", "duplicate_old_url", number, f"Same old URL as row {seen[old]}"))
        else:
            seen[old] = number

        if action not in REDIRECT_ACTIONS:
            problems.append(issue("error", "invalid_action", number, f"Action must be one of {sorted(REDIRECT_ACTIONS)}"))
            continue

        if action in {"keep", "301"} and not new:
            problems.append(issue("error", "invalid_new_url", number, "Action requires a valid new URL"))
        if action in {"404", "410"} and new_raw:
            problems.append(issue("warning", "removed_with_target", number, "404/410 usually should not specify new_url"))
        if action == "keep" and old and new and old != new:
            problems.append(issue("error", "keep_changed_url", number, "keep requires old_url == new_url"))
        if action == "301" and old and new:
            if old == new:
                problems.append(issue("error", "self_redirect", number, "301 redirects URL to itself"))
            else:
                redirect_to[old] = new
                if urlsplit(new).path == "/" and urlsplit(old).path != "/":
                    problems.append(issue("warning", "redirect_to_home", number, "Review redirect from internal URL to homepage"))
        if not row.get("reason", ""):
            problems.append(issue("warning", "missing_reason", number, "Document why this mapping is appropriate"))
        if not row.get("owner", ""):
            problems.append(issue("warning", "missing_owner", number, "Assign mapping owner"))

    for old, target in redirect_to.items():
        if target in redirect_to:
            problems.append(issue("warning", "redirect_chain", seen.get(old, 0), f"Potential 301 chain: {old} -> {target}"))

    visited: set[str] = set()
    for start in redirect_to:
        if start in visited:
            continue
        trail: set[str] = set()
        current = start
        while current in redirect_to:
            if current in trail:
                problems.append(issue("error", "redirect_cycle", seen.get(start, 0), f"301 cycle involving {current}"))
                break
            if current in visited:
                break
            trail.add(current)
            current = redirect_to[current]
        visited.update(trail)

    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages", help="Path to page-content-matrix.csv")
    parser.add_argument("--redirects", help="Path to redirect-map.csv")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    args = parser.parse_args(argv)
    if not args.pages and not args.redirects:
        parser.error("Specify --pages and/or --redirects")

    problems: list[dict] = []
    try:
        if args.pages:
            problems.extend(validate_pages(read_csv(args.pages, PAGE_COLUMNS)))
        if args.redirects:
            problems.extend(validate_redirects(read_csv(args.redirects, REDIRECT_COLUMNS)))
    except (OSError, UnicodeError, csv.Error, ValueError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2

    errors = sum(p["level"] == "error" for p in problems)
    warnings = sum(p["level"] == "warning" for p in problems)
    if args.format == "json":
        print(json.dumps({"errors": errors, "warnings": warnings, "issues": problems}, ensure_ascii=False, indent=2))
    else:
        for p in problems:
            print(f'{p["level"].upper()} {p["code"]} row={p["row"]}: {p["detail"]}')
        print(f"QA summary: {errors} error(s), {warnings} warning(s)")

    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
