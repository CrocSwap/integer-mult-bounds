#!/usr/bin/env python3
"""Exact finite corroboration of the README; not an all-parameter proof."""

from collections import Counter
from fractions import Fraction
import hashlib
from heapq import heappop, heappush
from itertools import permutations, product
import json
from pathlib import Path


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _rejects(function, *args):
    try:
        function(*args)
    except ValueError:
        return 1
    raise RuntimeError(f"negative control accepted: {function.__name__}")


def _cut(n, p):
    _require(type(n) is int and n >= 2, "n must be an integer >= 2")
    _require(type(p) is int and 1 <= p < n, "cut must satisfy 1 <= p < n")


def _permutation(w, n):
    _require(isinstance(w, (tuple, list)) and len(w) == n,
             "permutation has wrong size or type")
    _require(all(type(x) is int for x in w) and set(w) == set(range(1, n + 1)),
             "permutation must contain each integer 1..n once")
    return tuple(w)


def _prices(alpha, beta):
    _require(all(type(x) in (int, Fraction) and x >= 0 for x in (alpha, beta)),
             "prices must be nonnegative int/Fraction values")


def _inversions(w):
    return sum(a > b for i, a in enumerate(w) for b in w[i + 1:])


def _crossings(w, p):
    return sum(x > p for x in w[:p])


def tariff(targets, n, p, alpha, beta):
    """Exact proposed tariff on its stated domain, including an empty tuple."""
    _cut(n, p)
    _prices(alpha, beta)
    _require(beta >= alpha, "the tariff requires beta >= alpha")
    _require(isinstance(targets, (tuple, list)), "targets must be a tuple/list")
    words = [_permutation(w, n) for w in targets]
    return sum(alpha * _inversions(w) + (beta - alpha) * _crossings(w, p)
               for w in words)


def sorting_word(w, p):
    """Return 1-based sorting labels, also the chronological left-call word."""
    _require(isinstance(w, (tuple, list)), "permutation must be a tuple/list")
    n = len(w)
    _cut(n, p)
    a = list(_permutation(w, n))
    word = []
    while True:
        for lo, hi in ((0, p), (p, n)):
            for end in range(hi - 1, lo, -1):
                for i in range(lo, end):
                    if a[i] > a[i + 1]:
                        a[i], a[i + 1] = a[i + 1], a[i]
                        word.append(i + 1)
        if all(x <= p for x in a[:p]):
            return tuple(word)
        a[p - 1], a[p] = a[p], a[p - 1]
        word.append(p)


def _dijkstra(n, p, alpha, beta):
    # Deliberately independent of both the tariff and the sorting construction.
    _cut(n, p)
    _prices(alpha, beta)
    start = tuple(range(1, n + 1))
    distances = {start: 0}
    queue = [(0, start)]
    settled = edges = 0
    while queue:
        distance, w = heappop(queue)
        if distances[w] != distance:
            continue
        settled += 1
        for i in range(n - 1):
            v = list(w)
            v[i], v[i + 1] = v[i + 1], v[i]
            v = tuple(v)
            candidate = distance + (beta if i + 1 == p else alpha)
            edges += 1
            if v not in distances or candidate < distances[v]:
                distances[v] = candidate
                heappush(queue, (candidate, v))
    return distances, settled, edges


def _check_distances(counts):
    prices = ((0, 0), (0, 1), (1, 1), (1, 2), (2, 5),
              (Fraction(1, 2), Fraction(3, 2)))
    for n in range(2, 8):
        group = tuple(permutations(range(1, n + 1)))
        counts["permutations"] += len(group)
        identity = tuple(range(1, n + 1))
        for p in range(1, n):
            words = {}
            for w in group:
                word = sorting_word(w, p)
                sorted_w, endpoint = list(w), identity
                for label in word:
                    _require(1 <= label < n and sorted_w[label - 1] > sorted_w[label],
                             f"not an adjacent descent: {n, p, w, label}")
                    sorted_w[label - 1], sorted_w[label] = sorted_w[label], sorted_w[label - 1]
                    # A left call swaps values; sorting above swaps positions.
                    endpoint = tuple(label + 1 if x == label else
                                     label if x == label + 1 else x for x in endpoint)
                _require(tuple(sorted_w) == identity and endpoint == w, "word order/endpoints")
                _require(len(word) == _inversions(w) and word.count(p) == _crossings(w, p),
                         f"construction counts: {n, p, w}")
                words[w] = word
                counts["sorting_cases"] += 1
            for alpha, beta in prices:
                distances, settled, edges = _dijkstra(n, p, alpha, beta)
                _require(set(distances) == set(group) and settled == len(group),
                         "Dijkstra did not settle the complete Cayley graph")
                counts["dijkstra_runs"] += 1
                counts["dijkstra_settled"] += settled
                counts["dijkstra_edges"] += edges
                for w, word in words.items():
                    actual_cost = sum(beta if label == p else alpha for label in word)
                    proposed = tariff((w,), n, p, alpha, beta)
                    _require(distances[w] == proposed == actual_cost,
                             f"weighted distance mismatch: {n, p, alpha, beta, w}")
                    counts["tariff_comparisons"] += 1


