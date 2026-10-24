"""Exact corroboration of the paired-Dn bipartite basis theorem. Stdlib only."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
HASH_FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
              "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows):
    """Binary elimination, with at most len(rows) pivots."""
    pivots = {}
    for original in rows:
        value = original
        for _ in range(original.bit_length() + 1):
            if not value:
                break
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
        else:
            raise ValueError("elimination did not terminate")
    return len(pivots)


def span_rank(rows):
    """Independent cardinality-of-span oracle, bounded to eight input rows."""
    require(len(rows) <= 8, "span oracle capacity exceeded")
    span = {0}
    for row in rows:
        span |= {value ^ row for value in span}
    require(len(span) & (len(span) - 1) == 0, "span size is not a power of two")
    return len(span).bit_length() - 1


def roots(n, edges):
    require(2 <= n <= 8, "fixture dimension outside 2..8")
    require(len(edges) <= n * (n - 1) // 2, "too many fixture edges")
    require(len(set(edges)) == len(edges), "duplicate edge")
    result = []
    for a, b in edges:
        require(0 <= a < b < n, "invalid edge")
        for sign in (1, -1):
            result.append(tuple(int(i == a) + sign * int(i == b)
                                for i in range(n)))
    return result


def dot(left, right):
    return sum(a * b for a, b in zip(left, right, strict=True))


def fitting_pairings(r):
    """Complete small directed pairing census, including the diagonal ones."""
    free = [(i, j) for i in range(len(r)) for j in range(len(r))
            if i != j and dot(r[i], r[j]) == 0]
    require(len(free) <= 12, "complete pairing census capacity exceeded")
    for bits in range(1 << len(free)):
        rows = [1 << i for i in range(len(r))]
        for k, (i, j) in enumerate(free):
            rows[i] |= ((bits >> k) & 1) << j
        yield rows


def attaining_pairing(r):
    """One J_2 block for each sign pair; zero between different edges."""
    return [3 << (2 * (i // 2)) for i in range(len(r))]


def sample_pairing(r, seed):
    rows = [1 << i for i in range(len(r))]
    for i in range(len(r)):
        for j in range(len(r)):
            if i != j and dot(r[i], r[j]) == 0:
                bit = ((i + 3) * (j + 5) + seed * (i + 2 * j + 1)) % 7 < 3
                rows[i] |= int(bit) << j
    return rows


def factors(n, edges, split, coefficients):
    """R(I+N), R(I-N^T), where N maps the complement into split."""
    require(0 <= split < 1 << n, "invalid coordinate split")
    pairs = [(a, b) for a in range(n) for b in range(n)
             if (split >> a) & 1 and not (split >> b) & 1]
    require(len(coefficients) == len(pairs), "wrong coefficient count")
    require(all(isinstance(x, (int, F)) and not isinstance(x, bool)
                for x in coefficients), "nonrational coefficient")
    r = roots(n, edges)
    p = [list(row) for row in r]
    q = [list(row) for row in r]
    for (a, b), coefficient in zip(pairs, coefficients, strict=True):
        for i, row in enumerate(r):
            p[i][b] += row[a] * coefficient
            q[i][a] -= row[b] * coefficient
    for i in range(len(r)):
        for j in range(len(r)):
            require(dot(p[i], q[j]) == dot(r[i], r[j]), "literal Gram identity")
    supports = [([i for i in range(len(r)) if p[i][j]],
                 [i for i in range(len(r)) if q[i][j]]) for j in range(n)]
    return r, supports


def rectangle(rows, left, right):
    return [sum(((rows[i] >> j) & 1) << k for k, j in enumerate(right))
            for i in left]


def prices(rows, supports, independent=False):
    result = []
    for left, right in supports:
        block = rectangle(rows, left, right)
        value = rank(block)
        if independent:
            require(value == span_rank(block), "rank oracles disagree")
        result.append(value)
    return result


def check_minor(rows, supports, edges, n):
    """Check the proof's actual identity minor, one surviving root per edge."""
    for j in range(n):
        left, right = supports[j]
        common = set(left) & set(right)
        selected = []
        for e, edge in enumerate(edges):
            if j in edge:
                candidates = [i for i in (2 * e, 2 * e + 1) if i in common]
                require(candidates, "no surviving sign root")
                selected.append(candidates[0])
        require(rectangle(rows, selected, selected)
                == [1 << k for k in range(len(selected))], "forced identity minor")


