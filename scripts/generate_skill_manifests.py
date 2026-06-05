from __future__ import annotations

import json
import hashlib
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skill"
MANIFEST_ROOT = ROOT / "manifests"

CATEGORIES = {
    "ai-ml",
    "devops",
    "data",
    "web",
    "security",
    "media",
    "productivity",
    "finance",
    "science",
    "networking",
}

CATEGORY_HINTS: list[tuple[str, tuple[str, ...]]] = [
    ("security", ("security", "auth", "oauth", "password", "secret", "pii", "privacy", "vulnerability", "cve", "tls", "kyc", "compliance", "policy", "risk", "redteam")),
    ("finance", ("finance", "financial", "investment", "portfolio", "fund", "bank", "banking", "market", "trading", "fx", "rate", "loan", "tax", "invoice", "valuation", "equity", "bond", "option", "lbo", "nav", "macro")),
    ("media", ("image", "photo", "video", "audio", "subtitle", "srt", "tts", "voice", "music", "transcribe", "gif", "png", "jpeg", "media", "design", "canva")),
    ("web", ("web", "website", "browser", "frontend", "html", "css", "react", "next", "page", "seo", "api", "http", "url", "fetch", "scrape", "crawl")),
    ("devops", ("git", "github", "repo", "docker", "kubernetes", "k8s", "ci", "deploy", "cloud", "server", "mcp", "plugin", "command", "hook", "terminal", "shell", "code", "test", "build", "vercel")),
    ("data", ("data", "dataset", "csv", "excel", "spreadsheet", "sql", "database", "schema", "json", "etl", "analytics", "query", "table", "report")),
    ("science", ("science", "research", "paper", "citation", "latex", "math", "olympiad", "lab", "medical", "health", "biology", "chemistry", "physics")),
    ("networking", ("network", "dns", "proxy", "vpn", "tcp", "udp", "packet", "pcap", "mqtt", "socket", "firewall")),
    ("ai-ml", ("ai", "agent", "llm", "claude", "prompt", "skill", "embedding", "rag", "model", "eval", "benchmark", "inference", "machine learning", "ml")),
]


def kebab(value: str, max_len: int = 50) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:max_len].strip("-") or "agent-skill"


def read_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, flags=re.S)
    if not match:
        return {}, text
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, raw = line.split(":", 1)
        meta[key.strip()] = raw.strip().strip('"').strip("'")
    return meta, match.group(2)


def compact_description(value: str, name: str) -> str:
    text = re.sub(r"\s+", " ", value).strip()
    text = re.split(r"(?<=[.!?])\s+", text)[0] if text else ""
    if len(text) < 10:
        text = f"Agent skill for {name.replace('-', ' ')} workflows."
    if len(text) > 200:
        text = text[:197].rstrip() + "..."
    return text


def classify(name: str, description: str, body: str) -> str:
    haystack = f"{name} {description} {body[:4000]}".lower()
    scores: Counter[str] = Counter()
    for category, words in CATEGORY_HINTS:
        for word in words:
            if word in haystack:
                scores[category] += 1
    if scores:
        return scores.most_common(1)[0][0]
    return "productivity"


