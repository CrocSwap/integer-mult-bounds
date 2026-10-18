"""Separate set/integer-minor replay; imports no primary checker code.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
Both implementations are by the same assisted author, not independent human review.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
from itertools import combinations
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASES = (592, 600, 608, 624, 632, 640, 648, 656, 672, 680, 688, 696)


def check(ok, message):
    if not ok:
        raise ValueError(message)


def span(generators, initial=frozenset({0})):
    out = set(initial)
    for x in generators:
        out.update([a ^ x for a in out])
    return frozenset(out)


def det(a):
    """Integer Bareiss determinant, with exact division checked."""
    a = [row.copy() for row in a]
    last, sign = 1, 1
    for k in range(len(a) - 1):
        p = next((i for i in range(k, len(a)) if a[i][k]), None)
        if p is None:
            return 0
        if p != k:
            a[p], a[k] = a[k], a[p]
            sign = -sign
        pivot = a[k][k]
        for i in range(k + 1, len(a)):
            for j in range(k + 1, len(a)):
                n = pivot * a[i][j] - a[i][k] * a[k][j]
                check(n % last == 0, "nonexact Bareiss division")
                a[i][j] = n // last
            a[i][k] = 0
        last = pivot
    return sign * a[-1][-1] if a else 1


def column_rank(q, columns):
    # Every Q entry is a half integer. Its real Gram matrix is positive semidefinite.
    a = [[2 * Fraction(row[j]) for j in columns] for row in q]
    check(all(x.denominator == 1 for row in a for x in row), "non-half-integer input")
    a = [[int(x) for x in row] for row in a]
    gram = [[sum(x * y for x, y in zip(r, s)) for s in a] for r in a]
    for n in range(min(4, len(columns)), 0, -1):
        for s in combinations(range(4), n):
            if det([[gram[i][j] for j in s] for i in s]):
                return n
    return 0


def registers(g):
    return g[1:3] if g[0] == "add" else g[1:2]


def modular_boundary(prefix, wanted, width, prime):
    check(prime > 2 and all(prime % d for d in range(2, int(prime ** .5) + 1)), "nonprime modulus")
    rows = [{i: 1} for i in range(width)]
    for g in prefix:
        if g[0] == "add":
            _, dst, src, n, d, _ = g
            check(d % prime != 0, "nonunit modular denominator")
            q = n * pow(d, -1, prime) % prime
            for k, v in rows[src].items():
                rows[dst][k] = (rows[dst].get(k, 0) + q * v) % prime
            rows[dst] = {k: v for k, v in rows[dst].items() if v}
        else:
            _, dst, n, d, _ = g
            check(d % prime != 0, "nonunit modular denominator")
            q = n * pow(d, -1, prime) % prime
            rows[dst] = {k: q * v % prime for k, v in rows[dst].items() if q * v % prime}
    pivots = {}
    product = 1
    for r in wanted:
        row = rows[r].copy()
        while row:
            c = min(row)
            factor = row[c]
            if c in pivots:
                for j, v in pivots[c].items():
                    row[j] = (row.get(j, 0) - factor * v) % prime
                row = {j: v for j, v in row.items() if v}
            else:
                product = product * factor % prime
                inverse = pow(factor, -1, prime)
                pivots[c] = {j: v * inverse % prime for j, v in row.items()}
                break
    return {"prime": prime, "rank": len(pivots), "pivot_columns": list(pivots),
            "pivot_product_mod_prime": product}


def compute():
    expected = json.loads((HERE / "CERTIFICATE.json").read_text())
    sources = json.loads((HERE / "SOURCES.json").read_text())
    pin = next(p for p in sources["files"] if p["usage"] == "input")
    data = (ROOT / pin["path"]).read_bytes()
    check(hashlib.sha256(data).hexdigest() == pin["sha256"], "input source mismatch")
    with tarfile.open(ROOT / pin["path"], "r:gz") as t:
        raw = gzip.decompress(t.extractfile("t16/global/base/providers/gauge44/CANONICAL-WORD.json.gz").read())
    check(hashlib.sha256(raw).hexdigest() == expected["source_payload_sha256"], "payload mismatch")
    w = json.loads(raw)
    frames = [span(f) for f in w["frames"]]
    state = [frames[i] for i in w["start"]]
    for g in w["A"]:
        for r in registers(g):
            check(state[r] <= frames[g[-1]], "independent A descent")
            state[r] = frames[g[-1]]
    states = []
    for g in w["B"]:
        states.append(state.copy())
        for r in registers(g):
            check(state[r] <= frames[g[-1]], "independent B descent")
            state[r] = frames[g[-1]]
    blocks = expected["blocks"]
    check([b["base"] for b in blocks] == list(BASES), "missing or reordered block")
    kernels = []
    checked_columns = 0
    corrections = set()
    for b, local in zip(blocks, expected["local"]):
        hs = set(range(b["base"], b["base"] + 8))
        reads = [(i, g) for i, g in enumerate(w["B"]) if g[0] == "add" and g[1] in hs
                 and g[2] not in hs and len(frames[g[-1]]) > 2]
        check([g[2] for _, g in reads] == b["inputs"], "input extraction")
        check([frames[g[-1]] for _, g in reads] == list(map(span, b["input_frames"])), "input frames")
        corr = [i for i, g in enumerate(w["B"][:reads[0][0]])
                if g[0] == "add" and g[1] in hs and g[2] in hs]
        check(corr == b["corrections"], "correction extraction")
        corrections.update(corr)
        start = min(corr)
        low = sorted(r for r in hs if len(states[start][r]) == 2)
        high = sorted(hs - set(low))
        check(low == b["low"] and high == b["high"], "low/high extraction")
        check(all(states[start][r] == span(b["common"]) for r in high), "common extraction")
        outs = [(i, g) for i, g in enumerate(w["B"]) if i >= start and g[0] == "add"
                and g[2] in hs and g[1] not in hs]
        targets = sorted({g[1] for _, g in outs})
        check(targets == b["targets"], "output extraction")
        for r, entry, cap, at in zip(targets, b["target_entries"], b["caps"], b["output_entries"]):
            check(at == next(i for i, g in outs if g[1] == r), "output boundary")
            check(states[at][r] == span(entry) and frames[w["final"][r]] == span(cap), "output frames")
        # Execute each formal input separately, including arbitrary target dirt.
        variables = sorted(hs) + b["inputs"] + targets
        maps = {r: [] for r in targets}
        for origin in variables:
            values = {r: Fraction(int(r == origin)) for r in variables}
            for i, g in enumerate(w["B"]):
                if i >= start and hs.intersection(registers(g)):
                    if g[0] == "add":
                        values[g[1]] += Fraction(g[3], g[4]) * values[g[2]]
                    else:
                        values[g[1]] *= Fraction(g[2], g[3])
            for r in targets:
                maps[r].append(values[r])
            checked_columns += 1
        q = [[str(v) for v in maps[r][8:16]] for r in targets]
        check(q == b["Q"], "literal Q map")
        check([[str(maps[r][variables.index(h)]) for h in low] for r in targets] == b["R"], "literal R map")
        check(all(maps[r][variables.index(h)] == 0 for r in targets for h in high), "dirty-high output")
        check(all(maps[r][16 + j] == int(r == t) for r in targets for j, t in enumerate(targets)), "target dirt")
        paths = {r: states[start][r] for r in hs}
        bill = Counter()
        for i, g in enumerate(w["B"]):
            if i >= start:
                for r in hs.intersection(registers(g)):
                    a, z = paths[r], frames[g[-1]]
                    check(a <= z, "independent helper descent")
                    d = (len(z) // len(a)).bit_length() - 1
                    if d:
                        bill[d] += 1
                    paths[r] = z
        for r, f in paths.items():
            check(len(frames[w["final"][r]]) == 512, "full endpoint")
            d = (512 // len(f)).bit_length() - 1
            if d:
                bill[d] += 1
        check({str(k): v for k, v in bill.items()} == b["profile"], "independent complete bill")
        spaces = {0: frozenset({0})}
        spectrum, projections = Counter(), Counter()
        found = set()
        for mask in range(1, 256):
            lowbit = mask & -mask
            j = lowbit.bit_length() - 1
            spaces[mask] = span(b["input_frames"][j], spaces[mask ^ lowbit])
            cols = [j for j in range(8) if mask >> j & 1]
            dim = len(spaces[mask]).bit_length() - 1
            r = column_rank(q, cols)
            spectrum[len(cols), dim, r] += 1
            if len(cols) <= 4:
                other = [j for j in range(8) if j not in cols]
                proj = len(cols) - 4 + column_rank(q, other)
                projections[len(cols), proj] += 1
                check(proj >= (3 * len(cols) + 3) // 4, "independent projection")
            if r < len(cols):
                check(dim >= 7, "independent low-rank kernel")
                if dim == 7:
                    found.add(spaces[mask])
        check(found == {span(f) for f in local["kernels"]}, "kernel-frame census")
        check([list(k) + [v] for k, v in sorted(spectrum.items())] == local["spectrum"], "subset rank census")
        check([list(k) + [v] for k, v in sorted(projections.items())] == local["projections"], "projection census")
        kernels.extend((b["base"], f) for f in found)
    inputs = [(b["base"], r, span(f)) for b in blocks for r, f in zip(b["inputs"], b["input_frames"])]
    caps = [(r, span(f)) for b in blocks for r, f in zip(b["targets"], b["caps"])]
    entries = [span(f) for b in blocks for f in b["target_entries"]]
    check(len(inputs) == len({r for _, r, _ in inputs}) == 96, "independent global input alias")
    check(len(caps) == len({r for r, _ in caps}) == len({f for _, f in caps}) == 48, "global target identity")
    check(all(not f <= g and not g <= f for (_, _, f), (_, _, g) in combinations(inputs, 2)), "independent antichain")
    check(all(not span(b["common"]) <= f for b in blocks for owner, _, f in inputs if owner != b["base"]), "independent high locality")
    check(all(len(f) * len(g) >= 256 * len(f & g) for _, _, f in inputs for g in entries), "independent output wall")
    check(len({f for _, f in kernels}) == 24, "global kernel identity")
    for owner, f in kernels:
        included = [(o, r, len(g)) for o, r, g in inputs if g <= f]
        allowed = sorted(r for r, g in caps if f <= g)
        check(all(o == owner and size == 32 for o, _, size in included), "independent kernel locality")
        check(len(allowed) <= 1, "independent kernel outputs")
        record = next(k for k in expected["global"]["kernel_frames"] if span(k["frame"]) == f)
        check(record["owner"] == owner and record["eligible_targets"] == allowed
              and record["contained_inputs"] == [r for _, r, _ in included], "global kernel receipt")
    cut = min(b["first_input"] for b in blocks)
    prefix = w["A"] + w["cut"] + [g for i, g in enumerate(w["B"][:cut]) if i not in corrections]
    wanted = sorted({r for b in blocks for r in b["helpers"] + b["inputs"]})
    minor_witnesses = [modular_boundary(prefix, wanted, len(w["start"]), p) for p in (65521, 65537)]
    check(all(m["rank"] == 192 for m in minor_witnesses), "joint boundary rank")
    check(modular_boundary(prefix, wanted[:-1] + wanted[:1], len(w["start"]), 65521)["rank"] == 191,
          "duplicated boundary coordinate control")
    broken = prefix + [["scale", wanted[0], 0, 1, 0]]
    check(modular_boundary(broken, wanted, len(w["start"]), 65521)["rank"] == 191,
          "singular boundary control")
    return {"status": "PASS_INDEPENDENT_CROSS_BLOCK_PREMISES", "source_payload_sha256": hashlib.sha256(raw).hexdigest(),
            "literal_columns": checked_columns, "subset_cases": 3060, "input_pairs": 4560,
            "foreign_high_tests": 1056, "input_target_tests": 4608, "kernel_frames": 24,
            "boundary_witnesses": minor_witnesses, "boundary_controls": 2}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    result = compute()
    out = HERE / "INDEPENDENT.json"
    if args.record:
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        check(json.loads(out.read_text()) == result, "independent saved receipt mismatch")
    print("PASS_INDEPENDENT_CROSS_BLOCK_PREMISES columns=240 subsets=3060 boundary_rank=192 primes=2 controls=2")


if __name__ == "__main__":
    main()
