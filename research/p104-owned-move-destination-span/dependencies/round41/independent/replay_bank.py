"""Reproduce R43 full-bank membership using denominator-free augmented ranks."""

import argparse
from functools import reduce
import gzip
from hashlib import sha256
import json
from math import gcd
from pathlib import Path
import runpy
import time

WORD = "2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756"
CORE = "fd7a1a7f9cb8f71caa5e0d89ed16ea056503fa283bc05f655eb0da7e8d5fc6e0"
HEAD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"


def checked(path, digest):
    data = path.read_bytes()
    if sha256(data).hexdigest() != digest:
        raise ValueError(f"Unexpected SHA-256 for {path.name}")
    return data


def primitive(row):
    common = reduce(gcd, row.values(), 0)
    if common > 1:
        return {k: v // common for k, v in row.items()}
    return row


def add_row(basis, raw):
    # Copy before elimination because the literal row is still in use.
    row = raw.copy()
    while row:
        pivot = max(row)
        known = basis.get(pivot)
        if known is None:
            basis[pivot] = primitive(row)
            return True
        p, q = row[pivot], known[pivot]
        common = gcd(p, q)
        row = {
            key: value for key in row.keys() | known.keys()
            if (value := (q//common)*row.get(key, 0) - (p//common)*known.get(key, 0))
        }
        row = primitive(row)
    return False


def ranks(rows, target):
    basis = {}
    # Each stored denominator multiplies its entire row by a nonzero unit of Q.
    for _, numerators in rows:
        add_row(basis, numerators)
    old = len(basis)
    add_row(basis, target[1])
    return old, len(basis)


def observer(records):
    def visit(index, role, source, destination, paid_rank, charts, rows, owned):
        donors = [
            rows[r] for r in range(len(rows)) if r != role and charts[r] == destination and rows[r][1]
        ]
        if len(donors) < 3:
            return
        old, augmented = ranks(donors, rows[role])
        records.append({
            "literal_index": index, "role": role, "from": source, "to": destination,
            "paid_rank": paid_rank, "donors": len(donors),
            "donor_rank": old, "augmented_rank": augmented, "in_span": old == augmented,
        })
    return visit


def controls():
    bank = [(3, {0:1, 1:1}), (5, {0:1, 1:-1}), (7, {2:2})]
    target = (2, {0:1, 2:-1})
    assert ranks(bank, target) == (3,3)
    assert all(ranks([bank[j] for j in range(3) if j != i], target) == (2,3) for i in range(3))
    dependent = (11, {0:-6, 1:-6})
    assert ranks([*bank, dependent], target) == (3,3)
    assert ranks(bank, (2, {0:1, 2:-1, 3:1})) == (3,4)
    return {"three_donor_required": True, "dependent_extra_donor": True, "outside_coordinate_rejected": True}


def main():
    start = time.monotonic()
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", required=True, type=Path)
    parser.add_argument("--cap", default=22, type=float)
    args = parser.parse_args()
    assert 0 < args.cap <= 22
    core = Path(__file__).resolve().with_name("replay_core.py")
    checked(core, CORE)
    audit = runpy.run_path(str(core))["audit"]
    word = json.loads(gzip.decompress(checked(args.word, WORD)))
    records = []
    report = audit(word, start, args.cap, observer(records))
    payload = {
        **report, "scientific_head": HEAD, "word_sha256": WORD, "replay_core_sha256": CORE,
        "banks_tested": len(records), "donors": sum(r["donors"] for r in records),
        "matches": sum(r["in_span"] for r in records), "records": records, "controls": controls(),
    }
    if report["scope_exhausted"]:
        assert (report["paid_owned_moves"], payload["banks_tested"], payload["donors"]) == (47,39,411)
    print(json.dumps(payload, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
