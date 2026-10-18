"""Exact controls for the dirty-auxiliary register note.

Two independent checks accompany the C++ engine:

* ``symbolic_terminals`` recomputes, for one word and one relation option,
  the formal product with Laurent exponent vectors and reduces exponents
  modulo the relation lattice.  It shares no pairing tables with the engine.
* ``formal_product`` multiplies actual rational rank-one frames in the
  F2 group algebra of (Q^{3x3}, +).  It is used to realize engine terminals
  physically and to check positive and negative identities.

Only the Python standard library is used.
"""

from fractions import Fraction
from itertools import product
import random

# ---------------------------------------------------------------- scalars


def projectors(n):
    """All binary rank-one idempotents in M_n(F2), ordered like engine.cpp."""
    found = []
    for code in range(1, 1 << (n * n)):
        m = [[(code >> (i * n + j)) & 1 for j in range(n)] for i in range(n)]
        sq = [[sum(m[i][k] & m[k][j] for k in range(n)) & 1 for j in range(n)]
              for i in range(n)]
        if sq != m:
            continue
        rows = {tuple(r) for r in m if any(r)}
        if len(rows) == 1:  # rank one over F2: all nonzero rows equal
            found.append(tuple(tuple(r) for r in m))
    return found


def cube_options(s):
    """R = 0 followed by sign-normalized cube relations of support >= 2."""
    options = [None]
    for code in range(3 ** s):
        r, c = [], code
        for _ in range(s):
            r.append(c % 3 - 1)
            c //= 3
        support = [v for v in r if v]
        if len(support) >= 2 and support[0] > 0:
            options.append(tuple(r))
    return options


def _reduce(vector, r):
    """Canonical representative of an integer vector modulo Z r."""
    if r is None:
        return tuple(vector)
    pivot = next(j for j, v in enumerate(r) if v)
    k = vector[pivot] * r[pivot]  # |r_pivot| = 1, so the pivot entry becomes 0
    return tuple(v - k * rv for v, rv in zip(vector, r))


