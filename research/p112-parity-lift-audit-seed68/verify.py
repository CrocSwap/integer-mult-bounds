"""Exact audit of the two-sided P112 parity-lift census. Apache-2.0.

Sagar Thakrar, with substantial OpenAI Codex assistance. Standard library only.
Recovers our interrupted seed-32 checker. No external checker is imported.
See README.md for the quantified boundary.
"""

import argparse
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from hashlib import sha1, sha256
from itertools import combinations, product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXPERIMENT_SEED = 32
AUDIT_SEED = 68
PAIR = list(combinations(range(8), 2))[EXPERIMENT_SEED % 28]
# Every other complex amplitude has the support represented by 2.
AMPLITUDES = (0, 1, -1, 2)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def support(values):
    return sum((value != 0) << i for i, value in enumerate(values))


def basis(rows):
    """Canonical high-pivot elimination on nine-bit label vectors."""
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
                continue
            for k in sorted(pivots, reverse=True):
                if row >> k & 1:
                    row ^= pivots[k]
            for k in pivots:
                if pivots[k] >> pivot & 1:
                    pivots[k] ^= row
            pivots[pivot] = row
            break
    return tuple(pivots[k] for k in sorted(pivots, reverse=True))


def direct_basis(rows):
    """Independent low-pivot set elimination on literal pairing-matrix rows."""
    remaining = set(rows) - {0}
    result = []
    while remaining:
        row = min(remaining)
        pivot = row & -row
        result.append(row)
        remaining = {other ^ row if other & pivot else other
                     for other in remaining} - {0}
    return tuple(result)


def load_geometry():
    pins = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    for name, expected in pins['inputs'].items():
        raw = (ROOT / name).read_bytes()
        require(sha256(raw).hexdigest() == expected['sha256'], 'source SHA256: ' + name)
        blob = sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(blob == expected['git_blob'], 'source Git blob: ' + name)
    return json.loads((ROOT / pins['geometry']).read_text(encoding='utf-8'))