def _rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def _binary_product(a, b):
    result = []
    for row in a:
        value = 0
        for j, other in enumerate(b):
            if row >> j & 1:
                value ^= other
        result.append(value)
    return tuple(result)


def _inverse(matrix):
    r = len(matrix)
    rows = [row | (1 << (r + i)) for i, row in enumerate(matrix)]
    for col in range(r):
        pivot = next((i for i in range(col, r) if rows[i] >> col & 1), None)
        _require(pivot is not None, "singular scalar matrix")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        for i in range(r):
            if i != col and rows[i] >> col & 1:
                rows[i] ^= rows[col]
    return tuple(row >> r for row in rows)


def _idempotents(r):
    result = []
    for u in range(1, 1 << r):
        for v in range(1, 1 << r):
            if (u & v).bit_count() % 2:
                matrix = tuple(v if u >> i & 1 else 0 for i in range(r))
                _require(_rank(matrix) == 1 and _binary_product(matrix, matrix) == matrix,
                         "invalid rank-one inventory")
                result.append(matrix)
    _require(len(set(result)) == (2**r - 1) * 2**(r - 1), "incomplete projector inventory")
    return result


def _general_linear(r):
    return [rows for rows in product(range(1 << r), repeat=r) if _rank(rows) == r]


def _action_rows(w, basis):
    index = {address: i for i, address in enumerate(basis)}
    rows = [0] * len(basis)
    for col, address in enumerate(basis):
        rows[index[tuple(w[x - 1] for x in address)]] ^= 1 << col
    return tuple(rows)


def _tensor(scalar, action):
    m = len(action)
    return tuple(sum(row << (j * m) for j in range(len(scalar)) if coefficients >> j & 1)
                 for coefficients in scalar for row in action)


def _crossing_rank(rows, basis, r, p):
    m = len(basis)
    h = [i for i, address in enumerate(basis)
         if (address[0] <= p if len(address) == 1 else address[0] < address[1])]
    columns = sum(1 << (role * m + i) for role in range(r) for i in h)
    return _rank(row & columns for i, row in enumerate(rows) if not columns >> i & 1)


def _check_ranks(counts):
    for r in range(1, 4):
        projectors = _idempotents(r)
        scalars = _general_linear(r)
        counts["rank_one_idempotents"] += len(projectors)
        counts["invertible_scalars"] += len(scalars)
        for n in range(2, 6):
            natural = tuple((i,) for i in range(1, n + 1))
            pairs = tuple((i, j) for i in range(1, n + 1) for j in range(1, n + 1) if i != j)
            for p in range(1, n):
                for name, basis in (("natural", natural), ("ordered_pair", pairs)):
                    for label in range(1, n):
                        w = list(range(1, n + 1))
                        w[label - 1], w[label] = w[label], w[label - 1]
                        action = _action_rows(w, basis)
                        delta = tuple(row ^ (1 << i) for i, row in enumerate(action))
                        for projector in projectors:
                            rows = tuple(row ^ (1 << i)
                                         for i, row in enumerate(_tensor(projector, delta)))
                            expected = int(name == "ordered_pair" or label == p)
                            _require(_crossing_rank(rows, basis, r, p) == expected,
                                     f"paid factor rank: {r, n, p, label, name, projector}")
                            counts[name + "_paid_ranks"] += 1
                    identity = tuple(1 << i for i in range(len(basis)))
                    for scalar in scalars:
                        rows = _tensor(scalar, identity)
                        _require(_crossing_rank(rows, basis, r, p) == 0, "free scalar charge")
                        counts[name + "_free_ranks"] += 1


def _compose(g, h):
    return tuple(g[x - 1] for x in h)


