"""Exact premise checks and independent certificates for PROOF.md (stdlib).

No SAT solver, numerical rank routine, or upstream implementation is imported.
The written proof covers arbitrary lengths; this program verifies its finite
geometric premises and independently excludes the only ten-term threat.
"""
import argparse
import copy
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

from exact import Instance, dot, generated_root_set, inverse_f2, parity, rank_f2, require

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
WORDS = {
    "pr545": "research/e8-punctured111-star/data/bitE8mut-v111-r489.json.gz",
    "pr555": "research/e8-bit-p111/data/bitE8mut-p111.json.gz",
}


def fraction_basis(rows):
    """Gaussian elimination with explicit rational division, separate from exact.py."""
    echelon = {}
    for row in rows:
        row = list(map(Fraction, row))
        for pivot in sorted(echelon):
            scale = row[pivot]
            if scale:
                row = [x - scale * y for x, y in zip(row, echelon[pivot])]
        p = next((i for i, x in enumerate(row) if x), None)
        if p is not None:
            scale = row[p]
            echelon[p] = [x / scale for x in row]
    return list(echelon.values())


def decoder_entries(instance):
    """Compare reconstructed and geometric decoder on every live ordered pair."""
    count = 0
    for t, r in zip(instance.live, instance.labels):
        for s, q in zip(instance.live, instance.labels):
            rq = 0
            for j, row in enumerate(instance.target):
                rq |= parity(row & q) << j
            actual = parity(r & rq)
            want = (1 + dot(instance.lines[t], instance.lines[s]) // 2) % 2
            require(actual == want, "live decoder entry mismatch")
            count += 1
    return count


def geometry(instance):
    full_word = json.loads(gzip.decompress((REPO / "research/e8-bit-r420/data/bitE8mut-r420.json.gz").read_bytes()))
    require(full_word["lines"] == [list(r) for r in instance.lines], "full root ordering/source mismatch")
    word = json.loads(gzip.decompress((REPO / WORDS[instance.name]).read_bytes()))
    require(word["punctured"] == instance.punctures, "puncture/source mismatch")
    require(word["ports_geom"] == instance.live, "live/source mismatch")
    require(word["lines"] == [list(instance.lines[i]) for i in instance.live],
            "root numbering/source mismatch")
    require(all((row >> i) & 1 for i, row in enumerate(instance.B)), "missing unit diagonal")
    require(all(((instance.B[i] >> j) & 1) == ((instance.B[j] >> i) & 1)
                for i in range(9) for j in range(9)), "nonsymmetric puncture Gram")
    independent = {}
    for x in range(1, 512):
        # Derive support directly from root inner products, without labels.
        support = []
        for v in instance.live:
            bit = sum(((1 + dot(instance.lines[v], instance.lines[p]) // 2) % 2)
                      for j, p in enumerate(instance.punctures) if (x >> j) & 1) % 2
            if bit:
                support.append(v)
        require(support == instance.readers[x], "reader support mismatch")
        independent[x] = fraction_basis(instance.lines[v] for v in support)
        unit = x & (x - 1) == 0
        require(len(independent[x]) == (7 if unit else 8), "rational span mismatch")
        if unit:
            normal = instance.lines[instance.punctures[x.bit_length() - 1]]
            require(all(dot(v, normal) == 0 for v in independent[x]), "wrong normal")

    # Nine deficient hyperplanes and the full space: complete span-class cover.
    representatives = [1 << i for i in range(9)] + [3]
    for x, y in product(representatives, repeat=2):
        block = [[dot(r, s) for s in independent[y]] for r in independent[x]]
        require(len(fraction_basis(block)) == instance.cost(x, y), "copy-rank mismatch")
    costs = Counter(instance.cost(x, y) for x in range(1, 512) for y in range(1, 512))
    return {
        "reader_spans": 511,
        "span_dimensions": {"7": 9, "8": 502},
        "ordered_span_class_pairs": 100,
        "ordered_nonzero_pairs_covered": 511 ** 2,
        "pair_cost_histogram": {str(k): v for k, v in sorted(costs.items())},
        "live_decoder_entries": decoder_entries(instance),
        "punctures": instance.punctures,
        "binary_puncture_gram_rows": instance.B,
        "target_inverse_rows": instance.target,
    }


def minor_rank(rows, row_indices, column_indices):
    sub = [sum(((rows[r] >> c) & 1) << j for j, c in enumerate(column_indices))
           for r in row_indices]
    return rank_f2(sub), sub


def ten_term_minor(instance):
    """A second, finite obstruction, independent of the projection proof.

Find a rank-three target minor on which every cost-six unit cell vanishes.
Then at least three noncheap terms are needed; cost <=62 at n=10 permits
at most two. This check proves infeasibility below63, not the stronger >=64.
"""
    for rows in combinations(range(9), 3):
        for columns in combinations(range(9), 3):
            if any(instance.cost(1 << r, 1 << c) == 6 for r in rows for c in columns):
                continue
            rank, minor = minor_rank(instance.target, rows, columns)
            if rank == 3:
                return {"rows": list(rows), "columns": list(columns),
                        "minor_rows_binary": minor, "rank": 3,
                        "cost6_cells_on_minor": 0}
    raise ValueError("no independent ten-term minor certificate")


def binary_matvec(columns, bits):
    out = 0
    for i, c in enumerate(columns):
        if (bits >> i) & 1:
            out ^= c
    return out


def small_projection_checks():
    """Exhaust all nonsingular symmetric unit-diagonal 3x3 B and all
    nonzero 3x3/3x4 factorizations B^-1=XY^t. Tests the proof mechanism,
    not a substitute for the dimension-nine argument.
    """
    dimension = 3
    count = {3: 0, 4: 0}
    matrices = 0
    for mask in range(8):
        B = [1 << i for i in range(3)]
        for bit, (i, j) in enumerate(combinations(range(3), 2)):
            if (mask >> bit) & 1:
                B[i] |= 1 << j
                B[j] |= 1 << i
        if rank_f2(B) != 3:
            continue
        matrices += 1
        target = inverse_f2(B, 3)
        for n in (3, 4):
            for X in product(range(1, 8), repeat=n):
                if rank_f2(X) != 3:
                    continue
                preimages = [[] for _ in range(8)]
                for z in range(1 << n):
                    preimages[binary_matvec(X, z)].append(z)
                # target is symmetric, so its rows are also its columns.
                for zcols in product(*(preimages[t] for t in target)):
                    Y = [sum(((zcols[j] >> i) & 1) << j for j in range(3)) for i in range(n)]
                    if not all(Y):
                        continue
                    count[n] += 1
                    unitX = {x for x in X if x & (x - 1) == 0}
                    unitY = {y for y in Y if y & (y - 1) == 0}
                    K = []
                    for y in Y:
                        row = 0
                        for j, x in enumerate(X):
                            bx = sum(parity(b & x) << a for a, b in enumerate(B))
                            row |= parity(y & bx) << j
                        K.append(row)
                    if n == 3:
                        require(K == [1 << i for i in range(n)], "biorthogonality failed")
                        same = sum(x == y and x & (x - 1) == 0 for x, y in zip(X, Y))
                        require(len(unitX & unitY) == same, "unit-intersection lemma failed")
                    else:
                        require(rank_f2([r ^ (1 << i) for i, r in enumerate(K)]) == 1,
                                "rank-one projection complement failed")
                        cheap = [i for i, (x, y) in enumerate(zip(X, Y))
                                 if x in unitX and y in unitY and x != y and (K[i] >> i) & 1]
                        k = len(cheap)
                        require(k <= (2 * dimension) // 3, "cheap-term projection bound failed")
                        rank, _ = minor_rank(K, cheap, cheap)
                        require(rank == k, "cheap principal minor singular")
    return {"dimension": 3, "binary_gram_matrices": matrices,
            "square_factorizations": count[3], "one_extra_term_factorizations": count[4]}


def rejected(fn):
    try:
        fn()
    except (ValueError, TypeError, IndexError):
        return
    raise ValueError("negative control was not rejected")


def negative_controls(instance):
    baseline = instance.baseline()
    wrong = copy.deepcopy(baseline)
    wrong[0][1] ^= 1
    rejected(lambda: instance.evaluate(wrong))
    rejected(lambda: instance.evaluate(baseline[:-1]))
    wrong = copy.deepcopy(baseline)
    wrong[0][0] = 0
    rejected(lambda: instance.evaluate(wrong))
    wrong = copy.deepcopy(baseline)
    wrong[0][0] = True
    rejected(lambda: instance.evaluate(wrong))
    bad = copy.deepcopy(instance)
    bad.target[0] ^= 1
    rejected(lambda: decoder_entries(bad))
    bad = copy.deepcopy(instance)
    bad.labels[0] ^= 1
    rejected(lambda: decoder_entries(bad))
    bad = copy.deepcopy(instance)
    bad.lines = generated_root_set()
    rejected(lambda: geometry(bad))
    # A false unit-pair discount must disagree with direct rational rank.
    rejected(lambda: require(instance.direct_cost(1, 1) == 6, "false discount"))
    # Without unit diagonal, the endpoint-count lemma really is false:
    # B=[[0,1],[1,0]], X=I, Y=B yields biorthogonality but four distinct
    # endpoint occurrences across two coordinates and no same-term match.
    B = [2, 1]
    require(inverse_f2(B, 2) == B, "control inverse")
    X, Y = [1, 2], [2, 1]
    require(sum(x == y for x, y in zip(X, Y)) == 0 and len(set(X) & set(Y)) == 2,
            "diagonal-premise counterexample lost")
    rejected(lambda: require(all((r >> i) & 1 for i, r in enumerate(B)), "missing diagonal premise"))
    return ["wrong_coefficient", "missing_total", "zero_factor", "boolean_factor",
            "corrupted_target", "corrupted_live_label", "wrong_root_order", "false_copy_discount", "missing_unit_diagonal"]


def source_pins():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for name, expected in sources["files"].items():
        actual = hashlib.sha256((REPO / name).read_bytes()).hexdigest()
        require(actual == expected, "source pin mismatch: " + name)
    return len(sources["files"])


def run():
    pins = source_pins()
    results = {}
    for name in ("pr545", "pr555"):
        instance = Instance(name)
        row = geometry(instance)
        witness = json.loads((HERE / ("baseline-" + name + ".json")).read_text())
        require(witness["instance"] == name, "witness fixture mismatch")
        row["attainment"] = instance.evaluate(witness["terms"])
        require(row["attainment"]["cost"] == 63, "baseline cost changed")
        row["independent_ten_term_minor"] = ten_term_minor(instance)
        row["negative_controls"] = negative_controls(instance)
        results[name] = row
    old = generated_root_set()
    actual = Instance("pr545").lines
    permutation = [actual.index(r) for r in old]
    ordering = {"first_mismatch": {"index": 8, "archived_root": list(old[8]), "supplier_root": list(actual[8])},
                "same_signed_root_set": set(old) == set(actual),
                "archived_to_supplier_permutation": permutation,
                "mapped_archived_punctures": {name: sorted(permutation[i] for i in row["punctures"])
                                              for name, row in results.items()}}
    require(ordering == json.loads((HERE / "ORDERING.json").read_text()), "root ordering receipt mismatch")
    return {
        "format": "p111-copy-rank-certificate-v1",
        "source_pins_checked": pins,
        "root_ordering_checked": True,
        "fixtures": results,
        "small_projection_checks": small_projection_checks(),
        "proved_bounds_by_term_count": {"n_lt_9": "rank obstruction",
                                        "n_eq_9": 63, "n_eq_10": 64, "n_ge_11": "6*n >= 66"},
        "optimum": 63,
        "scope": "Written algebraic proof plus exact finite premise checks; no new kappa or full supplier proof",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    result = run()
    if args.check:
        require(json.loads(args.check.read_text()) == result, "receipt mismatch")
    if args.write:
        args.write.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print("PASS_P111_COPY_RANK: optimum 63 on two fixtures; exact geometry, independent minors, 18 negative controls")


if __name__ == "__main__":
    main()
