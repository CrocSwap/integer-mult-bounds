#!/usr/bin/env python3
"""Exact checks for the count-vector Pareto frontier of the R16 radical-triple fanout.

Produced by Nick Petalas. Apache-2.0. Python 3.12, standard library only.
Source question: lee-phys's PR6210 (research/r16-radical-triple-fanout), Open next
question 1. No predecessor code is imported or run; its README is a pinned input.

Model (unchanged from PR6210): three arbitrary dirty rows A_0,A_1,A_2, one preserved
source p, gates P_r(beta): A_r += beta p and E_ab(alpha): A_a += alpha A_b with every
nonzero coefficient, any finite word, every dirt column restored, and the final source
column equal to lambda.  A word has the count vector (P_0,P_1,P_2; K_0,K_1,K_2) of
insertions per row and incoming ADDs per row.

What this file establishes (all in R = F2[e,h,z]/(e,h,z)^2, demand (e,h,e+h+z)):
  1. The explicit eight-gate word V_{ij;k} has count vector (1,1,0;2,2,2) up to row
     labels, and is correct in three finite local rings for every demand with
     lambda_i, lambda_j in m and lambda_k != 0, literally on every scalar input in R16.
  2. A bounded exhaustive search over all words of at most nine gates, via an exact
     first-order criterion valid because m^2 = 0, finds no attainable count vector
     outside the up-set of the 13 frontier vectors and attains all 13 itself.
"""
from hashlib import sha256
from itertools import permutations, product
from pathlib import Path
import json

SEARCH_GATES = 9  # exhaustive depth; the longest frontier vector has eight gates


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


