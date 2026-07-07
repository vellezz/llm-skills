#!/usr/bin/env python3
"""Static validation of the dotnet-angular-docs plugin.

Free, deterministic, CI-friendly. Exit 0 = all checks pass.
Requires: pyyaml.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

# scripts/ lives inside the plugin directory - the plugin root is one level up
PLUGIN = Path(__file__).resolve().parent.parent
ERRORS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        err(f"{path}: no frontmatter block")
        return None
    try:
        d = yaml.safe_load(m.group(1))
    except yaml.YAMLError as exc:
        err(f"{path}: frontmatter is not valid YAML: {exc}")
        return None
    if not isinstance(d, dict):
        err(f"{path}: frontmatter is not a mapping")
        return None
    return d


def check_manifest() -> None:
    p = PLUGIN / ".claude-plugin" / "plugin.json"
    if not p.is_file():
        err(f"missing manifest: {p}")
        return
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        err(f"{p}: invalid JSON: {exc}")
        return
    name = d.get("name", "")
    if not re.fullmatch(r"[a-z0-9-]+", name):
        err(f"{p}: name {name!r} is not kebab-case")
    # manifest must be the ONLY thing in .claude-plugin/
    extras = [f.name for f in (PLUGIN / ".claude-plugin").iterdir() if f.name != "plugin.json"]
    if extras:
        err(f".claude-plugin/ must contain only plugin.json, found: {extras}")


def check_skills() -> None:
    skill_dirs = sorted((PLUGIN / "skills").iterdir()) if (PLUGIN / "skills").is_dir() else []
    if not skill_dirs:
        err("no skills/ directory or it is empty")
    for d in skill_dirs:
        skill_md = d / "SKILL.md"
        if not skill_md.is_file():
            err(f"{d}: missing SKILL.md")
            continue
        fm = frontmatter(skill_md)
        if fm is None:
            continue
        if fm.get("name") != d.name:
            err(f"{skill_md}: name {fm.get('name')!r} != directory {d.name!r}")
        desc = fm.get("description") or ""
        if not desc:
            err(f"{skill_md}: missing description")
        elif len(desc) > 1024:
            err(f"{skill_md}: description too long ({len(desc)} > 1024)")

        body = skill_md.read_text(encoding="utf-8")
        # every templates/references file mentioned must exist (incl. ../ paths)
        for ref in set(re.findall(r"`((?:\.\./)?[\w./-]*?(?:references|templates)/[\w.-]+\.md)`", body)):
            if not (d / ref).resolve().is_file():
                err(f"{skill_md}: broken reference {ref}")
        # no orphaned templates/references
        for sub in ("templates", "references"):
            if (d / sub).is_dir():
                for f in (d / sub).glob("*.md"):
                    rel = f"{sub}/{f.name}"
                    if rel not in body:
                        err(f"{f}: orphaned — not mentioned in {d.name}/SKILL.md")


def check_commands() -> None:
    cmd_dir = PLUGIN / "commands"
    if not cmd_dir.is_dir():
        return
    for f in sorted(cmd_dir.glob("*.md")):
        fm = frontmatter(f)
        if fm is None:
            continue
        if not isinstance(fm.get("description"), str) or not fm["description"]:
            err(f"{f}: missing/invalid description")
        hint = fm.get("argument-hint")
        if hint is not None and not isinstance(hint, str):
            err(f"{f}: argument-hint parsed as {type(hint).__name__}, quote it as a string")
        if "$ARGUMENTS" not in f.read_text(encoding="utf-8"):
            err(f"{f}: body does not use $ARGUMENTS")


def check_agents() -> None:
    for f in sorted((PLUGIN / "agents").glob("*.md")) if (PLUGIN / "agents").is_dir() else []:
        fm = frontmatter(f)
        if fm and not fm.get("description"):
            err(f"{f}: missing description")


def check_encoding_and_fences() -> None:
    for f in sorted(PLUGIN.rglob("*.md")):
        try:
            text = f.read_text(encoding="utf-8", errors="strict")
        except UnicodeDecodeError:
            err(f"{f}: not valid UTF-8")
            continue
        if text.startswith("﻿"):
            err(f"{f}: has a BOM")
        fences = sum(1 for line in text.splitlines() if line.strip().startswith("```"))
        if fences % 2:
            err(f"{f}: unbalanced code fences ({fences})")


def main() -> int:
    for check in (check_manifest, check_skills, check_commands, check_agents,
                  check_encoding_and_fences):
        check()
    if ERRORS:
        print(f"FAIL — {len(ERRORS)} problem(s):")
        for e in ERRORS:
            print(f"  - {e}")
        return 1
    print("PASS — plugin static validation clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
