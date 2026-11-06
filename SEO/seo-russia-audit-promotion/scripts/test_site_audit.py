"""Offline regression tests for the read-only SEO crawler."""

import tempfile
import unittest
from pathlib import Path

from site_audit import normalized_url, page_findings, parse_html, write_report


class URLTests(unittest.TestCase):
    def test_relative_url_and_fragment(self):
        self.assertEqual(
            normalized_url("/catalog/?sort=price#top", "https://example.com/"),
            "https://example.com/catalog/?sort=price",
        )

    def test_reject_external_and_unsafe(self):
        origin = "https://example.com/"
        self.assertIsNone(normalized_url("https://evil.example/path", origin))
        self.assertIsNone(normalized_url("javascript:alert(1)", origin))
        self.assertIsNone(normalized_url("https://user:secret@example.com/", origin))


class HTMLTests(unittest.TestCase):
    def test_extract_metadata(self):
        html = """<html lang="ru"><head><title>Каталог — Пример</title>
        <meta name="description" content="Описание каталога">
        <meta name="robots" content="index,follow">
        <link rel="canonical" href="https://example.com/catalog/">
        <script type="application/ld+json">{"@type":"BreadcrumbList"}</script>
        </head><body><h1>Каталог</h1><a href="/product/">Товар</a>
        <img src="product.jpg"></body></html>"""
        page = parse_html(html)
        self.assertEqual(page.title, "Каталог — Пример")
        self.assertEqual(page.lang, "ru")
        self.assertEqual(page.canonical, "https://example.com/catalog/")
        self.assertEqual(page.headings, [("h1", "Каталог")])
        self.assertEqual(page.images_missing_alt, 1)
        self.assertEqual(len(page.jsonld), 1)
        self.assertEqual(page.links, ["/product/"])

    def test_sitemap_noindex_is_flagged(self):
        url = "https://example.com/service/"
        page = {
            "url": url,
            "final_url": url,
            "status": 200,
            "content_type": "text/html; charset=utf-8",
            "title": "Услуга",
            "description": "Подробное описание",
            "h1": ["Услуга"],
            "images_missing_alt": 0,
            "invalid_jsonld": 0,
            "robots": {"robots": "noindex,follow"},
            "x_robots_tag": "",
            "canonical": url,
        }
        codes = {item["code"] for item in page_findings(page, {url})}
        self.assertIn("sitemap_noindex", codes)
        self.assertNotIn("missing_title", codes)

    def test_404_sitemap_is_flagged(self):
        url = "https://example.com/old/"
        page = {"url": url, "status": 404, "content_type": "text/html"}
        codes = {item["code"] for item in page_findings(page, {url})}
        self.assertIn("client_error", codes)
        self.assertIn("sitemap_non_200", codes)


class ReportTests(unittest.TestCase):
    def test_writes_json_csv_and_multiline_markdown(self):
        report = {
            "checked_at_utc": "2026-11-06T00:00:00+00:00",
            "start_url": "https://example.com/",
            "pages_received": 1,
            "pages_requested": 1,
            "sitemap_url_count": 0,
            "issues": [{"priority": "P2", "code": "missing_title", "url": "https://example.com/", "detail": "Empty"}],
            "notes": ["No rendered JS"],
        }
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_report(report, output)
            self.assertTrue((output / "report.json").is_file())
            self.assertTrue((output / "issues.csv").is_file())
            summary = (output / "summary.md").read_text(encoding="utf-8")
            self.assertIn("# Preliminary SEO audit\n\n- Checked:", summary)
            self.assertIn("## Limitations", summary)


if __name__ == "__main__":
    unittest.main()
