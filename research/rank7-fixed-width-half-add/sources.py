# SPDX-License-Identifier: Apache-2.0
"""Authenticate frozen inputs and locate candidate literal word occurrences."""

import gzip
import hashlib
import io
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

from kernel import require

PACKAGE = Path(__file__).resolve().parent
SOURCE_COMMIT = "3da2ea9729f70b074713a5d0f69f0bdab32f2b47"
MAX_BYTES = 8_000_000


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def read(path: Path) -> object:
    require(path.is_file() and path.stat().st_size <= MAX_BYTES, "bounded file")
    raw = path.read_bytes()
    if path.suffix == ".gz":
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(MAX_BYTES + 1)
    require(len(raw) <= MAX_BYTES, "bounded decompressed input")
    return json.loads(raw)


def authenticate(package: Path = PACKAGE) -> dict[str, str]:
    records = read(package / "VENDOR.json")["files"]
    names = {
        "vendor/WORD-base.json.gz",
        "vendor/WORD-extra.json.gz",
        "vendor/CREDITS.md",
        "vendor/NOTICE",
    }
    require(
        len(records) == 4 and {r["path"] for r in records} == names, "frozen inventory"
    )
    result = {}
    for record in records:
        require(record["source_commit"] == SOURCE_COMMIT, "exact predecessor head")
        require(
            record["source_path"]
            == "research/rank7-primitive-lowering/" + record["path"],
            "predecessor path",
        )
        path = package / record["path"]
        require(path.resolve().is_relative_to(package.resolve()), "contained source")
        require(path.is_file() and path.stat().st_size <= MAX_BYTES, "bounded source")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        require(actual == record["sha256"], "source bytes: " + record["path"])
        result[record["path"]] = actual
    return result


def inventory(word: dict) -> dict:
    counts = Counter()
    occurrences = []
    examples = {}
    for phase in ("A", "B", "restore", "cleanup"):
        gates = word[phase]
        require(type(gates) is list and len(gates) <= 12_000, "bounded word phase")
        for index, gate in enumerate(gates):
            require(type(gate) is list and 1 <= len(gate) <= 6, "word gate")
            if gate[0] != "add":
                continue
            require(len(gate) == 6, "literal ADD shape")
            _, target, source, a, b, _frame = gate
            require(all(type(x) is int for x in (target, source, a, b)), "ADD integers")
            require(target != source and b > 0, "ADD arguments")
            q = Fraction(a, b)
            if abs(q.numerator) != 1 or q.denominator not in (2, 4, 8):
                continue
            key = str(q)
            counts[phase + ":" + key] += 1
            occurrences.append([phase, index, gate])
            examples.setdefault(key, {"phase": phase, "index": index, "gate": gate})
    return {
        "status": "candidates only; producer guards and ownership unverified",
        "count": len(occurrences),
        "by_phase_coefficient": dict(sorted(counts.items())),
        "occurrences_sha256": digest(occurrences),
        "first_examples": examples,
    }
