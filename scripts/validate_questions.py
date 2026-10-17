"""Validate the question bank under data/.

Checks every question file: JSON parses (utf-8), wrapper fields match the
directory layout, elimination items have 4 options and an in-range `correct`,
ids are unique per file, and no duplicate question strings per file.

Usage: python scripts/validate_questions.py
"""

import io
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
DIFFICULTIES = {"easy", "average", "difficult"}


def check_file(path: Path, errors: list[str]) -> None:
    rel = path.relative_to(DATA)
    try:
        doc = json.load(io.open(path, encoding="utf-8"))
    except Exception as e:
        errors.append(f"{rel}: unreadable JSON: {e}")
        return

    parts = rel.parts
    mode = parts[2] if len(parts) > 2 else "?"
    expected_mode = "finals" if mode == "finals" else "elimination"
    if doc.get("mode") != expected_mode:
        errors.append(f"{rel}: mode={doc.get('mode')!r}, expected {expected_mode!r}")
    if doc.get("subtopic_id") != parts[1]:
        errors.append(f"{rel}: subtopic_id={doc.get('subtopic_id')!r} != dir {parts[1]!r}")
    if expected_mode == "finals":
        diff = parts[3] if len(parts) > 3 else "?"
        if diff not in DIFFICULTIES:
            errors.append(f"{rel}: unexpected difficulty dir {diff!r}")
        if doc.get("difficulty") != diff:
            errors.append(f"{rel}: difficulty={doc.get('difficulty')!r} != dir {diff!r}")

    questions = doc.get("questions")
    if not isinstance(questions, list) or not questions:
        errors.append(f"{rel}: missing/empty questions list")
        return

    ids: set[str] = set()
    texts: set[str] = set()
    for i, q in enumerate(questions):
        where = f"{rel} [{i}]"
        if not isinstance(q.get("question"), str) or not q["question"].strip():
            errors.append(f"{where}: empty question")
        if q.get("id") in ids:
            errors.append(f"{where}: duplicate id {q.get('id')!r}")
        ids.add(q.get("id"))
        text = q.get("question", "").strip().lower()
        if text in texts:
            errors.append(f"{where}: duplicate question text")
        texts.add(text)
        if not isinstance(q.get("explanation"), str) or not q["explanation"].strip():
            errors.append(f"{where}: missing explanation")

        if expected_mode == "elimination":
            opts = q.get("options")
            if not isinstance(opts, list) or len(opts) != 4:
                errors.append(f"{where}: options must be 4, got {len(opts) if isinstance(opts, list) else opts!r}")
            elif len(set(opts)) != 4:
                errors.append(f"{where}: duplicate options")
            if not isinstance(q.get("correct"), int) or not 0 <= q["correct"] < 4:
                errors.append(f"{where}: bad correct index {q.get('correct')!r}")
        else:
            if not isinstance(q.get("answer"), str) or not q["answer"].strip():
                errors.append(f"{where}: missing answer")
            if not isinstance(q.get("alternatives"), list):
                errors.append(f"{where}: alternatives must be a list")


def main() -> int:
    errors: list[str] = []
    files = sorted(DATA.glob("*/*/elimination/*.json")) + sorted(
        DATA.glob("*/*/finals/*/*.json")
    )
    counts = {"files": len(files), "questions": 0}
    for f in files:
        check_file(f, errors)
        try:
            counts["questions"] += len(json.load(io.open(f, encoding="utf-8"))["questions"])
        except Exception:
            pass

    for e in errors:
        print(f"ERROR {e}")
    print(f"{counts['files']} files, {counts['questions']} questions, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
