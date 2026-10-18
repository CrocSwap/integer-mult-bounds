#!/usr/bin/env python3
"""Read V45 in the shipped words: end frames, buffers, and recorded caps.

The four helpers already exist in the parent and end on the rank-7 subspace in
both shipped words. The five new private buffers are the later extractions.
The recorded fixed-capacity brackets rise at that stage. This does not re-solve
the caps or admit the claimed exponent.
"""

import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
DATA = ROOT / "research/rank7-joint-endframes"
HELPERS = ("249", "251", "265", "267")
SUBSPACE = [256, 128, 64, 35, 16, 11, 5]
PARENT_FRAME = [256, 128, 64, 33, 16, 9, 5, 2]
EXTRACTIONS = ("226", "228", "230", "363", "395")
MARKER = (
    "PASS_RANK7_V45_SHIPPED_INVOICE helpers=4 buffers=86to91 "
    "v45_buffers_added=0 caps_rise no_new_kappa"
)


def fail(message):
    raise SystemExit("FAIL_RANK7_V45_SHIPPED_INVOICE " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)


def basis_of(vectors):
    basis = []
    for value in vectors:
        reduced = value
        for row in basis:
            candidate = reduced ^ row
            if candidate < reduced:
                reduced = candidate
        if reduced:
            basis.append(reduced)
            basis.sort(reverse=True)
    return basis


def contained(vectors, ambient):
    basis = basis_of(ambient)

    def reduces(value):
        reduced = value
        for row in basis:
            candidate = reduced ^ row
            if candidate < reduced:
                reduced = candidate
        return reduced == 0

    return all(reduces(value) for value in vectors)


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/rank7-joint-endframes/data/WORD-base.json.gz",
        "research/rank7-joint-endframes/data/WORD-extra.json.gz",
        "research/rank7-joint-endframes/data/PARENT-base.json.gz",
        "research/rank7-joint-endframes/data/PARENT-extra.json.gz",
        "research/rank7-joint-endframes/certificates/RELAX-STAGES.json",
        "research/rank7-joint-endframes/certificates/RELAX-CAP.json",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def finals(word):
    return {helper: word["helper_final"][helper] for helper in HELPERS}


def evaluate():
    authenticate()
    shipped = [load(DATA / "data" / name) for name in ("WORD-base.json.gz", "WORD-extra.json.gz")]
    parents = [load(DATA / "data" / name) for name in ("PARENT-base.json.gz", "PARENT-extra.json.gz")]
    require(len(basis_of(PARENT_FRAME)) == 8 and len(basis_of(SUBSPACE)) == 7, "frame ranks changed")
    require(contained(SUBSPACE, PARENT_FRAME), "the subspace is not inside the parent frame")
    for word in shipped:
        require(finals(word) == {helper: SUBSPACE for helper in HELPERS}, "a shipped word moved V45")
        require(len(word["helper_final"]) == 91, "shipped buffer count changed")
    for word in parents:
        require(finals(word) == {helper: PARENT_FRAME for helper in HELPERS}, "a parent word moved V45")
        require(len(word["helper_final"]) == 86, "parent buffer count changed")
    added = sorted(set(shipped[0]["helper_final"]) - set(parents[0]["helper_final"]), key=int)
    require(tuple(added) == EXTRACTIONS, "the new buffers are not the five extractions")
    require(set(shipped[1]["helper_final"]) - set(parents[1]["helper_final"]) == set(added), "providers disagree on new buffers")
    require(all(helper in parents[0]["helper_final"] for helper in HELPERS), "V45 added a buffer")

    stages = load(DATA / "certificates/RELAX-STAGES.json")
    final = load(DATA / "certificates/RELAX-CAP.json")
    brackets = [
        ("parent", stages["parent"]["cap_lower"], stages["parent"]["cap_upper"]),
        ("stage1", stages["stage1"]["cap_lower"], stages["stage1"]["cap_upper"]),
        ("stage2", stages["stage2"]["cap_lower"], stages["stage2"]["cap_upper"]),
        ("final", final["cap_lower"], final["cap_upper"]),
    ]
    parsed = [(name, Fraction(low), Fraction(high)) for name, low, high in brackets]
    require(all(low < high for _name, low, high in parsed), "a cap bracket is empty")
    require(all(left[2] < right[1] for left, right in zip(parsed, parsed[1:])), "a later cap does not rise")
    require(stages["stage1"]["local_per_call"] != final["local_per_call"], "stage 1 was stored as the shipped profile")
    return {
        "helpers": [int(helper) for helper in HELPERS],
        "subspace": SUBSPACE,
        "parent_frame": PARENT_FRAME,
        "parent_rank": 8,
        "shipped_rank": 7,
        "providers": 2,
        "parent_buffers": 86,
        "shipped_buffers": 91,
        "buffers_added": [int(helper) for helper in added],
        "v45_buffers_added": 0,
        "stage1_local_profile": stages["stage1"]["local_per_call"],
        "shipped_local_profile": shipped[0]["report"]["local_profile"],
        "cap_brackets": [{"stage": name, "lower": low, "upper": high} for name, low, high in brackets],
        "caps_strictly_increase": True,
        "cap_basis_resolved": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
