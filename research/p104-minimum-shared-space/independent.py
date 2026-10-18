"""Separate dense integer replay, enumerated subspaces and dense matrix audit.

All frozen scalar rows have denominator dividing four, checked at every ADD.
No producer, predecessor, sparse checker or its linear algebra is imported.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import HERE, certificate, cli, digest, need, read, sources


@lru_cache(None)
def subspace(vectors):
    points = {0}
    for vector in vectors:
        need(type(vector) is int and 0 < vector < 512, "binary label")
        points.update(x ^ vector for x in tuple(points))
    need(len(points) == 2 ** len(vectors), "independent binary frame")
    return frozenset(points)


def geometry(fixture):
    oriented = []
    for i in range(8):
        for j in range(i + 1, 8):
            for si in (-2, 2):
                for sj in (-2, 2):
                    v = [0] * 8
                    v[i], v[j] = si, sj
                    oriented.append(v)
    for bits in range(256):
        if bits.bit_count() % 2 == 0:
            oriented.append([1 - 2 * ((bits >> j) & 1) for j in range(8)])
    lines = set()
    for v in oriented:
        sign = 1 if next(x for x in v if x) > 0 else -1
        lines.add(tuple(sign * x for x in v))
    removed = {tuple(v) for v in fixture["F0"] + fixture["C"]}
    need(len(oriented) == 240 and len(lines) == 120 and
         len(removed) == 16 and removed <= lines, "root enumeration")
    return sorted(lines - removed)


def dense_rank(matrix):
    if not matrix:
        return 0
    a = [[Fraction(x) for x in row] for row in matrix]
    pivot = 0
    for col in range(len(a[0])):
        found = next((i for i in range(pivot, len(a)) if a[i][col]), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        value = a[pivot][col]
        a[pivot] = [x / value for x in a[pivot]]
        for i in range(pivot + 1, len(a)):
            value = a[i][col]
            if value:
                a[i] = [x - value * y for x, y in zip(a[i], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def analyze(data, cert):
    word = data["LOWRANK-WITNESS.json"]
    ports = geometry(data["P104-FIXTURE.json"]["section4_explicit_P104"])
    names = list(word["initial_frames"])
    need(len(names) == len(set(names)) == 280 and
         names[:104] == ["X" + str(i) for i in range(104)], "boundary coordinates")
    x_columns = [names.index("X" + str(i)) for i in range(104)]
    y_columns = [names.index("Y" + str(i)) for i in range(104)]
    need(all(sum(p[i] * p[j] for p in ports) == 104 * (i == j)
             for i in range(8) for j in range(8)), "tight root frame")
    vectors, vector_ids = [], {}

    def intern(row):
        row = tuple(row)
        if row not in vector_ids:
            vector_ids[row] = len(vectors)
            vectors.append(row)
        return vector_ids[row]

    current = {name: intern([4 * (j == i) for j in range(280)])
               for i, name in enumerate(names)}
    frames = {n: subspace(tuple(f)) for n, f in word["initial_frames"].items()}
    pools, captured, contacts = [set() for _ in range(104)], set(), {}
    at_cut = defaultdict(list)
    for index, (target, cut, reg, weight) in enumerate(cert["terms"]):
        at_cut[cut].append((index, target, reg))

    def observe(cut):
        classes = defaultdict(dict)
        for reg in current:
            classes[frames[reg]][reg] = current[reg]
        for group in classes.values():
            targets = [(int(r[1:]), r) for r in group if r.startswith("Y")]
            if targets:
                captured.update(group.values())
            for target, name in targets:
                pools[target].update(rid for reg, rid in group.items() if reg != name)
        for index, target, reg in at_cut[cut]:
            need(reg in current and reg != "Y" + str(target), "live contact register")
            need(frames[reg] == frames["Y" + str(target)], "actual contact frame")
            contacts[index] = vectors[current[reg]]

    paid, scalar = Counter(), Counter()
    observe(0)
    need(len(word["program"]) == 4058, "event count")
    for index, event in enumerate(word["program"]):
        op, reg = event[:2]
        if op == "transport":
            before, after = subspace(tuple(event[2])), subspace(tuple(event[3]))
            need(frames[reg] == before, "transport old frame")
            need(before <= after or after <= before, "nested frame change")
            rank = abs(len(before).bit_length() - len(after).bit_length())
            need(type(event[4]) is int and rank == event[4] > 0, "priced rank")
            frames[reg] = after
            paid[rank] += 1
        elif op == "add":
            _, _, src, raw, frame = event
            need(reg != src and frames[reg] == frames[src] == subspace(tuple(frame)),
                 "ADD equality of full subspaces")
            factor = Fraction(raw)
            source, dest = vectors[current[src]], vectors[current[reg]]
            scaled = [factor.numerator * x for x in source]
            need(all(x % factor.denominator == 0 for x in scaled),
                 "exact denominator-four lattice")
            current[reg] = intern([a + b // factor.denominator for a, b in zip(dest, scaled)])
            scalar[op] += 1
        elif op == "zero":
            need(reg == "C" and reg not in current, "private lifetime allocation")
            current[reg], frames[reg] = intern([0] * 280), subspace(tuple(event[2]))
            scalar[op] += 1
        elif op == "copy":
            need(reg == "C" and not any(vectors[current[reg]]) and
                 frames[reg] == frames[event[2]] == subspace(tuple(event[3])), "private COPY")
            current[reg] = current[event[2]]
            scalar[op] += 1
        elif op == "erase":
            need(reg == "C" and frames[reg] == subspace(tuple(event[2])), "private discard")
            del current[reg], frames[reg]
            scalar[op] += 1
        else:
            raise ValueError("unknown operation")
        observe(index + 1)
    need(set(current) == set(names), "closed private lifetimes")
    gram = [[sum(a * b for a, b in zip(p, q)) // 4 for q in ports] for p in ports]
    for index, name in enumerate(names):
        expected = [4 * (j == index) for j in range(280)]
        if name.startswith("Y"):
            target = int(name[1:])
            for j in range(104):
                expected[x_columns[j]] = 2 * gram[target][j]
        need(tuple(expected) == vectors[current[name]], "dense endpoint " + name)
        need(frames[name] == subspace(tuple(word["final_frames"][name])), "terminal frame")
    need(dict(paid) == {int(k): v for k, v in data["LOWRANK-RESULT.json"]["paid_profile"].items()}
         and sum(k * v for k, v in paid.items()) == 2368, "original native invoice")
    # Numerators of the eight root-code coordinates, with denominator 416.
    projected = {}
    for rid in captured:
        row = vectors[rid]
        coordinates = [sum(row[x_columns[j]] * ports[j][k] for j in range(104))
                       for k in range(8)]
        need(all(sum(coordinates[k] * ports[j][k] for k in range(8)) ==
                 104 * row[x_columns[j]] for j in range(104)), "projected root code")
        projected[rid] = coordinates
    dims = []
    for target, pool in enumerate(pools):
        for col in range(104, 280):
            if col != y_columns[target]:
                unit = tuple(4 * (j == col) for j in range(280))
                need(vector_ids[unit] in pool, "initial outside coordinate")
        need(all(vectors[r][y_columns[target]] == 0 for r in pool), "missing own target input")
        # Deduplicate the 8-vectors before separate dense rational elimination.
        dims.append(dense_rank(sorted({tuple(projected[r]) for r in pool})))
    A = [[Fraction(0)] * 8 for _ in range(104)]
    representatives = [[Fraction(0)] * 280 for _ in range(104)]
    for index, (target, cut, reg, weight) in enumerate(cert["terms"]):
        weight = Fraction(weight)
        need(weight and str(weight) == cert["terms"][index][3], "rational normalization")
        row = contacts[index]
        for j in range(280):
            representatives[target][j] += weight * Fraction(row[j], 4)
    for t in range(104):
        for k in range(8):
            A[t][k] = sum(representatives[t][x_columns[j]] * ports[j][k]
                          for j in range(104)) / 104
    need(all(sum(ports[t][i] * A[t][j] for t in range(104)) == int(i == j)
             for i in range(8) for j in range(8)), "dense right inverse")
    C = [[Fraction(t == j) - Fraction(gram[t][j], 2) for j in range(104)] for t in range(104)]
    H = [[C[t][j] + 12 * representatives[t][x_columns[j]] for j in range(104)] for t in range(104)]
    need(dense_rank(C) == 104 and dense_rank(H) == 96, "both exact matrix ranks")
    # Direct 280-coordinate certificate: H_t - 12 times the full snapshot
    # combination, plus its 175 available outside-unit corrections, is C_t.
    for t in range(104):
        full = [Fraction(0)] * 280
        for j in range(104):
            full[x_columns[j]] = H[t][j]
        for col in range(280):
            full[col] -= 12 * representatives[t][col]
            if col >= 104:
                need(col != y_columns[t] or representatives[t][col] == 0,
                     "cannot cancel own Y by a free snapshot")
                full[col] += 12 * representatives[t][col]
        need(full == C[t] + [Fraction(0)] * 176, "full-space correction identity")
    return {"schema": "p104-minimum-shared-space/1", "minimum_dimension": 96,
            "targets": 104, "arbitrary_input_columns": 280, "cuts": 4059,
            "captured_snapshot_rows": len(captured),
            "pooled_x_rank_histogram": {str(k): v for k, v in sorted(Counter(dims).items())},
            "pool_sizes": list(map(len, pools)), "certificate_terms": len(cert["terms"]),
            "nonzero_A_rows": sum(any(row) for row in A),
            "A_sha256": digest([[str(x) for x in row] for row in A]),
            "H_sha256": digest([[str(x) for x in row] for row in H]),
            "original_paid_profile": {str(k): v for k, v in sorted(paid.items())},
            "original_scalar_events": dict(scalar),
            "scope": "Exact algebraic pooled-span minimum only; no chronological producer, transport price, supplier or new kappa."}


def run(data=None, cert=None):
    return analyze(sources() if data is None else data,
                   certificate(read(HERE / "WITNESS.json") if cert is None else cert))


if __name__ == "__main__":
    cli(run, "PASS_P104_MINIMUM_SHARED_SPACE_INDEPENDENT")
