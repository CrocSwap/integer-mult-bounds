#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact new transfer checks; the inherited support theorem is a premise."""

import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WIDTH = 9
MASK = (1 << WIDTH) - 1
MAX_FILE_BYTES = 2 * 1024 * 1024


def need(ok, message):
    if not ok:
        raise ValueError(message)


def parity(value):
    return value.bit_count() & 1


def read_bytes(path):
    need(path.stat().st_size <= MAX_FILE_BYTES, "input exceeds 2 MiB")
    return path.read_bytes()


def basis(rows, width=WIDTH):
    """At most len(rows)*width eliminations, with bounded integer rows."""
    pivots = [0] * width
    for original in rows:
        need(0 <= original < (1 << width), "row range")
        row = original
        for bit in range(width - 1, -1, -1):
            if (row >> bit) & 1:
                if pivots[bit]:
                    row ^= pivots[bit]
                else:
                    pivots[bit] = row
                    break
    return tuple(row for row in pivots if row)


def outer(left, right):
    return tuple(right if (left >> bit) & 1 else 0 for bit in range(WIDTH))


def form(matrix, left, right):
    image = sum(parity(row & right) << bit for bit, row in enumerate(matrix))
    return parity(left & image)


def block_rows(matrix, readers, sources):
    return tuple(sum(form(matrix, left, right) << bit
                     for bit, right in enumerate(sources)) for left in readers)


def restricted_rank(matrix, readers, sources):
    return len(basis(block_rows(matrix, readers, sources)))


def double_rank(forward, reverse, u0, v0, u1, v1):
    ident = tuple(1 << bit for bit in range(WIDTH))
    a, b = block_rows(ident, u0, v0), block_rows(forward, u0, v1)
    c, d = block_rows(reverse, u1, v0), block_rows(ident, u1, v1)
    rows = tuple(x | (y << len(v0)) for x, y in zip(a, b))
    rows += tuple(x | (y << len(v0)) for x, y in zip(c, d))
    return len(basis(rows, 2 * WIDTH))


def inputs():
    manifest = json.loads(read_bytes(HERE / "SOURCES.json"))
    for item in manifest["files"]:
        if item["usage"] == "input":
            digest = hashlib.sha256(read_bytes(ROOT / item["path"])).hexdigest()
            need(digest == item["sha256"], "source hash: " + item["path"])
    data = json.loads(read_bytes(ROOT / "research/p112-single-lift/reference-geometry.json"))
    roots, readers, sources = data["X"], data["duals"], data["labels"]
    need(len(roots) == len(readers) == len(sources) == 112, "geometry shape")
    need(all(len(row) == 8 for row in roots), "root width")
    u = tuple(basis([label for row, label in zip(roots, readers) if row[j]])
              for j in range(8))
    v = tuple(basis([label for row, label in zip(roots, sources) if row[j]])
              for j in range(8))
    r, s = [], []
    for spaces, normals in ((u, r), (v, s)):
        for space in spaces:
            need(len(space) == 8, "coordinate support dimension")
            annihilators = [h for h in range(1, MASK + 1)
                           if all(parity(h & row) == 0 for row in space)]
            need(len(annihilators) == 1, "unique coordinate annihilator")
            normals.append(annihilators[0])
    return u, v, tuple(r), tuple(s)


def transfer_checks(r, s):
    hull = basis(s)
    span = tuple(value for value in range(MASK + 1)
                 if len(basis(hull + (value,))) == len(hull))
    need(len(span) == 16, "exceptional source hull size")
    checks = 0
    for reader, row_normal, source_normal, source in itertools.product(r, r, s, span):
        z = reader ^ (row_normal if parity(reader & source_normal) else 0)
        need(parity(z & source_normal) == 0, "projected vector is in source space")
        need(parity(source & z) == 0, "reverse Schur transfer vanishes")
        checks += 1
    return checks


def fixture_checks(u, v, r, s):
    forward = outer(r[0], 1)
    reverse = tuple(a ^ b for a, b in zip(outer(r[1], s[0]), outer(1, s[1])))
    need((len(basis(forward)), len(basis(reverse))) == (1, 2), "fixture global ranks")
    minima = tuple(min(restricted_rank(matrix, left, right) for left in u for right in v)
                   for matrix in (forward, reverse))
    need(minima == (0, 0), "prior sufficient test must abstain")
    full = tuple(1 << bit for bit in range(WIDTH))
    count, minimum = 0, 2 * WIDTH
    for u0, v0, u1, v1 in itertools.product(u + (full,), v + (full,), repeat=2):
        cost = double_rank(forward, reverse, u0, v0, u1, v1)
        need(cost >= 16, "fixture double price")
        minimum = min(minimum, cost)
        count += 1
    need(count == 6561 and minimum == 16, "fixture domain and sharp double price")
    ident = tuple(1 << bit for bit in range(WIDTH))
    attainer = sum(restricted_rank(ident, u[j], v[j]) for j in range(8)) * 2
    need(attainer == 128, "sixteen coordinate-term attainer")
    return {"forward": list(forward), "reverse": list(reverse),
            "ranks": [1, 2], "minima": list(minima), "double_cases": count,
            "minimum_double_price": minimum, "attaining_cost": attainer}


def controls(u, v, r, s):
    # Each removed geometric hypothesis admits an actual price-15 double.
    off_source = next(1 << bit for bit in range(WIDTH)
                      if any(parity((1 << bit) & (r[0] ^ row)) for row in r))
    off_reader = next(1 << bit for bit in range(WIDTH)
                      if any(parity((1 << bit) & (s[0] ^ row)) for row in s))
    pairs = ((outer(r[0], off_source), outer(r[1], off_source)),
             (outer(off_reader, s[0]), outer(off_reader, s[1])))
    witnesses = []
    for forward, reverse in pairs:
        witness = None
        for indices in itertools.product(range(8), repeat=4):
            a, b, c, d = indices
            if double_rank(forward, reverse, u[a], v[b], u[c], v[d]) == 15:
                witness = list(indices)
                break
        need(witness is not None, "hypothesis-removal price-15 control")
        witnesses.append(witness)
    return witnesses


def main():
    u, v, r, s = inputs()
    need(all(parity(a & b) == 1 for a in r for b in s), "exceptional cross pairings")
    result = {"reader_normals": list(r), "source_normals": list(s),
              "transfer_checks": transfer_checks(r, s),
              "fixture": fixture_checks(u, v, r, s),
              "control_witnesses": controls(u, v, r, s)}
    need(result["transfer_checks"] == 8192, "transfer domain size")
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256(read_bytes(HERE / name)).hexdigest() for name in names}
    manifest = json.loads(read_bytes(HERE / "SOURCES.json"))
    for item in manifest["files"]:
        if item["usage"] == "input":
            hashes[item["path"]] = hashlib.sha256(read_bytes(ROOT / item["path"])).hexdigest()
    print(json.dumps({"result": result, "sha256": hashes}, sort_keys=True))
    print("PASS_P112_EXCEPTIONAL_HULL transfer=8192 doubles=6561 floor=128 controls=2")


if __name__ == "__main__":
    main()
