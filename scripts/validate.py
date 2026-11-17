#!/usr/bin/env python3
"""Validate the skill pack document against the app's loader limits and the registry shape.

The app's loader CUTS and DROPS what is over its caps, silently. A translation is where that
matters: Korean prose can run longer than the English it replaces, and a body over 8,000
characters would reach the agent truncated. So every cap the loader applies is checked here.

A pack written since the pack page (2026-11-09) carries two texts: `summary`, the one line a card
shows, and `description`, the pack's page in Markdown. The registry lists no pack without both
(verify_pinned.py), so a document with `summary` is held to both caps. One without it is the older
shape, where `description` is the one line, and is still accepted because the app still loads it.

The repo README is checked too: its version, identifier, applies-to and requires rows must agree
with the document, and every section id must be named there. A stale README is the first thing a
reviewer reads, and it drifts silently because nothing else compares it with the JSON. Both the
Korean and the English README spellings are accepted, so the same check runs on either repo.

Run: python3 scripts/validate.py [ROOT]   (ROOT defaults to this repo; pass the English repo to check it the same way)
"""

from __future__ import annotations

import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
IDENTIFIER_RE = re.compile(r"^(?:[a-z0-9]+(?:-[a-z0-9]+)*\.){2,}skillpacks\.[a-z0-9_]+$")
PLUGIN_ID_RE = re.compile(r"^(?:[a-z0-9]+(?:-[a-z0-9]+)*\.){2,}(?:plugins|pluginpacks)\.[a-z0-9_]+$")
NODE_TYPE_RE = re.compile(r"^[a-z][a-z0-9_]{0,30}\.[a-z][a-z0-9_]{0,30}$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+].+)?$")
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VARIABLE_KEY_RE = re.compile(r"^[A-Za-z0-9_.-]{1,40}$")
BLANK_RE = re.compile(r"\{\{\s*([\w.-]+)\s*\}\}")
QUOTED_ID_RE = re.compile(r'"([a-z0-9]+(?:-[a-z0-9]+)*)"')

LIMITS = {
    "identifier": 200,
    "name": 128,
    "description": 240,
    "summary": 250,
    "page": 16000,
    "author": 128,
    "version": 64,
    "overview": 8000,
    "sections": 64,
    "section_id": 120,
    "body": 8000,
    "starters": 48,
    "starter_id": 120,
    "starter_label": 80,
    "starter_summary": 200,
    "category": 40,
    "prompt": 1200,
    "variables": 8,
    "variable_label": 80,
    "placeholder": 120,
    "label_items": 32,
    "label": 240,
}

errors: list[str] = []
warnings: list[str] = []


def err(where: str, message: str) -> None:
    errors.append(f"{where}: {message}")


def warn(where: str, message: str) -> None:
    warnings.append(f"{where}: {message}")


def one_line(value: object, where: str, cap: int, required: bool = True) -> None:
    if not isinstance(value, str):
        err(where, "must be text")
        return
    if required and not value:
        err(where, "is required")
    if value != " ".join(value.split()):
        err(where, "must be one line with no leading/trailing or repeated spaces")
    if len(value) > cap:
        err(where, f"is {len(value)} characters, over the {cap}-character limit")


def text(value: object, where: str, cap: int, required: bool = True) -> None:
    if not isinstance(value, str):
        err(where, "must be text")
        return
    if required and not value.strip():
        err(where, "is required")
    if "\r" in value:
        err(where, "must not contain a carriage return")
    if len(value) > cap:
        err(where, f"is {len(value)} characters, over the {cap}-character limit")


def labels(value: object, where: str, each=None) -> None:
    if not isinstance(value, list):
        err(where, "must be a list")
        return
    if len(value) > LIMITS["label_items"]:
        err(where, f"has {len(value)} items, over the {LIMITS['label_items']}-item limit")
    if len(set(value)) != len(value):
        err(where, "has duplicate items")
    for i, item in enumerate(value):
        one_line(item, f"{where}[{i}]", LIMITS["label"])
        if each and isinstance(item, str):
            each(item, f"{where}[{i}]")


