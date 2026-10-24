#!/usr/bin/env python3
"""Exact bounded checks for README.md; no new kappa.

lee-phys with substantial OpenAI Codex assistance; Apache-2.0.
Retains #5045/#5139/#5163/#5208 and the credited fanout lineage.
"""
from dataclasses import dataclass
from fractions import Fraction
from heapq import heappop, heappush
from itertools import permutations, product
from math import lcm
import json


def require(test, message):
    if not test:
        raise RuntimeError(message)


@dataclass(frozen=True)
class Ring:
    name: str
    n: int
    one: int
    add: tuple
    mul: tuple

    def neg(self, x):
        return next(y for y in range(self.n) if self.add[x][y] == 0)

    def principal(self, x):
        return frozenset(self.mul[a][x] for a in range(self.n))

    def ideal(self, xs):
        out = frozenset([0])
        for x in xs:
            out = frozenset(self.add[a][b] for a in out for b in self.principal(x))
        return out


def ring_from_functions(name, n, one, add, mul):
    return Ring(name, n, one, tuple(tuple(add(x, y) for y in range(n)) for x in range(n)),
                tuple(tuple(mul(x, y) for y in range(n)) for x in range(n)))


def square_zero(p):
    def digits(x):
        return (x % p, (x//p) % p, x//(p*p))
    def add(x, y):
        a, b = digits(x), digits(y)
        return sum(((a[k]+b[k]) % p)*p**k for k in range(3))
    def mul(x, y):
        a, b = digits(x), digits(y)
        return a[0]*b[0] % p + p*((a[0]*b[1]+a[1]*b[0]) % p) + p*p*((a[0]*b[2]+a[2]*b[0]) % p)
    return ring_from_functions(f'F{p}[e,h]/(e,h)^2', p**3, 1, add, mul)


def dual_z4():
    return ring_from_functions('Z/4[t]/t^2', 16, 1,
                              lambda x, y: (x % 4+y % 4) % 4+4*((x//4+y//4) % 4),
                              lambda x, y: (x % 4)*(y % 4) % 4+4*(((x % 4)*(y//4)+(x//4)*(y % 4)) % 4))


def product_ring(eight):
    return ring_from_functions('F2[e,h]/(e,h)^2 x F2', 16, 9,
                              lambda x, y: eight.add[x % 8][y % 8]+8*((x//8+y//8) % 2),
                              lambda x, y: eight.mul[x % 8][y % 8]+8*((x//8)*(y//8)))


def check_ring(r):
    es = range(r.n)
    for a, b in product(es, repeat=2):
        require(r.add[a][b] in es and r.mul[a][b] in es, 'ring closure')
        require(r.add[a][b] == r.add[b][a] and r.mul[a][b] == r.mul[b][a], 'commutative ring')
    for a in es:
        require(r.add[a][0] == a and r.mul[a][r.one] == a and r.mul[a][0] == 0, 'ring identities')
        require(r.add[a][r.neg(a)] == 0, 'additive inverse')
    for a, b, c in product(es, repeat=3):
        require(r.add[r.add[a][b]][c] == r.add[a][r.add[b][c]], 'addition associativity')
        require(r.mul[r.mul[a][b]][c] == r.mul[a][r.mul[b][c]], 'multiplication associativity')
        require(r.mul[a][r.add[b][c]] == r.add[r.mul[a][b]][r.mul[a][c]], 'distributivity')


def validate_demand(r, d):
    if len(d) != 3 or any(not isinstance(x, int) or x not in range(r.n) for x in d):
        raise ValueError('three ring elements required')
    if r.add[r.add[d[0]][d[1]]][d[2]] != 0:
        raise ValueError('the demand must sum to zero')
    if r.ideal(d) in {r.principal(x) for x in range(r.n)}:
        raise ValueError('the generated ideal must be nonprincipal')


def formula(mu, c):
    if len(mu) != 3 or len(c) != 3 or min((*mu, *c)) <= 0:
        raise ValueError('six strictly positive prices required')
    out = [sum(mu)]
    for k in range(3):
        i, j = [r for r in range(3) if r != k]
        out.append(2*mu[k]+2*c[i]+2*c[j])
        out.append(mu[i]+mu[j]+2*c[k]+min(mu[i], mu[j], 2*c[i], 2*c[j], 2*c[k]))
    return min(out)


def patterns():
    out = [('D', 0, 1, 2, (1, 1, 1, 0, 0, 0))]
    for i in range(3):
        j, k = [r for r in range(3) if r != i]
        v = [0]*6
        v[i], v[3+j], v[3+k] = 2, 2, 2
        out.append(('T', i, j, k, tuple(v)))
    for mode in ('R', 'M'):
        for i, j, k in permutations(range(3)):
            v = [0]*6
            v[i], v[j], v[3+k] = 1, 1, 2
            if mode == 'R':
                v[i] = 2
            else:
                v[3+i] = 2
            out.append((mode, i, j, k, tuple(v)))
    for k in range(3):
        i, j = [r for r in range(3) if r != k]
        v = [0]*6
        v[i], v[j], v[3+k] = 1, 1, 4
        out.append(('Q', i, j, k, tuple(v)))
    return out


def construct(r, d, pattern):
    mode, i, j, k, _ = pattern
    u, v = r.one, r.neg(r.one)
    if mode == 'D':
        return [(t, 3, d[t]) for t in range(3)]
    if mode == 'T':
        return [(j, i, u), (i, 3, r.neg(d[j])), (j, i, v),
                (k, i, u), (i, 3, r.neg(d[k])), (k, i, v)]
    if mode == 'R':
        return [(k, i, u), (i, 3, r.neg(d[k])), (k, i, v),
                (i, 3, r.neg(d[j])), (j, 3, d[j])]
    if mode == 'M':
        return [(i, j, u), (k, i, u), (i, 3, r.neg(d[k])), (j, 3, d[j]),
                (k, i, v), (i, j, v)]
    if mode == 'Q':
        return [(k, i, u), (k, j, u), (i, 3, d[i]), (j, 3, d[j]), (k, j, v), (k, i, v)]
    raise ValueError('unknown word family')


def inverse(r, word):
    return [(i, j, r.neg(a)) for i, j, a in reversed(word)]


def execute(r, word, entry):
    out = list(entry)
    for i, j, a in word:
        out[i] = r.add[out[i]][r.mul[a][out[j]]]
    return tuple(out)


def target(r, d, entry):
    return tuple(r.add[entry[i]][r.mul[d[i]][entry[3]]] for i in range(3))+(entry[3],)


def endpoint(r, d, word):
    for k in range(4):
        entry = tuple(r.one if j == k else 0 for j in range(4))
        want = target(r, d, entry)
        if execute(r, word, entry) != want or execute(r, inverse(r, word), want) != entry:
            return False
    return True


def counts(word):
    return tuple(sum(i == k and j == 3 for i, j, _ in word) for k in range(3))+tuple(
        sum(i == k and j != 3 for i, j, _ in word) for k in range(3))


def bill(word, prices):
    return sum(prices[i if j == 3 else 3+i] for i, j, _ in word)


# Independent eight-element implementation: 12-bit rows, 36-bit affine states.
# No constructor, price formula, ideal routine or ring table is called here.
def packed_tables():
    return [None]+[tuple(sum((((a & 1)*((x >> (3*k)) & 7)) ^
                             (((x >> (3*k)) & 1)*(a & 6))) << (3*k) for k in range(4))
                         for x in range(4096)) for a in range(1, 8)]


def neighbors(state, weights, tables):
    rows = [(state >> (12*i)) & 4095 for i in range(3)]
    for i in range(3):
        for a in range(1, 8):
            yield state ^ (a << (12*i+9)), weights[i], (i, 3, a)
        for j in range(3):
            if j != i:
                for a in range(1, 8):
                    yield state ^ (tables[a][rows[j]] << (12*i)), weights[3+i], (i, j, a)


def oracle(demand, prices, tables):
    scale = lcm(*(Fraction(x).denominator for x in prices))
    weights = tuple(int(Fraction(x)*scale) for x in prices)
    require(min(weights) > 0, 'positive oracle weights')
    start = 1 | (8 << 12) | (64 << 24)
    goal = start | sum(x << (12*i+9) for i, x in enumerate(demand))
    ds = [{start: 0}, {goal: 0}]
    qs = [[(0, start)], [(0, goal)]]
    ps = [{start: None}, {goal: None}]
    best, meet = None, None
    settled = [0, 0]
    while qs[0] and qs[1]:
        for s in (0, 1):
            while qs[s] and qs[s][0][0] != ds[s][qs[s][0][1]]:
                heappop(qs[s])
        if not qs[0] or not qs[1]:
            break
        if best is not None and qs[0][0][0]+qs[1][0][0] >= best:
            break
        s = int(qs[1][0][0] < qs[0][0][0])
        du, u = heappop(qs[s])
        settled[s] += 1
        for v, cost, gate in neighbors(u, weights, tables):
            dv = du+cost
            if v not in ds[s] or dv < ds[s][v]:
                ds[s][v] = dv
                ps[s][v] = (u, gate)
                heappush(qs[s], (dv, v))
                if v in ds[1-s]:
                    candidate = dv+ds[1-s][v]
                    if best is None or candidate < best:
                        best, meet = candidate, v
    require(meet is not None, 'oracle endpoints disconnected')
    forward, back = [], []
    u = meet
    while ps[0][u] is not None:
        u, gate = ps[0][u]
        forward.append(gate)
    u = meet
    while ps[1][u] is not None:
        u, gate = ps[1][u]
        back.append(gate)  # Every primitive inverse equals itself in characteristic two.
    return Fraction(best, scale), list(reversed(forward))+back, settled


def main():
    eight = square_zero(2)
    pats = patterns()
    vectors = [p[-1] for p in pats]
    require(len(vectors) == len(set(vectors)) == 19, 'nineteen distinct count vectors')
    require(all(not all(a <= b for a, b in zip(v, w)) for v in vectors for w in vectors if v != w),
            'Pareto vectors incomparable')
    total = dict(demands=0, words=0, formal_forward_inverse=0, literal_forward_inverse=0,
                 exposed_vectors=0, oracle_queries=0, oracle_settled=0, controls=0)
    fixtures = []
    for r in (eight, square_zero(3), dual_z4(), product_ring(eight)):
        check_ring(r)
        principal_ideals = {r.principal(x) for x in range(r.n)}
        accepted = 0
        for a, b in product(range(r.n), repeat=2):
            d = (a, b, r.neg(r.add[a][b]))
            if r.ideal(d) in principal_ideals:
                continue
            validate_demand(r, d)
            require(all(x != 0 for x in d), 'nonprincipal zero-sum demands are nonzero')
            require(all(d[i] not in r.principal(d[j]) for i in range(3) for j in range(3) if i != j),
                    'pairwise principal incomparability')
            accepted += 1
            for pattern in pats:
                word = construct(r, d, pattern)
                require(all(a != 0 for _, _, a in word), 'exact-price words have no zero gates')
                require(endpoint(r, d, word), 'constructed dirt endpoint/inverse')
                require(counts(word) == pattern[-1], 'claimed gate counts')
                total['words'] += 1
                total['formal_forward_inverse'] += 8
        total['demands'] += accepted
        fixtures.append({'ring': r.name, 'zero_sum_nonprincipal_triples': accepted})

    d = (2, 4, 6)
    words = [construct(eight, d, p) for p in pats]
    for word in words:
        rev = inverse(eight, word)
        for entry in product(range(8), repeat=4):
            want = target(eight, d, entry)
            require(execute(eight, word, entry) == want and execute(eight, rev, want) == entry,
                    'literal eight-element endpoint/inverse')
            total['literal_forward_inverse'] += 2

    representative_prices = [(1,1,1,1,1,1), (1,3,3,1,1,1), (1,2,5,1,2,1),
                             (3,5,10,1,3,2), (3,3,5,2,2,1)]
    exposed = set()
    for prices in representative_prices:
        for perm in permutations(range(3)):
            p = tuple(prices[i] for i in perm)+tuple(prices[3+i] for i in perm)
            costs = [bill(word, p) for word in words]
            minimum = min(costs)
            require(costs.count(minimum) == 1, 'strict positive-price exposure')
            require(minimum == formula(p[:3], p[3:]), 'compressed nineteen-term envelope')
            exposed.add(costs.index(minimum))
    require(len(exposed) == 19, 'every vector exposed by positive prices')
    total['exposed_vectors'] = len(exposed)

    # A one-insertion discriminator when the nonprincipal-ideal hypothesis is dropped.
    boolean = ring_from_functions('F2 x F2 x F2', 8, 7, lambda x, y: x ^ y, lambda x, y: x & y)
    check_ring(boolean)
    bd = (3,5,6)
    suffix = [(1,0,5), (2,0,6), (0,1,4)]
    one_call = inverse(boolean, suffix)+[(0,3,7)]+suffix
    prices = (10,100,100,1,1,1)
    require(endpoint(boolean, bd, one_call), 'principal-ideal one-insertion discriminator')
    require(bill(one_call, prices) == 16 < formula(prices[:3], prices[3:]) == 24,
            'nonprincipality is essential')
    total['controls'] += 1
    for ring, demand, fragment in [(boolean, bd, 'nonprincipal'), (eight, (2,4,2), 'sum to zero')]:
        try:
            validate_demand(ring, demand)
        except ValueError as error:
            require(fragment in str(error), 'correct domain rejection')
            total['controls'] += 1
        else:
            raise RuntimeError('accepted demand outside the theorem')
    bad_sum_word = construct(eight, (2,4,2), pats[1])
    require(not endpoint(eight, (2,4,2), bad_sum_word), 'zero-sum hypothesis is substantive')
    total['controls'] += 1
    corrupted = words[1][1:]
    require(execute(eight, corrupted, (0,0,0,1)) == (*d,1), 'dirty-only corruption premise')
    require(not endpoint(eight, d, corrupted), 'reject missing dirt preparation')
    total['controls'] += 1
    relator = [(0,1,1), (1,2,1), (0,1,1), (1,2,1), (0,2,1)]
    require(endpoint(eight, (0,0,0), relator), 'single-edge identity control')
    require(sum((i,j) == (0,2) for i,j,_ in relator) == 1, 'no universal per-edge return lemma')
    total['controls'] += 1
    for bad_prices in [(0,1,1,1,1,1), (1,1,1,-1,1,1)]:
        try:
            formula(bad_prices[:3], bad_prices[3:])
        except ValueError:
            total['controls'] += 1
        else:
            raise RuntimeError('accepted nonpositive tariff')

    tables = packed_tables()
    cases = list(zip(('D','T','R','M','Q'), representative_prices))
    cases += [('cheap-root', (1,9,9,1,1,1)),
              ('rational', (Fraction(1,2),Fraction(4,3),Fraction(7,3),
                            Fraction(2,3),Fraction(3,4),Fraction(1,5)))]
    results = []
    for name, prices in cases:
        value, path, settled = oracle(d, prices, tables)
        require(value == formula(prices[:3], prices[3:]), f'oracle mismatch: {name}')
        require(endpoint(eight, d, path) and bill(path, prices) == value, 'oracle word replay and tariff')
        total['oracle_queries'] += 1
        total['oracle_settled'] += sum(settled)
        results.append({'case': name, 'optimum': str(value), 'settled': settled})
        print('CHECK_ORACLE', name, str(value), flush=True)
    print(json.dumps({'fixtures': fixtures, 'counts': total, 'oracle': results}, sort_keys=True))
    print('PASS_SQUARE_ZERO_TRIPLE_FANOUT no_new_kappa')


if __name__ == '__main__':
    main()
