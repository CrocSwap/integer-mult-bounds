"""Constructive radius-3/2 rounder for the PR4933 mode map (PROOF.md, Theorem D).

Exact rational arithmetic, standard library only. Given y in Q^112 whose mode
vector M^T y lies in L = M^T Z^112, returns an integer z with M^T z = M^T y and
max_i |z_i - y_i| <= 3/2. Every step of the proof is executed literally, so a
failure of any lemma raises instead of being silently repaired.
Prepared for apoursh with substantial Anthropic Claude assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import itertools

HALF = Q(1, 2)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def support(r):
    return tuple(j for j in range(8) if r[j])


def blocks_of(rows):
    """support -> (row indices, pinned coordinate, pin sign, free coordinates)."""
    out = {}
    for i, r in enumerate(rows):
        out.setdefault(support(r), []).append(i)
    info = {}
    for s, ix in out.items():
        fixed = [j for j in s if len({rows[i][j] for i in ix}) == 1]
        need(len(ix) == 8 and len(fixed) == 1, 'block has eight rows and one pinned coordinate')
        p, free = fixed[0], [j for j in s if j != fixed[0]]
        need({tuple(rows[i][j] for j in free) for i in ix} == set(itertools.product((-1, 1), repeat=3)),
             'block rows are every sign pattern on the free coordinates')
        info[s] = (ix, p, rows[ix[0]][p], free)
    need(len(info) == 14, 'fourteen blocks')
    return info


def direction(rows, block, a, b):
    """j with m_a - m_b = +-2 e_j (rows differ at one free coordinate) or m_a + m_b = 2 sigma e_p (antipodal)."""
    ix, p, sign, free = block
    diff = [k for k in free if rows[a][k] != rows[b][k]]
    return diff[0] if len(diff) == 1 else p if len(diff) == 3 else None


def straight(rows, block, j):
    """The four disjoint pairs of the block in direction j."""
    ix = block[0]
    pairs, used = [], set()
    for a in ix:
        if a not in used:
            b = next(b for b in ix if b != a and b not in used and direction(rows, block, a, b) == j)
            pairs.append((a, b, j))
            used.update((a, b))
    need(len(pairs) == 4, 'four pairs in one direction')
    return pairs


def rainbow(rows, block):
    """A perfect matching of the block into four pairs with four distinct directions."""
    ix, p, sign, free = block
    parity = {i: sum(rows[i][k] < 0 for k in free) % 2 for i in ix}
    even = [i for i in ix if parity[i] == 0]
    odd = [i for i in ix if parity[i] == 1]
    for perm in itertools.permutations(odd):
        dirs = [direction(rows, block, a, b) for a, b in zip(even, perm)]
        if None not in dirs and len(set(dirs)) == 4:
            return [(a, b, d) for a, b, d in zip(even, perm, dirs)]
    raise ValueError('no rainbow matching')


def kernel_vector(vectors):
    """A nonzero rational dependency among vectors in Q^8, or None if they are independent."""
    n = len(vectors)
    a = [[Q(vectors[k][j]) for k in range(n)] for j in range(8)]
    pivots, r = [], 0
    for c in range(n):
        piv = next((i for i in range(r, 8) if a[i][c]), None)
        if piv is None:
            continue
        a[r], a[piv] = a[piv], a[r]
        a[r] = [x / a[r][c] for x in a[r]]
        for i in range(8):
            if i != r and a[i][c]:
                f = a[i][c]
                a[i] = [x - f * y for x, y in zip(a[i], a[r])]
        pivots.append(c)
        r += 1
        if r == 8:
            break
    freec = next((c for c in range(n) if c not in pivots), None)
    if freec is None:
        return None
    d = [Q(0)] * n
    d[freec] = Q(1)
    for row, c in enumerate(pivots):
        d[c] = -a[row][freec]
    return d


def vertex(rows, w):
    """Move w inside {w' in [0,1]^112 : M^T w' = M^T w} until its fractional rows are independent."""
    w = list(w)
    while True:
        frac = [i for i in range(len(w)) if w[i].denominator != 1]
        sample = frac[:9]
        d = kernel_vector([rows[i] for i in sample])
        if d is None:
            return w, frac
        step = min([(1 - w[i]) / di for i, di in zip(sample, d) if di > 0] +
                   [-w[i] / di for i, di in zip(sample, d) if di < 0])
        for i, di in zip(sample, d):
            w[i] += step * di


def word(coords):
    return tuple(int(j in coords) for j in range(8))


def plan(rows, blocks, h):
    """Matchings for every block: rainbow by default (seven pairs, an odd count, per coordinate), and
    straight on the toggled blocks, which makes the counts even exactly where the parity word h is 0."""
    even = tuple(1 - x for x in h)
    supp = {word(s): s for s in blocks}
    if even == (0,) * 8:
        toggled = []
    elif even in supp:
        toggled = [supp[even]]
    else:
        need(even == (1,) * 8, 'parity word lies in H8')
        s = min(blocks)
        toggled = [s, supp[tuple(1 - x for x in word(s))]]
    pairs = []
    for s, block in blocks.items():
        pairs += straight(rows, block, s[0]) if s in toggled else rainbow(rows, block)
    return pairs, toggled


def round_three_halves(rows, y, blocks=None):
    blocks = blocks or blocks_of(rows)
    n = len(rows)
    t = [sum(rows[i][j] * y[i] for i in range(n)) for j in range(8)]
    c = [(v + HALF).numerator // (v + HALF).denominator for v in y]       # nearest integers
    w = [y[i] - c[i] + HALF for i in range(n)]                            # in [0, 1]
    need(all(0 <= x <= 1 for x in w), 'centred box')
    wstar, F = vertex(rows, w)
    need(len(F) <= 8 and kernel_vector([rows[i] for i in F]) is None, 'independent fractional rows')
    snap = [Q(1) if wstar[i] >= HALF else Q(0) for i in range(n)]         # every row now at +-1/2
    u = [sum((rows[i][j] * (wstar[i] - snap[i]) for i in F), Q(0)) for j in range(8)]
    need(all(v.denominator == 1 and abs(v) <= 4 for v in u), 'balancing target u in Z^8 with |u_j| <= 4')
    u = [int(v) for v in u]
    pairs, toggled = plan(rows, blocks, tuple(v % 2 for v in u))
    need(sorted(x for a, b, _ in pairs for x in (a, b)) == list(range(n)), 'pairs partition the rows')
    kappa = [0] * n
    for j in range(8):
        mine = [pr for pr in pairs if pr[2] == j]
        need(len(mine) % 2 == u[j] % 2 and abs(u[j]) <= len(mine), 'pair count covers u_j')
        plus = (len(mine) + u[j]) // 2
        for k, (a, b, _) in enumerate(mine):
            eps = 1 if k < plus else -1
            block = blocks[support(rows[a])]
            if j == block[1] and rows[a][j] == rows[b][j]:    # antipodal: m_a + m_b = 2 sigma e_p
                kappa[a] = kappa[b] = eps * block[2]
            else:                                              # m_a - m_b = 2 (m_a)_j e_j
                kappa[a], kappa[b] = eps * rows[a][j], -eps * rows[a][j]
    need([sum(kappa[i] * rows[i][j] for i in range(n)) for j in range(8)] == [2 * v for v in u],
         'signed row sum equals 2u')
    z = [c[i] + int(snap[i]) + (kappa[i] - 1) // 2 for i in range(n)]
    need([sum(rows[i][j] * z[i] for i in range(n)) for j in range(8)] == t, 'modes preserved')
    err = max(abs(z[i] - y[i]) for i in range(n))
    need(err <= Q(3, 2), 'radius at most 3/2')
    return z, err, toggled
