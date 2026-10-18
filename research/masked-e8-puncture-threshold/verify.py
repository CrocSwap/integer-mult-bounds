#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Closed-flat census and sharp one-sided E8 mask boundary.

New implementation for @ToikY with substantial OpenAI Codex assistance.
No predecessor executable is imported; checks remain active under -O.
"""
import argparse
from collections import Counter, deque
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
P = 65537
TARGET = (2, 2, 0, 0, 0, 0, 0, 0)
NORMAL = (1, -1, 2, 0, 0, 0, 0, 0)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def line(v):
    return tuple(v) if next(x for x in v if x) > 0 else tuple(-x for x in v)


def roots():
    out = set()
    for a, b in itertools.combinations(range(8), 2):
        for s in (-1, 1):
            v = [0] * 8
            v[a], v[b] = 2, 2 * s
            out.add(tuple(v))
    for v in itertools.product((-1, 1), repeat=8):
        if sum(x < 0 for x in v) % 2 == 0:
            out.add(line(v))
    return sorted(out)


def reduce(v, basis):
    v = [x % P for x in v]
    for pivot, row in basis:
        c = v[pivot]
        if c:
            v = [(x - c * y) % P for x, y in zip(v, row)]
    return tuple(v)


def normalize(v):
    pivot = next((i for i, x in enumerate(v) if x), None)
    if pivot is None:
        return None
    c = pow(v[pivot], -1, P)
    return pivot, tuple(x * c % P for x in v)


def extend(basis, residual):
    p, row = residual
    old = [(j, tuple((x - r[p] * y) % P for x, y in zip(r, row))) for j, r in basis]
    return tuple(sorted([*old, (p, row)]))


def rank(rows):
    basis = ()
    for row in rows:
        residual = normalize(reduce(row, basis))
        if residual is not None:
            basis = extend(basis, residual)
    return len(basis)


def rational_rank(rows):
    m = [[Fraction(x) for x in row] for row in rows]
    p = 0
    for col in range(8):
        found = next((i for i in range(p, len(m)) if m[i][col]), None)
        if found is None:
            continue
        m[p], m[found] = m[found], m[p]
        c = m[p][col]
        m[p] = [x / c for x in m[p]]
        for i in range(p + 1, len(m)):
            c = m[i][col]
            if c:
                m[i] = [x - c * y for x, y in zip(m[i], m[p])]
        p += 1
    return p


def census(e7):
    # Every quotient direction gives one closed extension; induction from
    # the empty flat establishes coverage of every root-generated flat.
    level, counts = {0: ()}, [1]
    for dim in range(1, 7):
        following = {}
        for mask, basis in level.items():
            groups = {}
            for i, root in enumerate(e7):
                if mask >> i & 1:
                    continue
                residual = normalize(reduce(root, basis))
                need(residual is not None, "parent closure omitted a root")
                groups[residual] = groups.get(residual, 0) | (1 << i)
            for residual, extra in groups.items():
                child = mask | extra
                if child not in following:
                    following[child] = extend(basis, residual)
        level = following
        counts.append(len(level))
        print(f"CENSUS rank={dim} flats={len(level)}", flush=True)
    need(counts == [1, 63, 1281, 10395, 33411, 36435, 8821], "flat coverage mismatch")
    hist = dict(sorted(Counter(m.bit_count() for m in level).items()))
    need(hist == {10: 5040, 13: 2016, 16: 1008, 21: 666, 30: 63, 36: 28}, "E7 histogram mismatch")
    flats = sorted(tuple(i for i in range(63) if mask >> i & 1) for mask in level)
    return {"counts_by_rank": counts, "rank6_size_histogram": hist,
            "rank6_flats": len(flats), "rank6_supports_sha256": digest(flats),
            "maximum_proper_flat": max(hist)}


def symmetry(lines):
    index = {r: i for i, r in enumerate(lines)}
    permutations = []
    for a in lines:
        image = []
        for r in lines:
            d = dot(r, a)
            need(d % 4 == 0, "reflection not integral")
            v = line(tuple(x - (d // 4) * y for x, y in zip(r, a)))
            need(v in index, "reflection leaves root lines")
            image.append(index[v])
        need(len(set(image)) == 120, "reflection not bijective")
        permutations.append(image)
    reached = {index[TARGET]}
    todo = deque(reached)
    while todo:
        for image in permutations:
            i = image[todo[0]]
            if i not in reached:
                reached.add(i)
                todo.append(i)
        todo.popleft()
    need(len(reached) == 120, "target orbit incomplete")
    return {"reflections": 120, "checked_root_images": 14400, "target_orbit": 120}


def f2_rank(rows):
    basis = {}
    for v in rows:
        while v:
            p = v.bit_length() - 1
            if p in basis:
                v ^= basis[p]
            else:
                basis[p] = v
                break
    return len(basis)


def copy_cost(lines, live, source):
    costs = []
    for k in range(8):
        left = [i for i in live if lines[i][k]]
        right = [j for j in live if source[j][k]]
        costs.append(f2_rank([sum(((dot(lines[i], lines[j]) // 4 + 1) & 1) << h
                                  for h, j in enumerate(right)) for i in left]))
    return costs


def errors(lines, live, source):
    # Twice the residual for D_i=q_i/2 and T_j=source_j.
    out = []
    for i in live:
        for j in live:
            d = dot(lines[i], source[j]) - dot(lines[i], lines[j])
            if d:
                out.append((i, j, d, (dot(lines[i], lines[j]) // 4) % 2 == 0))
    return out


def witness(lines):
    t = lines.index(TARGET)
    deleted = [i for i, r in enumerate(lines) if dot(r, TARGET) == 0 and dot(r, NORMAL)]
    live = [i for i in range(120) if i not in deleted]
    ns = [i for i in live if i == t or dot(lines[i], TARGET) == 0]
    need(len(deleted) == 27 and len(live) == 93, "wrong puncture")
    need(rank([lines[i] for i in live]) == rational_rank([lines[i] for i in live]) == 8, "live rank not eight")
    need(len(ns) == 37 and rank([lines[i] for i in ns]) == rational_rank([lines[i] for i in ns]) == 7, "wrong deficient neighbourhood")
    need(all(dot(lines[i], NORMAL) == 0 for i in ns), "normal fails on neighbour")
    original = {i: lines[i] for i in live}
    source = dict(original)
    source[t] = tuple(x + y for x, y in zip(TARGET, NORMAL))
    need(not errors(lines, live, original), "coordinate control failed")
    wrong = errors(lines, live, source)
    need(len(wrong) == 56 and all(not e[3] and e[1] == t for e in wrong), "not masked exact")
    first = next((e for e in wrong if e[2] == 6), None)
    need(first is not None, "missing explicit residual three")
    costs = copy_cost(lines, live, source)
    need(costs == copy_cost(lines, live, original) == [9] * 8, "COPY diagnostic mismatch")
    for restored in deleted:
        ls = sorted([*live, restored])
        src = {**source, restored: lines[restored]}
        need(any(e[3] for e in errors(lines, ls, src)), "26-deletion control did not reject")
        need(rank([lines[i] for i in ls if i == t or dot(lines[i], TARGET) == 0]) == 8, "restored span not eight")
    bad = dict(original)
    bad[t] = tuple(2 * x for x in TARGET)
    need(any(e[3] for e in errors(lines, live, bad)), "diagonal mutation not rejected")
    return {"target_index": t, "target_doubled_root": TARGET, "normal": NORMAL,
            "deleted_indices": deleted, "live_ports": 93, "live_rank": 8,
            "bad_neighbourhood_lines": 37, "bad_neighbourhood_rank": 7,
            "matrix_entries_checked": 8649, "unmasked_error_entries": 56,
            "masked_error_entries": 0, "first_residual_three": {"source_index": first[0], "source_doubled_root": lines[first[0]], "residual": 3},
            "copy_ranks": costs, "comparator_copy_ranks": costs,
            "single_restoration_controls": 27, "diagonal_mutation_controls": 1}


def run():
    lines = roots()
    need(len(lines) == 120 and all(dot(r, r) == 8 for r in lines), "invalid E8")
    need(all(dot(a, b) % 4 == 0 for a in lines for b in lines), "invalid Gram")
    e7 = [r for r in lines if dot(r, TARGET) == 0]
    need(len(e7) == 63 and rank(e7) == 7, "invalid E7")
    return {"schema_version": 1, "status": "PASS_MASKED_E8_PUNCTURE_THRESHOLD",
            "geometry_sha256": digest(lines), "prime": P,
            "rank_certificate": "Integer root minors have absolute value at most 4096 by squared row norm eight and Hadamard; 65537 exceeds this bound.",
            "census": census(e7), "symmetry": symmetry(lines), "witness": witness(lines),
            "rigid_through_deletions": 26, "first_failure_deletions": 27,
            "no_new_kappa": True}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", type=Path, help="create a fresh receipt; never overwrite")
    args = ap.parse_args()
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for name, expected in {**pins["implementation_sha256"], **pins["receipt_sha256"]}.items():
        need(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == expected,
             "package source/receipt drift: " + name)
    if args.write:
        need(not args.write.exists(), "refusing to overwrite an existing receipt")
    result = run()
    if args.write:
        with args.write.open("x") as out:
            json.dump(result, out, indent=2, sort_keys=True)
            out.write("\n")
    else:
        need(json.loads((HERE / "CERTIFICATE.json").read_text()) == json.loads(json.dumps(result)), "certificate differs from exact replay")
    print("PASS_MASKED_E8_PUNCTURE_THRESHOLD rigid=26 first_failure=27 flats=8821 witness_entries=8649 copy=72 no_new_kappa")


if __name__ == "__main__":
    main()
