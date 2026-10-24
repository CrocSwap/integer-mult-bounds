#!/usr/bin/env python3
"""Exact finite checks for the scoped local-ring theorem in README.md.

lee-phys with substantial OpenAI Codex assistance; Apache-2.0.
#3063/#4916/#5045 retain the credited return and echo/mixing constructions.
"""
from dataclasses import dataclass
from fractions import Fraction
from heapq import heappop, heappush
from itertools import product
from math import lcm
import json


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


@dataclass(frozen=True)
class Ring:
    name: str
    n: int
    add: tuple
    mul: tuple

    def neg(self, x):
        return next(y for y in range(self.n) if self.add[x][y] == 0)

    def sub(self, x, y):
        return self.add[x][self.neg(y)]

    def inv(self, x):
        return next(y for y in range(self.n) if self.mul[x][y] == 1)

    def units(self):
        return frozenset(x for x in range(self.n) if 1 in self.mul[x])

    def local(self):
        nonunits = set(range(self.n))-self.units()
        return (all(self.add[x][y] in nonunits for x in nonunits for y in nonunits)
                and all(self.mul[x][y] in nonunits for x in nonunits for y in range(self.n)))


def residue(n):
    return Ring(f'Z/{n}', n, tuple(tuple((x+y) % n for y in range(n)) for x in range(n)),
                tuple(tuple(x*y % n for y in range(n)) for x in range(n)))


def square_zero_eight():
    def mul(x, y):
        return ((x & 1)*(y & 1)) ^ ((x & 1)*(y & 6)) ^ ((y & 1)*(x & 6))
    return Ring('F2[e,h]/(e^2,eh,h^2)', 8,
                tuple(tuple(x ^ y for y in range(8)) for x in range(8)),
                tuple(tuple(mul(x, y) for y in range(8)) for x in range(8)))


def check_ring(r):
    es, add, mul = range(r.n), r.add, r.mul
    for x, y in product(es, repeat=2):
        require(add[x][y] in es and mul[x][y] in es, 'ring closure')
        require(add[x][y] == add[y][x] and mul[x][y] == mul[y][x], 'commutativity')
    for x in es:
        require(add[x][0] == x and mul[x][1] == x and mul[x][0] == 0, 'identities')
        require(add[x][r.neg(x)] == 0, 'additive inverse')
    for x, y, z in product(es, repeat=3):
        require(add[add[x][y]][z] == add[x][add[y][z]], 'addition associativity')
        require(mul[mul[x][y]][z] == mul[x][mul[y][z]], 'multiplication associativity')
        require(mul[x][add[y][z]] == add[mul[x][y]][mul[x][z]], 'distributivity')


def raw_candidates(r, demand, mu, c):
    """Algebraic expressions only; callers must establish the theorem domain."""
    units = r.units()
    u = [i for i, x in enumerate(demand) if x in units]
    n = [i for i, x in enumerate(demand) if x not in units]
    a = [min(mu[i], 2*c[i]) if x != 0 else 0 for i, x in enumerate(demand)]
    total = sum(a)
    b = 2*sum(c[i] for i in u)+sum(a[i] for i in n)
    out = [('F', i, total+mu[i]-a[i]) for i in u]
    out += [('T', i, b+2*mu[i]-a[i]) for i in n]
    out += [('S', i, b+mu[i]+2*c[i]-a[i]) for i in n]
    return out


def candidates(r, demand, mu, c):
    q = len(demand)
    if q < 1 or len(mu) != q or len(c) != q or min((*mu, *c)) <= 0:
        raise ValueError('positive prices and matching nonempty row arrays required')
    if not all(isinstance(x, int) and 0 <= x < r.n for x in demand):
        raise ValueError('demand outside the finite ring')
    if not any(demand):
        return [('Z', -1, 0)]
    if not r.local():
        raise ValueError('the tariff theorem requires a local ring')
    if not any(x in r.units() for x in demand):
        raise ValueError('nonzero all-nonunit demands are outside the theorem')
    return raw_candidates(r, demand, mu, c)


def reverse_word(r, word):
    return [(i, j, r.neg(a)) for i, j, a in reversed(word)]


