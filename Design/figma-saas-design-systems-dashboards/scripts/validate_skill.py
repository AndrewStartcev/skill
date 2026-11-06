#!/usr/bin/env python3
"""Offline structure validator for the Figma SaaS design skill."""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
EXPECTED = ("SKILL.md", "references", "scripts", "assets")


def error(message: str) -> None:
    ERRORS.append(message)


def check_structure() -> None:
    for name in EXPECTED:
        if not (ROOT / name).exists():
            error(f"Missing required path: {name}")
    skill = ROOT / "SKILL.md"
    if not skill.is_file():
        return
    content = skill.read_text(encoding="utf-8")
    blocks = content.split("---", 2)
    if len(blocks) < 3 or blocks[0].strip():
        error("SKILL.md must start with YAML frontmatter")
        return
    for field in ("name:", "description:"):
        if not any(line.strip().startswith(field) for line in blocks[1].splitlines()):
            error(f"SKILL.md missing frontmatter field: {field}")


def check_links_and_secrets() -> None:
    markdown_link = re.compile(r"\]\(([^)\n]+)\)")
    secret_patterns = (
        re.compile(r"gh[opsur]_[A-Za-z0-9]{20,}"),
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    )
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in (".md", ".py", ".json", ".csv"):
            continue
        content = path.read_text(encoding="utf-8")
        for pattern in secret_patterns:
            if pattern.search(content):
                error(f"Possible secret in {path.relative_to(ROOT)}")
        if path.suffix != ".md":
            continue
        for link in markdown_link.findall(content):
            link = link.split("#", 1)[0].split("?", 1)[0].strip()
            if not link or link.startswith(("https://", "http://", "mailto:", "data:", "//")):
                continue
            target = (path.parent / unquote(link)).resolve()
            if not target.is_relative_to(ROOT.parent):
                error(f"Link outside category: {path.relative_to(ROOT)} -> {link}")
            elif not target.exists():
                error(f"Broken local link: {path.relative_to(ROOT)} -> {link}")


def check_assets() -> None:
    token_path = ROOT / "assets/tokens-example.json"
    try:
        data = json.loads(token_path.read_text(encoding="utf-8"))
        if "semantic" not in data or "primitives" not in data:
            error("tokens-example.json must contain semantic and primitives")
    except (OSError, ValueError) as exc:
        error(f"Invalid tokens JSON: {exc}")
    for path in (ROOT / "assets").glob("*.csv"):
        try:
            with path.open(encoding="utf-8", newline="") as stream:
                rows = list(csv.reader(stream))
            if len(rows) < 2:
                error(f"Empty CSV template: {path.name}")
            elif any(len(row) != len(rows[0]) for row in rows[1:]):
                error(f"CSV row width mismatch: {path.name}")
        except (OSError, csv.Error) as exc:
            error(f"Invalid CSV {path.name}: {exc}")


if __name__ == "__main__":
    check_structure()
    check_links_and_secrets()
    check_assets()
    if ERRORS:
        for message in ERRORS:
            print("ERROR:", message)
        sys.exit(1)
    print("OK: Figma SaaS skill structure, links and sample assets are valid")
