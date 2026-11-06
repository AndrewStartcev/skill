#!/usr/bin/env python3
"""Read-only, same-host, robots-aware preliminary SEO crawler (Python 3.11+)."""

from __future__ import annotations

import argparse
import csv
import ipaddress
import json
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import xml.etree.ElementTree as ET
from collections import Counter, deque
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

USER_AGENT = "SEO-RU-Audit/1.0"
MAX_RESPONSE_BYTES = 2_000_000
MAX_SITEMAPS = 5
MAX_SITEMAP_URLS = 1000


def normalized_url(value: str, origin: str) -> str | None:
    """Normalize a URL without leaving the original hostname and port."""
    candidate = urllib.parse.urljoin(origin, value.strip())
    parts = urllib.parse.urlsplit(candidate)
    scope = urllib.parse.urlsplit(origin)
    if (
        parts.scheme not in ("http", "https")
        or not parts.hostname
        or parts.username is not None
        or parts.password is not None
        or parts.netloc.lower() != scope.netloc.lower()
    ):
        return None
    return urllib.parse.urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), parts.path or "/", parts.query, "")
    )


def check_host(host: str, allow_private: bool) -> None:
    """Refuse local, reserved and private DNS answers by default."""
    if allow_private:
        return
    try:
        addresses = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise RuntimeError(f"DNS resolution failed for {host}: {exc}") from exc
    if not addresses:
        raise RuntimeError(f"No DNS answers for {host}")
    for item in addresses:
        address = ipaddress.ip_address(item[4][0].split("%")[0])
        if not address.is_global:
            raise RuntimeError(f"Non-public IP blocked for {host}: {address}")


class ScopedRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, origin: str, allow_private: bool):
        super().__init__()
        self.origin = origin
        self.allow_private = allow_private

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = normalized_url(newurl, self.origin)
        if target is None:
            raise RuntimeError(f"Off-site redirect blocked: {newurl}")
        check_host(urllib.parse.urlsplit(target).hostname or "", self.allow_private)
        return super().redirect_request(req, fp, code, msg, headers, target)