def construct(r, demand, mu, c, mode, root):
    q = len(demand)
    if mode == 'Z':
        return []
    units = r.units()
    direct = {root}
    for i, x in enumerate(demand):
        allowed = mode == 'F' or x not in units
        if i != root and x != 0 and allowed and mu[i] <= 2*c[i]:
            direct.add(i)
    echoed = [i for i, x in enumerate(demand) if x != 0 and i not in direct]
    other_calls = [(i, q, demand[i]) for i in sorted(direct-{root})]
    if mode == 'F':
        factor = r.inv(demand[root])
        pre = [(i, root, r.neg(r.mul[demand[i]][factor])) for i in echoed]
        word = pre+[(root, q, demand[root])]+reverse_word(r, pre)
    elif mode == 'T':
        pre = [(i, root, r.neg(demand[i])) for i in echoed]
        word = pre+[(root, q, 1)]+reverse_word(r, pre)+[(root, q, r.sub(demand[root], 1))]
    elif mode == 'S':
        pivot = next(i for i, x in enumerate(demand) if x in units)
        factor = r.inv(demand[pivot])
        b = r.mul[demand[root]][factor]
        pre = [(i, pivot, r.neg(r.mul[demand[i]][factor])) for i in echoed if i != pivot]
        core = [(root, pivot, r.sub(1, b)), (pivot, root, r.neg(1)),
                (root, q, demand[pivot]), (pivot, root, 1), (root, pivot, r.sub(b, 1))]
        word = pre+core+reverse_word(r, pre)
    else:
        raise ValueError('unknown construction')
    return word+other_calls


def execute(r, word, values):
    out = list(values)
    for i, j, a in word:
        out[i] = r.add[out[i]][r.mul[a][out[j]]]
    return tuple(out)


def endpoint(r, demand, word):
    q = len(demand)
    for k in range(q+1):
        entry = tuple(int(j == k) for j in range(q+1))
        target = tuple(r.add[entry[i]][r.mul[demand[i]][entry[q]]] for i in range(q))+(entry[q],)
        if execute(r, word, entry) != target or execute(r, reverse_word(r, word), target) != entry:
            return False
    return True


def bill(word, q, mu, c):
    return sum(mu[i] if j == q else c[i] for i, j, _ in word)


def gate_counts(word, q):
    return tuple(sum(i == k and j == q for i, j, _ in word) for k in range(q)) + tuple(
        sum(i == k and j != q for i, j, _ in word) for k in range(q))


# The oracle below uses only modular packed affine states and primitive gates.
# It never calls the formula, local-ring criterion or word constructors.
def packed_tables():
    return [None]+[bytes(sum(((((x >> (2*k)) & 3)+a*((y >> (2*k)) & 3)) % 4) << (2*k)
                                 for k in range(4)) for x in range(256) for y in range(256))
                   for a in (1, 2, 3)]


def packed_neighbors(state, weights, tables):
    for i in range(3):
        shift = 8*i
        row = (state >> shift) & 255
        source = row >> 6
        for a in (1, 2, 3):
            updated = (row & 63) | (((source+a) & 3) << 6)
            yield state ^ ((row ^ updated) << shift), weights[i], (i, 3, a)
        for j in range(3):
            if i == j:
                continue
            other = (state >> (8*j)) & 255
            index = (row << 8) | other
            for a in (1, 2, 3):
                updated = tables[a][index]
                yield state ^ ((row ^ updated) << shift), weights[3+i], (i, j, a)


def oracle(demand, mu, c, tables):
    scale = lcm(*(Fraction(x).denominator for x in (*mu, *c)))
    weights = tuple(int(Fraction(x)*scale) for x in (*mu, *c))
    require(min(weights) > 0, 'oracle positive prices')
    start = 1 | (4 << 8) | (16 << 16)
    goal = start | sum(x << (8*i+6) for i, x in enumerate(demand))
    if start == goal:
        return Fraction(0), [], (0, 0)
    dist = [{start: 0}, {goal: 0}]
    parents = [{start: None}, {goal: None}]
    queues = [[(0, start)], [(0, goal)]]
    best, meeting = None, None
    settled = [0, 0]
    while queues[0] and queues[1]:
        for side in (0, 1):
            while queues[side] and queues[side][0][0] != dist[side][queues[side][0][1]]:
                heappop(queues[side])
        if not queues[0] or not queues[1]:
            break
        if best is not None and queues[0][0][0]+queues[1][0][0] >= best:
            break
        side = int(queues[1][0][0] < queues[0][0][0])
        du, u = heappop(queues[side])
        settled[side] += 1
        other_dist = dist[1-side]
        for v, cost, gate in packed_neighbors(u, weights, tables):
            dv = du+cost
            if v not in dist[side] or dv < dist[side][v]:
                dist[side][v] = dv
                parents[side][v] = (u, gate)
                heappush(queues[side], (dv, v))
                if v in other_dist:
                    total = dv+other_dist[v]
                    if best is None or total < best:
                        best, meeting = total, v
    require(meeting is not None, 'oracle failed to connect endpoints')
    forward, back = [], []
    u = meeting
    while parents[0][u] is not None:
        u, gate = parents[0][u]
        forward.append(gate)
    u = meeting
    while parents[1][u] is not None:
        u, (i, j, a) = parents[1][u]
        back.append((i, j, (-a) % 4))
    path = list(reversed(forward))+back
    return Fraction(best, scale), path, tuple(settled)


