#!/usr/bin/env python3
"""P112 joint deletion boundary and two-column cancellation obstruction.

Sricharan Vagvala (@theon199), substantial OpenAI Codex assistance. Apache-2.0.
Finite premises plus a written proof; no predecessor checker is imported.
"""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GEOMETRY = "research/p112-single-lift/reference-geometry.json"
SEED, CAP = 49, 47


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(values):
    return sha256(canonical(sorted(values))).hexdigest()


def ports(mask):
    return [i for i in range(112) if mask >> i & 1]


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p not in pivots:
                pivots[p] = row
                break
            row ^= pivots[p]
    return len(pivots)


def literal_rank(matrix):
    """Independent list-of-bits Gauss-Jordan oracle; no packed-row helper."""
    a = [list(row) for row in matrix]
    r = 0
    for j in range(len(a[0]) if a else 0):
        p = next((i for i in range(r, len(a)) if a[i][j]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        for i in range(len(a)):
            if i != r and a[i][j]:
                a[i] = [u ^ v for u, v in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def det3(a):
    return (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
            - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
            + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]))


def rational_rank(matrix):
    """Exact characteristic-zero oracle for the small fixture source spaces."""
    a, r = [[Fraction(v) for v in row] for row in matrix], 0
    for j in range(len(a[0]) if a else 0):
        p = next((i for i in range(r, len(a)) if a[i][j]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        pivot = a[r][j]
        a[r] = [v / pivot for v in a[r]]
        for i in range(r + 1, len(a)):
            factor = a[i][j]
            if factor:
                a[i] = [u - factor * v for u, v in zip(a[i], a[r])]
        r += 1
    return r


def check_source(raw, expected):
    need(sha256(raw).hexdigest() == expected, "geometry SHA256 mismatch")
    return json.loads(raw)


def load_geometry():
    inventory = json.loads((HERE / "SOURCES.json").read_text())["files"]
    expected = next(v["sha256"] for v in inventory if v["path"] == GEOMETRY)
    raw = (ROOT / GEOMETRY).read_bytes()
    data = check_source(raw, expected)
    changed = json.loads(raw)
    changed["labels"][0] ^= 1
    rejected(lambda: check_source(canonical(changed), expected), "source-drift control")
    return data


def rejected(function, message):
    try:
        function()
    except ValueError:
        return
    raise ValueError(message + " accepted")


def codes_from_geometry(data):
    x, labels, duals = data["X"], data["labels"], data["duals"]
    need(len(x) == len(labels) == len(duals) == 112, "112-port geometry")
    need(all(len(row) == 8 and all(type(v) is int for v in row) for row in x), "integer X")
    need(len(set(labels)) == 112 and all(0 < q < 512 for q in labels), "distinct live labels")
    need(all(type(q) is int and 0 < q < 512 for q in duals), "nine-bit dual labels")
    supports, codes = [], []
    for j in range(8):
        support = sum((row[j] != 0) << i for i, row in enumerate(x))
        active = ports(support)
        code = sorted({sum(((q & labels[i]).bit_count() & 1) << i for i in active)
                       for q in range(512)})
        span = {0}
        for i in active:
            row = sum(((duals[i] & labels[t]).bit_count() & 1) << t for t in active)
            if row not in span:
                span |= {v ^ row for v in span}
        need(len(active) == 56 and len(code) == 256 and set(code) == span, "literal/ambient code equality")
        need(rank(duals[i] for i in active) == 8, "fixed-reader dual span")
        need(Counter(w.bit_count() for w in code) == {0: 1, 24: 63, 28: 128, 32: 63, 56: 1}, "weights")
        supports.append(support)
        codes.append(code)
    need(all((supports[j] & supports[k]).bit_count() == 24 for j, k in combinations(range(8), 2)), "pair intersections")
    return supports, codes


def losses(codes, deleted):
    out = []
    for code in codes:
        n = sum(w & ~deleted == 0 for w in code)
        need(n > 0 and n & (n - 1) == 0, "kernel cardinality")
        out.append(n.bit_length() - 1)
    return out


def copy_rank(data, reader, source, literal=False):
    rows = [i for i, v in enumerate(reader) if v]
    columns = [i for i, v in enumerate(source) if v]
    a = [[(data["duals"][i] & data["labels"][t]).bit_count() & 1 for t in columns] for i in rows]
    return literal_rank(a) if literal else rank(sum(v << j for j, v in enumerate(row)) for row in a)


def checked_losses(data, codes, deleted):
    out = []
    for j in range(8):
        reader = [row[j] for row in data["X"]]
        source = [v if not deleted >> i & 1 else 0 for i, v in enumerate(reader)]
        out.append(8 - copy_rank(data, reader, source, literal=True))
    need(out == losses(codes, deleted), "kernel/literal rank disagreement")
    return out


def local_inventories(codes, supports):
    two, three, report = [], [], []
    for j, code in enumerate(codes):
        atoms = [w for w in code if 0 < w.bit_count() <= CAP]
        pairs = sorted({a | b for a, b in combinations(atoms, 2) if (a | b).bit_count() <= CAP})
        need(len(pairs) == 10353, "two-space support count")
        need(all(sum(w & ~u == 0 for w in code) == 4 for u in pairs), "two-space closures")
        triples = sorted({u | w for u in pairs for w in atoms if w & ~u and (u | w).bit_count() <= CAP})
        need(len(triples) == 12012, "three-space support count")
        need(all(sum(w & ~u == 0 for w in code) == 8 for u in triples), "three-space closures")
        fourth = min((u | w).bit_count() for u in triples for w in atoms if w & ~u)
        need(min(u.bit_count() for u in pairs) == 36, "second loss threshold")
        need(Counter(u.bit_count() for u in triples) == {44: 1260, 46: 10752}, "third loss supports")
        need(fourth == 48, "fourth loss threshold")
        extra = min(((supports[j] & supports[k]) & ~u).bit_count()
                    for u in triples for k in range(8) if k != j if (supports[j] & supports[k]) & ~u)
        need(extra == 4, "positive third-support common-cut extension")
        report.append({"reader": j, "code_digest": digest(code), "two_count": len(pairs),
                       "two_weights": dict(Counter(u.bit_count() for u in pairs)), "two_digest": digest(pairs),
                       "three_count": len(triples), "three_weights": dict(Counter(u.bit_count() for u in triples)),
                       "three_digest": digest(triples), "fourth_minimum": fourth, "positive_common_cut_extension": extra})
        two.append(pairs)
        three.append(triples)
    return two, three, report


def reader_joins(codes, two, data):
    atoms = [[w for w in code if 0 < w.bit_count() <= CAP] for code in codes]
    joins, reports, four = {(): {0}}, [], set()
    for size in range(1, 6):
        for readers in combinations(range(8), size):
            values = {u | w for u in joins[readers[:-1]] for w in atoms[readers[-1]] if (u | w).bit_count() <= CAP}
            joins[readers] = values
            reports.append({"readers": list(readers), "count": len(values),
                            "weights": dict(Counter(u.bit_count() for u in values)), "digest": digest(values)})
            if size == 3:
                need(min(u.bit_count() for u in values) == 40, "three-reader threshold")
            if size == 4:
                four |= values
            if size == 5:
                need(not values, "no five affected readers through 47")
    need(len(four) == 42 and all(u.bit_count() == 40 for u in four), "complete four-reader unions through 47")
    cuts = []
    for u in sorted(four):
        profile = checked_losses(data, codes, u)
        hit = [j for j, d in enumerate(profile) if d]
        need(len(hit) == 4 and sum(profile) == 4, "four-cut losses")
        extra = min((v & ~u).bit_count() for j in hit for v in two[j])
        need(extra == 12, "four-cut second-loss margin")
        cuts.append({"ports": ports(u), "losses": profile, "extra_for_second": extra})
    return reports, cuts


def cancellation_obligations(data, codes, supports):
    cross, minors = [], []
    for j in range(8):
        for k in range(8):
            if j == k:
                continue
            contained = [w for w in codes[k] if w and w & ~supports[j] == 0]
            need(contained == [supports[j] & supports[k]], "unique shared cut")
            extra = min((w & ~supports[j]).bit_count() for w in codes[k] if w & ~supports[j])
            need(extra == 12, "nonshared word outside another coordinate")
            cross.append({"inside_reader": j, "word_reader": k, "contained_ports": ports(contained[0]), "noncontained_minimum": extra})
    x = data["X"]
    for columns in combinations(range(8), 3):
        common = [i for i, row in enumerate(x) if all(row[j] for j in columns)]
        need(len(common) == 8, "triple support intersection")
        witness = next((idx for idx in combinations(common, 3) if det3([[x[i][j] for j in columns] for i in idx])), None)
        need(witness is not None, "rank-three common cancellation block")
        matrix = [[x[i][j] for j in columns] for i in witness]
        minors.append({"columns": list(columns), "common_ports": common, "minor_ports": list(witness), "matrix": matrix, "determinant": det3(matrix)})
    return cross, minors


def critical_cancellation_classes(data, supports, three):
    """Explicitly check every minimal 3+1+1 class, without using symmetry."""
    report = []
    x = data["X"]
    for j in range(8):
        critical = []
        for u in three[j]:
            other = [k for k in range(8) if k != j and (supports[j] & supports[k]) & ~u == 0]
            if len(other) < 2:
                continue
            need(len(other) == 2 and u.bit_count() == 44, "critical shape and minimum support")
            columns = [j, *other]
            common = supports[j] & supports[other[0]] & supports[other[1]]
            need(common & ~u == 0, "common cancellation rows lie inside the third-loss support")
            matrix = [[x[i][k] for k in columns] for i in ports(common)]
            need(rational_rank(matrix) == 3, "critical partial completion requires rank three")
            critical.append([u, *columns])
        need(len(critical) == 84, "84 critical cancellation classes per reader")
        report.append({"third_loss_reader": j, "critical_classes": len(critical),
                       "support_size": 44, "forced_rank": 3, "classes_digest": digest(critical)})
    return report


def minor2(matrix):
    for i, j in combinations(range(len(matrix)), 2):
        d = matrix[i][0] * matrix[j][1] - matrix[i][1] * matrix[j][0]
        if d:
            return {"rows": [i, j], "determinant": d}
    raise ValueError("fixture should have rank two")


def fixture(data, deleted, coordinates, mixed):
    x, width = data["X"], len(coordinates)
    a = [[int(j == k) for k in coordinates] for j in range(8)]
    z = [[row[k] if deleted >> i & 1 else 0 for k in coordinates] for i, row in enumerate(x)]
    if mixed:
        # A -> A [[1,1],[0,1]], Z -> Z [[1,0],[-1,1]] preserves AZ^t.
        need(width == 2, "mixed fixture width")
        a = [[row[0], row[0] + row[1]] for row in a]
        z = [[row[0] - row[1], row[1]] for row in z]
    d = [[sum(row[j] * a[j][h] for j in range(8)) for h in range(width)] for row in x]
    t = [[row[j] - sum(z[i][h] * a[j][h] for h in range(width)) for j in range(8)] for i, row in enumerate(x)]
    for i in range(112):
        for u in range(112):
            left = sum(x[i][j] * x[u][j] for j in range(8))
            right = sum(x[i][j] * t[u][j] for j in range(8)) + sum(d[i][h] * z[u][h] for h in range(width))
            need(left == right, "complete all-pairs identity")
    retained, added = [], []
    for readers, sources, count, out in [(x, t, 8, retained), (d, z, width, added)]:
        for j in range(count):
            reader, source = [row[j] for row in readers], [row[j] for row in sources]
            r = copy_rank(data, reader, source)
            need(r == copy_rank(data, reader, source, literal=True), "fixture rank oracles")
            out.append(r)
    union = sum(any(row) << i for i, row in enumerate(z))
    need(union == deleted, "fixture source union")
    result = {"coordinates": coordinates, "A": a, "Z": z, "source_union_ports": ports(union),
              "retained_copy_ranks": retained, "added_copy_ranks": added, "total_copy_rank": sum(retained + added),
              "retained_loss": 64 - sum(retained), "all_pairs_checked": 12544}
    result["source_matrix_rank"] = rational_rank(z)
    result["extended_source_rank"] = rational_rank([row + z[i] for i, row in enumerate(x)])
    need(result["source_matrix_rank"] == width, "independent fixture source columns")
    need(result["extended_source_rank"] == 8 + width, "fixture sources leave col(X)")
    if mixed:
        need(any(row[0] and row[1] for row in a), "overlapping coefficient supports")
        result.update({"A_rank_two_minor": minor2(a), "Z_rank_two_minor": minor2(z)})
    return result


def added_reader_premise(data):
    # F3 rank supplies a LOWER bound only; symbolic zero columns/width give upper bounds.
    counts, exceptions = Counter(), []
    for q in range(1, 512):
        raw = [row for row, dual in zip(data["X"], data["duals"]) if (q & dual).bit_count() & 1]
        a, r = [[v % 3 for v in row] for row in raw], 0
        for j in range(8):
            p = next((i for i in range(r, len(a)) if a[i][j]), None)
            if p is None:
                continue
            a[r], a[p] = a[p], a[r]
            inverse = pow(a[r][j], -1, 3)
            a[r] = [v * inverse % 3 for v in a[r]]
            for i in range(r + 1, len(a)):
                f = a[i][j]
                if f:
                    a[i] = [(u - f * v) % 3 for u, v in zip(a[i], a[r])]
            r += 1
        counts[r] += 1
        if r == 7:
            zero = [j for j in range(8) if all(row[j] == 0 for row in raw)]
            need(len(zero) == 1, "symbolic exceptional upper rank bound")
            exceptions.append({"q": q, "kernel_coordinate": zero[0]})
        else:
            need(r == 8, "rank-eight modular lower bound")
    need(counts == {7: 8, 8: 503}, "503/8 rank premise")
    need(sorted(row["kernel_coordinate"] for row in exceptions) == list(range(8)), "distinct exceptional kernels")
    need(not set(data["labels"]) & {row["q"] for row in exceptions}, "live-label visibility")
    return {"modulus": 3, "rank_counts": dict(counts), "exceptions": exceptions}


def calculate(data):
    supports, codes = codes_from_geometry(data)
    two, three, local = local_inventories(codes, supports)
    joins, four = reader_joins(codes, two, data)
    cross, minors = cancellation_obligations(data, codes, supports)
    critical = critical_cancellation_classes(data, supports, three)
    added = added_reader_premise(data)
    j = SEED % 8
    candidates = [u for u in three[j] if u.bit_count() == 44 and sum(losses(codes, u)) == 5]
    need(len(candidates) == 84, "84 sharp supports for seed-selected reader")
    anchor = min(candidates, key=lambda u: sha256(f"{SEED}:{u}".encode()).digest())
    anchor_losses = checked_losses(data, codes, anchor)
    other = [k for k, value in enumerate(anchor_losses) if value == 1]
    need(anchor_losses[j] == 3 and len(other) == 2, "sharp loss shape 3+1+1")
    deleted, witnesses = anchor, []
    for size in range(44, 48):
        if size > 44:
            i = next((SEED + k) % 112 for k in range(112) if not deleted >> ((SEED + k) % 112) & 1)
            deleted |= 1 << i
        profile = checked_losses(data, codes, deleted)
        need(deleted.bit_count() == size and sum(profile) == 5, "sharp geometric five-loss witness")
        witnesses.append({"size": size, "ports": ports(deleted), "losses": profile})
    positive = fixture(data, anchor, [j, other[0]], mixed=True)
    relaxed = fixture(data, anchor, [j, *other], mixed=False)
    need(positive["retained_loss"] == 4, "rank-two loss-four attainment")
    need(relaxed["retained_loss"] == 5, "rank-three control attains five")
    need(sum(checked_losses(data, codes, anchor ^ (anchor & -anchor))) <= 4, "one-port-short control")
    prices = []
    def price(m):
        return next(r for r in range(1, 9) if m <= 1 << (r + 1))
    for size in range(1, 48):
        geometric = 0 if size < 24 else 2 if size < 36 else 3 if size < 40 else 4 if size < 44 else 5
        realizable = min(geometric, 4)
        bill = min(price(a) + price(b) for a in range(1, size + 1) for b in range(1, size + 1) if a + b >= size)
        lower = 64 - realizable + bill
        need(lower >= 66, "complete full-rank on-column COPY lower bill")
        prices.append({"source_union_size": size, "geometric_loss_upper_bound": geometric,
                       "rank_two_loss_upper_bound": realizable, "added_price_lower_bound": bill, "total_copy_lower_bound": lower})
    return {"schema_version": 1, "assignment_seed": SEED, "deletion_domain": [0, CAP],
            "local_support_inventories": local, "first_loss_joins": joins, "four_reader_cuts": four,
            "ordered_cross_reader_obligations": cross, "cancellation_minors": minors, "added_reader_premise": added,
            "critical_cancellation_classes": critical,
            "new_geometric_sharpness_witnesses": witnesses, "rank_two_overlapping_fixture": positive,
            "rank_three_relaxed_control": relaxed, "full_rank_two_total_price_screen": prices,
            "controls": ["source drift rejected", "geometric loss four falsified at 44", "three-total relaxation attains loss five",
                         "56 nonzero cancellation minors", "one port short reduces loss", "packed/literal ranks agree"]}


def validate_result(actual, expected):
    need(canonical(actual) == canonical(expected), "complete result mismatch")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new receipt; refuse to overwrite")
    args = parser.parse_args()
    actual = calculate(load_geometry())
    changed = json.loads(canonical(actual))
    changed["new_geometric_sharpness_witnesses"][0]["losses"][SEED % 8] -= 1
    rejected(lambda: validate_result(actual, changed), "corrupted-receipt control")
    if args.write:
        with args.write.open("x") as stream:
            json.dump(actual, stream, sort_keys=True, indent=2)
            stream.write("\n")
    else:
        validate_result(actual, json.loads((HERE / "RESULT.json").read_text()))
    print("PASS_P112_JOINT_LOSS_BOUNDARY domain=44..47 geometric_max=5 rank_two_loss_bound=4 full_rank_copy_floor=66 no_new_kappa")


if __name__ == "__main__":
    main()
