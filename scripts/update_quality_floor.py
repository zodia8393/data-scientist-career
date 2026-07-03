#!/usr/bin/env python3
"""Ratchet the portfolio quality floor from a quality gate score artifact."""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime
from pathlib import Path


DEFAULT_STATE_FILE = Path("/DATA/HJ/prj/data-scientist-career/state/weekend-project-state.md")
BASE_QUALITY_FLOOR = 92.0
BASE_README_PRESENTATION_FLOOR = 94.0

ACTIVE_FLOOR_RE = re.compile(r"Active quality score floor:\s*`(?P<score>\d+(?:\.\d+)?)`")
LAST_UPDATED_RE = re.compile(r"^Last updated: .*$", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quality-gate", required=True, help="quality_gate_scores.csv path")
    parser.add_argument("--state-file", default=str(DEFAULT_STATE_FILE))
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_score(raw_score: str) -> tuple[float | None, str | None]:
    raw = raw_score.strip()
    try:
        score = float(raw)
    except ValueError:
        return None, "non-numeric score"
    if score < 0 or score >= 100:
        return None, "score must satisfy 0 <= score < 100; 100 is not allowed"
    if score >= 99 and "." not in raw:
        return None, "scores >=99 must be written with decimal precision"
    return score, None


def load_active_floor(state_file: Path) -> float:
    if not state_file.is_file():
        return BASE_QUALITY_FLOOR
    match = ACTIVE_FLOOR_RE.search(read_text(state_file))
    if not match:
        return BASE_QUALITY_FLOOR
    return max(BASE_QUALITY_FLOOR, float(match.group("score")))


def parse_quality_scores(path: Path) -> dict[str, object]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"empty quality gate file: {path}")
    if "score" not in rows[0]:
        raise ValueError(f"quality gate file has no score column: {path}")

    scores: list[float] = []
    presentation_scores: list[float] = []
    min_category = ""
    min_score = 100.0
    for row in rows:
        category = str(row.get("category", "")).strip() or "unknown category"
        score, error = parse_score(str(row.get("score", "")))
        if error:
            raise ValueError(f"{error} in {path}: {category}")
        scores.append(score)
        if score < min_score:
            min_score = score
            min_category = category
        if "portfolio presentation" in category.lower() or "readme" in category.lower():
            presentation_scores.append(score)

    return {
        "min_score": min_score,
        "min_category": min_category,
        "category_count": len(scores),
        "presentation_min": min(presentation_scores) if presentation_scores else None,
    }


def replace_active_floor(state_text: str, new_floor: float) -> str:
    replacement = f"Active quality score floor: `{new_floor:g}`"
    if ACTIVE_FLOOR_RE.search(state_text):
        state_text = ACTIVE_FLOOR_RE.sub(replacement, state_text, count=1)
    else:
        state_text = state_text.rstrip() + f"\n\n## Portfolio Quality Floor\n\n- {replacement}.\n"

    stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M KST")
    updated = f"Last updated: {stamp} quality floor ratchet"
    if LAST_UPDATED_RE.search(state_text):
        return LAST_UPDATED_RE.sub(updated, state_text, count=1)
    return updated + "\n\n" + state_text


def main() -> int:
    args = parse_args()
    quality_gate = Path(args.quality_gate)
    state_file = Path(args.state_file)

    current_floor = load_active_floor(state_file)
    summary = parse_quality_scores(quality_gate)
    min_score = float(summary["min_score"])
    presentation_min = summary["presentation_min"]
    presentation_floor = max(BASE_README_PRESENTATION_FLOOR, current_floor)

    payload: dict[str, object] = {
        "quality_gate": str(quality_gate),
        "state_file": str(state_file),
        "current_floor": current_floor,
        **summary,
        "presentation_floor": presentation_floor,
        "dry_run": args.dry_run,
    }

    if presentation_min is not None and float(presentation_min) < presentation_floor:
        payload["action"] = "blocked"
        payload["reason"] = "presentation score is below its required floor"
        print(json.dumps(payload, ensure_ascii=False))
        return 1

    if min_score <= current_floor:
        payload["action"] = "no_update"
        payload["reason"] = "minimum score did not exceed current floor"
        print(json.dumps(payload, ensure_ascii=False))
        return 0

    payload["new_floor"] = min_score
    if args.dry_run:
        payload["action"] = "would_update"
        print(json.dumps(payload, ensure_ascii=False))
        return 0

    if not state_file.is_file():
        raise FileNotFoundError(f"state file not found: {state_file}")
    state_file.write_text(replace_active_floor(read_text(state_file), min_score), encoding="utf-8")
    payload["action"] = "updated"
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