def _algebra_product(a, b, table):
    result = 0
    while a:
        low_a = a & -a
        i = low_a.bit_length() - 1
        remaining = b
        while remaining:
            low_b = remaining & -remaining
            result ^= 1 << table[i][low_b.bit_length() - 1]
            remaining ^= low_b
        a ^= low_a
    return result


def _formal_product(a, b, table):
    r = len(a)
    rows = [[0] * r for _ in range(r)]
    for i in range(r):
        for j in range(r):
            for k in range(r):
                rows[i][j] ^= _algebra_product(a[i][k], b[k][j], table)
    return tuple(tuple(row) for row in rows)


def _formal_scalar(scalar):
    return tuple(tuple(row >> j & 1 for j in range(len(scalar))) for row in scalar)


def _paid_factor(projector, generator):
    return tuple(tuple(int(i == j) ^ (((1 << generator) ^ 1) if row >> j & 1 else 0)
                       for j in range(len(projector))) for i, row in enumerate(projector))


def _target(targets, index):
    diagonal = [1 << index[w] for w in targets] + [1] * (3 - len(targets))
    return tuple(tuple(diagonal[i] if i == j else 0 for j in range(3)) for i in range(3))


def _replay(factors, table):
    endpoint = _formal_scalar((1, 2, 4))
    for factor in factors:
        endpoint = _formal_product(factor, endpoint, table)
    return endpoint


def _accept_endpoint(actual, expected):
    _require(actual == expected, "full formal endpoint mismatch")


def _check_endpoints(counts):
    group = tuple(permutations(range(1, 5)))
    index = {w: i for i, w in enumerate(group)}
    _require(index[(1, 2, 3, 4)] == 0, "formal identity encoding")
    table = tuple(tuple(index[_compose(g, h)] for h in group) for g in group)
    generators = {}
    for label in range(1, 4):
        w = list(range(1, 5))
        w[label - 1], w[label] = w[label], w[label - 1]
        generators[label] = index[tuple(w)]
    projectors = [tuple(1 << j if i == j else 0 for i in range(3)) for j in range(3)]
    factors = {(role, label): _paid_factor(projectors[role], generator)
               for role in range(3) for label, generator in generators.items()}
    for targets in product(group, repeat=2):
        word = [(role, label) for role, w in enumerate(targets) for label in sorting_word(w, 2)]
        endpoint = _replay((factors[call] for call in word), table)
        _accept_endpoint(endpoint, _target(targets, index))
        _require(sum(2 if label == 2 else 1 for _, label in word) == tariff(targets, 4, 2, 1, 2),
                 "pair construction cost")
        counts["formal_s4_pairs"] += 1
        counts["formal_coordinate_calls"] += len(word)
    _accept_endpoint(_replay((), table), _target((), index))
    counts["empty_formal_endpoints"] += 1

    targets = ((2, 3, 1, 4), (1, 3, 4, 2))
    _require(_compose(*targets) != _compose(*reversed(targets)), "mixed targets must not commute")
    word = [(role, label) for role, w in enumerate(targets) for label in sorting_word(w, 2)]
    expected = _target(targets, index)
    scalars = _general_linear(3)
    _require(len(scalars) == 168, "incomplete GL3 inventory")
    for scalar in scalars:
        inverse = _inverse(scalar)
        _require(_binary_product(scalar, inverse) == _binary_product(inverse, scalar) == (1, 2, 4),
                 "scalar inverse")
        conjugates = [_binary_product(_binary_product(scalar, e), inverse) for e in projectors]
        for e in conjugates:
            _require(_rank(e) == 1 and _binary_product(e, e) == e, "invalid conjugate")
            counts["projector_conjugations"] += 1
        # Chronological S, (S D S^-1)'s, S^-1 yields the original diagonal T.
        mixed = [_formal_scalar(scalar)]
        mixed.extend(_paid_factor(conjugates[role], generators[label]) for role, label in word)
        mixed.append(_formal_scalar(inverse))
        _accept_endpoint(_replay(mixed, table), expected)
        counts["formal_gl3_endpoints"] += 1

    counts["endpoint_rejections"] += _rejects(
        _accept_endpoint, _replay((factors[call] for call in word[1:]), table), expected)
    _require(word != word[::-1], "reversal control needs a non-palindromic word")
    counts["endpoint_rejections"] += _rejects(
        _accept_endpoint, _replay((factors[call] for call in reversed(word)), table), expected)
    leakage = _formal_product(_formal_scalar((5, 2, 4)), expected, table)
    _require(all(leakage[i][j] == expected[i][j] for i in range(3) for j in range(2)),
             "leakage must agree on every clean-spectator input")
    counts["endpoint_rejections"] += _rejects(_accept_endpoint, leakage, expected)

    omega = (1 << len(group)) - 1
    _require(omega != 0, "full group sum must be formally nonzero")
    for basis in (tuple((i,) for i in range(1, 5)),
                  tuple((i, j) for i in range(1, 5) for j in range(1, 5) if i != j)):
        image = [0] * len(basis)
        for w in group:
            for i, row in enumerate(_action_rows(w, basis)):
                image[i] ^= row
        _require(not any(image), "full S4 sum must vanish in this representation")
        counts["kernel_images"] += 1
    corrupted = [list(row) for row in expected]
    corrupted[0][2] ^= omega
    counts["endpoint_rejections"] += _rejects(
        _accept_endpoint, tuple(tuple(row) for row in corrupted), expected)


