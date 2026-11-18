#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the sharp even-difference constructions and their small exception.

Binary primitives and the disjoint core are adapted from PR7703 by
Ali Romman with substantial OpenAI Codex assistance. See CREDITS.md.
"""
from collections import Counter
from hashlib import sha256
import itertools
import json
from pathlib import Path
import sys

def require(value, message):
    if not value:
        raise ValueError(message)


def parity(value):
    return value.bit_count() & 1


def basis(values):
    pivots = {}
    for value in values:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return tuple(pivots.values())


def span(values):
    result = [0]
    for value in basis(values):
        result += [old ^ value for old in result]
    return result


def outer(x, y, width):
    result = 0
    while x:
        bit = x & -x
        result |= y << ((bit.bit_length() - 1) * width)
        x ^= bit
    return result


def off(matrix, width):
    for i in range(width):
        matrix &= ~(1 << (i * width + i))
    return matrix


def patterns(pairs, width):
    return [off(outer(x, y, width), width) for x, y in pairs]


def lifts(pattern, width):
    """An off-diagonal one fixes all factor bits except two."""
    require(pattern != 0, 'zero pattern is outside the pool')
    i, j = divmod((pattern & -pattern).bit_length() - 1, width)
    require(i != j, 'diagonal pattern entry')
    x = sum(((pattern >> (r * width + j)) & 1) << r for r in range(width))
    y = (pattern >> (i * width)) & ((1 << width) - 1)
    result = []
    for xj, yi in itertools.product((0, 1), repeat=2):
        xx, yy = x | (xj << j), y | (yi << i)
        if parity(xx & yy) and off(outer(xx, yy, width), width) == pattern:
            result.append((xx, yy))
    return result


def pool(pattern_basis, width):
    return sorted(pair for pattern in span(pattern_basis) if pattern
                  for pair in lifts(pattern, width))


def orbit_irreducible(pairs):
    """Check all nonzero vectors for small fixtures by direct closure."""
    image_space = span(x for x, _ in pairs)
    n = len(basis(image_space))
    for value in image_space[1:]:
        vectors = basis([value])
        while True:
            expanded = basis((*vectors, *(x for x, y in pairs
                              if any(parity(y & v) for v in vectors))))
            if len(expanded) == len(vectors):
                break
            vectors = expanded
        if len(vectors) != n:
            return False
    return True


def edges(pattern_basis, width):
    return sorted({tuple(sorted(divmod(p.bit_length() - 1, width)))
                   for p in span(pattern_basis) if p.bit_count() == 1})


def matching(edge_list):
    best = ()
    def visit(i, used, chosen):
        nonlocal best
        if len(chosen) + len(edge_list) - i <= len(best):
            return
        if i == len(edge_list):
            best = chosen
            return
        a, b = edge_list[i]
        mask = (1 << a) | (1 << b)
        if not used & mask:
            visit(i + 1, used | mask, chosen + ((a, b),))
        visit(i + 1, used, chosen)
    visit(0, 0, ())
    return best


def core(t, r):
    pairs = []
    offset = 0
    for _ in range(t):
        pairs += [(1 << offset, 3 << offset), (3 << offset, 2 << offset)]
        offset += 2
    for _ in range(r):
        pairs += [(6 << offset, 5 << offset), (5 << offset, 6 << offset),
                  (7 << offset, 7 << offset)]
        offset += 3
    hx = hy = 0
    for x, y in pairs:
        hx ^= x
        hy ^= y
    return pairs, hx, hy, offset


def family(t, r, mode=None):
    require(t + r > 0, 'the old core must be nonempty')
    old, hx, hy, m = core(t, r)
    f, g = 1 << m, 2 << m
    swapped = r % 2 if mode is None else mode
    links = [(hx | f, hy | (g if swapped else f)),
             (hx | g, hy | (f if swapped else g))]
    return old + links, m + 2


def graph_connected(pairs):
    for start in range(len(pairs)):
        seen = {start}
        while True:
            expanded = seen | {j for i in seen for j, (_, y) in enumerate(pairs)
                               if parity(y & pairs[i][0])}
            if expanded == seen:
                break
            seen = expanded
        if len(seen) != len(pairs):
            return False
    return True


def action_rows(pairs):
    return [sum(parity(y & x) << j for j, (x, _) in enumerate(pairs))
            for _, y in pairs]


def raw_pool(hb, width):
    values = set(span(hb)) - {0}
    return sorted((x, y) for x in range(1, 1 << width)
                  for y in range(1, 1 << width)
                  if parity(x & y) and off(outer(x, y, width), width) in values)


def attaining_families():
    receipts = []
    total_patterns = raw_pairs = 0
    for t in range(5):
        for r in range(5):
            if t + r == 0:
                continue
            selected, width = family(t, r)
            require(all(parity(x & y) for x, y in selected), 'link idempotence')
            ps = patterns(selected, width)
            require(0 not in ps, 'coordinate projector entered')
            hb = basis(ps)
            k, n = t + 2 * r + 2, 2 * t + 3 * r + 2
            require(len(hb) == k and len(basis(x for x, _ in selected)) == n,
                    'pattern or image dimension')
            units = edges(hb, width)
            require(len(units) == len(matching(units)) == t, 'matching number')
            require(2 * n == 3 * k + t - 2, 'integral upper bound is not attained')
            complete = pool(hb, width)
            expected = list(selected)
            if (t, r) == (0, 1):
                expected.append((28, 28))
            require(complete == sorted(expected), 'complete pool differs')
            require(len(basis(action_rows(selected))) == n, 'common covector kernel')
            require(graph_connected(selected), 'projector action is not connected')
            require(len(basis(x for x, _ in complete)) == width, 'full ambient image')
            if n <= 9:
                require(orbit_irreducible(selected) and orbit_irreducible(complete),
                        'all-vector orbit check')
            if width <= 7:
                require(raw_pool(hb, width) == complete, 'raw and pattern-lift pools differ')
                raw_pairs += ((1 << width) - 1) ** 2
            digest = sha256(json.dumps(complete, separators=(',', ':')).encode()).hexdigest()
            total_patterns += (1 << k) - 1
            receipts.append({'t': t, 'r': r, 'k': k, 'nu': t, 'image': n,
                             'width': width, 'pool_size': len(complete),
                             'selected': selected, 'extra_members': sorted(set(complete) - set(selected)),
                             'pool_sha256': digest, 'raw_pool_checked': width <= 7,
                             'all_vector_orbits': n <= 9})
    return {'families': receipts, 'nonzero_patterns_lifted': total_patterns,
            'raw_factor_pairs': raw_pairs}


def apply_matrix(matrix, vector, width):
    return sum(parity(((matrix >> (i * width)) & ((1 << width) - 1)) & vector) << i
               for i in range(width))


def small_exception():
    raw = [(x, y) for x in range(1, 4) for y in range(1, 4) if parity(x & y)]
    require(len(raw) == 6, 'two-dimensional rank-one alphabet')
    matrices = [outer(x, y, 2) for x, y in raw]
    total = 0
    for matrix in matrices:
        total ^= matrix
    require(total == 9, 'sum of all six projectors is not I')
    receipts = []
    certificates = []
    for size in (2, 3):
        visits = eligible = 0
        common_lines = Counter()
        for selected in itertools.product(raw, repeat=size):
            visits += 1
            if size == 3:
                summed = 0
                for x, y in selected:
                    summed ^= outer(x, y, 2)
                if any(apply_matrix(summed, apply_matrix(summed, v, 2), 2)
                       != apply_matrix(summed, v, 2) for v in (1, 2)):
                    continue
            eligible += 1
            invariant_line = next((v for v in (1, 2, 3)
                                   if all((x if parity(y & v) else 0) in (0, v)
                                          for x, y in selected)), None)
            require(invariant_line is not None, 'small irreducible counterexample')
            if len(basis(x for x, _ in selected)) == 2:
                require(not orbit_irreducible(selected), 'independent orbit check')
            common_lines[invariant_line] += 1
            certificates.append((selected, invariant_line))
        receipts.append({'size': size, 'visited': visits, 'eligible': eligible,
                         'invariant_line_counts': dict(sorted(common_lines.items()))})
    require([r['eligible'] for r in receipts] == [36, 168], 'restriction census counts')
    witness = [(7, 1), (7, 2)]
    hb = basis(patterns(witness, 3))
    require(len(hb) == 2 and not edges(hb, 3), 'exception witness parameters')
    require(pool(hb, 3) == raw_pool(hb, 3) == witness, 'exception complete pool')
    require(len(basis(x for x, _ in witness)) == 1 and orbit_irreducible(witness),
            'exception does not attain one')
    return {'restriction_censuses': receipts,
            'certificate_sha256': sha256(json.dumps(certificates, separators=(',', ':')).encode()).hexdigest(),
            'maximum': 1, 'witness': witness}


def zero_difference():
    receipts = []
    for k in range(1, 7):
        pairs, _, _, width = core(k, 0)
        hb = basis(patterns(pairs, width))
        require(len(hb) == k and len(matching(edges(hb, width))) == k, 'zero-difference parameters')
        require(pool(hb, width) == sorted(pairs), 'zero-difference complete pool')
        for mask in range(1 << k):
            one_per_pair = [pairs[2 * i + ((mask >> i) & 1)] for i in range(k)]
            require(orbit_irreducible(one_per_pair) == (k == 1), 'disjoint block irreducibility')
        require(not orbit_irreducible(pairs), 'complete disjoint-edge pool is reducible')
        receipts.append({'k': k, 'nu': k, 'complete_pool_size': 2 * k,
                         'one_per_edge_subcollections': 1 << k})
    return receipts


def controls():
    receipts = []
    for t, r in ((1, 0), (0, 1), (0, 2), (1, 1)):
        bad, width = family(t, r, 1 - r % 2)
        require(all(not parity(x & y) for x, y in bad[-2:]), 'wrong parity links were idempotent')
        good, _ = family(t, r)
        old, hx, hy, m = core(t, r)
        fresh_covector = 0 if r % 2 else 3 << m
        broken = old + [(hx | (1 << m), hy | fresh_covector),
                        (hx | (2 << m), hy | fresh_covector)]
        require(all(parity(x & y) for x, y in broken), 'singular control is not idempotent')
        common = (1 if r % 2 else 3) << m
        require(all(not parity(y & common) for _, y in broken), 'singular fresh pairing lost its kernel')
        require(graph_connected(broken), 'singular control lost its connected action')
        require(not orbit_irreducible(broken) if width <= 9 else
                len(basis(action_rows(broken))) < len(broken), 'singular pairing was accepted')
        require(graph_connected(good), 'positive control lost connectivity')
        receipts.append({'t': t, 'r': r, 'wrong_parity_rejects': 2,
                         'singular_pairing_common_kernel': common})
    return receipts


def predecessor_comparison():
    selected = [(5, 6), (6, 5), (7, 7), (12, 11), (29, 18)]
    hb = basis(patterns(selected, 5))
    require(all(parity(x & y) for x, y in selected), 'PR7094 idempotence')
    require(len(hb) == 4 and not edges(hb, 5), 'PR7094 parameters')
    require(pool(hb, 5) == raw_pool(hb, 5) == sorted(selected), 'PR7094 complete pool')
    require(len(basis(x for x, _ in selected)) == 5 and orbit_irreducible(selected),
            'PR7094 joint image or action')
    return {'prior_pr': 7094, 'k': 4, 'nu': 0, 'image': 5, 'pool_size': 5,
            'selected': selected, 'patterns_lifted': 15, 'raw_factor_pairs': 961,
            'scope': 'Prior attained instance; the new family has a different six-member pool.'}


def result():
    return {'attaining': attaining_families(), 'small_exception': small_exception(),
            'zero_difference': zero_difference(), 'controls': controls(),
            'predecessor_comparison': predecessor_comparison(),
            'scope': 'Sharp positive-even k-nu image maximum, plus the zero-difference existence boundary.'}


def main():
    actual = json.loads(json.dumps(result()))
    if sys.argv[1:] == ['--emit']:
        print(json.dumps(actual, indent=2))
        return
    require(not sys.argv[1:], 'unknown arguments')
    require(actual == json.loads(Path(__file__).with_name('RESULT.json').read_text()), 'receipt differs')
    print('PASS_EDGE_MATCHING_EVEN_ATTAINMENT')


if __name__ == '__main__':
    main()