def validate(path: Path) -> None:
    rel = path.relative_to(ROOT)
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        err(str(rel), f"cannot read JSON: {exc}")
        return
    if not isinstance(doc, dict):
        err(str(rel), "must be a JSON object")
        return

    required = {"content_type", "identifier", "name", "description", "author", "version", "overview"}
    if "summary" in doc:
        required.add("summary")
    missing = required - set(doc)
    if missing:
        err(str(rel), f"missing required keys: {sorted(missing)}")

    if doc.get("content_type") != "vineyard:skillpack":
        err(str(rel), 'content_type must be "vineyard:skillpack"')

    one_line(doc.get("identifier"), "identifier", LIMITS["identifier"])
    ident = doc.get("identifier")
    if isinstance(ident, str) and ident and not IDENTIFIER_RE.match(ident):
        err("identifier", "does not match the registry skillpack identifier pattern")
    one_line(doc.get("name"), "name", LIMITS["name"])
    if "summary" in doc:
        one_line(doc.get("summary"), "summary", LIMITS["summary"])
        text(doc.get("description"), "description", LIMITS["page"])
        page = doc.get("description")
        # The page may hold newlines and tabs and nothing else below U+0020: the registry refuses the
        # rest, and a carriage return is already refused by text().
        if isinstance(page, str) and re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", page):
            err("description", "the page may hold newlines and tabs, and no other control characters")
    else:
        one_line(doc.get("description"), "description", LIMITS["description"])
    one_line(doc.get("author"), "author", LIMITS["author"])
    one_line(doc.get("version"), "version", LIMITS["version"])
    version = doc.get("version")
    if isinstance(version, str) and version and not VERSION_RE.match(version):
        err("version", "is not SemVer")

    labels(doc.get("applies_to", []), "applies_to",
           lambda v, w: None if NODE_TYPE_RE.match(v) else err(w, "is not a category.name node type"))
    labels(doc.get("triggers", []), "triggers")
    labels(doc.get("requires", []), "requires",
           lambda v, w: None if PLUGIN_ID_RE.match(v) else err(w, "is not a plugin pack identifier"))

    overview = doc.get("overview")
    text(overview, "overview", LIMITS["overview"])
    overview_ok = isinstance(overview, str)

    sections = doc.get("sections")
    section_ids: set[str] = set()
    if not isinstance(sections, list):
        err("sections", "must be a list")
        sections = []
    elif len(sections) > LIMITS["sections"]:
        err("sections", f"has {len(sections)} items, over the {LIMITS['sections']}-item limit")
    for i, sec in enumerate(sections):
        at = f"sections[{i}]"
        if not isinstance(sec, dict):
            err(at, "must be an object")
            continue
        extra = set(sec) - {"id", "summary", "body"}
        if extra:
            err(at, f"has unknown fields: {sorted(extra)}")
        sid = sec.get("id")
        if not isinstance(sid, str) or not sid:
            err(f"{at}.id", "is required")
            continue
        if len(sid) > LIMITS["section_id"]:
            err(f"{at}.id", f"is over the {LIMITS['section_id']}-character limit")
        if not ID_RE.match(sid):
            err(f"{at}.id", "is not lowercase letters, digits and single hyphens")
        if sid in section_ids:
            err(f"{at}.id", f'"{sid}" is used by another section')
        section_ids.add(sid)
        one_line(sec.get("summary", ""), f"{at}.summary", LIMITS["label"], required=False)
        text(sec.get("body", ""), f"{at}.body", LIMITS["body"], required=False)
        if overview_ok and f'"{sid}"' not in overview:
            warn(f"{at}.id", f'the overview does not mention "{sid}"')

    starters = doc.get("starters", [])
    if not isinstance(starters, list):
        err("starters", "must be a list")
        starters = []
    elif len(starters) > LIMITS["starters"]:
        err("starters", f"has {len(starters)} items, over the {LIMITS['starters']}-item limit")
    starter_ids: set[str] = set()
    for i, st in enumerate(starters):
        at = f"starters[{i}]"
        if not isinstance(st, dict):
            err(at, "must be an object")
            continue
        extra = set(st) - {"id", "label", "category", "summary", "prompt", "variables"}
        if extra:
            err(at, f"has unknown fields: {sorted(extra)}")
        sid = st.get("id")
        if not isinstance(sid, str) or not sid:
            err(f"{at}.id", "is required")
            sid = None
        else:
            if len(sid) > LIMITS["starter_id"]:
                err(f"{at}.id", f"is over the {LIMITS['starter_id']}-character limit")
            if not ID_RE.match(sid):
                err(f"{at}.id", "is not lowercase letters, digits and single hyphens")
            if sid in starter_ids:
                err(f"{at}.id", f'"{sid}" is used by another starter')
            starter_ids.add(sid)
        one_line(st.get("label"), f"{at}.label", LIMITS["starter_label"])
        if "category" in st:
            one_line(st.get("category"), f"{at}.category", LIMITS["category"], required=False)
            category = st.get("category")
            if isinstance(category, str) and category != category.strip():
                err(f"{at}.category", "must be trimmed")
        if "summary" in st:
            one_line(st.get("summary"), f"{at}.summary", LIMITS["starter_summary"], required=False)
        prompt = st.get("prompt")
        text(prompt, f"{at}.prompt", LIMITS["prompt"])

        declared: set[str] = set()
        variables = st.get("variables", [])
        if not isinstance(variables, list):
            err(f"{at}.variables", "must be a list")
            variables = []
        elif len(variables) > LIMITS["variables"]:
            err(f"{at}.variables", f"has {len(variables)} items, over the {LIMITS['variables']}-item limit")
        for j, var in enumerate(variables):
            vat = f"{at}.variables[{j}]"
            if not isinstance(var, dict):
                err(vat, "must be an object")
                continue
            extra = set(var) - {"key", "label", "placeholder", "required", "multiline"}
            if extra:
                err(vat, f"has unknown fields: {sorted(extra)}")
            key = var.get("key")
            if not isinstance(key, str) or not key:
                err(f"{vat}.key", "is required")
            else:
                if key in declared:
                    err(f"{vat}.key", f"{{{{{key}}}}} is declared twice")
                declared.add(key)
                if not VARIABLE_KEY_RE.match(key):
                    err(f"{vat}.key", "is not letters, digits, '.', '_' or '-'")
            one_line(var.get("label"), f"{vat}.label", LIMITS["variable_label"])
            if "placeholder" in var:
                one_line(var.get("placeholder"), f"{vat}.placeholder", LIMITS["placeholder"], required=False)
            for flag in ("required", "multiline"):
                if flag in var and not isinstance(var[flag], bool):
                    err(f"{vat}.{flag}", "must be true or false")

        if isinstance(prompt, str):
            used = set(BLANK_RE.findall(prompt))
            for key in sorted(used - declared):
                err(f"{at}.prompt", f"{{{{{key}}}}} is not a declared variable")
            for key in sorted(declared - used):
                err(f"{at}.prompt", f"variable '{key}' is never used")
            for quoted in QUOTED_ID_RE.findall(prompt):
                if quoted not in section_ids:
                    warn(f"{at}.prompt", f'"{quoted}" is not a section id')

    readme_check(doc, str(rel))