def _check_inputs(counts):
    for bad in ((), (1,), (1, 1), (0, 2), (1, 3), (1, 2, 3), (1, 2.0), (True, 2), "12", None):
        counts["input_rejections"] += _rejects(tariff, (bad,), 2, 1, 1, 2)
        if bad != (1, 2, 3):
            counts["input_rejections"] += _rejects(sorting_word, bad, 1)
    for p in (0, 2, -1, Fraction(1), True):
        counts["input_rejections"] += _rejects(tariff, ((1, 2),), 2, p, 1, 2)
        counts["input_rejections"] += _rejects(sorting_word, (1, 2), p)
    for n in (0, 1, -2, Fraction(2), True):
        counts["input_rejections"] += _rejects(tariff, (), n, 1, 1, 2)
    for alpha, beta in ((-1, 2), (0, -1), (2, 1), (Fraction(-1, 2), 1),
                        (1.0, 2), (0, 2.0), (True, 2), (0, float("nan")), (0, "2")):
        counts["input_rejections"] += _rejects(tariff, (), 2, 1, alpha, beta)
    counts["input_rejections"] += _rejects(tariff, None, 2, 1, 1, 2)
    for targets, alpha, beta, expected in (
            ((), 1, 2, 0), (((1, 2, 3, 4),) * 2, 2, 5, 0),
            (((4, 3, 2, 1),), 0, 0, 0), (((2, 1, 3, 4),), 0, 1, 0),
            (((2, 3, 1, 4), (1, 3, 4, 2)), Fraction(1, 2), Fraction(3, 2), 4)):
        _require(tariff(targets, 4, 2, alpha, beta) == expected, "positive tariff control")
        counts["positive_controls"] += 1
    distances, settled, edges = _dijkstra(3, 1, 2, 1)
    reversal = (3, 2, 1)
    inadmissible = 2 * _inversions(reversal) - _crossings(reversal, 1)
    _require(distances[reversal] == 4 and inadmissible == 5, "discount counterexample")
    counts["input_rejections"] += _rejects(tariff, (reversal,), 3, 1, 2, 1)
    counts["discount_settled"] += settled
    counts["discount_edges"] += edges


def _check_digest(data, expected):
    _require(hashlib.sha256(data).hexdigest() == expected, "input SHA256 drift")


def _check_sources(counts):
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    records = [entry for entry in json.loads((package / "SOURCES.json").read_text())["files"]
               if entry["usage"] == "input"]
    paths = {"research/symmetric-adjacent-cut-bound/" + name for name in ("PROOF.md", "README.md")}
    _require(len(records) == 2 and {entry["path"] for entry in records} == paths,
             "expected the two pinned predecessor inputs")
    for entry in records:
        data = (root / entry["path"]).read_bytes()
        _check_digest(data, entry["sha256"])
        counts["input_pins"] += 1
        counts["source_drift_rejections"] += _rejects(_check_digest, data + b"\n", entry["sha256"])


def main():
    counts = Counter()
    _check_sources(counts)
    _check_inputs(counts)
    _check_distances(counts)
    _check_ranks(counts)
    _check_endpoints(counts)
    print("PASS_SYMMETRIC_SINGLE_PREMIUM_TARIFF",
          " ".join(f"{key}={value}" for key, value in sorted(counts.items())))


if __name__ == "__main__":
    main()
