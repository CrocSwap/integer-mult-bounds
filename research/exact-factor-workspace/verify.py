"""Exact finite controls for fixed-factor spectator basis restriction."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DOMAINS = ((2, 4), (3, 3), (5, 2))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(x, y, q):
    return sum(a * b for a, b in zip(x, y, strict=True)) % q


def subspaces(q, n):
    """Enumerate unique RREF bases and their literal vector-set masks."""
    require(any(q == prime and 0 <= n <= cap for prime, cap in DOMAINS),
            'outside the registered finite domain')
    universe = tuple(itertools.product(range(q), repeat=n))
    indices = {v: i for i, v in enumerate(universe)}
    spaces = []
    for size in range(n + 1):
        for pivots in itertools.combinations(range(n), size):
            free = [(i, j) for i, p in enumerate(pivots)
                    for j in range(p + 1, n) if j not in pivots]
            for values in itertools.product(range(q), repeat=len(free)):
                rows = [[int(j == p) for j in range(n)] for p in pivots]
                for (i, j), value in zip(free, values, strict=True):
                    rows[i][j] = value
                basis = tuple(tuple(row) for row in rows)
                mask = 0
                for coefficients in itertools.product(range(q), repeat=size):
                    v = tuple(sum(c * row[j] for c, row in
                                  zip(coefficients, basis, strict=True)) % q
                              for j in range(n))
                    mask |= 1 << indices[v]
                require(mask.bit_count() == q ** size, 'RREF span size')
                spaces.append((basis, mask))
    require(len({mask for _, mask in spaces}) == len(spaces), 'duplicate space')
    return universe, spaces


def parameters(q, n, ubasis, vbasis, universe):
    """Find pairing rank from its entire evaluation image, without elimination."""
    images = set()
    for coefficients in itertools.product(range(q), repeat=len(ubasis)):
        u = tuple(sum(c * row[j] for c, row in
                      zip(coefficients, ubasis, strict=True)) % q
                  for j in range(n))
        images.add(tuple(dot(v, u, q) for v in vbasis))
    ranks = [t for t in range(n + 1) if q ** t == len(images)]
    require(len(ranks) == 1, 'evaluation image is not a vector space')
    t = ranks[0]
    u, v = len(ubasis), len(vbasis)
    d = u + v - t
    k = n - d
    require(0 <= t <= min(u, v) and 0 <= d <= n, 'dimension bounds')
    ann = sum(1 << i for i, x in enumerate(universe)
              if all(dot(row, x, q) == 0 for row in vbasis))
    return d, q ** ((u - t) * k), q ** (k * (u + v - 2 * t)), ann


def census(q, n):
    universe, spaces = subspaces(q, n)
    # The oracle enumerates every ordered direct-sum decomposition, with no
    # use of the predicted dimension or the counting formulas.
    splits = [(i, j) for i, (a, amask) in enumerate(spaces)
              for j, (b, bmask) in enumerate(spaces)
              if len(a) + len(b) == n and amask & bmask == 1]
    digest = hashlib.sha256()
    records = 0
    for ubasis, umask in spaces:
        for vbasis, _ in spaces:
            d, n_count, pair_count, ann = parameters(q, n, ubasis, vbasis, universe)
            legal = [(i, j) for i, j in splits
                     if umask & ~spaces[i][1] == 0 and spaces[j][1] & ~ann == 0]
            require(bool(legal), 'missing decomposition')
            best = min(len(spaces[i][0]) for i, _ in legal)
            optimal = [(i, j) for i, j in legal if len(spaces[i][0]) == best]
            observed = (best, len({j for _, j in optimal}), len(optimal))
            require(observed == (d, n_count, pair_count), 'formula mismatch')
            digest.update(json.dumps([umask, list(vbasis), observed],
                                     separators=(',', ':')).encode('ascii'))
            records += 1
    return {'q': q, 'n': n, 'spaces': len(spaces), 'pairs': records,
            'direct_sum_decompositions': len(splits), 'sha256': digest.hexdigest()}


def apply(columns, vector):
    require(0 <= vector < 1 << len(columns), 'column input range')
    value = 0
    for i, column in enumerate(columns):
        if vector >> i & 1:
            value ^= column
    return value


def compose(left, right):
    return tuple(apply(left, column) for column in right)


def scalar_lift(columns, output_roles):
    require(all(0 <= c < 1 << output_roles for c in columns), 'role range')
    return tuple(sum(((c >> i) & 1) << (6 * i + g)
                     for i in range(output_roles))
                 for c in columns for g in range(6))


def factor(roles, u, v, label):
    """Faithful left regular S3 action on every role, including all dirt."""
    require(1 <= roles <= 5 and 0 < u < 1 << roles and
            0 < v < 1 << roles and (u & v).bit_count() % 2 == 1,
            'nonzero rank-one idempotent required')
    group = tuple(itertools.permutations(range(3)))
    indices = {p: i for i, p in enumerate(group)}
    require(label in ((1, 0, 2), (0, 2, 1)), 'illegal S3 label')
    result = []
    for j in range(roles):
        for g, p in enumerate(group):
            column = 1 << (6 * j + g)
            if v >> j & 1:
                moved = indices[tuple(label[p[i]] for i in range(3))]
                for i in range(roles):
                    if u >> i & 1:
                        column ^= (1 << (6 * i + g)) ^ (1 << (6 * i + moved))
            result.append(column)
    return tuple(result)


def fixture(n, ubasis, vbasis):
    require(0 <= n <= 4, 'fixture size')
    universe, spaces = subspaces(2, n)
    predicted, _, _, ann = parameters(2, n, ubasis, vbasis, universe)
    umask = 0
    for cs in itertools.product(range(2), repeat=len(ubasis)):
        u = tuple(sum(c * row[j] for c, row in zip(cs, ubasis, strict=True)) % 2
                  for j in range(n))
        umask |= 1 << universe.index(u)
    choices = [(a, b) for a, am in spaces for b, bm in spaces
               if len(a) == predicted and len(a) + len(b) == n and
               am & bm == 1 and umask & ~am == 0 and bm & ~ann == 0]
    require(bool(choices), 'fixture has no optimal split')
    kept, discarded = choices[0]
    basis = (1,) + tuple(sum(x << (j + 1) for j, x in enumerate(row))
                         for row in kept + discarded)
    lookup = {apply(basis, x): x for x in range(1 << (n + 1))}
    require(len(lookup) == 1 << (n + 1), 'basis not invertible')
    inverse = tuple(lookup[1 << i] for i in range(n + 1))
    return check_word(n, ubasis, vbasis, predicted, basis, inverse)


def check_word(n, ubasis, vbasis, d, basis, inverse):
    a, b = (1, 0, 2), (0, 2, 1)
    word = [(1, 1, a)]
    projectors = [(1 | sum(x << (j + 1) for j, x in enumerate(row)), 1)
                  for row in ubasis]
    projectors += [(1, 1 | sum(x << (j + 1) for j, x in enumerate(row)))
                   for row in vbasis]
    for u, v in projectors:
        word.extend((u, v, label) for label in (a, b, a, b, a, b))
    full = tuple(1 << i for i in range(6 * (n + 1)))
    reduced = tuple(1 << i for i in range(6 * (d + 1)))
    lifted = scalar_lift(basis, n + 1)
    ilifted = scalar_lift(inverse, n + 1)
    identity_dirt = tuple(1 << i for i in range(6 * (n + 1)))
    for u, v, label in word:
        gate = factor(n + 1, u, v, label)
        up = apply(inverse, u)
        vp = sum(((v & column).bit_count() % 2) << j
                 for j, column in enumerate(basis))
        require(up < 1 << (d + 1) and vp < 1 << (d + 1), 'discarded support')
        small = factor(d + 1, up, vp, label)
        target = small + identity_dirt[6 * (d + 1):]
        require(compose(ilifted, compose(gate, lifted)) == target,
                'full factor intertwiner')
        full = compose(gate, full)
        reduced = compose(small, reduced)
    require(full == factor(n + 1, 1, 1, a), 'original dirty endpoint')
    require(reduced == factor(d + 1, 1, 1, a), 'reduced dirty endpoint')
    return {'n': n, 'u': len(ubasis), 'v': len(vbasis), 'minimum': d,
            'factors': len(word), 'basis': list(basis),
            'regular_input_columns_per_factor': 6 * (n + 1)}


def report():
    rows = [census(q, n) for q, cap in DOMAINS for n in range(cap + 1)]
    e1, e2 = (1, 0), (0, 1)
    fixtures = [fixture(0, (), ()), fixture(2, (e1,), ()),
                fixture(2, (), (e2,)), fixture(2, (e1,), (e1,)),
                fixture(2, (e1,), (e2,)),
                fixture(4, ((1, 0, 0, 0), (0, 1, 0, 0)),
                        ((0, 0, 1, 0), (0, 0, 0, 1))),
                fixture(3, ((1, 1, 0), (0, 1, 1)),
                        ((1, 0, 1), (1, 1, 1)))]
    return {'schema_version': 1, 'claim_type': 'scoped proof with finite controls',
            'census': rows, 'subspace_pairs': sum(r['pairs'] for r in rows),
            'formal_word_fixtures': fixtures,
            'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in sorted(ROOT.iterdir())
                              if p.is_file() and p.name != 'RESULT.json'}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', type=Path)
    args = parser.parse_args()
    measured = report()
    if args.write_result:
        with args.write_result.open('x', encoding='utf-8') as handle:
            payload = json.dumps(measured, indent=2, sort_keys=True) + '\n'
            require(handle.write(payload) == len(payload), 'short receipt write')
    else:
        expected = json.loads((ROOT / 'RESULT.json').read_text(encoding='utf-8'))
        require(measured == expected, 'receipt or source mismatch')
    print('PASS_EXACT_FACTOR_WORKSPACE', measured['subspace_pairs'],
          'subspace pairs;', len(measured['formal_word_fixtures']), 'formal words')


if __name__ == '__main__':
    main()