def price_fixtures(q):
    return [((1,)*q, (1,)*q),
            (tuple(2*i+5 for i in range(q)), tuple(i+1 for i in range(q))),
            (tuple(Fraction(i+1, 3) for i in range(q)), tuple(Fraction(q-i, 5) for i in range(q)))]


def main():
    rings = [residue(n) for n in (2, 3, 4, 8, 9)]+[square_zero_eight()]
    totals = dict(demands=0, price_instances=0, words=0, basis_forward_inverse=0,
                  literal_forward_inverse=0, oracle_runs=0, oracle_settled=0, controls=0)
    fixture_records = []
    def check_problem(r, demand):
        totals['demands'] += 1
        for mu, c in price_fixtures(len(demand)):
            options = candidates(r, demand, mu, c)
            totals['price_instances'] += 1
            for mode, root, expected in options:
                word = construct(r, demand, mu, c, mode, root)
                require(all(a != 0 for _, _, a in word), 'zero gate in exact-price construction')
                require(endpoint(r, demand, word), f'word endpoint/inverse: {r.name} {demand} {mode}{root}')
                require(bill(word, len(demand), mu, c) == expected, 'exact candidate price')
                totals['words'] += 1
                totals['basis_forward_inverse'] += 2*(len(demand)+1)
    for r in rings:
        check_ring(r)
        require(r.local(), 'positive local-ring fixture')
        count = 0
        units = r.units()
        for q in (1, 2, 3):
            for demand in product(range(r.n), repeat=q):
                if not any(demand) or any(x in units for x in demand):
                    check_problem(r, demand)
                    count += 1
        for q in (4, 5, 7):
            nonunit = next((x for x in range(1, r.n) if x not in units), 0)
            for offset in range(q):
                demand = tuple((1, nonunit, 0)[(i+offset) % 3] for i in range(q))
                check_problem(r, demand)
                count += 1
        fixture_records.append({'ring': r.name, 'demand_lists': count})

    four = residue(4)
    demand = (2, 1, 1)
    names = ('D', 'F01', 'F02', 'F12', 'F1', 'F2', 'T0', 'S0')
    vectors = ((1,1,1,0,0,0), (1,1,0,0,0,2), (1,0,1,0,2,0), (0,1,1,2,0,0),
               (0,1,0,2,0,2), (0,0,1,2,2,0), (2,0,0,0,2,2), (1,0,0,2,2,2))
    regimes = ((1,1,1,1,1,1), (1,1,20,10,10,1), (1,20,1,10,1,10), (20,1,1,1,10,10),
               (20,1,20,1,10,1), (20,20,1,1,1,10), (1,20,20,10,1,1), (5,20,20,1,1,1))
    chosen_words = []
    for index, prices in enumerate(regimes):
        costs = [sum(x*y for x, y in zip(v, prices)) for v in vectors]
        require(costs[index] < min(v for i, v in enumerate(costs) if i != index), 'strict eight-term regime')
        totals['controls'] += 1
        mu, c = prices[:3], prices[3:]
        mode, root, value = min(candidates(four, demand, mu, c), key=lambda x: x[2])
        word = construct(four, demand, mu, c, mode, root)
        require(value == costs[index] and gate_counts(word, 3) == vectors[index], 'three-row table count')
        chosen_words.append(word)
        for entry in product(range(4), repeat=4):
            target = tuple((entry[i]+demand[i]*entry[3]) % 4 for i in range(3))+(entry[3],)
            require(execute(four, word, entry) == target, 'literal three-row word')
            require(execute(four, reverse_word(four, word), target) == entry, 'literal inverse')
            totals['literal_forward_inverse'] += 2

    # Three-row identity with one occurrence of a particular directed edge.
    relator = [(0,1,1), (1,2,1), (0,1,3), (1,2,3), (0,2,1)]
    require(endpoint(four, (0,0,0), relator), 'five-ADD identity')
    require(sum((i, j) == (0, 2) for i, j, _ in relator) == 1, 'single edge-occurrence control')
    totals['controls'] += 1
    # Source column alone would miss this failed restoration.
    bad = chosen_words[6][1:]
    require(execute(four, bad, (0,0,0,1)) == (2,1,1,1), 'dirty-only mutation premise')
    require(not endpoint(four, demand, bad), 'reject missing dirt preparation')
    totals['controls'] += 1
    try:
        candidates(four, (2,2,2), (1,1,1), (1,1,1))
    except ValueError:
        totals['controls'] += 1
    else:
        raise RuntimeError('accepted all-nonunit demand outside the theorem')

    six = residue(6)
    check_ring(six)
    nonlocal_demand, mu, c = (2,3,1), (10,10,100), (100,100,1)
    require(not six.local(), 'nonlocal fixture')
    try:
        candidates(six, nonlocal_demand, mu, c)
    except ValueError:
        totals['controls'] += 1
    else:
        raise RuntimeError('accepted nonlocal ring')
    require(min(x[2] for x in raw_candidates(six, nonlocal_demand, mu, c)) == 32, 'invalid extension discriminator')
    witness_word = [(2,0,4), (2,1,5), (0,3,2), (1,3,3), (2,1,1), (2,0,2)]
    require(bill(witness_word, 3, mu, c) == 24 and endpoint(six, nonlocal_demand, witness_word), 'nonlocal cost-24 word')
    for entry in product(range(6), repeat=4):
        target = tuple((entry[i]+nonlocal_demand[i]*entry[3]) % 6 for i in range(3))+(entry[3],)
        require(execute(six, witness_word, entry) == target and execute(six, reverse_word(six, witness_word), target) == entry,
                'literal nonlocal counterexample')
        totals['literal_forward_inverse'] += 2
    totals['controls'] += 1

    tables = packed_tables()
    oracle_cases = [(name, demand, p[:3], p[3:]) for name, p in zip(names, regimes)]
    oracle_cases += [
        ('requested-first-matrix', demand, (1,9,9), (1,1,1)),
        ('expensive-source-mixing', demand, (100,1000,1000), (1,1,1)),
        ('repeat-mix-tie', demand, (2,9,9), (1,1,1)),
        ('rational', demand, (Fraction(3,2),Fraction(7,2),Fraction(11,2)),
         (Fraction(1,3),Fraction(2,3),Fraction(4,3))),
        ('zero-temporary-recipient', (0,1,2), (1,9,9), (1,1,1)),
        ('permuted-nonunit-1', (1,2,3), (9,1,9), (1,1,1)),
        ('permuted-nonunit-2', (1,3,2), (9,9,1), (1,1,1)),
        ('unit-demand-calibration', (1,3,1), (1,9,9), (1,1,1)),
    ]
    oracle_records = []
    for name, target, mu, c in oracle_cases:
        value, path, settled = oracle(target, mu, c, tables)
        predicted = min(x[2] for x in candidates(four, target, mu, c))
        require(value == predicted, f'oracle mismatch: {name}: {value} != {predicted}')
        require(endpoint(four, target, path) and bill(path, 3, mu, c) == value, 'oracle path replay and bill')
        totals['oracle_runs'] += 1
        totals['oracle_settled'] += sum(settled)
        oracle_records.append({'case': name, 'optimum': str(value), 'settled': list(settled)})
        print('CHECK_ORACLE', name, str(value), flush=True)
    require(oracle_records[8]['optimum'] == '6' and oracle_records[9]['optimum'] == '106', 'named exact optima')
    totals['controls'] += 2
    print(json.dumps({'fixtures': fixture_records, 'counts': totals, 'oracle': oracle_records}, sort_keys=True))
    print('PASS_LOCAL_RING_ROW_FANOUT no_new_kappa')


if __name__ == '__main__':
    main()