def symbolic_product(word_matrices):
    """Formal product with entries {Laurent exponent vector: 1} over F2."""
    n, s = len(word_matrices[0]), len(word_matrices)
    zero = tuple([0] * s)
    state = [[({zero: 1} if i == k else {}) for k in range(n)] for i in range(n)]
    for j, N in enumerate(word_matrices):
        e = tuple(1 if q == j else 0 for q in range(s))
        # factor = I + (t_j - 1) N = (I + N) + t_j N over F2
        factor = [[{} for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for k in range(n):
                coeff = {}
                if (1 if i == k else 0) ^ N[i][k]:
                    coeff[zero] = 1
                if N[i][k]:
                    coeff[e] = 1
                factor[i][k] = coeff
        new = [[{} for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for k in range(n):
                acc = {}
                for m in range(n):
                    for ea, ca in state[i][m].items():
                        for eb, cb in factor[m][k].items():
                            key = tuple(x + y for x, y in zip(ea, eb))
                            acc[key] = acc.get(key, 0) ^ (ca & cb)
                new[i][k] = {key: 1 for key, v in acc.items() if v}
        state = new
    return state


def symbolic_terminals(state, r):
    """Return the diagonal class representatives, or None if not terminal."""
    n = len(state)
    reps = []
    for i in range(n):
        for k in range(n):
            acc = {}
            for key in state[i][k]:
                red = _reduce(key, r)
                acc[red] = acc.get(red, []) + [key]
            odd = [keys for keys in acc.values() if len(keys) % 2]
            if i != k and odd:
                return None
            if i == k:
                if len(odd) != 1:
                    return None
                # engine convention: the smallest subset bit mask in the class
                key = odd[0][0]
                members = [key] if r is None else [
                    tuple(x + c * y for x, y in zip(key, r)) for c in (-1, 0, 1)]
                masks = [sum(b << q for q, b in enumerate(m)) for m in members
                         if all(b in (0, 1) for b in m)]
                reps.append(min(masks))
    return reps


# ------------------------------------------------------ physical frames


def rank_q(rows):
    """Exact rank of a rational matrix (list of rows)."""
    m = [list(map(Fraction, row)) for row in rows]
    rank, cols = 0, len(m[0]) if m else 0
    for c in range(cols):
        pivot = next((i for i in range(rank, len(m)) if m[i][c] != 0), None)
        if pivot is None:
            continue
        m[rank], m[pivot] = m[pivot], m[rank]
        for i in range(len(m)):
            if i != rank and m[i][c] != 0:
                f = m[i][c] / m[rank][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[rank])]
        rank += 1
    return rank


def frame_key(matrix):
    return tuple(Fraction(x) for row in matrix for x in row)


def outer(u, v):
    return [[Fraction(a) * Fraction(b) for b in v] for a in u]


def add(*mats):
    return [[sum((m[i][j] for m in mats), Fraction(0)) for j in range(3)] for i in range(3)]


def scale(c, m):
    return [[Fraction(c) * x for x in row] for row in m]


ZERO_KEY = frame_key([[0] * 3] * 3)


def formal_product(word_matrices, frames):
    """Product of D_N([A]) = I + ([A]-1)N in M_n(F2[(Q^{3x3},+)])."""
    n = len(word_matrices[0])
    state = [[({ZERO_KEY} if i == k else set()) for k in range(n)] for i in range(n)]
    for N, A in zip(word_matrices, frames):
        a = frame_key(A)
        factor = [[set() for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for k in range(n):
                entry = set()
                if i == k:
                    entry ^= {ZERO_KEY}
                if N[i][k]:
                    entry ^= {a}
                    entry ^= {ZERO_KEY}
                factor[i][k] = entry
        new = [[set() for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for k in range(n):
                acc = set()
                for m in range(n):
                    for x in state[i][m]:
                        for y in factor[m][k]:
                            acc ^= {tuple(p + q for p, q in zip(x, y))}
                new[i][k] = acc
        state = new
    return state


def diagonal_endpoint(state):
    """Return the diagonal frames if the product is a diagonal monomial matrix."""
    n = len(state)
    out = []
    for i in range(n):
        for k in range(n):
            if i != k and state[i][k]:
                return None
        if len(state[i][i]) != 1:
            return None
        key = next(iter(state[i][i]))
        out.append([list(key[0:3]), list(key[3:6]), list(key[6:9])])
    return out


def random_vector(rng):
    while True:
        v = [Fraction(rng.randint(-5, 5), rng.randint(1, 4)) for _ in range(3)]
        if any(v):
            return v


def frames_with_relation(s, r, rng):
    """Rank-one rational frames whose integral relation lattice is exactly Z r.

    Support frames share one left vector u: A_j = u v_j^T with sum r_j v_j = 0.
    Requires a support of size at most four.  Others are generic rank-one.
    The exact relation lattice is checked by rational rank computations.
    """
    for _ in range(100):
        frames = [outer(random_vector(rng), random_vector(rng)) for _ in range(s)]
        if r is not None:
            support = [j for j in range(s) if r[j]]
            u = random_vector(rng)
            vs = {j: random_vector(rng) for j in support[:-1]}
            last = support[-1]
            vs[last] = [-sum(r[j] * vs[j][c] for j in support[:-1]) / r[last]
                        for c in range(3)]
            if not any(vs[last]):
                continue
            for j in support:
                frames[j] = outer(u, vs[j])
        flat = [[x for row in A for x in row] for A in frames]
        expected_span = s - (0 if r is None else 1)
        if rank_q(flat) != expected_span:
            continue
        if r is not None and any(sum(r[j] * flat[j][c] for j in range(s)) != 0
                                 for c in range(9)):
            continue
        return frames
    raise RuntimeError('could not realize relation')


# ----------------------------------------------------------- controls


def six_call_construction(rng):
    """Two invertible data targets in six calls, with an untouched auxiliary."""
    e = [[1 if i == k else 0 for k in range(3)] for i in range(3)]
    E = [tuple(tuple(1 if (i == k == w) else 0 for k in range(3)) for i in range(3))
         for w in range(3)]
    targets = []
    while len(targets) < 2:
        C = [[Fraction(rng.randint(-4, 4)) for _ in range(3)] for _ in range(3)]
        if rank_q(C) == 3:
            targets.append(C)
    word, frames = [], []
    for w, C in enumerate(targets):
        for i in range(3):
            column = [C[a][i] for a in range(3)]
            word.append(E[w])
            frames.append(outer(column, e[i]))
    return word, frames, targets


def check_formal_controls(seed=20261013):
    rng = random.Random(seed)
    result = {}
    # 1. six-call positive construction with the auxiliary restored
    word, frames, targets = six_call_construction(rng)
    end = diagonal_endpoint(formal_product(word, frames))
    zero = [[Fraction(0)] * 3 for _ in range(3)]
    assert end is not None and end[0] == targets[0] and end[1] == targets[1]
    assert end[2] == zero
    result['six_call_positive'] = True
    # 2. its one-frame mutation is rejected
    bad = [row[:] for row in frames[0]]
    bad[0][0] += 1
    mutated = diagonal_endpoint(formal_product(word, [bad] + frames[1:]))
    assert mutated is None or rank_q(mutated[0]) != 3 or mutated[0] != targets[0]
    result['mutated_frame_changes_endpoint'] = True
    # 3. a J block over all three registers with frames B, -B is the identity
    J = tuple(tuple(1 for _ in range(3)) for _ in range(3))
    B = outer(random_vector(rng), random_vector(rng))
    word2 = word[:3] + [J, J] + word[3:]
    frames2 = frames[:3] + [B, scale(-1, B)] + frames[3:]
    end2 = diagonal_endpoint(formal_product(word2, frames2))
    assert end2 is not None and end2[:2] == targets and end2[2] == zero
    # moving one J factor past a data call breaks diagonality
    word3 = word[:2] + [J] + word[2:3] + [J] + word[3:]
    frames3 = frames[:2] + [B] + frames[2:3] + [scale(-1, B)] + frames[3:]
    assert diagonal_endpoint(formal_product(word3, frames3)) is None
    result['j_block_identity_and_order_control'] = True
    return result


def parse_terminal(line):
    flag, rest = line.split(' ', 1)
    word_part, rel_part, rep_part = rest.split('|')
    word = list(map(int, word_part.split()))
    rel = list(map(int, rel_part.split()))
    reps = list(map(int, rep_part.split()))
    return int(flag), word, (None if rel == [0] else tuple(rel)), reps


def realize_terminals(lines, n, count, seed=7):
    """Realize engine terminals with physical frames and check them exactly.

    For each selected terminal the formal product of random frames having
    exactly the stated relation lattice must be a diagonal monomial matrix,
    the endpoint frames must be the class sums reported by the engine, and
    some data target must have rank at most two.
    """
    rng = random.Random(seed)
    P = projectors(n)
    checked = 0
    for line in lines:
        flag, word, r, reps = parse_terminal(line)
        if r is not None and sum(1 for v in r if v) > 4:
            continue
        mats = [P[p] for p in word]
        frames = frames_with_relation(len(word), r, rng)
        end = diagonal_endpoint(formal_product(mats, frames))
        assert end is not None, line
        for i, rep in enumerate(reps):
            expected = add(*[frames[j] for j in range(len(word)) if rep >> j & 1]) \
                if rep else [[Fraction(0)] * 3 for _ in range(3)]
            assert end[i] == expected, line
        assert flag == 0 and any(rank_q(end[w]) <= 2 for w in range(2)), line
        checked += 1
        if checked == count:
            break
    return checked


def compare_symbolic(lines, n, s, words):
    """Compare engine terminals with the symbolic implementation on words."""
    P = projectors(n)
    options = cube_options(s)
    by_word = {}
    for line in lines:
        flag, word, r, reps = parse_terminal(line)
        by_word.setdefault(tuple(word), set()).add((r, tuple(reps)))
    for word in words:
        state = symbolic_product([P[p] for p in word])
        found = set()
        for r in options:
            reps = symbolic_terminals(state, r)
            if reps is not None:
                found.add((r, tuple(reps)))
        assert found == by_word.get(tuple(word), set()), word
    return len(words)
