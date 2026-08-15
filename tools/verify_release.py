"""Release checks for the public research preview."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote

import yaml
from jsonschema import Draft202012Validator

from eup.cli import build_demo_receipt


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_HASH = "D942497DAB71573CA39A7021E6443C4F2AC4516513B92E0847D26BA5FEFB6A71"
FIXTURE_HASH = "2C2F8E2EB9477F1AD15682F3EDA1572C01A003C2EEC8E136FB4DF1A5C1B2BC89"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def validate_artifacts() -> None:
    archive = ROOT / "archive" / "Blueprint_Etica_do_Desconhecimento_v1.original.md"
    fixture_path = ROOT / "fixtures" / "demo-receipt.json"
    assert sha256(archive) == ARCHIVE_HASH, "historical archive digest changed"
    assert sha256(fixture_path) == FIXTURE_HASH, "demonstration fixture digest changed"

    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    assert fixture == build_demo_receipt(), "fresh demo differs from committed fixture"

    schemas = {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in (ROOT / "schemas").glob("*.json")
    }
    assert set(schemas) == {
        "consent-grant.schema.json",
        "ledger-record.schema.json",
        "policy-decision.schema.json",
    }
    for schema in schemas.values():
        Draft202012Validator.check_schema(schema)
    Draft202012Validator(schemas["policy-decision.schema.json"]).validate(
        fixture["decision"]
    )
    ledger_validator = Draft202012Validator(schemas["ledger-record.schema.json"])
    for record in fixture["ledger"]:
        ledger_validator.validate(record)

    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    assert citation["cff-version"] == "1.2.0"
    assert citation["version"] == "0.1.1"


def validate_local_links() -> None:
    markdown_link = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)#]+)(?:#[^)]+)?\)")
    html_link = re.compile(r'href=["\'](?!https?://|mailto:|#)([^"\'#]+)(?:#[^"\']*)?["\']')
    missing: list[str] = []
    for path in ROOT.rglob("*.md"):
        if any(part in {".venv", "__pycache__"} or part.endswith(".egg-info") for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        targets = [match.group(1) for match in markdown_link.finditer(text)]
        targets.extend(match.group(1) for match in html_link.finditer(text))
        for target in targets:
            resolved = path.parent / unquote(target)
            if not resolved.exists():
                missing.append(f"{path.relative_to(ROOT)} -> {target}")
    assert not missing, "missing local links:\n" + "\n".join(missing)


def validate_public_boundary() -> None:
    private_marker = chr(0xE200) + "filecite"
    for path in ROOT.rglob("*"):
        if not path.is_file() or "archive" in path.parts:
            continue
        if any(part in {".venv", "__pycache__"} or part.endswith(".egg-info") for part in path.parts):
            continue
        if path.suffix.lower() not in {".md", ".py", ".json", ".toml", ".yml", ".cff"}:
            continue
        text = path.read_text(encoding="utf-8")
        assert private_marker not in text, f"private citation marker in {path.relative_to(ROOT)}"


def main() -> int:
    validate_artifacts()
    validate_local_links()
    validate_public_boundary()
    print("release verification: archive, fixture, schemas, CFF, links, and boundaries OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