def fetch(opener, url: str, timeout: float, allow_private: bool) -> dict:
    host = urllib.parse.urlsplit(url).hostname
    if not host:
        raise RuntimeError(f"Invalid URL: {url}")
    check_host(host, allow_private)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xml,text/xml,*/*"},
    )
    try:
        response = opener.open(request, timeout=timeout)
    except urllib.error.HTTPError as exc:
        response = exc  # Preserve 4xx/5xx status and headers for diagnosis.
    with response:
        data = response.read(MAX_RESPONSE_BYTES + 1)
        if len(data) > MAX_RESPONSE_BYTES:
            raise RuntimeError(f"Response exceeds {MAX_RESPONSE_BYTES} bytes: {url}")
        return {
            "status": response.status,
            "final_url": response.geturl(),
            "content_type": response.headers.get("Content-Type", ""),
            "x_robots_tag": response.headers.get("X-Robots-Tag", ""),
            "body": data,
            "charset": response.headers.get_content_charset() or "utf-8",
        }


def decode_response(response: dict) -> str:
    try:
        return response["body"].decode(response["charset"], errors="replace")
    except LookupError:
        return response["body"].decode("utf-8", errors="replace")


class SEOHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.description = ""
        self.lang = ""
        self.canonical = ""
        self.robots: dict[str, str] = {}
        self.links: list[str] = []
        self.headings: list[tuple[str, str]] = []
        self.images_missing_alt = 0
        self.jsonld: list[str] = []
        self._in_title = False
        self._heading: str | None = None
        self._heading_text: list[str] = []
        self._in_jsonld = False
        self._jsonld_text: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = {key.lower(): (value or "") for key, value in attrs if key}
        if tag == "html":
            self.lang = a.get("lang", "")
        elif tag == "title":
            self._in_title = True
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            if self._heading is None:
                self._heading, self._heading_text = tag, []
        elif tag == "meta":
            name = a.get("name", "").lower()
            if name == "description" and not self.description:
                self.description = a.get("content", "").strip()
            if name in ("robots", "googlebot", "yandex"):
                self.robots[name] = a.get("content", "").lower()
        elif tag == "link":
            if "canonical" in a.get("rel", "").lower().split() and not self.canonical:
                self.canonical = a.get("href", "")
        elif tag == "a":
            if a.get("href"):
                self.links.append(a["href"])
        elif tag == "img":
            if a.get("src") and "alt" not in a:
                self.images_missing_alt += 1
        elif tag == "script":
            if a.get("type", "").lower() == "application/ld+json":
                self._in_jsonld = True
                self._jsonld_text = []

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._heading is not None:
            self._heading_text.append(data)
        if self._in_jsonld:
            self._jsonld_text.append(data)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == self._heading:
            value = " ".join("".join(self._heading_text).split())
            self.headings.append((tag, value))
            self._heading, self._heading_text = None, []
        if tag == "script" and self._in_jsonld:
            self.jsonld.append("".join(self._jsonld_text).strip())
            self._in_jsonld, self._jsonld_text = False, []


def parse_html(html: str) -> SEOHTMLParser:
    parser = SEOHTMLParser()
    parser.feed(html)
    parser.close()
    parser.title = " ".join(parser.title.split())
    return parser


def read_robots(opener, origin: str, timeout: float, allow_private: bool):
    url = origin + "/robots.txt"
    response = fetch(opener, url, timeout, allow_private)
    status = response["status"]
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(url)
    if status == 404:
        parser.parse([])
        return parser, "", status
    if status != 200:
        raise RuntimeError(f"Cannot safely read robots.txt (HTTP {status}); crawl aborted")
    text = decode_response(response)
    parser.parse(text.splitlines())
    return parser, text, status


def discover_sitemap(
    opener, origin: str, robots_text: str, timeout: float, allow_private: bool
) -> tuple[set[str], list[str], list[str]]:
    sources = [
        line.split(":", 1)[1].strip()
        for line in robots_text.splitlines()
        if line.strip().lower().startswith("sitemap:")
    ]
    sources.append(origin + "/sitemap.xml")
    queue = deque(filter(None, (normalized_url(s, origin) for s in sources)))
    checked: set[str] = set()
    urls: set[str] = set()
    notes: list[str] = []
    while queue and len(checked) < MAX_SITEMAPS and len(urls) < MAX_SITEMAP_URLS:
        current = queue.popleft()
        if current in checked:
            continue
        checked.add(current)
        try:
            response = fetch(opener, current, timeout, allow_private)
            if response["status"] != 200:
                notes.append(f"Sitemap HTTP {response['status']}: {current}")
                continue
            root = ET.fromstring(response["body"])
            root_name = root.tag.rsplit("}", 1)[-1].lower()
            locations = [
                (node.text or "").strip()
                for node in root.iter()
                if node.tag.rsplit("}", 1)[-1].lower() == "loc"
            ]
            if root_name == "sitemapindex":
                for location in locations:
                    next_url = normalized_url(location, origin)
                    if next_url and next_url not in checked:
                        queue.append(next_url)
            elif root_name == "urlset":
                for location in locations:
                    next_url = normalized_url(location, origin)
                    if next_url:
                        urls.add(next_url)
                        if len(urls) >= MAX_SITEMAP_URLS:
                            notes.append("Sitemap URL collection capped")
                            break
            else:
                notes.append(f"Unexpected sitemap root element: {current}")
        except (ET.ParseError, RuntimeError, urllib.error.URLError, TimeoutError) as exc:
            notes.append(f"Sitemap unavailable/invalid: {current} ({exc})")
    if queue:
        notes.append(f"Sitemap files capped at {MAX_SITEMAPS}")
    return urls, sorted(checked), notes


def issue(level: str, code: str, url: str, detail: str) -> dict:
    return {"priority": level, "code": code, "url": url, "detail": detail}


def page_findings(page: dict, sitemap_urls: set[str]) -> list[dict]:
    url = page["url"]
    status = page["status"]
    findings: list[dict] = []
    if status >= 500:
        findings.append(issue("P0", "server_error", url, f"HTTP {status}"))
    elif status >= 400:
        findings.append(issue("P1", "client_error", url, f"HTTP {status}"))
    if url in sitemap_urls and status != 200:
        findings.append(issue("P1", "sitemap_non_200", url, f"Listed in sitemap; HTTP {status}"))
    if page["content_type"].lower().startswith("text/html") and status == 200:
        if not page["title"]:
            findings.append(issue("P2", "missing_title", url, "HTML title is empty"))
        if not page["h1"]:
            findings.append(issue("P2", "missing_h1_review", url, "No H1; review template intent"))
        if len(page["h1"]) > 1:
            findings.append(issue("P3", "multiple_h1_review", url, "Multiple H1; not always an error"))
        if not page["description"]:
            findings.append(issue("P3", "missing_description_review", url, "May affect snippet; not mandatory"))
        if page["images_missing_alt"]:
            findings.append(issue("P3", "image_alt_review", url, f"{page['images_missing_alt']} img without alt attribute; review informative images"))
        if page["invalid_jsonld"]:
            findings.append(issue("P2", "invalid_jsonld", url, f"{page['invalid_jsonld']} JSON-LD blocks not valid JSON"))
        directives = " ".join(page["robots"].values()) + " " + page["x_robots_tag"].lower()
        if url in sitemap_urls and "noindex" in directives:
            findings.append(issue("P1", "sitemap_noindex", url, "Sitemap URL has noindex; verify intent"))
        if page["canonical"]:
            canonical = normalized_url(page["canonical"], url)
            if canonical and canonical != page["final_url"] and url in sitemap_urls:
                findings.append(issue("P2", "sitemap_canonical_mismatch", url, f"Canonical: {canonical}; verify duplicate intent"))
            if not canonical:
                findings.append(issue("P2", "canonical_outside_scope_review", url, f"Canonical: {page['canonical']}"))
    return findings


def crawl(args: argparse.Namespace) -> dict:
    parts = urllib.parse.urlsplit(args.url)
    if parts.scheme not in ("http", "https") or not parts.hostname or parts.username:
        raise RuntimeError("Provide an http(s) URL with a hostname and no credentials")
    origin = urllib.parse.urlunsplit((parts.scheme, parts.netloc, "", "", ""))
    start = normalized_url(args.url, origin)
    if not start:
        raise RuntimeError("Invalid start URL")
    check_host(parts.hostname, args.allow_private)
    opener = urllib.request.build_opener(ScopedRedirect(origin, args.allow_private))
    robots, robots_text, robots_status = read_robots(
        opener, origin, args.timeout, args.allow_private
    )
    sitemap_urls, sitemap_files, notes = discover_sitemap(
        opener, origin, robots_text, args.timeout, args.allow_private
    )
    effective_delay = max(args.delay, robots.crawl_delay(USER_AGENT) or 0)
    queue = deque([start, origin + "/"])
    queue.extend(sorted(sitemap_urls))
    queued = set(queue)
    visited: set[str] = set()
    pages: list[dict] = []
    findings: list[dict] = []
    while queue and len(visited) < args.max_pages:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        if not robots.can_fetch(USER_AGENT, url):
            notes.append(f"Blocked by robots.txt: {url}")
            continue
        try:
            response = fetch(opener, url, args.timeout, args.allow_private)
        except (RuntimeError, urllib.error.URLError, TimeoutError, OSError) as exc:
            findings.append(issue("P1", "fetch_failed", url, str(exc)))
            time.sleep(effective_delay)
            continue
        final_url = normalized_url(response["final_url"], origin)
        if not final_url:
            findings.append(issue("P1", "unsafe_redirect", url, "Final URL outside scope"))
            continue
        html = response["content_type"].lower().startswith("text/html")
        parsed = parse_html(decode_response(response)) if html and response["status"] == 200 else None
        h1 = [value for tag, value in parsed.headings if tag == "h1"] if parsed else []
        invalid_jsonld = 0
        if parsed:
            for block in parsed.jsonld:
                try:
                    json.loads(block)
                except (ValueError, TypeError):
                    invalid_jsonld += 1
        page = {
            "url": url,
            "final_url": final_url,
            "status": response["status"],
            "content_type": response["content_type"],
            "title": parsed.title if parsed else "",
            "description": parsed.description if parsed else "",
            "lang": parsed.lang if parsed else "",
            "canonical": parsed.canonical if parsed else "",
            "robots": parsed.robots if parsed else {},
            "x_robots_tag": response["x_robots_tag"],
            "h1": h1,
            "headings": parsed.headings if parsed else [],
            "images_missing_alt": parsed.images_missing_alt if parsed else 0,
            "jsonld_blocks": len(parsed.jsonld) if parsed else 0,
            "invalid_jsonld": invalid_jsonld,
            "links_count": len(parsed.links) if parsed else 0,
            "in_sitemap": url in sitemap_urls,
        }
        pages.append(page)
        findings.extend(page_findings(page, sitemap_urls))
        if parsed:
            for raw_link in parsed.links:
                next_url = normalized_url(raw_link, final_url)
                if next_url and next_url not in queued and next_url not in visited:
                    queue.append(next_url)
                    queued.add(next_url)
        time.sleep(effective_delay)
    titles: dict[str, list[str]] = {}
    for page in pages:
        if page["title"] and page["status"] == 200:
            titles.setdefault(page["title"].casefold(), []).append(page["url"])
    for title, urls in titles.items():
        if len(urls) > 1:
            findings.append(issue("P2", "duplicate_title_review", urls[0], f"{len(urls)} URLs share title: {title[:100]}"))
    if queue:
        notes.append(f"Crawl limited to {args.max_pages} requested URLs; remaining queue not audited")
    notes.append("Only raw HTTP/HTML; no JavaScript rendering, real index, positions, CWV, analytics or schema eligibility")
    return {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "start_url": start,
        "scope_host": parts.netloc,
        "robots_status": robots_status,
        "sitemap_files": sitemap_files,
        "sitemap_url_count": len(sitemap_urls),
        "pages_requested": len(visited),
        "pages_received": len(pages),
        "pages": pages,
        "issues": findings,
        "notes": notes,
    }


def write_report(report: dict, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    with (output / "issues.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["priority", "code", "url", "detail"])
        writer.writeheader()
        writer.writerows(report["issues"])
    counts = Counter(item["priority"] for item in report["issues"])
    lines = [
        "# Preliminary SEO audit",
        "",
        f"- Checked: {report['checked_at_utc']}",
        f"- Start: {report['start_url']}",
        f"- HTTP pages: {report['pages_received']} / {report['pages_requested']} requests",
        f"- Sitemap URLs discovered: {report['sitemap_url_count']}",
        f"- Issues: P0={counts['P0']}, P1={counts['P1']}, P2={counts['P2']}, P3={counts['P3']}",
        "",
        "## Findings (sample)",
        "",
    ]
    for item in report["issues"][:50]:
        lines.append(f"- **{item['priority']} {item['code']}**: {item['url']} — {item['detail']}")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {note}" for note in report["notes"])
    (output / "summary.md").write_text("\\n".join(lines) + "\\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Public http(s) site URL, e.g. https://example.com/")
    parser.add_argument("--max-pages", type=int, default=50)
    parser.add_argument("--delay", type=float, default=0.5, help="Seconds between page requests")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--output", type=Path, default=Path("./seo-audit-output"))
    parser.add_argument("--allow-private", action="store_true", help="Only for your own authorized staging site")
    args = parser.parse_args()
    if not 1 <= args.max_pages <= 500 or not 0 <= args.delay <= 30 or not 1 <= args.timeout <= 60:
        parser.error("Allowed: max-pages 1..500, delay 0..30, timeout 1..60")
    try:
        report = crawl(args)
        write_report(report, args.output)
    except (RuntimeError, OSError, ValueError) as exc:
        print(f"Audit aborted: {exc}", file=sys.stderr)
        return 2
    print(f"Saved {report['pages_received']} pages and {len(report['issues'])} findings to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
