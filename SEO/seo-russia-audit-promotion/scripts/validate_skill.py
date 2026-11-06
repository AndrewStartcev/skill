#!/usr/bin/env python3
"""Validate this skill's structure, frontmatter and local Markdown references."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def validate() -> list[str]:
    problems: list[str] = []
    for dirname in ("references", "scripts", "assets"):
        if not (ROOT / dirname).is_dir():
            problems.append(f"Missing directory: {dirname}")
    skill = ROOT / "SKILL.md"
    if not skill.is_file():
        return problems + ["Missing SKILL.md"]
    content = skill.read_text(encoding="utf-8")
    if not content.startswith("---\\n"):
        problems.append("SKILL.md must start with YAML frontmatter")
    else:
        parts = content.split("---", 2)
        frontmatter = parts[1] if len(parts) > 2 else ""
        for key in ("name:", "description:"):
            if not re.search(rf"(?m)^{re.escape(key)}\\s*\\S", frontmatter):
                problems.append(f"Missing frontmatter field: {key}")
    for markdown in ROOT.rglob("*.md"):
        text = markdown.read_text(encoding="utf-8")
        for link in re.findall(r"\\]\\(([^)]+)\\)", text):
            if link.startswith(("http://", "https://", "#", "mailto:")):
                continue
            relative = link.split("#", 1)[0]
            if relative and not (markdown.parent / relative).exists():
                problems.append(f"Broken link: {markdown.relative_to(ROOT)} -> {link}")
    return problems


if __name__ == "__main__":
    failures = validate()
    if failures:
        print("\\n".join(failures), file=sys.stderr)
        raise SystemExit(1)
    print("Skill structure and relative links: OK")