def load_source(skill_dir: Path) -> dict:
    source_file = skill_dir / "_source.json"
    if not source_file.exists():
        return {}
    try:
        return json.loads(source_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def unique_manifest_path(category: str, base_name: str, source: dict, current: Path | None = None) -> tuple[Path, str]:
    name = kebab(base_name)
    path = MANIFEST_ROOT / category / f"{name}.json"
    if not path.exists() or (current is not None and path == current):
        return path, name
    owner = kebab(str(source.get("owner", "")))
    repo = kebab(str(source.get("repo", "")))
    source_key = json.dumps(source, sort_keys=True)
    digest = hashlib.sha1(source_key.encode("utf-8")).hexdigest()[:8]
    short_name = kebab(name, 40)
    for candidate in (f"{short_name}-{repo}", f"{short_name}-{owner}", f"{short_name}-{owner}-{repo}", f"{short_name}-{digest}"):
        candidate = kebab(candidate)
        path = MANIFEST_ROOT / category / f"{candidate}.json"
        if not path.exists() or (current is not None and path == current):
            return path, candidate
    for i in range(2, 100):
        candidate = kebab(f"{short_name}-{digest}-{i}")
        path = MANIFEST_ROOT / category / f"{candidate}.json"
        if not path.exists() or (current is not None and path == current):
            return path, candidate
    raise RuntimeError(f"Could not find unique manifest path for {base_name}")


def build_manifest(skill_dir: Path) -> tuple[dict, str]:
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    meta, body = read_frontmatter(text)
    source = load_source(skill_dir)
    raw_name = meta.get("name") or source.get("skill") or skill_dir.name.split("__")[-1]
    base_name = kebab(raw_name)
    description = compact_description(meta.get("description", ""), base_name)
    category = classify(base_name, description, body)
    manifest_name = base_name

    topic = base_name.replace("-", " ")
    repo = source.get("repo", "")
    source_tag = source.get("source", "skill")
    license_spdx = (source.get("license") or {}).get("spdx", "MIT")
    triggers = [
        f"use the {topic} agent skill",
        f"run a workflow for {topic}",
        f"help me with {topic}",
        f"我需要處理 {topic} 相關工作",
        f"幫我啟用 {topic} 這個 skill",
        f"用 agent skill 完成 {topic}",
    ]
    if repo:
        triggers.append(f"use {topic} from {repo}")

    manifest = {
        "name": manifest_name,
        "version": "0.1.0",
        "category": category,
        "description": description,
        "intent_triggers": triggers,
        "input_schema": {
            "task": {
                "type": "string",
                "required": True,
                "description": "Natural-language task or instruction for the agent skill.",
            },
            "context_path": {
                "type": "string",
                "required": False,
                "description": "Optional workspace path or file context for the skill.",
            },
        },
        "output_schema": {
            "format": "text",
            "fields": ["result", "notes"],
        },
        "examples": [
            {
                "intent": f"Use the {topic} skill for this task.",
                "invocation": f"codex --skill {base_name} \"<task>\"",
            }
        ],
        "error_codes": {
            "1": "Skill invocation failed or required context was missing.",
        },
        "tags": sorted({category, "agent-skill", source_tag, str(license_spdx).lower()}),
    }
    return manifest, category


def is_generated_skill_manifest(path: Path) -> bool:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return False
    return "agent-skill" in data.get("tags", [])


def remove_previous_generated_manifests() -> int:
    removed = 0
    for path in MANIFEST_ROOT.rglob("*.json"):
        if is_generated_skill_manifest(path):
            path.unlink()
            removed += 1
    return removed


def main() -> None:
    removed = remove_previous_generated_manifests()
    skill_files = sorted(SKILL_ROOT.rglob("SKILL.md"))
    written = []
    category_counts: Counter[str] = Counter()

    for skill_file in skill_files:
        if not skill_file.exists():
            continue
        skill_dir = skill_file.parent
        manifest, category = build_manifest(skill_dir)
        if category not in CATEGORIES:
            category = "productivity"
            manifest["category"] = category
        source_for_name = load_source(skill_dir)
        source_for_name["_relpath"] = str(skill_dir.relative_to(ROOT))
        output_path, unique_name = unique_manifest_path(category, manifest["name"], source_for_name)
        manifest["name"] = unique_name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append(
            {
                "skill_dir": str(skill_dir.relative_to(ROOT)),
                "manifest": str(output_path.relative_to(ROOT)),
                "name": manifest["name"],
                "category": category,
            }
        )
        category_counts[category] += 1

    index = {
        "removed_previous_generated": removed,
        "generated_count": len(written),
        "category_counts": dict(sorted(category_counts.items())),
        "items": written,
    }
    (SKILL_ROOT / "_manifest_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"removed_previous_generated": removed, "generated_count": len(written), "category_counts": index["category_counts"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