def check_family(n, edges, split, coefficients, pairings, stats, independent):
    r, supports = factors(n, edges, split, coefficients)
    stats["gram_factorizations"] += 1
    degrees = [sum(j in edge for edge in edges) for j in range(n)]
    require(prices(attaining_pairing(r), supports, independent) == degrees,
            "attaining pairing missed exact degree prices")
    stats["attainments"] += 1
    for rows in pairings:
        check_minor(rows, supports, edges, n)
        bill = prices(rows, supports, independent)
        require(all(a >= b for a, b in zip(bill, degrees, strict=True)),
                "degree floor failed")
        stats["pairing_bills"] += 1
        stats["term_minors"] += n


def small_census(stats):
    """Every nonempty D3 paired graph, every split and ternary cross matrix."""
    edges_all = list(combinations(range(3), 2))
    for graph in range(1, 8):
        edges = [edge for k, edge in enumerate(edges_all) if (graph >> k) & 1]
        pairings = list(fitting_pairings(roots(3, edges)))
        for split in range(8):
            size = split.bit_count() * (3 - split.bit_count())
            for values in product((-1, 0, 1), repeat=size):
                check_family(3, edges, split, values, pairings, stats, True)


def larger_fixtures(stats):
    """Paired deletions, disjoint-edge freedoms and rational multi-axis mixing."""
    edges = [(0, 1), (2, 3)]
    r = roots(4, edges)
    for values in ((1, 0, 0, 0), (1, -1, F(1, 2), F(2, 3))):
        check_family(4, edges, 3, values, fitting_pairings(r), stats, True)
    for n in range(4, 9):
        all_edges = list(combinations(range(n), 2))
        for mode in range(3):
            edges = [edge for k, edge in enumerate(all_edges)
                     if mode == 0 or k % 3 == mode - 1]
            for split in (1, (1 << (n // 2)) - 1, (1 << n) - 2):
                size = split.bit_count() * (n - split.bit_count())
                values = tuple(F(((k + mode) % 5) - 2, (k % 3) + 1)
                               for k in range(size))
                r = roots(n, edges)
                pairings = [sample_pairing(r, seed) for seed in range(7)]
                check_family(n, edges, split, values, pairings, stats, False)


def first_fixture(stats):
    edges = [(0, 1), (0, 2), (0, 4), (1, 2), (2, 3), (3, 4)]
    r, supports = factors(5, edges, 1, (1, 0, 0, 0))
    bill = prices(attaining_pairing(r), supports)
    require(bill == [3, 2, 3, 2, 2], "D5 single-shear first fixture")
    stats["first_D5_fixture"] = {"edges": edges, "prices": bill, "total": sum(bill)}


def controls():
    r, supports = factors(3, [(0, 1), (0, 2), (1, 2)], 1, (1, -1))
    all_ones = [(1 << len(r)) - 1] * len(r)
    require(sum(prices(all_ones, supports)) < len(r), "missing-zero control")
    require(sum(prices([0] * len(r), supports)) == 0, "missing-diagonal control")
    require(dot((1, 1), (1, 1)) % 2 == 0
            and dot((1, -1), (1, 1)) % 2 == 0, "characteristic-two control")
    require(dot((1, 1), (1, -1)) == 0, "single-sign cancellation control")
    require(rank([3, 3]) == 1 and span_rank([3, 3]) == 1,
            "pair block must cost one, not its two rows")
    rejected = 0
    invalid = ((2, [(0, 0)], 1, (1,)), (2, [(0, 1)], 4, ()),
               (2, [(0, 1)], 1, ()), (2, [(0, 1)], 1, (True,)))
    for args in invalid:
        try:
            factors(*args)
        except ValueError:
            rejected += 1
    require(rejected == len(invalid), "input rejection control")
    return {"mathematical_boundaries": 5, "invalid_inputs": rejected}


def evidence():
    stats = {"gram_factorizations": 0, "attainments": 0,
             "pairing_bills": 0, "term_minors": 0}
    first_fixture(stats)
    small_census(stats)
    larger_fixtures(stats)
    return {"claim_type": "scoped proof with finite exact corroboration",
            "theorem": "minimum COPY cost = 2|E| for paired Dn bipartite bases",
            "evidence": stats, "controls": controls(),
            "source_sha256": {name: sha256((HERE / name).read_bytes()).hexdigest()
                              for name in HASH_FILES}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="create a new generated receipt")
    args = parser.parse_args()
    actual = evidence()
    serialized = json.dumps(actual, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        with args.output.open("x", encoding="utf-8") as stream:
            require(stream.write(serialized) == len(serialized), "partial receipt write")
    else:
        expected = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
        require(json.dumps(expected, sort_keys=True) == json.dumps(actual, sort_keys=True),
                "receipt or source hashes differ")
    print("PASS_DN_BIPARTITE_BASIS_FLOOR " + json.dumps(actual["evidence"], sort_keys=True))


if __name__ == "__main__":
    main()
