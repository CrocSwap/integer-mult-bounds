# SPDX-License-Identifier: Apache-2.0
# Jeremy Diviney, with substantial OpenAI Codex assistance.
"""Complete orthogonal-set rank screening for the pinned P112 root model.

Every nonempty clique is generated directly from the orthogonality graph.
Subsets of maximum eight-root frames do not cover the whole domain.
Passing this necessary test is not a decoder or a physical supplier.
"""
from itertools import combinations


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def geometry(model):
    roots, live = model['lines'], model['live']
    products = [[sum(a*b for a, b in zip(x, y)) for y in roots] for x in roots]
    if any(v % 4 for row in products for v in row):
        raise ValueError('nonintegral root pairing')
    gram = [[v // 4 for v in row] for row in products]
    binary = [sum(int(v % 2 == 0) << j for j, v in enumerate(row)) for row in gram]
    supports = []
    for a in range(len(roots)):
        star = sum(1 << i for i in live if gram[a][i])
        supports.extend([star, star & ~(1 << a)])
    return gram, binary, supports


def all_orthogonal_sets(live, gram):
    """Enumerate each clique once, with increasing vertex labels."""
    later_neighbors = {i: sum(1 << j for j in live if j > i and gram[i][j] == 0) for i in live}
    found = []

    def extend(chosen, candidates):
        while candidates:
            bit = candidates & -candidates
            candidates ^= bit
            i = bit.bit_length() - 1
            new = chosen | bit
            found.append(new)
            extend(new, candidates & later_neighbors[i])

    extend(0, sum(1 << i for i in live))
    return sorted(found, key=lambda q: (q.bit_count(), q))


def frame_subsets(cliques):
    """Historical weaker domain, retained only for the comparison fixture."""
    result = set()
    for q in cliques:
        if q.bit_count() != 8:
            continue
        vertices = tuple(bits(q))
        for size in range(1, 9):
            result.update(sum(1 << i for i in part) for part in combinations(vertices, size))
    return result


def pairing_rank(binary, left, right):
    pivots = {}
    for i in bits(left):
        row = binary[i] & right
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def decode_terms(terms, supports, live_mask):
    result = []
    for a, b, cut_hex in terms:
        if not (0 <= a < len(supports) and 0 <= b < len(supports)):
            raise ValueError('invalid star index')
        cut = int(cut_hex, 16)
        if cut < 0 or cut & ~supports[a]:
            raise ValueError('cut is outside its parent support')
        left, right = supports[a] & ~cut, supports[b]
        if (left | right) & ~live_mask:
            raise ValueError('nonlive support vertex')
        result.append((left, right))
    return result


def rank_violations(factors, cliques):
    """Return exact rank-subadditivity witnesses; invariant under transpose."""
    failures = []
    for q in cliques:
        incident = [k for k, (L, R) in enumerate(factors) if L & q and R & q]
        if len(incident) < q.bit_count():
            failures.append({'roots': list(bits(q)), 'required_rank': q.bit_count(),
                             'available_terms': incident, 'maximum_available_rank': len(incident)})
    return failures


def require_rank_demands(factors, cliques):
    """Reusable necessary-condition guard. Raises with a concrete witness."""
    failures = rank_violations(factors, cliques)
    if failures:
        q = failures[0]
        raise ValueError(f"orthogonal roots {q['roots']} need rank {q['required_rank']}; "
                         f"at most {q['maximum_available_rank']} terms meet both factors")