def check_geometry(g):
    roots, frame, x = g['roots'], g['frame'], g['X']
    labels, duals = g['labels'], g['duals']
    require(len(roots) == len(x) == len(labels) == len(duals) == 112, 'P112 size')
    require(len(frame) == 8, 'frame size')
    expected = set()
    for i, j in combinations(range(8), 2):
        for a, b in product((-2, 2), repeat=2):
            r = [0] * 8
            r[i], r[j] = a, b
            expected.add(max(tuple(r), tuple(-v for v in r)))
    for r in product((-1, 1), repeat=8):
        if r.count(-1) % 2 == 0:
            expected.add(max(r, tuple(-v for v in r)))
    canonical = lambda r: max(tuple(r), tuple(-v for v in r))
    expected_frame = []
    for i in range(0, 8, 2):
        for sign in (-1, 1):
            r = [0] * 8
            r[i], r[i + 1] = 2, 2 * sign
            expected_frame.append(canonical(r))
    require({canonical(r) for r in frame} == set(expected_frame), 'deleted frame')
    require({canonical(r) for r in roots} == expected - set(expected_frame), 'E8 roots')
    require(len(set(labels)) == len(set(duals)) == 112, 'distinct labels')
    require(all(type(v) is int and 0 <= v < 512 for v in labels + duals), 'nine-bit labels')
    require(all(len(row) == 8 and set(row) <= {-1, 0, 1} for row in x), 'X alphabet')
    for i, r in enumerate(roots):
        require(dot(r, r) == 8, 'root norm')
        require(x[i] == [dot(r, f) // 4 for f in frame], 'frame coordinates')
        for j, s in enumerate(roots):
            require(dot(r, s) % 4 == 0, 'integral Gram')
            gram = dot(r, s) // 4
            require(dot(x[i], x[j]) == 2 * gram, 'XX transpose')
            require(((duals[i] & labels[j]).bit_count() & 1) == (1 + gram) % 2,
                    'label pairing')
    require([[sum(row[i] * row[j] for row in x) for j in range(8)]
             for i in range(8)] == [[56 * (i == j) for j in range(8)]
                                   for i in range(8)], 'X transpose X')


def outside_code(values, x):
    coefficients = [sum(row[j] * v for row, v in zip(x, values)) for j in range(8)]
    return any(dot(row, coefficients) != 56 * value for row, value in zip(x, values))


def corrections(g, q, s, t, h):
    i, j = PAIR
    u = [-t * row[i] * ((q & label).bit_count() & 1)
         for row, label in zip(g['X'], g['labels'])]
    v = [h * row[j] * ((s & label).bit_count() & 1)
         for row, label in zip(g['X'], g['labels'])]
    return u, v


def factors(g, q, s, t, h):
    i, j = PAIR
    u, v = corrections(g, q, s, t, h)
    d, e = [], []
    for row, a, b in zip(g['X'], u, v):
        left, right = row[:], row[:]
        left[i] += a
        left[j] += a
        right[i] += b
        right[j] -= b
        d.append(left + [a, row[i] - row[j]])
        e.append(right + [-row[i] - row[j], -b])
    return d, e


def exact_identity(g, d, t):
    return all(dot(a, b) == dot(g['X'][i], g['X'][j])
               for i, a in enumerate(d) for j, b in enumerate(t))


def run():
    g = load_geometry()
    check_geometry(g)
    labels, duals, x = g['labels'], g['duals'], g['X']
    i, j = PAIR
    xi, xj = [row[i] for row in x], [row[j] for row in x]
    plus = support([a + b for a, b in zip(xi, xj)])
    minus = support([a - b for a, b in zip(xi, xj)])
    # This second engine derives the literal 112x112 binary matrix from roots.
    e_rows = [sum(((1 + dot(r, s) // 4) % 2) << k for k, s in enumerate(g['roots']))
              for r in g['roots']]

    @lru_cache(None)
    def span(mask, dual):
        return basis(v for k, v in enumerate(duals if dual else labels) if mask >> k & 1)

    @lru_cache(None)
    def beta_spaces(a, b):
        return len(basis(sum(((u & v).bit_count() & 1) << k for k, v in enumerate(b))
                         for u in a))

    @lru_cache(None)
    def direct_space(mask):
        return direct_basis(row for k, row in enumerate(e_rows) if mask >> k & 1)

    @lru_cache(None)
    def direct_price(a, col_mask):
        return len(direct_basis(row & col_mask for row in a))

    @lru_cache(None)
    def price(row_mask, col_mask):
        result = beta_spaces(span(row_mask, True), span(col_mask, False))
        independent = direct_price(direct_space(row_mask), col_mask)
        require(result == independent, 'independent COPY price')
        return result

    require(len(span(plus, False)) == len(span(minus, True)) == 9, 'mixed coordinate spans')
    require([price(support([r[k] for r in x]), support([r[k] for r in x]))
             for k in range(8)] == [8] * 8, 'baseline cost')
    rows, cols = [], []
    outside_counts = Counter()
    support_roots = set()
    for amplitude in AMPLITUDES:
        for gate in range(512):
            u, v = corrections(g, gate, gate, amplitude, amplitude)
            a = support([z + w for z, w in zip(xi, u)])
            b = support([z + w for z, w in zip(xj, u)])
            c = support([z + w for z, w in zip(xi, v)])
            d = support([z - w for z, w in zip(xj, v)])
            outside_u, outside_v = outside_code(u, x), outside_code(v, x)
            outside_counts[(amplitude, 'reader', outside_u)] += 1
            outside_counts[(amplitude, 'source', outside_v)] += 1
            rows.append((amplitude, gate, a, b, price(support(u), plus), outside_u))
            cols.append((amplitude, gate, c, d, price(minus, support(v)), outside_v))
            for row, label in zip(x, labels):
                chi = (gate & label).bit_count() & 1
                for constant, slope in [(row[i], -row[i] * chi),
                                        (row[j], -row[i] * chi),
                                        (row[i], row[j] * chi),
                                        (row[j], -row[j] * chi)]:
                    if slope:
                        support_roots.add(Fraction(-constant, slope))
    require(support_roots == {Fraction(-1), Fraction(0), Fraction(1)}, 'amplitude classes')

    histogram, vectors, by_outside = Counter(), Counter(), Counter()
    witnesses = {}
    unit_histogram = Counter()
    for t, q, a, b, extra_u, outside_u in rows:
        for h, s, c, d, extra_v, outside_v in cols:
            ranks = (price(a, c), price(b, d), extra_u, extra_v)
            total = 48 + sum(ranks)
            require(max(ranks) <= 8, 'rank cap')
            require(total >= 64, 'COPY floor')
            histogram[total] += 1
            vectors[ranks] += 1
            by_outside[(int(outside_u) + int(outside_v), total)] += 1
            witnesses.setdefault(ranks, [q, s, t, h])
            if t == h == 1:
                unit_histogram[total] += 1
    require(sum(histogram.values()) == 512 ** 2 * 16, 'full domain coverage')
    require(dict(unit_histogram) == {64: 16, 70: 4064, 76: 258064}, 'unit-amplitude census')

    reader_gates = [q for t, q, *_, outside in rows if t == 1 and outside]
    source_gates = [s for h, s, *_, outside in cols if h == 1 and outside]
    require(reader_gates and source_gates, 'two-sided gates exist')
    witness_q = reader_gates[AUDIT_SEED % len(reader_gates)]
    witness_s = source_gates[-1 - AUDIT_SEED % len(source_gates)]
    identity_cases = list(witnesses.values()) + [
        [witness_q, witness_s, Fraction(3, 2), Fraction(-5, 3)],
        [witness_q, witness_s, 1 + Fraction(1, 2**80), -1 + Fraction(1, 3**60)]]
    for args in identity_cases:
        d, t = factors(g, *args)
        require(exact_identity(g, d, t), 'complete ten-term identity')
        expected = tuple(price(support([r[k] for r in d]), support([r[k] for r in t]))
                         for k in range(10))
        require(sum(expected) >= 64, 'literal factor prices')

    controls = []
    old_u, old_v = corrections(g, EXPERIMENT_SEED, 97, 1, 1)
    require(old_u == [-value for value in xi] and not outside_code(old_u, x)
            and outside_code(old_v, x), 'old witness is only one-sided')
    controls.append('old-witness-is-one-sided')
    d, t = factors(g, witness_q, witness_s, 1, 1)
    require(exact_identity(g, d, t), 'unmutated control identity')
    require(outside_code(corrections(g, witness_q, witness_s, 1, 1)[0], x)
            and outside_code(corrections(g, witness_q, witness_s, 1, 1)[1], x),
            'two-sided witness')
    control_prices = [price(support([r[k] for r in d]), support([r[k] for r in t]))
                      for k in range(10)]
    require(sum(control_prices) == 76 and sum(control_prices[:8]) == 62,
            'omitting both extra COPY prices fabricates a saving')
    controls.append('unpaid-extras-fabricate-62')
    generic_d, generic_t = factors(g, witness_q, witness_s, 2, 2)
    near_d, near_t = factors(g, *identity_cases[-1])
    masks = lambda matrix: tuple(support([r[k] for r in matrix]) for k in range(10))
    require(masks(near_d) == masks(generic_d) and masks(near_t) == masks(generic_t),
            'near-breakpoint amplitudes retain generic supports exactly')
    require(masks(near_d) != masks(d), 'rounding near one loses support')
    controls.append('near-breakpoint-is-not-rounded')
    for index in (8, 9):
        bad = [row[:] for row in t]
        for row in bad:
            row[index] = 0
        require(not exact_identity(g, d, bad), 'omitted compensation must fail')
        controls.append('omit-extra-' + str(index))
    bad = [row[:] for row in t]
    for row in bad:
        row[9] *= -1
    require(not exact_identity(g, d, bad), 'wrong compensation sign must fail')
    controls.append('wrong-compensation-sign')
    bad = [row[:] for row in t]
    _, v = corrections(g, witness_q, witness_s, 1, 1)
    for row, value in zip(bad, v):
        row[j] += 2 * value
    require(not exact_identity(g, d, bad), 'nonorthogonal update directions must fail')
    controls.append('nonorthogonal-directions')
    require(price(support(xi), support(xi)) == 8 != sum(v != 0 for v in xi), 'support count is not rank')
    controls.append('support-cardinality-is-not-rank')
    require(len(direct_basis([3, 5, 6])) == 2 and len(basis([3, 5, 6])) == 2,
            'dependent binary rows')
    controls.append('binary-dependence')
    require(len(basis([1, 2])) == len(basis([1, 4]))
            and beta_spaces(basis([1, 2]), (2,)) == 1
            and beta_spaces(basis([1, 4]), (2,)) == 0,
            'equal dimensions can have different pairing ranks')
    controls.append('dimension-only-cache-rejected')
    mutation = dict(g, labels=labels[:])
    mutation['labels'][0] ^= 2
    try:
        check_geometry(mutation)
    except ValueError:
        controls.append('corrupt-label-rejected')
    else:
        raise ValueError('corrupt label was accepted')
    return {
        'status': 'PASS_P112_PARITY_LIFT_AUDIT_S68',
        'experiment_seed': EXPERIMENT_SEED, 'audit_seed': AUDIT_SEED,
        'coordinate_pair': list(PAIR),
        'negative_control_gates': [witness_q, witness_s],
        'amplitude_representatives': list(AMPLITUDES),
        'generic_complex_class': 'C minus {0, 1, -1}, represented by 2',
        'gate_pairs_per_amplitude_pair': 512 ** 2,
        'parameter_class_records': sum(histogram.values()),
        'copy_cost_histogram': {str(k): v for k, v in sorted(histogram.items())},
        'unit_amplitude_histogram': {str(k): v for k, v in sorted(unit_histogram.items())},
        'outside_factor_cost_histogram': [{'outside_factors': n, 'cost': c, 'count': v}
                                          for (n, c), v in sorted(by_outside.items())],
        'one_side_outside_counts': [{'amplitude': a, 'side': s, 'outside': o, 'count': n}
                                   for (a, s, o), n in sorted(outside_counts.items())],
        'rank_vectors': [{'changed_and_extra_ranks': list(r), 'count': n,
                          'witness_q_s_t_h': witnesses[r]} for r, n in sorted(vectors.items())],
        'maximum_term_rank': 8, 'minimum_copy_cost': min(histogram),
        'minimum_both_outside_copy_cost': min(c for (n, c) in by_outside if n == 2),
        'literal_identity_cases': len(identity_cases),
        'independently_checked_support_pairs': price.cache_info().currsize,
        'controls': controls,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true', help='print the regenerated receipt')
    parser.add_argument('--certificate', type=Path, default=HERE / 'CERTIFICATE.json')
    args = parser.parse_args()
    result = run()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    expected = json.loads(args.certificate.read_text(encoding='utf-8'))
    require(result == expected, 'saved certificate differs from exact replay')
    print(result['status'], 'records=' + str(result['parameter_class_records']),
          'minimum=64', 'rank_cap=8',
          'independent_pairs=' + str(result['independently_checked_support_pairs']))


if __name__ == '__main__':
    main()
