#!/usr/bin/env python3
"""Exact bounded checks for the Boolean triple tariff; Apache-2.0.

lee-phys with substantial OpenAI Codex assistance. Adapted word, interpreter
and Dijkstra infrastructure from #5259, head d2a7d88f011ca9c520333da8d4e03f1f22d23e91.
Credit #5045/#5139/#5163/#5208 and the earlier fanout lineage in README.md.
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
    for i in range(3):
        j, k = [r for r in range(3) if r != i]
        v = [0, 0, 0, 2, 2, 2]
        v[i] = 1
        out.append(('U', i, j, k, tuple(v)))
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
    if mode == 'U':
        g = r.add[r.add[d[0]][d[1]]][r.mul[d[0]][d[1]]]
        suffix = [(j, i, d[j]), (k, i, d[k]), (i, j, r.add[g][d[i]])]
        return inverse(r, suffix)+[(i, 3, g)]+suffix
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
    start = 7 | (56 << 12) | (448 << 24)
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


def boolean_ring(n):
    # Coordinate arithmetic supplies the primary tables, independently of the
    # packed oracle's bitwise-AND implementation.
    return ring_from_functions(f'F2^{n}', 2**n, 2**n-1,
        lambda a, b: sum((((a//2**k) % 2+(b//2**k) % 2) % 2)*2**k for k in range(n)),
        lambda a, b: sum(((a//2**k) % 2)*((b//2**k) % 2)*2**k for k in range(n)))


def validate_demand(r, d):
    if any(r.mul[x][x] != x for x in range(r.n)):
        raise ValueError('a Boolean ring is required')
    if len(d) != 3 or any(type(x) is not int or not 0 <= x < r.n for x in d):
        raise ValueError('three ring elements required')
    if r.add[r.add[d[0]][d[1]]][d[2]] != 0:
        raise ValueError('the demand must sum to zero')
    if any(d[i] in r.principal(d[j]) for i in range(3) for j in range(3) if i != j):
        raise ValueError('pairwise incomparable principal ideals required')


def formula(mu, c):
    if len(mu) != 3 or len(c) != 3 or min((*mu, *c)) <= 0:
        raise ValueError('six strictly positive prices required')
    out = [sum(mu), min(mu)+2*sum(c)]
    for k in range(3):
        i, j = [r for r in range(3) if r != k]
        out.append(2*mu[k]+2*c[i]+2*c[j])
        out.append(mu[i]+mu[j]+2*c[k]+min(mu[i], mu[j], 2*c[i], 2*c[j], 2*c[k]))
    return min(out)


def packed_tables():
    # Four 3-bit coefficients in each 12-bit row; multiplication is AND.
    return [None]+[tuple(x & (a | a << 3 | a << 6 | a << 9) for x in range(4096))
                   for a in range(1, 8)]


def main():
    pats = patterns()
    vectors = [p[-1] for p in pats]
    require(len(vectors) == len(set(vectors)) == 22, 'twenty-two distinct vectors')
    require(all(not all(a <= b for a, b in zip(v, w)) for v in vectors for w in vectors if v != w),
            'Pareto vectors incomparable')
    total = dict(demands=0, words=0, formal_forward_inverse=0, literal_forward_inverse=0,
                 exposed_vectors=0, oracle_queries=0, oracle_settled=0, controls=0)
    fixtures = []
    for n in (3, 4, 5):
        r = boolean_ring(n)
        check_ring(r)
        accepted = proper = 0
        for a, b in product(range(r.n), repeat=2):
            d = (a, b, r.add[a][b])
            if any(d[i] in r.principal(d[j]) for i in range(3) for j in range(3) if i != j):
                continue
            validate_demand(r, d)
            g = r.add[r.add[a][b]][r.mul[a][b]]
            require(r.ideal(d) == r.principal(g), 'principal demand ideal')
            require(all(r.principal(x) != r.principal(g) for x in d), 'no demand generates I')
            atoms = [r.mul[d[i]][d[j]] for i, j in ((0,1),(0,2),(1,2))]
            require(all(atoms) and all(r.mul[x][y] == 0 for x,y in permutations(atoms,2)),
                    'three disjoint nonzero atoms')
            accepted += 1
            proper += int(g != r.one)
            for pattern in pats:
                word = construct(r, d, pattern)
                require(all(a != 0 and 0 <= i < 3 and 0 <= j < 4 and i != j for i,j,a in word),
                        'nonzero legal gates')
                require(endpoint(r, d, word), 'constructed dirt endpoint/inverse')
                require(counts(word) == pattern[-1], 'claimed gate counts')
                total['words'] += 1
                total['formal_forward_inverse'] += 8
        require(accepted == 4**n-3*3**n+3*2**n-1, 'all three support atoms nonempty')
        total['demands'] += accepted
        fixtures.append({'ring': r.name, 'demands': accepted, 'proper_ideal_demands': proper})

    r, d = boolean_ring(3), (3,5,6)
    words = [construct(r, d, p) for p in pats]
    for word in words:
        rev = inverse(r, word)
        for entry in product(range(8), repeat=4):
            want = target(r, d, entry)
            require(execute(r, word, entry) == want and execute(r, rev, want) == entry,
                    'literal eight-element endpoint/inverse')
            total['literal_forward_inverse'] += 2

    representatives = [(1,1,1,1,1,1), (1,3,3,1,1,1), (1,2,5,1,2,1),
                       (3,5,10,1,3,2), (3,3,5,2,2,1), (3,9,9,1,1,1)]
    exposed = set()
    for prices in representatives:
        for perm in permutations(range(3)):
            p = tuple(prices[i] for i in perm)+tuple(prices[3+i] for i in perm)
            costs = [bill(word, p) for word in words]
            minimum = min(costs)
            require(costs.count(minimum) == 1, 'strict positive-price exposure')
            require(minimum == formula(p[:3], p[3:]), 'compressed twenty-two-term envelope')
            exposed.add(costs.index(minimum))
    require(len(exposed) == 22, 'every vector exposed by positive prices')
    total['exposed_vectors'] = len(exposed)
    for mu, c in product(range(1,13), repeat=2):
        require(formula((mu,)*3, (c,)*3) == min(3*mu, mu+6*c), 'uniform-price corollary')

    # The old nineteen-term formula is strictly too expensive for this demand.
    p = (10,100,100,1,1,1)
    require(min(bill(w,p) for w in words[:19]) == 24 and formula(p[:3],p[3:]) == 16,
            'one-insertion branch changes the optimum')
    total['controls'] += 1
    for bad, fragment in [((3,5,3),'sum to zero'), ((1,1,0),'incomparable')]:
        try:
            validate_demand(r, bad)
        except ValueError as error:
            require(fragment in str(error), 'correct hypothesis rejection')
            total['controls'] += 1
        else:
            raise RuntimeError('accepted out-of-scope demand')
    require(not endpoint(r, (3,5,3), construct(r,(3,5,3),pats[1])), 'zero sum is substantive')
    total['controls'] += 1
    # The first three preparations of U_0 do not act on a zero source column.
    corrupted = words[19][3:]
    require(execute(r, corrupted, (0,0,0,7)) == (*d,7), 'dirty-only corruption premise')
    require(not endpoint(r, d, corrupted), 'reject omitted one-insertion dirt preparation')
    total['controls'] += 1
    wrong = [g if g[1] != 3 else (g[0],g[1],1) for g in words[19]]
    require(not endpoint(r, d, wrong), 'Boolean identity is 7, not bitmask 1')
    total['controls'] += 1
    relator = [(0,1,7),(1,2,7),(0,1,7),(1,2,7),(0,2,7)]
    require(endpoint(r, (0,0,0), relator), 'identity with one call on edge 02')
    total['controls'] += 1
    # Outside the incomparable-ideal hypothesis, a two-ADD echo costs only 5.
    comparable = (1,1,0)
    echo = [(1,0,7),(0,3,1),(1,0,7)]
    p = (1,9,9,1,2,1)
    require(endpoint(r,comparable,echo) and bill(echo,p) == 5 < formula(p[:3],p[3:]),
            'pairwise incomparability is substantive')
    total['controls'] += 1
    z4 = ring_from_functions('Z/4',4,1,lambda a,b:(a+b)%4,lambda a,b:a*b%4)
    try:
        validate_demand(z4,(1,1,2))
    except ValueError as error:
        require('Boolean' in str(error), 'non-Boolean rejection')
        total['controls'] += 1
    else:
        raise RuntimeError('accepted non-Boolean ring')
    for bad_prices in [(0,1,1,1,1,1),(1,1,1,-1,1,1)]:
        try:
            formula(bad_prices[:3],bad_prices[3:])
        except ValueError:
            total['controls'] += 1
        else:
            raise RuntimeError('accepted nonpositive prices')

    tables = packed_tables()
    for a in range(1,8):
        for x in range(4096):
            require(tables[a][x] == sum(r.mul[a][(x >> (3*k)) & 7] << (3*k) for k in range(4)),
                    'oracle multiplication agrees with coordinate arithmetic')
    cases = list(zip(('D','T','R','M','Q','U'), representatives))
    cases += [('rational', (Fraction(1,2),Fraction(4,3),Fraction(7,3),
                            Fraction(2,3),Fraction(3,4),Fraction(1,5)))]
    results = []
    for name, prices in cases:
        value, path, settled = oracle(d, prices, tables)
        require(value == formula(prices[:3], prices[3:]), f'oracle mismatch: {name}')
        require(endpoint(r,d,path) and bill(path,prices) == value, 'oracle path replay and price')
        total['oracle_queries'] += 1
        total['oracle_settled'] += sum(settled)
        results.append({'case': name, 'optimum': str(value), 'settled': settled})
        print('CHECK_ORACLE', name, str(value), flush=True)
    print(json.dumps({'fixtures': fixtures, 'counts': total, 'oracle': results}, sort_keys=True))
    print('PASS_BOOLEAN_TRIPLE_FANOUT no_new_kappa')


if __name__ == '__main__':
    main()
