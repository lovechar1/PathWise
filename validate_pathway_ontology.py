#!/usr/bin/env python3
"""Validate ontology-backed references in PathWise pathway JSON files."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


CATEGORY_BY_REFERENCE = {
    "pathway": "biological pathways",
    "biological entity": "biological entities",
    "relationship": "relationship types",
    "organism": "organisms",
}


@dataclass(frozen=True)
class MissingReference:
    category: str
    value: str
    file: Path
    json_path: str


def load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def ontology_ids(ontology: object) -> dict[str, set[str]]:
    if not isinstance(ontology, dict) or not isinstance(ontology.get("categories"), list):
        raise ValueError("ontology must be an object containing a 'categories' array")

    result: dict[str, set[str]] = {}
    for category in ontology["categories"]:
        if not isinstance(category, dict):
            continue
        name = category.get("category")
        terms = category.get("terms")
        if isinstance(name, str) and isinstance(terms, list):
            result[name] = {
                term["id"]
                for term in terms
                if isinstance(term, dict) and isinstance(term.get("id"), str)
            }

    missing_categories = sorted(set(CATEGORY_BY_REFERENCE.values()) - result.keys())
    if missing_categories:
        raise ValueError(
            "ontology is missing required categories: " + ", ".join(missing_categories)
        )
    return result


def add_if_missing(
    missing: list[MissingReference],
    known: dict[str, set[str]],
    reference_type: str,
    value: object,
    file: Path,
    json_path: str,
) -> None:
    if not isinstance(value, str):
        raise ValueError(f"{file}: {json_path} must be a string")
    category = CATEGORY_BY_REFERENCE[reference_type]
    if value not in known[category]:
        missing.append(MissingReference(category, value, file, json_path))


def validate_pathway(path: Path, known: dict[str, set[str]]) -> list[MissingReference]:
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: pathway JSON must contain an object")

    missing: list[MissingReference] = []
    add_if_missing(missing, known, "pathway", path.stem, path, "<filename>")

    key_events = data.get("key_events", [])
    if not isinstance(key_events, list):
        raise ValueError(f"{path}: key_events must be an array")
    for index, event in enumerate(key_events):
        if not isinstance(event, dict):
            raise ValueError(f"{path}: key_events[{index}] must be an object")
        if "biological_entity_id" in event:
            add_if_missing(
                missing,
                known,
                "biological entity",
                event["biological_entity_id"],
                path,
                f"key_events[{index}].biological_entity_id",
            )
        species = event.get("species_annotation", {})
        if not isinstance(species, dict):
            raise ValueError(f"{path}: key_events[{index}].species_annotation must be an object")
        for organism in species:
            add_if_missing(
                missing,
                known,
                "organism",
                organism,
                path,
                f"key_events[{index}].species_annotation.{organism}",
            )

    relationships = data.get("key_event_relationships", [])
    if not isinstance(relationships, list):
        raise ValueError(f"{path}: key_event_relationships must be an array")
    for index, relationship in enumerate(relationships):
        if not isinstance(relationship, dict):
            raise ValueError(f"{path}: key_event_relationships[{index}] must be an object")
        values = relationship.get("relationship", [])
        if not isinstance(values, list):
            raise ValueError(
                f"{path}: key_event_relationships[{index}].relationship must be an array"
            )
        for value_index, value in enumerate(values):
            add_if_missing(
                missing,
                known,
                "relationship",
                value,
                path,
                f"key_event_relationships[{index}].relationship[{value_index}]",
            )
        for field in ("active_in", "absent_in"):
            organisms = relationship.get(field, [])
            if not isinstance(organisms, list):
                raise ValueError(
                    f"{path}: key_event_relationships[{index}].{field} must be an array"
                )
            for organism_index, organism in enumerate(organisms):
                add_if_missing(
                    missing,
                    known,
                    "organism",
                    organism,
                    path,
                    f"key_event_relationships[{index}].{field}[{organism_index}]",
                )
    return missing


def markdown_report(missing: Iterable[MissingReference]) -> str:
    grouped: dict[tuple[str, str], list[MissingReference]] = defaultdict(list)
    for item in missing:
        grouped[(item.category, item.value)].append(item)

    lines = ["# Missing PathWise ontology entries", ""]
    if not grouped:
        lines.extend(["All pathway references exist in the ontology.", ""])
        return "\n".join(lines)

    lines.extend(
        [
            f"Found **{len(grouped)} unique missing entries** across "
            f"**{sum(len(items) for items in grouped.values())} references**.",
            "",
        ]
    )
    for category in sorted({category for category, _ in grouped}):
        lines.extend([f"## {category}", ""])
        for key in sorted(key for key in grouped if key[0] == category):
            lines.append(f"- `{key[1]}`")
            for item in sorted(grouped[key], key=lambda item: (str(item.file), item.json_path)):
                lines.append(f"  - `{item.file}` — `{item.json_path}`")
        lines.append("")
    return "\n".join(lines)


def emit_github_annotations(missing: Iterable[MissingReference]) -> None:
    for item in missing:
        message = (
            f"'{item.value}' is not defined in ontology category '{item.category}' "
            f"(JSON path: {item.json_path})"
        )
        print(f"::error file={item.file}::{message}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check pathway JSON references against the PathWise ontology."
    )
    parser.add_argument("paths", nargs="*", type=Path, help="Pathway JSON files")
    parser.add_argument(
        "--changed-from",
        metavar="GIT_REF",
        help=(
            "Validate pathway files changed since GIT_REF. If the ontology changed, "
            "validate every pathway file."
        ),
    )
    parser.add_argument(
        "--ontology", type=Path, default=Path("pathwise_ontology.json")
    )
    parser.add_argument(
        "--report", type=Path, default=Path("missing_ontology_entries.md")
    )
    return parser.parse_args()


def select_paths(explicit_paths: list[Path], changed_from: str | None) -> list[Path]:
    if explicit_paths:
        return explicit_paths
    all_pathways = sorted(Path("pathways").glob("*.json"))
    if not changed_from:
        return all_pathways

    result = subprocess.run(
        ["git", "diff", "--name-only", f"{changed_from}...HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    changed = {Path(line) for line in result.stdout.splitlines() if line}
    if Path("pathwise_ontology.json") in changed:
        return all_pathways
    return sorted(
        path
        for path in changed
        if path.parent == Path("pathways") and path.suffix == ".json" and path.exists()
    )


def main() -> int:
    args = parse_args()
    try:
        paths = select_paths(args.paths, args.changed_from)
        known = ontology_ids(load_json(args.ontology))
        missing = [item for path in paths for item in validate_pathway(path, known)]
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError, ValueError) as error:
        print(f"Validation could not run: {error}", file=sys.stderr)
        return 2

    report = markdown_report(missing)
    args.report.write_text(report, encoding="utf-8")
    if summary_path := os.environ.get("GITHUB_STEP_SUMMARY"):
        with Path(summary_path).open("a", encoding="utf-8") as summary:
            summary.write(report)

    if missing:
        emit_github_annotations(missing)
        unique_count = len({(item.category, item.value) for item in missing})
        print(
            f"Ontology validation failed: {unique_count} unique entries are missing. "
            f"See {args.report}."
        )
        return 1

    print(f"Ontology validation passed for {len(paths)} pathway file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
