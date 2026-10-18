#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact finite premises and controls; no predecessor code imports.

The arbitrary-factorization result is the written proof. CountFloor.lean
formalizes its arithmetic interface, with matrix premises explicitly assumed.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GEOMETRY = "research/p112-single-lift/reference-geometry.json"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def reject(action, label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError("control was accepted: " + label)


def basis(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p] = row
                break
    return tuple(pivots.values())


def rank2(rows):
    return len(basis(rows))


def rankq(rows):
    """Fraction-free elimination with primitive integer rows."""
    pivots = {}
    for source in rows:
        row = list(source)
        for p, other in sorted(pivots.items()):
            if row[p]:
                a, b = other[p], row[p]
                row = [a * x - b * y for x, y in zip(row, other)]
                g = 0
                for x in row:
                    g = gcd(g, x)
                if g > 1:
                    row = [x // g for x in row]
        p = next((i for i, x in enumerate(row) if x), None)
        if p is not None:
            pivots[p] = row
    return len(pivots)


def rankq_reference(rows):
    """A separate Fraction oracle used on the coefficient endpoints."""
    a = [[Fraction(x) for x in row] for row in rows]
    r = 0
    for c in range(len(a[0]) if a else 0):
        p = next((i for i in range(r, len(a)) if a[i][c]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        a[r] = [x / a[r][c] for x in a[r]]
        for i in range(r + 1, len(a)):
            q = a[i][c]
            a[i] = [x - q * y for x, y in zip(a[i], a[r])]
        r += 1
    return r


def parity(x):
    return x.bit_count() & 1


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def form(matrix, x, y):
    return parity(x & sum(parity(row & y) << i for i, row in enumerate(matrix)))


def restricted(matrix, left, right):
    return rank2(sum(form(matrix, x, y) << j for j, y in enumerate(right))
                 for x in left)


def pins():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for item in manifest["files"]:
        if item["usage"] == "input":
            need(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest()
                 == item["sha256"], "input pin: " + item["path"])
    for item in manifest.get("predecessors", []):
        need(hashlib.sha256((HERE / item["local_path"]).read_bytes()).hexdigest()
             == item["sha256"], "predecessor pin: " + item["local_path"])


def geometry():
    data = json.loads((ROOT / GEOMETRY).read_text())
    x, labels, duals = data["X"], data["labels"], data["duals"]
    need(len(x) == len(labels) == len(duals) == 112, "geometry size")
    # Reconstruct the norm-four Hamming-shell lines independently of the file.
    shell = set()
    for a in range(1, 8):
        for b in range(2):
            support = [i for i in range(8) if parity(a & i) == b]
            for signs in itertools.product((-1, 1), repeat=3):
                row = [0] * 8
                row[support[0]] = 1
                for i, sign in zip(support[1:], signs):
                    row[i] = sign
                shell.add(tuple(row))
    def canonical(row):
        sign = next(t for t in row if t)
        return tuple(t if sign > 0 else -t for t in row)
    need({canonical(row) for row in x} == shell, "independent Hamming shell")
    need(rank2(labels) == rank2(duals) == 9, "two full label spans")
    for i in range(8):
        for j in range(8):
            need(sum(row[i] * row[j] for row in x) == 56 * (i == j), "left inverse")
    for i in range(112):
        for j in range(112):
            d = dot(x[i], x[j])
            need(d % 2 == 0, "even root dot")
            need(parity(duals[i] & labels[j]) == (1 + d // 2) % 2,
                 "within-call pairing")
    histories = []
    for name, lab in [("reader", duals), ("source", labels)]:
        history, exceptional = Counter(), []
        for h in range(1, 512):
            rows = [row for row, label in zip(x, lab) if parity(h & label)]
            r = rankq(rows)
            history[r] += 1
            if r < 8:
                zeros = [i for i in range(8) if all(row[i] == 0 for row in rows)]
                need(r == 7 and len(zeros) == 1, name + " exceptional kernel")
                exceptional.extend(zeros)
        need(history == {8: 503, 7: 8}, name + " support census")
        need(sorted(exceptional) == list(range(8)), name + " coordinate exceptions")
        histories.append({str(k): v for k, v in sorted(history.items())})
    readers = [basis(duals[i] for i in range(112) if x[i][j]) for j in range(8)]
    sources = [basis(labels[i] for i in range(112) if x[i][j]) for j in range(8)]
    ident = tuple(1 << i for i in range(9))
    for u in readers:
        for v in sources:
            need(len(u) == len(v) == 8 and restricted(ident, u, v) == 8,
                 "64 within-support ranks")
    return data, readers, sources, histories


def matrix_census():
    mats = [tuple((word >> (2 * i)) & 3 for i in range(2)) for word in range(16)]
    gl = [a for a in mats if rank2(a) == 2]
    tight = Counter()
    total = 0
    for a, d, b, c in itertools.product(gl, gl, mats, mats):
        rows = tuple(a[i] | (b[i] << 2) for i in range(2)) + \
               tuple(c[i] | (d[i] << 2) for i in range(2))
        actual = rank2(rows)
        rb, rc = rank2(b), rank2(c)
        lower = 4 - min(2, rb, rc)
        need(actual >= lower, "block Schur minimum-rank bound")
        if actual == lower:
            tight[f"{rb},{rc}"] += 1
        total += 1
    need(total == 9216 and len(tight) == 9, "exhaustive block coverage and sharpness")
    return {"matrices": total, "tight_by_cross_rank": dict(sorted(tight.items()))}


def unit(i):
    return tuple(int(i == j) for j in range(16))


def decoder_fixtures():
    standard = [(unit(i), unit(i)) for i in range(16)]
    one = [(unit(i), tuple(int(j == i) - int(i == 0 and j == 8)
                          for j in range(16))) for i in range(16)]
    one.append((unit(0), unit(8)))
    two = [(unit(i), unit(i)) for i in range(16) if i not in (0, 8)]
    z = tuple(int(i == 0) - int(i == 8) for i in range(16))
    two += [(z, z), (unit(0), unit(8)), (unit(8), unit(0))]
    schur = []
    for i in range(8):
        z = tuple(int(j == i) - int(j == i + 8) for j in range(16))
        schur += [(z, z), (unit(i), unit(i + 8)), (unit(i + 8), unit(i))]
    mixed = []
    for k in range(8):
        a = tuple(int(i <= k) for i in range(8))
        c = tuple(int(i == k) - int(i == k + 1) for i in range(8))
        mixed.append((a + tuple(-v for v in a), c + tuple(-v for v in c)))
        mixed += [(unit(k), unit(k + 8)), (unit(k + 8), unit(k))]
    return {"standard": standard, "one_cross": one, "two_cross": two,
            "schur": schur, "noncoordinate_schur": mixed}


def coefficient_counts(terms):
    endpoint = [[sum(a[i] * c[j] for a, c in terms) for j in range(16)] for i in range(16)]
    need(endpoint == [[int(i == j) for j in range(16)] for i in range(16)], "I16 endpoint")
    kinds = []
    for a, c in terms:
        ac = [any(a[8 * s:8 * s + 8]) for s in range(2)]
        cc = [any(c[8 * s:8 * s + 8]) for s in range(2)]
        need(any(ac) and any(cc), "discard zero factors")
        kinds.append("D" if all(ac + cc) else "N" if any(ac[s] and cc[s] for s in range(2))
                     else "P01" if ac[0] else "P10")
    ranks = []
    for name, i0, j0 in [("P01", 0, 8), ("P10", 8, 0)]:
        matrix = [[sum(a[i0 + i] * c[j0 + j] for (a, c), kind in zip(terms, kinds)
                       if kind == name) for j in range(8)] for i in range(8)]
        r = rankq(matrix)
        need(r == rankq_reference(matrix), "independent coefficient rank")
        ranks.append(r)
    n, d = sum(k in ("N", "D") for k in kinds), kinds.count("D")
    mu = min(ranks)
    need(n + d >= 16 and n + mu >= 16, "incidence and Schur counts")
    return kinds, n, d, mu, ranks


def price_data(data, terms):
    x, duals, labels = data["X"], data["duals"], data["labels"]
    def spans(coef, lab):
        return [basis(label for row, label in zip(x, lab)
                      if dot(row, coef[8 * s:8 * s + 8])) for s in range(2)]
    return [(spans(a, duals), spans(c, labels)) for a, c in terms]


def cost(b, c, reader, source):
    rows = []
    for s in range(2):
        for u in reader[s]:
            bits, j = 0, 0
            for t in range(2):
                for v in source[t]:
                    bit = parity(u & v) if s == t else form(b if s == 0 else c, u, v)
                    bits |= bit << j
                    j += 1
            rows.append(bits)
    return rank2(rows)


def form_fixtures(data, readers, sources):
    fixture_data = {}
    for name, terms in decoder_fixtures().items():
        fixture_data[name] = (coefficient_counts(terms), price_data(data, terms))
    # Each rank is realized by an actual form; these are fixtures, not all forms.
    pairs, sufficient, old_sufficient, example = 0, 0, 0, None
    total_checks = 0
    undecided_control = None
    cases = []
    for r, s in itertools.product(range(10), repeat=2):
        b = tuple((1 << i) if i < r else 0 for i in range(9))
        c = tuple((1 << ((i + 2) % 9)) if i < s else 0 for i in range(9))
        cases.append((r, s, b, c, "rank_pair"))
    # This rank-(1,1) case forces abstention; a few decoders cannot decide it.
    ar = next(v for v in range(1, 512) if all(not parity(v & u) for u in readers[0]))
    ac = next(v for v in range(1, 512) if all(not parity(v & u) for u in sources[0]))
    low = tuple(ac if (ar >> i) & 1 else 0 for i in range(9))
    cases.append((1, 1, low, low, "undecided_control"))
    for r, s, b, c, case in cases:
        need(rank2(b) == r and rank2(c) == s, "prescribed form ranks")
        c01 = min(restricted(b, u, v) for u in readers for v in sources)
        c10 = min(restricted(c, u, v) for u in readers for v in sources)
        k = min(8, r, s)
        need(c01 >= max(0, r - 2) and c10 >= max(0, s - 2), "codimension loss")
        if case == "rank_pair":
            sufficient += c01 + c10 >= k
            old_sufficient += c01 + c10 >= 8
        prices = {}
        for name, ((kinds, n, d, mu, ranks), entries) in fixture_data.items():
            charges = [cost(b, c, left, right) for left, right in entries]
            for kind, charge in zip(kinds, charges):
                lower = 16 - k if kind == "D" else 8 if kind == "N" else c01 if kind == "P01" else c10
                need(charge >= lower, "term-price premise")
            strong = 8 * n + (8 - k) * d + c01 * kinds.count("P01") + c10 * kinds.count("P10")
            need(sum(charges) >= strong, "additive rank price")
            if c01 + c10 >= k:
                formal_input = 8 * n + (8 - k) * d + k * mu
                need(sum(charges) >= formal_input >= 128, "formal count interface")
            prices[name] = sum(charges)
            if name == "standard":
                need(sum(charges) == 128, "sharp separate-call attainer")
            total_checks += 1
        if (r, s) == (4, 4):
            example = {"beta01_rows": list(b), "beta10_rows": list(c), "ranks": [r, s],
                       "support_minima": [c01, c10], "k": k, "decoder_costs": prices}
            need(c01 + c10 < 8 and c01 + c10 >= k, "strict extension example")
        if case == "rank_pair":
            pairs += 1
        else:
            need([c01, c10, k] == [0, 0, 1], "criterion must abstain")
            undecided_control = {"ranks": [r, s], "support_minima": [c01, c10],
                                 "beta01_rows": list(b), "beta10_rows": list(c),
                                 "decoder_costs": prices, "verdict": "criterion inconclusive"}
    return {"form_pairs": pairs, "decoder_cases": total_checks,
            "criterion_passes": sufficient, "old_criterion_passes": old_sufficient,
            "new_rank44_example": example, "coefficient_endpoints": len(fixture_data),
            "undecided_control": undecided_control}


def rank_region():
    yes, no, prior = [], [], []
    for r, s in itertools.product(range(10), repeat=2):
        test = max(0, r - 2) + max(0, s - 2) >= min(8, r, s)
        (yes if test else no).append([r, s])
        if r + s >= 12:
            prior.append([r, s])
    need(len(yes) == 93 and len(prior) == 28, "rank-only region")
    need(no == [[1, 1], [1, 2], [2, 1], [2, 2], [2, 3], [3, 2], [3, 3]], "seven unresolved rank pairs")
    return {"certified_pairs": len(yes), "prior_rank_sum12_pairs": len(prior), "unresolved_pairs": no}


def controls():
    result = []
    # These are witnesses that individual theorem hypotheses cannot be dropped.
    result.append(reject(lambda: need(8 * 8 >= 128, "incidence absent"), "missing_incidence"))
    need(8 + 8 >= 16, "first control retains Schur")
    result.append(reject(lambda: need(8 * 0 + 0 * 16 + 8 * 0 >= 128, "Schur absent"), "missing_schur"))
    need(0 + 16 >= 16, "second control retains incidence")
    result.append(reject(lambda: need(8 * 8 + 0 * 8 >= 128, "pure price absent"), "missing_pure_surcharge"))
    # Replacing the within-call rank-eight price by seven would be false.
    result.append(reject(lambda: need(7 * 16 >= 128, "within price undercount"),
                         "undercounted_within_price"))
    # An overstrong block lower bound fails at A=D=B=C=I_2.
    ident = (1, 2)
    block = tuple(ident[i] | (ident[i] << 2) for i in range(2)) * 2
    need(rank2(block) == 2, "sharp Schur control")
    result.append(reject(lambda: need(rank2(block) >= 3, "extra rank unit"), "overstrong_schur"))
    zero = (0, 0)
    result.append(reject(lambda: need(rank2(zero + zero) >= 4, "missing invertible diagonal"), "missing_within_rank"))
    mat = (1, 2, 4, 8, 0, 0, 0, 0, 0)
    u = tuple(1 << i for i in range(1, 9))
    v = tuple(1 << i for i in range(9) if i != 1)
    need(restricted(mat, u, v) == 2, "two-codimension loss attainer")
    result.append(reject(lambda: need(restricted(mat, u, v) >= 3, "one loss only"), "codimension_two_loss"))
    damaged = decoder_fixtures()["two_cross"][:-1]
    result.append(reject(lambda: coefficient_counts(damaged), "missing_cross_endpoint_term"))
    return result


def run():
    pins()
    data, readers, sources, histories = geometry()
    return {"scope": "written conditional matrix proof; finite premises; separate Lean count theorem",
            "support_censuses": histories, "within_pairings": 12544, "support_pair_ranks": 64,
            "block_census": matrix_census(), "rank_region": rank_region(),
            "form_fixtures": form_fixtures(data, readers, sources), "controls": controls()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = run()
    path = HERE / "RESULT.json"
    if args.write_result:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        # JSON booleans and integers must remain distinct (Python True == 1).
        committed = json.dumps(json.loads(path.read_text()), sort_keys=True, separators=(",", ":"))
        generated = json.dumps(result, sort_keys=True, separators=(",", ":"))
        need(committed == generated, "committed result equality")
    print("PASS_P112_CROSS_FORM_RANK_TRADEOFF ranks=93/100 blocks=9216 decoders=505 controls=8 abstentions=1")


if __name__ == "__main__":
    main()
