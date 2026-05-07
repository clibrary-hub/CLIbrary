"""
validator.py — Validate CLIbrary manifest.json files against the schema.

Usage::

    from clibrary_hub import validator

    # 1) Validate a dict you already loaded
    result = validator.validate(manifest_dict)
    if result.ok:
        print("OK")
    else:
        for e in result.errors:   print("ERROR:", e)
        for w in result.warnings: print("WARN: ", w)

    # 2) Validate a single file
    result = validator.validate_file("manifests/data/sql-runner.json")

    # 3) Validate every manifest in a directory tree
    results = validator.validate_dir("manifests/")
    for path, r in results.items():
        if not r.ok:
            print(path, r.errors)

The validator runs entirely offline — no network calls, no LLM.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ── Schema constants ─────────────────────────────────────────────────────────

REQUIRED_FIELDS = (
    "name", "version", "category", "description",
    "intent_triggers", "input_schema", "output_schema",
)

ALLOWED_CATEGORIES = (
    "ai-ml", "data", "devops", "media", "web",
    "security", "productivity", "finance", "science", "networking",
)

ALLOWED_OUTPUT_FORMATS = ("json", "csv", "text")

ALLOWED_PARAM_TYPES = (
    "string", "integer", "number", "boolean", "array", "enum", "object",
)

NAME_RE = re.compile(r"^[a-z][a-z0-9-]{1,48}[a-z0-9]$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+([-+][0-9A-Za-z.-]+)?$")

DESC_MIN = 10
DESC_MAX = 200
TRIGGERS_MIN = 5

# Heuristic for non-ASCII (CJK etc.) presence in a trigger
_NON_ASCII_RE = re.compile(r"[^\x00-\x7F]")


# ── Result type ──────────────────────────────────────────────────────────────

@dataclass
class ValidationResult:
    """Outcome of validating one manifest.

    Attributes
    ----------
    ok : bool
        True when there are no errors. Warnings do not flip this.
    errors : list[str]
        Hard violations of the schema. Anything here means the manifest
        will not work correctly with the router.
    warnings : list[str]
        Soft suggestions (e.g. only one language in triggers, no examples).
        The manifest is technically valid but quality could be better.
    name : str | None
        The manifest's ``name`` field if it could be read, else None.
    """
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    name: str | None = None

    def __bool__(self) -> bool:  # truthy when valid
        return self.ok

    def __str__(self) -> str:
        head = "OK" if self.ok else f"FAIL ({len(self.errors)} errors)"
        if self.warnings:
            head += f", {len(self.warnings)} warnings"
        return f"{head}: {self.name or '<unnamed>'}"


# ── Core validators ──────────────────────────────────────────────────────────

def _check_name(value: Any, errs: list[str]) -> None:
    if not isinstance(value, str):
        errs.append("name: must be a string")
        return
    if not NAME_RE.match(value):
        errs.append(
            "name: must be lowercase kebab-case, start with a letter, "
            "end with a letter or digit, length 3-50 (got %r)" % value
        )


def _check_version(value: Any, errs: list[str]) -> None:
    if not isinstance(value, str) or not SEMVER_RE.match(value):
        errs.append(f"version: must be semver 'x.y.z' (got {value!r})")


def _check_category(value: Any, errs: list[str]) -> None:
    if value not in ALLOWED_CATEGORIES:
        errs.append(
            f"category: must be one of {ALLOWED_CATEGORIES} (got {value!r})"
        )


def _check_description(value: Any, errs: list[str]) -> None:
    if not isinstance(value, str):
        errs.append("description: must be a string")
        return
    n = len(value)
    if n < DESC_MIN or n > DESC_MAX:
        errs.append(
            f"description: length must be {DESC_MIN}-{DESC_MAX} chars (got {n})"
        )


def _check_intent_triggers(value: Any, errs: list[str], warns: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errs.append("intent_triggers: must be a non-empty list of strings")
        return
    if not all(isinstance(t, str) and t.strip() for t in value):
        errs.append("intent_triggers: every entry must be a non-empty string")
        return
    if len(value) < TRIGGERS_MIN:
        errs.append(
            f"intent_triggers: need at least {TRIGGERS_MIN} entries (got {len(value)})"
        )

    # Warnings only — quality hints
    has_cjk = any(_NON_ASCII_RE.search(t) for t in value)
    has_ascii_only = any(not _NON_ASCII_RE.search(t) for t in value)
    if not (has_cjk and has_ascii_only):
        warns.append(
            "intent_triggers: only one language detected — "
            "mixing languages improves cross-lingual routing"
        )

    # Near-duplicate check (very loose: case-insensitive set)
    lowered = [t.lower().strip() for t in value]
    if len(set(lowered)) < len(lowered):
        warns.append("intent_triggers: contains exact duplicates")


def _check_input_schema(value: Any, errs: list[str]) -> None:
    if not isinstance(value, dict):
        errs.append("input_schema: must be an object")
        return
    for key, spec in value.items():
        if not isinstance(spec, dict):
            errs.append(f"input_schema.{key}: must be an object with 'type'")
            continue
        t = spec.get("type")
        if t not in ALLOWED_PARAM_TYPES:
            errs.append(
                f"input_schema.{key}.type: must be one of "
                f"{ALLOWED_PARAM_TYPES} (got {t!r})"
            )


def _check_output_schema(value: Any, errs: list[str]) -> None:
    if not isinstance(value, dict):
        errs.append("output_schema: must be an object")
        return
    fmt = value.get("format")
    if fmt not in ALLOWED_OUTPUT_FORMATS:
        errs.append(
            f"output_schema.format: must be one of "
            f"{ALLOWED_OUTPUT_FORMATS} (got {fmt!r})"
        )


def _check_examples(value: Any, errs: list[str], warns: list[str]) -> None:
    if value is None:
        warns.append(
            "examples: missing — at least 1 example is strongly recommended "
            "(enables Path A template fill, no LLM cost)"
        )
        return
    if not isinstance(value, list):
        errs.append("examples: must be a list")
        return
    if not value:
        warns.append("examples: empty list — write at least one")
        return
    for i, ex in enumerate(value):
        if not isinstance(ex, dict):
            errs.append(f"examples[{i}]: must be an object")
            continue
        if "query" not in ex and "intent" not in ex:
            errs.append(f"examples[{i}]: missing 'query' (or 'intent') field")
        if "params" not in ex and "invocation" not in ex:
            errs.append(
                f"examples[{i}]: missing 'params' object "
                "(or legacy 'invocation' string)"
            )
    if len(value) < 3:
        warns.append(
            f"examples: only {len(value)} — recommend 3-5 for better A-path hit rate"
        )


def _check_error_codes(value: Any, warns: list[str]) -> None:
    if value is None:
        warns.append("error_codes: missing — define at least exit code '1'")
        return
    if not isinstance(value, dict) or "1" not in value:
        warns.append("error_codes: should at least define '1'")


# ── Public API ───────────────────────────────────────────────────────────────

def validate(manifest: dict[str, Any]) -> ValidationResult:
    """Validate a manifest dict and return a :class:`ValidationResult`.

    The manifest is **never** mutated.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(manifest, dict):
        return ValidationResult(
            ok=False,
            errors=["manifest must be a JSON object"],
        )

    missing = [f for f in REQUIRED_FIELDS if f not in manifest]
    for f in missing:
        errors.append(f"missing required field: {f!r}")

    if "name" in manifest:        _check_name(manifest["name"], errors)
    if "version" in manifest:     _check_version(manifest["version"], errors)
    if "category" in manifest:    _check_category(manifest["category"], errors)
    if "description" in manifest: _check_description(manifest["description"], errors)
    if "intent_triggers" in manifest:
        _check_intent_triggers(manifest["intent_triggers"], errors, warnings)
    if "input_schema" in manifest:
        _check_input_schema(manifest["input_schema"], errors)
    if "output_schema" in manifest:
        _check_output_schema(manifest["output_schema"], errors)

    _check_examples(manifest.get("examples"), errors, warnings)
    _check_error_codes(manifest.get("error_codes"), warnings)

    return ValidationResult(
        ok=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        name=manifest.get("name"),
    )


def validate_file(path: str | Path) -> ValidationResult:
    """Validate a single manifest.json file."""
    p = Path(path)
    if not p.exists():
        return ValidationResult(ok=False, errors=[f"file not found: {p}"])
    try:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return ValidationResult(ok=False, errors=[f"invalid JSON: {e}"])
    except OSError as e:
        return ValidationResult(ok=False, errors=[f"cannot read file: {e}"])
    return validate(data)


def validate_dir(directory: str | Path) -> dict[Path, ValidationResult]:
    """Recursively find every ``manifest.json`` and ``*.json`` under
    ``directory`` and validate each.

    Returns a dict mapping each file path to its :class:`ValidationResult`.
    """
    root = Path(directory)
    if not root.is_dir():
        raise NotADirectoryError(f"not a directory: {root}")

    results: dict[Path, ValidationResult] = {}
    for p in sorted(root.rglob("*.json")):
        # Skip non-manifest helpers like cli_meta.json / model_info.json
        if p.name in {
            "cli_meta.json", "trigger_meta.json",
            "example_meta.json", "model_info.json",
        }:
            continue
        results[p] = validate_file(p)
    return results


__all__ = [
    "ValidationResult",
    "validate",
    "validate_file",
    "validate_dir",
]
