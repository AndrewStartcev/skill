#!/usr/bin/env python3
"""Unit tests for the read-only CSV QA helper."""
import csv
import tempfile
import unittest
from pathlib import Path

from content_qa import (
    PAGE_COLUMNS,
    REDIRECT_COLUMNS,
    main,
    normalized_url,
    read_csv,
    validate_pages,
    validate_redirects,
)


def page(**overrides):
    item = {
        "url": "https://example.com/services/a/",
        "page_type": "service",
        "region": "Город N",
        "intent": "commercial",
        "primary_query": "ремонт",
        "secondary_queries": "",
        "title": "Ремонт мебели",
        "meta_description": "Описание услуги",
        "h1": "Ремонт мебели",
        "hero": "Понятное предложение",
        "cta": "Оставить заявку",
        "body_outline": "Условия;Этапы",
        "faq": "",
        "canonical": "https://example.com/services/a/",
        "status": "draft",
        "owner": "редактор",
        "evidence": "Уточнить факты",
    }
    item.update(overrides)
    return item


def redirect(old, new, action="301", **overrides):
    item = {"old_url": old, "new_url": new, "action": action, "reason": "Редизайн", "checked": "no", "owner": "SEO"}
    item.update(overrides)
    return item


class ContentQATests(unittest.TestCase):
    def test_url_normalization(self):
        self.assertEqual(normalized_url("HTTPS://EXAMPLE.COM/a/"), "https://example.com/a")
        self.assertIsNone(normalized_url("javascript:alert(1)"))
        self.assertIsNone(normalized_url("https://example.com/a#fragment"))

    def test_valid_page(self):
        self.assertEqual(validate_pages([page()]), [])

    def test_missing_and_duplicate_content(self):
        rows = [
            page(),
            page(url="https://example.com/services/b/", canonical="https://example.com/services/b/", cta=""),
        ]
        issues = validate_pages(rows)
        codes = {i["code"] for i in issues}
        self.assertIn("duplicate_title", codes)
        self.assertIn("duplicate_h1", codes)
        self.assertIn("missing_cta", codes)

    def test_duplicate_url(self):
        issues = validate_pages([page(), page()])
        self.assertIn("duplicate_page_url", {i["code"] for i in issues})

    def test_redirect_chain(self):
        issues = validate_redirects([
            redirect("https://example.com/a/", "https://example.com/b/"),
            redirect("https://example.com/b/", "https://example.com/c/"),
        ])
        self.assertIn("redirect_chain", {i["code"] for i in issues})

    def test_redirect_cycle(self):
        issues = validate_redirects([
            redirect("https://example.com/a/", "https://example.com/b/"),
            redirect("https://example.com/b/", "https://example.com/a/"),
        ])
        self.assertIn("redirect_cycle", {i["code"] for i in issues})

    def test_self_redirect(self):
        issues = validate_redirects([redirect("https://example.com/a/", "https://example.com/a/")])
        self.assertIn("self_redirect", {i["code"] for i in issues})

    def test_keep_changed_url(self):
        issues = validate_redirects([redirect("https://example.com/a/", "https://example.com/b/", "keep")])
        self.assertIn("keep_changed_url", {i["code"] for i in issues})

    def test_csv_schema_and_cli(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "pages.csv"
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=sorted(PAGE_COLUMNS))
                writer.writeheader()
                writer.writerow(page())
            self.assertEqual(len(read_csv(path, PAGE_COLUMNS)), 1)
            self.assertEqual(main(["--pages", str(path), "--strict"]), 0)
            with self.assertRaises(ValueError):
                read_csv(path, REDIRECT_COLUMNS)


if __name__ == "__main__":
    unittest.main()
