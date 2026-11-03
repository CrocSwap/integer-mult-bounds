#!/usr/bin/env python3
"""Check the answered-open-questions ledger against its pinned sources.

Every row names an open question stored in one package's TASK.json and one or
more later packages whose README answers it. The check reads only the pinned
input bytes (SHA256 from SOURCES.json), requires each stored question to match
its TASK.json entry exactly, and requires each quote to be a substring of one
README line. Whether a quoted README answers the question is a reading recorded
in the row's status and note; this script does not decide it.

Standard library only. Explicit exceptions are used, so `python -O` keeps every
check active. Nothing is written.

Loop bounds are enforced before each loop runs: at most MAX_ROWS rows, at most
MAX_ANSWERS_PER_ROW answers per row, at most MAX_INPUTS pinned inputs and at
most MAX_INPUT_BYTES bytes per input (which bounds the line scans). Memory is
bounded by those limits; Python allocates dynamically, so there is no
preallocation.
"""

import copy
import hashlib
import json
import re
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
STATUSES = ("answered", "answered-by-scope-inclusion", "partial")
MIN_QUOTE = 20
MAX_ROWS = 100
MAX_ANSWERS_PER_ROW = 8
MAX_INPUTS = 200
MAX_INPUT_BYTES = 1_000_000


class LedgerError(Exception):
    """A ledger row or pin failed its check."""


def need(condition, message):
    if not condition:
        raise LedgerError(message)


def load_inputs():
    """Return {path: text} for every live input, after the SHA256 pin check."""
    sources = json.loads((PKG / "SOURCES.json").read_text(encoding="utf-8"))
    pins = {row["path"]: row["sha256"] for row in sources["files"]
            if row["usage"] == "input"}
    need(pins, "SOURCES.json declares no live input")
    need(len(pins) <= MAX_INPUTS, "too many pinned inputs")
    data = {}
    for path, digest in sorted(pins.items()):
        raw = (ROOT / path).read_bytes()
        need(len(raw) <= MAX_INPUT_BYTES, "pinned input is too large: " + path)
        need(hashlib.sha256(raw).hexdigest() == digest, "pin mismatch: " + path)
        data[path] = raw.decode("utf-8")
    return data


def cites_by_path(readme_text, package):
    """True if the README names the package as research/<name> or ../<name>."""
    pattern = r"(?:research/|\.\./)" + re.escape(package) + r"(?![\w-])"
    return re.search(pattern, readme_text) is not None


def check_row(row, data):
    for key in ("id", "asking", "answers", "status", "note"):
        need(key in row, "row lacks " + key)
    need(row["status"] in STATUSES, "unknown status in " + row["id"])
    need(isinstance(row["note"], str) and row["note"].strip(), "empty note in " + row["id"])

    asking = row["asking"]
    ask_path = "research/%s/TASK.json" % asking["package"]
    need(ask_path in data, "asking TASK.json is not a pinned input: " + ask_path)
    questions = [q["question"] for q in json.loads(data[ask_path])["open_questions"]]
    index = asking["question_index"]
    need(isinstance(index, int) and 0 <= index < len(questions),
         "question index out of range in " + row["id"])
    need(questions[index] == asking["question"], "question text differs in " + row["id"])
    need(questions.count(asking["question"]) == 1, "question not unique in " + row["id"])

    need(row["answers"], "no answering package in " + row["id"])
    need(len(row["answers"]) <= MAX_ANSWERS_PER_ROW, "too many answers in " + row["id"])
    for answer in row["answers"]:
        package = answer["package"]
        need(package != asking["package"], "package answers itself in " + row["id"])
        need("research/%s/TASK.json" % package in data,
             "answering package is not pinned: " + package)
        path = "research/%s/README.md" % package
        need(path in data, "answering README is not a pinned input: " + path)
        quote = answer["quote"]
        need(isinstance(quote, str) and "\n" not in quote and quote == quote.strip()
             and len(quote) >= MIN_QUOTE, "malformed quote in " + row["id"])
        need(any(quote in line for line in data[path].split("\n")),
             "quote not found in one line of %s (%s)" % (path, row["id"]))
        need(not cites_by_path(data[path], asking["package"]),
             "answering README already cites the asking package by path: " + path)


def controls(rows, data):
    """Each mutated copy of a real row must be rejected with LedgerError."""
    base = rows[0]
    other = next(r for r in rows if r["asking"]["package"] != base["asking"]["package"])

    def mutate(edit):
        row = copy.deepcopy(base)
        edit(row)
        return row

    cases = {
        "question text changed": mutate(lambda r: r["asking"].update(question=r["asking"]["question"] + " ")),
        "question index moved": mutate(lambda r: r["asking"].update(question_index=0)),
        "quote not in README": mutate(lambda r: r["answers"][0].update(quote="a line that no pinned README contains")),
        "quote spans a newline": mutate(lambda r: r["answers"][0].update(quote="first line of a quote\nsecond line of it")),
        "quote too short": mutate(lambda r: r["answers"][0].update(quote="five-vertex")),
        "package answers itself": mutate(lambda r: r["answers"][0].update(package=r["asking"]["package"])),
        "answering package unpinned": mutate(lambda r: r["answers"][0].update(package="not-a-pinned-package")),
        "unknown status": mutate(lambda r: r.update(status="settled")),
        "no answering package": mutate(lambda r: r.update(answers=[])),
        "quote taken from another row": mutate(lambda r: r["answers"][0].update(quote=other["answers"][0]["quote"])),
    }
    cited = dict(data)
    path = "research/%s/README.md" % base["answers"][0]["package"]
    cited[path] = data[path] + "\nSee ../%s/README.md for the question.\n" % base["asking"]["package"]
    attempts = ([(name, row, data) for name, row in cases.items()]
                + [("answering README cites the asking package by path", copy.deepcopy(base), cited)])
    for name, row, table in attempts:
        try:
            check_row(row, table)
        except LedgerError:
            continue
        raise LedgerError("control was accepted: " + name)
    return len(attempts)


def main():
    ledger_bytes = (PKG / "ledger.json").read_bytes()
    ledger = json.loads(ledger_bytes.decode("utf-8"))
    need(ledger.get("schema") == "answered-open-questions-ledger/v1", "unknown ledger schema")
    rows = ledger["rows"]
    need(rows, "empty ledger")
    need(len(rows) <= MAX_ROWS, "too many rows")
    need(len({r["id"] for r in rows}) == len(rows), "duplicate row id")
    need(len({(r["asking"]["package"], r["asking"]["question_index"]) for r in rows}) == len(rows),
         "a question appears in two rows")
    data = load_inputs()
    for row in rows:
        check_row(row, data)
    n_controls = controls(rows, data)
    counts = {s: sum(1 for r in rows if r["status"] == s) for s in STATUSES}
    answering = {a["package"] for r in rows for a in r["answers"]}
    asking = {r["asking"]["package"] for r in rows}
    print("PASS_ANSWERED_OPEN_QUESTIONS_LEDGER rows=%d answered=%d scope_inclusion=%d partial=%d "
          "asking_packages=%d answering_packages=%d pinned_inputs=%d controls=%d ledger_sha256=%s"
          % (len(rows), counts["answered"], counts["answered-by-scope-inclusion"], counts["partial"],
             len(asking), len(answering), len(data), n_controls,
             hashlib.sha256(ledger_bytes).hexdigest()[:16]))


if __name__ == "__main__":
    main()