README_ROWS = {
    "version": ("Version", "버전"),
    "identifier": ("Identifier", "식별자"),
    "applies_to": ("Applies to", "적용 대상"),
    "requires": ("Requires", "필요"),
}


def readme_row(text: str, names: tuple[str, ...]) -> str | None:
    """The README table row whose first cell is one of `names`, as its cells. None when absent."""
    pattern = r"^\|\s*(?:" + "|".join(re.escape(n) for n in names) + r")\s*\|(.+)\|\s*$"
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1) if match else None


def readme_check(doc: dict, where: str) -> None:
    path = ROOT / "README.md"
    if not path.is_file():
        warn(where, "the repo has no README.md, so the README was not checked")
        return
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        err(str(path), f"cannot read README: {exc}")
        return

    rows = {key: readme_row(text, names) for key, names in README_ROWS.items()}
    ticked = {key: re.findall(r"`([^`]+)`", row) if row else [] for key, row in rows.items()}

    for key, document_key in (("version", "version"), ("identifier", "identifier")):
        if rows[key] is None:
            warn(str(path), f"no {README_ROWS[key][0]} row, so that value was not compared with the document")
        elif len(ticked[key]) != 1:
            err(str(path), f"the {README_ROWS[key][0]} row holds {len(ticked[key])} backticked values; expected one")
        elif ticked[key][0] != str(doc.get(document_key)):
            err(str(path), f'the {README_ROWS[key][0]} row says "{ticked[key][0]}" but the document says "{doc.get(document_key)}"')

    for key in ("applies_to", "requires"):
        if rows[key] is None:
            warn(str(path), f"no {README_ROWS[key][0]} row, so that list was not compared with the document")
            continue
        listed, document = set(ticked[key]), set(doc.get(key) or [])
        missing = sorted(document - listed)
        extra = sorted(listed - document)
        if missing:
            err(str(path), f"the {README_ROWS[key][0]} row is missing {', '.join(missing)}")
        if extra:
            err(str(path), f"the {README_ROWS[key][0]} row lists {', '.join(extra)}, which the document does not")

    if "## Structure" not in text:
        warn(str(path), "no ## Structure heading, so the README section list was not checked")
        return
    missing_sections = [sec["id"] for sec in doc.get("sections", []) if f"`{sec['id']}`" not in text]
    if missing_sections:
        err(str(path), f"the README Structure section does not name {', '.join(missing_sections)}")


def main() -> int:
    paths = sorted(Path(p) for p in glob.glob(str(ROOT / "skillpacks" / "*.json")))
    if not paths:
        print("::error::no skillpack documents under skillpacks/*.json")
        return 1
    for path in paths:
        validate(path)
    for message in warnings:
        print(f"::warning::{message}")
    for message in errors:
        print(f"::error::{message}")
    if errors:
        print(f"{len(errors)} problem(s)")
        return 1
    print(f"all {len(paths)} skill pack document(s) well-formed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