# ---------------------------------------------------------------- finite local rings
class Ring:
    """Z/q[x_1..x_v]/(x_i x_j): an element is an int with base-q digits (1, x_1..x_v)."""

    def __init__(self, q, v):
        self.q, self.v, self.n = q, v, q ** (v + 1)
        self.p = min(d for d in range(2, q + 1) if q % d == 0)  # residue field is F_p
        self.name = f'Z/{q}[{v} variables]/(variables)^2'
        digits = [tuple((x // q ** k) % q for k in range(v + 1)) for x in range(self.n)]

        def enc(d):
            return sum(d[k] * q ** k for k in range(v + 1))

        self.add = [[enc(tuple((a[k] + b[k]) % q for k in range(v + 1))) for b in digits]
                    for a in digits]
        self.mul = [[enc(((a[0] * b[0]) % q,) + tuple(
            (a[0] * b[k] + a[k] * b[0]) % q for k in range(1, v + 1)))
            for b in digits] for a in digits]
        self.neg = [row.index(0) for row in self.add]
        self.inv = {x: self.mul[x].index(1) for x in range(self.n) if 1 in self.mul[x]}
        self.maximal = [x for x in range(self.n) if x not in self.inv]
        products = {self.mul[a][b] for a in self.maximal for b in self.maximal}
        self.m2 = self._closure(products)

    def _closure(self, gens):
        group, changed = {0}, True
        while changed:
            changed = False
            for g in gens:
                new = {self.add[x][g] for x in group} - group
                if new:
                    group |= new
                    changed = True
        return group

    def times(self, c, x):
        out = 0
        for _ in range(c):
            out = self.add[out][x]
        return out

    def check_axioms(self):
        n, add, mul = self.n, self.add, self.mul
        for a in range(n):
            require(add[a][0] == a and mul[a][1] == a and mul[a][0] == 0, 'identities')
            for b in range(n):
                require(add[a][b] == add[b][a] and mul[a][b] == mul[b][a], 'commutative')
        for a, b, c in product(range(n), repeat=3):
            require(add[add[a][b]][c] == add[a][add[b][c]], 'additive associativity')
            require(mul[mul[a][b]][c] == mul[a][mul[b][c]], 'multiplicative associativity')
            require(mul[a][add[b][c]] == add[mul[a][b]][mul[a][c]], 'distributivity')
        require(len(self.maximal) * self.p == self.n, 'maximal ideal has index p')

    def independent_triples(self):
        """Ordered triples in m whose classes in m/m^2 are independent over R/m."""
        coeffs = [c for c in product(range(self.p), repeat=3) if any(c)]
        out = []
        for lam in product(self.maximal, repeat=3):
            ok = True
            for c in coeffs:
                s = 0
                for t in range(3):
                    s = self.add[s][self.times(c[t], lam[t])]
                if s in self.m2:
                    ok = False
                    break
            if ok:
                out.append(lam)
        return out


# ---------------------------------------------------------------- words and evaluation
def count_vector(word):
    counts = [0] * 6
    for gate in word:
        require(gate[-1] != 0, 'zero coefficient gate')
        if gate[0] == 'P':
            counts[gate[1]] += 1
        else:
            counts[3 + gate[1]] += 1
    return tuple(counts)


def run_matrix(ring, word):
    """Final [M | s] after the word, from the identity dirt matrix and zero source."""
    rows = [[1 if c == r else 0 for c in range(3)] + [0] for r in range(3)]
    for gate in word:
        if gate[0] == 'E':
            _, a, b, alpha = gate
            rows[a] = [ring.add[rows[a][c]][ring.mul[alpha][rows[b][c]]] for c in range(4)]
        else:
            _, r, beta = gate
            rows[r][3] = ring.add[rows[r][3]][beta]
    return rows


def target_matrix(lam):
    return [[1 if c == r else 0 for c in range(3)] + [lam[r]] for r in range(3)]


def inverse_word(ring, word):
    return [(g[0], g[1], g[2], ring.neg[g[3]]) if g[0] == 'E' else ('P', g[1], ring.neg[g[2]])
            for g in reversed(word)]


def run_inputs(ring, word, dirt, source):
    rows = list(dirt)
    for gate in word:
        if gate[0] == 'E':
            _, a, b, alpha = gate
            rows[a] = ring.add[rows[a]][ring.mul[alpha][rows[b]]]
        else:
            _, r, beta = gate
            rows[r] = ring.add[rows[r]][ring.mul[beta][source]]
    return rows


def v_word(ring, lam, i, j, k):
    """Eight gates; insertions in rows i and j only; incoming ADDs 2 into each row."""
    one = 1
    beta = ring.add[one][lam[i]]
    gamma = ring.neg[ring.mul[lam[k]][ring.inv[beta]]]
    a1 = ring.add[lam[j]][ring.neg[one]]
    return [('E', k, i, gamma), ('P', i, beta), ('E', k, i, ring.neg[gamma]),
            ('E', j, i, a1), ('E', i, j, one), ('P', j, one),
            ('E', i, j, ring.neg[one]), ('E', j, i, ring.neg[a1])]


def v_vector(i, j, k):
    return tuple(1 if r in (i, j) else 0 for r in range(3)) + (2, 2, 2)


# ---------------------------------------------------------------- frontier vectors
def frontier_vectors():
    out = {'D': (1, 1, 1, 0, 0, 0)}
    for i in range(3):
        out[f'T{i}'] = tuple(2 if r == i else 0 for r in range(3)) + tuple(
            0 if r == i else 2 for r in range(3))
    for i, j in permutations(range(3), 2):
        k = 3 - i - j
        out[f'R{i}{j};{k}'] = tuple({i: 2, j: 1, k: 0}[r] for r in range(3)) + tuple(
            2 if r == k else 0 for r in range(3))
    for k in range(3):
        i, j = [r for r in range(3) if r != k]
        out[f'V{k}'] = v_vector(i, j, k)
    return out


def dominates(a, b):
    return all(x >= y for x, y in zip(a, b))


# ---------------------------------------------------------------- first-order search
# Over R = F2 + m with m^2 = 0 every gate coefficient is a0 + x, a0 in F2, x in m = F2^3.
# Write the augmented state Q = [M | s] as Q0 + Q1 (residues and first order).  A gate with
# residue a0 acts on Q0 and Q1 by the same row operation E0 (identity when a0 = 0); its
# m-part x adds x * (e_a (x) row_b(Q0)) to Q1, and an insertion adds x * (e_r (x) unit
# source column).  Coordinates of m are independent, so a skeleton is solvable iff the span
# S of the propagated generators contains every pure-source vector [0 | s].
# Packing: bits 3..11 hold M (row r at bits 3r..3r+2), bits 0..2 hold s.
IDENTITY_STATE = ((1 | 2 << 3 | 4 << 6) << 3)


def apply_row_op(v, a, b):
    mat, src = v >> 3, v & 7
    mat ^= ((mat >> 3 * b) & 7) << 3 * a
    src ^= ((src >> b) & 1) << a
    return (mat << 3) | src


def add_generator(basis, v):
    """Reduced echelon insert; leading bits order M first so |v|<8 means pure source."""
    for b in basis:
        if v ^ b < v:
            v ^= b
    if v == 0:
        return basis
    lead = v.bit_length() - 1
    new = [b ^ v if (b >> lead) & 1 else b for b in basis]
    new.append(v)
    new.sort(reverse=True)
    return tuple(new)


def canonical(vectors):
    basis = ()
    for v in vectors:
        basis = add_generator(basis, v)
    return basis


def pure_source_dimension(basis):
    return sum(1 for b in basis if b < 8)


def order_zero_distances():
    dist = {IDENTITY_STATE: 0}
    queue = [IDENTITY_STATE]
    moves = [(a, b) for a in range(3) for b in range(3) if a != b]
    for state in queue:
        nxt = [apply_row_op(state, a, b) for a, b in moves] + [state ^ (1 << r) for r in range(3)]
        for t in nxt:
            if t not in dist:
                dist[t] = dist[state] + 1
                queue.append(t)
    return dist


GATES = ([('A', a, b, unit) for a in range(3) for b in range(3) if a != b for unit in (1, 0)]
         + [('I', r, None, unit) for r in range(3) for unit in (1, 0)])


def step(state, basis, gate):
    kind, a, b, unit = gate
    if kind == 'A':
        gen = (((state >> 3 >> 3 * b) & 7) << 3 * a) << 3 | (((state >> b) & 1) << a)
        if unit:
            state = apply_row_op(state, a, b)
            basis = canonical([apply_row_op(v, a, b) for v in basis])
    else:
        gen = 1 << a
        if unit:
            state ^= 1 << a
    return state, add_generator(basis, gen)


def bounded_search(limit, frontier, need_dim=3):
    """Explore every skeleton of <= limit gates whose counts avoid the up-set of the
    frontier; report solvable ones (counterexamples) and frontier vectors attained."""
    dist = order_zero_distances()
    fvals = list(frontier.values())
    status = {}

    def classify(counts):
        res = status.get(counts)
        if res is None:
            res = 0
            for name, f in frontier.items():
                if dominates(counts, f):
                    res = (name if counts == f else 1)
                    if counts == f:
                        break
            status[counts] = res
        return res

    attained, counterexamples, seen, stats = {}, [], set(), {'nodes': 0}

    def solved(state, basis):
        return state == IDENTITY_STATE and pure_source_dimension(basis) >= need_dim

    def rec(seq, state, basis, counts):
        for gate in GATES:
            kind, a, b, unit = gate
            c = list(counts)
            c[a if kind == 'I' else 3 + a] += 1
            c = tuple(c)
            cls = classify(c)
            if cls == 1:
                continue
            ns, nb = step(state, basis, gate)
            stats['nodes'] += 1
            rem = limit - sum(c)
            if isinstance(cls, str):
                if solved(ns, nb) and cls not in attained:
                    attained[cls] = seq + [gate]
                continue
            if solved(ns, nb):
                counterexamples.append((c, seq + [gate]))
                continue
            if dist.get(ns, 99) > rem or need_dim - pure_source_dimension(nb) > rem:
                continue
            key = (ns, nb, c)
            if key in seen:
                continue
            seen.add(key)
            rec(seq + [gate], ns, nb, c)

    rec([], IDENTITY_STATE, (), (0,) * 6)
    return attained, counterexamples, stats


# ---------------------------------------------------------------- skeleton -> literal word
def build_word(ring, seq, lam):
    """Solve the first-order systems and return the literal R16 word for a skeleton."""
    state, basis, gens, ops = IDENTITY_STATE, (), [], []
    for gate in seq:
        kind, a, b, unit = gate
        if kind == 'A':
            gens.append((((state >> 3 >> 3 * b) & 7) << 3 * a) << 3 | (((state >> b) & 1) << a))
            ops.append((a, b) if unit else None)
            if unit:
                state = apply_row_op(state, a, b)
        else:
            gens.append(1 << a)
            ops.append(None)
            if unit:
                state ^= 1 << a
    require(state == IDENTITY_STATE, 'skeleton does not close at order zero')
    propagated = []
    for t, g in enumerate(gens):
        for op in ops[t + 1:]:
            if op is not None:
                g = apply_row_op(g, *op)
        propagated.append(g)
    coords = []
    for c in range(3):
        target = sum(((lam[r] >> (c + 1)) & 1) << r for r in range(3))
        sol = None
        for mask in range(1 << len(seq)):
            acc = 0
            for t in range(len(seq)):
                if (mask >> t) & 1:
                    acc ^= propagated[t]
            if acc == target:
                sol = mask
                break
        require(sol is not None, 'first-order system unsolvable')
        coords.append(sol)
    word = []
    for t, (kind, a, b, unit) in enumerate(seq):
        coef = unit | sum(((coords[c] >> t) & 1) << (c + 1) for c in range(3))
        word.append(('E', a, b, coef) if kind == 'A' else ('P', a, coef))
    return word


def literal_scalar_check(ring, word, lam):
    """Every scalar dirty/source input, forward and inverse (R16 has 16^4 of them)."""
    inv = inverse_word(ring, word)
    for x0, x1, x2, p in product(range(ring.n), repeat=4):
        want = [ring.add[x][ring.mul[l][p]] for x, l in zip((x0, x1, x2), lam)]
        require(run_inputs(ring, word, (x0, x1, x2), p) == want, 'forward literal mismatch')
        require(run_inputs(ring, inv, want, p) == [x0, x1, x2], 'inverse literal mismatch')
    return ring.n ** 4


# ---------------------------------------------------------------- main
CITED = 'research/r16-radical-triple-fanout/README.md'
CITED_SENTENCES = (
    'If S contains all three rows, the bill is at least D',
    'If row i receives at least two insertions, the bill is at least `R_ij;k`',
    'exactly one insertion in each of i and j',
    'hence `K_i>=2` by the return lemma',
    'cannot be cheapest at any strictly positive price vector',
)


def check_cited_premise():
    """Bind the cited written lower bound: exact pinned bytes and its four case sentences."""
    here = Path(__file__).resolve().parent
    pins = {row['path']: row['sha256'] for row in json.loads((here / 'SOURCES.json').read_text())['files']}
    data = (here.parents[1] / CITED).read_bytes()
    require(sha256(data).hexdigest() == pins[CITED], 'cited README bytes differ from the pin')
    text = ' '.join(data.decode().split())
    for sentence in CITED_SENTENCES:
        require(sentence in text, 'cited case analysis missing: ' + sentence)


def main():
    check_cited_premise()
    r16 = Ring(2, 3)
    f3 = Ring(3, 3)
    z4 = Ring(4, 2)
    for ring in (r16, f3, z4):
        ring.check_axioms()
    expected_triples = {r16.name: 168, f3.name: 11232, z4.name: 10752}

    # 1. the explicit word in three rings
    total_words = 0
    for ring in (r16, f3, z4):
        triples = ring.independent_triples()
        require(len(triples) == expected_triples[ring.name], 'triple count ' + ring.name)
        for lam in triples:
            for i, j in permutations(range(3), 2):
                k = 3 - i - j
                word = v_word(ring, lam, i, j, k)
                require(count_vector(word) == v_vector(i, j, k), 'count vector')
                require(run_matrix(ring, word) == target_matrix(lam), 'word identity')
                total_words += 1
    e, h, z = 2, 4, 8
    lam16 = (e, h, e ^ h ^ z)
    literal = 0
    for i, j in permutations(range(3), 2):
        k = 3 - i - j
        literal += literal_scalar_check(r16, v_word(r16, lam16, i, j, k), lam16)
    # a relaxed demand shows the construction needs no independence: any lam_i, lam_j in m,
    # lam_k != 0 works
    for ring in (r16, f3, z4):
        for li, lj, lk in product(ring.maximal, ring.maximal, range(1, ring.n)):
            word = v_word(ring, (li, lj, lk), 0, 1, 2)
            require(run_matrix(ring, word) == target_matrix((li, lj, lk)), 'relaxed identity')
            total_words += 1

    # 2. controls on the explicit word
    base = v_word(r16, lam16, 0, 1, 2)
    mutants = {
        'drop last gate': base[:-1],
        'wrong echo coefficient': [('E', 2, 0, base[0][3] ^ e)] + base[1:],
        'swap moves': base[:3] + [base[4], base[3]] + base[5:],
        'nonunit second insertion': base[:5] + [('P', 1, lam16[1])] + base[6:],
        'drop first echo gate': base[1:],
    }
    for name, word in mutants.items():
        require(run_matrix(r16, word) != target_matrix(lam16), 'control accepted: ' + name)

    # 3. bounded exhaustive search
    frontier = frontier_vectors()
    names = sorted(frontier)
    vals = [frontier[n] for n in names]
    require(len(set(vals)) == 13, 'frontier size')
    for a, b in permutations(vals, 2):
        require(not dominates(a, b), 'frontier is not an antichain')
    attained, counter, stats = bounded_search(SEARCH_GATES, frontier)
    require(not counter, 'counterexample count vector found: %r' % (counter[:2],))
    reachable = [n for n in names if sum(frontier[n]) <= SEARCH_GATES]
    require(sorted(attained) == sorted(reachable), 'attained %r' % (sorted(attained),))
    built = 0
    for name, seq in attained.items():
        word = build_word(r16, seq, lam16)
        require(count_vector(word) == frontier[name], 'built counts ' + name)
        require(run_matrix(r16, word) == target_matrix(lam16), 'built word ' + name)
        built += 1

    # 4. sensitivity controls: a rank-two demand and a truncated frontier must be flagged
    cheap, ce2, _ = bounded_search(6, frontier, need_dim=2)
    require(ce2, 'rank-two control found no cheaper count vector')
    smaller = {n: v for n, v in frontier.items() if n != 'T0'}
    _, ce3, _ = bounded_search(6, smaller)
    require(any(c == frontier['T0'] for c, _ in ce3), 'removing T0 was not flagged')

    digest = sha256(repr((sorted(attained), stats['nodes'], total_words, literal)).encode())
    print('words_checked', total_words, 'literal_inputs', literal)
    print('search_gates', SEARCH_GATES, 'nodes', stats['nodes'], 'attained', sorted(attained))
    print('rebuilt_literal_words', built, 'rank_two_control_types', len(ce2))
    here = Path(__file__).resolve().parent
    bound = sha256(b''.join((here / name).read_bytes() for name in ('verify.py', 'VERIFY.json')))
    print('RECEIPT package_files', bound.hexdigest()[:16], 'result', digest.hexdigest()[:16])
    print('PASS_R16_RADICAL_PARETO_FRONTIER frontier=13 search_gates=%d' % SEARCH_GATES)


if __name__ == '__main__':
    main()
