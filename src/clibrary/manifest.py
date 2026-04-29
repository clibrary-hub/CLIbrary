"""
manifest.py — Load and validate CLI manifest files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = {"name", "description", "intent_triggers", "input_schema"}


class ManifestError(ValueError):
    pass


def load_manifest(path: str | Path) -> dict[str, Any]:
    """Load and validate a single manifest.json file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Manifest not found: {p}")

    with open(p, encoding="utf-8") as f:
        data = json.load(f)

    missing = REQUIRED_FIELDS - set(data.keys())
    if missing:
        raise ManifestError(f"Manifest {p.name} missing required fields: {missing}")

    return data


def load_manifests_from_dir(manifest_dir: str | Path) -> list[dict[str, Any]]:
    """
    Recursively load all manifest.json files under a directory.

    Parameters
    ----------
    manifest_dir : str | Path
        Root directory containing manifest subdirectories.

    Returns
    -------
    list[dict]
        List of validated manifest dicts, sorted by name.
    """
    root = Path(manifest_dir)
    manifests = []
    errors = []

    for manifest_file in sorted(root.rglob("manifest.json")):
        try:
            manifests.append(load_manifest(manifest_file))
        except (ManifestError, json.JSONDecodeError) as e:
            errors.append(f"{manifest_file}: {e}")

    if errors:
        import warnings
        warnings.warn(f"Skipped {len(errors)} invalid manifests:\n" + "\n".join(errors))

    return sorted(manifests, key=lambda m: m["name"])


def validate_manifest(data: dict[str, Any]) -> list[str]:
    """
    Validate a manifest dict. Returns a list of error strings (empty = valid).
    """
    errors = []

    missing = REQUIRED_FIELDS - set(data.keys())
    if missing:
        errors.append(f"Missing required fields: {missing}")

    if "intent_triggers" in data:
        triggers = data["intent_triggers"]
        if not isinstance(triggers, list) or len(triggers) == 0:
            errors.append("intent_triggers must be a non-empty list")
        elif len(triggers) < 3:
            errors.append(f"Recommend at least 3 intent_triggers (got {len(triggers)})")

    if "examples" in data:
        for i, ex in enumerate(data["examples"]):
            if "query" not in ex:
                errors.append(f"examples[{i}] missing 'query'")
            if "params" not in ex:
                errors.append(f"examples[{i}] missing 'params'")

    return errors
