#!/usr/bin/env python3
"""Exact finite corroboration of README.md; no third-party or live inputs.

lee-phys with substantial OpenAI Codex assistance; Apache-2.0.
The source-count tariff and standard words retain #5045/#5089 attribution.
"""
from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from heapq import heappop, heappush
from itertools import product
from math import lcm
import json


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


@dataclass
class Ring:
    name: str
    n: int
    one: int
    add: tuple
    mul: tuple

    @property
    def elements(self):
        return range(self.n)

    def neg(self, x):
        return next(y for y in self.elements if self.add[x][y] == 0)

    def sub(self, x, y):
        return self.add[x][self.neg(y)]


def table_ring(name, n, one, add, mul):
    return Ring(name, n, one,
                tuple(tuple(add(x, y) for y in range(n)) for x in range(n)),
                tuple(tuple(mul(x, y) for y in range(n)) for x in range(n)))


def residue(n):
    return table_ring(f'Z/{n}', n, 1, lambda x, y: (x+y) % n,
                      lambda x, y: x*y % n)


def square_zero(q, dimension):
    # Basis 1,e_1,...,e_dimension; every product e_i e_j is zero.
    n = q ** (dimension+1)
    digits = [tuple(x // q**i % q for i in range(dimension+1)) for x in range(n)]
    def pack(ds):
        return sum((d % q)*q**i for i, d in enumerate(ds))
    def mul(x, y):
        a, b = digits[x], digits[y]
        return pack([a[0]*b[0]] + [a[0]*b[i]+a[i]*b[0]
                                   for i in range(1, dimension+1)])
    return table_ring(f'F{q}+square-zero^{dimension}', n, 1,
                      lambda x, y: pack(a+b for a, b in zip(digits[x], digits[y])), mul)


def ring_product(r, s):
    return table_ring(f'({r.name})x({s.name})', r.n*s.n, r.one+r.n*s.one,
                      lambda x, y: r.add[x % r.n][y % r.n]
                      + r.n*s.add[x // r.n][y // r.n],
                      lambda x, y: r.mul[x % r.n][y % r.n]
                      + r.n*s.mul[x // r.n][y // r.n])


def field_four():
    def mul(x, y):
        v = 0
        for i in range(2):
            if (y >> i) & 1:
                v ^= x << i
        if v & 4:
            v ^= 7  # t^2+t+1
        return v
    return table_ring('F4', 4, 1, lambda x, y: x ^ y, mul)


def two_truncated_variables():
    # Basis indexed by exponent bit masks: 1,e,h,eh; e^2=h^2=0.
    def mul(x, y):
        out = 0
        for i, j in product(range(4), repeat=2):
            if x >> i & 1 and y >> j & 1 and not i & j:
                out ^= 1 << (i | j)
        return out
    return table_ring('F2[e,h]/(e^2,h^2)', 16, 1, lambda x, y: x ^ y, mul)


def check_ring(r):
    a, m, es = r.add, r.mul, r.elements
    require(r.one != 0, 'zero ring excluded')
    for x, y in product(es, repeat=2):
        require(a[x][y] in es and m[x][y] in es, 'closure')
        require(a[x][y] == a[y][x] and m[x][y] == m[y][x], 'commutativity')
    for x in es:
        require(a[x][0] == x and m[x][r.one] == x and m[x][0] == 0, 'identities')
        require(a[x][r.neg(x)] == 0, 'additive inverse')
    for x, y, z in product(es, repeat=3):
        require(a[a[x][y]][z] == a[x][a[y][z]], 'addition associativity')
        require(m[m[x][y]][z] == m[x][m[y][z]], 'multiplication associativity')
        require(m[x][a[y][z]] == a[m[x][y]][m[x][z]], 'distributivity')


def ideals(r):
    principal = tuple(frozenset(r.mul[t][x] for t in r.elements) for x in r.elements)
    generated = {(x, y): frozenset(r.add[a][b] for a in principal[x] for b in principal[y])
                 for x, y in product(r.elements, repeat=2)}
    return principal, generated


def witness(r, x, y, principal, target_ideal):
    for a in r.elements:
        beta = r.sub(x, r.mul[a][y])
        if principal[beta] == target_ideal:
            t = next(t for t in r.elements if r.mul[t][beta] == y)
            return a, beta, t
    raise RuntimeError('principal ideal lacks stable-reduction witness')


def candidate_counts(demand, principal, generated):
    x, y = demand
    out = {'D': (int(x != 0), int(y != 0), 0, 0),
           'T0': (2, 0, 0, 2), 'T1': (0, 2, 2, 0)}
    if generated[demand] in principal:
        for i in range(2):
            j = 1-i
            v = [0]*4
            v[i] = 1
            if demand[j] != 0:
                v[2+j] = 2
                if demand[j] not in principal[demand[i]]:
                    v[2+i] = 2
            out[f'S{i}'] = tuple(v)
    return out


def price(counts, prices):
    return sum(c*p for c, p in zip(counts, prices))


def words(r, demand, principal, generated):
    # Gate kind 0/1 is P_0/P_1; 2/3 is E_0/E_1.
    out = {'D': [(i, demand[i]) for i in range(2)]}
    for i in range(2):
        j, x, y = 1-i, demand[i], demand[1-i]
        out[f'T{i}'] = [(2+j, r.neg(r.one)), (i, y), (2+j, r.one), (i, r.sub(x, y))]
        if generated[demand] not in principal:
            continue
        if y == 0:
            out[f'S{i}'] = [(i, x)]
        elif y in principal[x]:
            t = next(t for t in r.elements if r.mul[t][x] == y)
            out[f'S{i}'] = [(2+j, r.neg(t)), (i, x), (2+j, t)]
        else:
            a, beta, t = witness(r, x, y, principal, generated[demand])
            out[f'S{i}'] = [(2+i, r.neg(a)), (2+j, r.neg(t)), (i, beta), (2+j, t), (2+i, a)]
    return {name: [(k, b) for k, b in word if b != 0] for name, word in out.items()}


def execute(r, word, state):
    # Literal scalar interpreter, separate from the graph transitions below.
    v = list(state)
    for kind, coefficient in word:
        i = kind % 2
        source = v[2] if kind < 2 else v[1-i]
        v[i] = r.add[v[i]][r.mul[coefficient][source]]
    return tuple(v)


def inverse(r, word):
    return [(k, r.neg(b)) for k, b in reversed(word)]


def endpoint(r, word, demand):
    for v in ((r.one, 0, 0), (0, r.one, 0), (0, 0, r.one)):
        target = (r.add[v[0]][r.mul[demand[0]][v[2]]],
                  r.add[v[1]][r.mul[demand[1]][v[2]]], v[2])
        if execute(r, word, v) != target or execute(r, inverse(r, word), target) != v:
            return False
    return True


def one_insertion_orbits(r, i):
    # Full elementary-column orbits, independent of ideal tests and witnesses.
    reached = set()
    for beta in range(1, r.n):
        root = (beta, 0) if i == 0 else (0, beta)
        orbit, queue = {root}, deque([root])
        while queue:
            x, y = queue.popleft()
            for a in range(1, r.n):
                for v in ((r.add[x][r.mul[a][y]], y), (x, r.add[y][r.mul[a][x]])):
                    if v not in orbit:
                        orbit.add(v)
                        queue.append(v)
        reached.update(orbit)
    return reached


def affine_graph(r):
    # State (a,b,u,c,d,v) encodes both dirt columns and the source column.
    # Only primitive gate transitions appear here, with no tariff pruning.
    start = (r.one, 0, 0, 0, r.one, 0)
    index, states, edges = {start: 0}, [start], []
    add, mul = r.add, r.mul
    for a, b, u, c, d, v in states:
        row = []
        for t in range(1, r.n):
            successors = (
                (a, b, add[u][t], c, d, v),
                (a, b, u, c, d, add[v][t]),
                (add[a][mul[t][c]], add[b][mul[t][d]], add[u][mul[t][v]], c, d, v),
                (a, b, u, add[c][mul[t][a]], add[d][mul[t][b]], add[v][mul[t][u]]),
            )
            for k, s in enumerate(successors):
                if s not in index:
                    index[s] = len(states)
                    states.append(s)
                row.append((k, index[s]))
        edges.append(tuple(row))
    # Independent full determinant-one inventory, including all translations.
    determinant_one = {(a, b, c, d) for a, b, c, d in product(r.elements, repeat=4)
                       if r.sub(mul[a][d], mul[b][c]) == r.one}
    require({(s[0], s[1], s[3], s[4]) for s in states} == determinant_one, 'dirt graph coverage')
    require(len(states) == len(determinant_one)*r.n**2, 'full affine graph coverage')
    targets = {(x, y): index[(r.one, 0, x, 0, r.one, y)]
               for x, y in product(r.elements, repeat=2)}
    return edges, targets


def shortest_paths(edges, prices):
    # Scale rational prices to integers; certify all-state distances afterwards.
    scale = lcm(*(Fraction(p).denominator for p in prices))
    weights = tuple(int(Fraction(p)*scale) for p in prices)
    require(min(weights) > 0, 'prices must be positive')
    dist, parent = [None]*len(edges), [None]*len(edges)
    dist[0] = 0
    queue = [(0, 0)]
    while queue:
        du, u = heappop(queue)
        if du != dist[u]:
            continue
        for k, v in edges[u]:
            dv = du+weights[k]
            if dist[v] is None or dv < dist[v]:
                dist[v], parent[v] = dv, (u, k)
                heappush(queue, (dv, v))
    require(all(x is not None for x in dist), 'unvisited reachable state')
    for u, row in enumerate(edges):
        for k, v in row:
            require(dist[v] <= dist[u]+weights[k], 'Bellman inequality')
        if u:
            p, k = parent[u]
            require((k, u) in edges[p] and dist[u] == dist[p]+weights[k], 'tight parent path')
    return dist, scale


def main():
    binary = residue(2)
    eight = square_zero(2, 2)
    cube = ring_product(ring_product(binary, binary), binary)
    rings = [residue(6), residue(18), square_zero(2, 1), field_four(), cube,
             eight, two_truncated_variables(), ring_product(eight, binary), square_zero(3, 2)]
    counts = dict(demands=0, orbit_comparisons=0, witnesses=0, words=0,
                  basis_forward_inverse=0, literal_forward_inverse=0,
                  dijkstra_runs=0, optimum_comparisons=0, controls=0)
    records = []
    for r in rings:
        check_ring(r)
        principal, generated = ideals(r)
        orbits = [one_insertion_orbits(r, i) for i in range(2)]
        nonprincipal = 0
        for demand, ideal in generated.items():
            is_principal = ideal in principal
            nonprincipal += not is_principal
            counts['demands'] += 1
            for i in range(2):
                expected = is_principal and demand != (0, 0)
                require((demand in orbits[i]) == expected, f'one-insertion criterion: {r.name} {demand}')
                counts['orbit_comparisons'] += 1
                if is_principal:
                    x, y = demand[i], demand[1-i]
                    a, beta, t = witness(r, x, y, principal, ideal)
                    require(r.mul[t][beta] == y and r.mul[r.add[r.one][r.mul[a][t]]][beta] == x,
                            'coefficient-selection identity')
                    require(principal[beta] == ideal, 'generator equality')
                    counts['witnesses'] += 1
            candidates = candidate_counts(demand, principal, generated)
            constructions = words(r, demand, principal, generated)
            require(candidates.keys() == constructions.keys(), 'candidate availability')
            for name, word in constructions.items():
                require(endpoint(r, word, demand), f'word or inverse: {r.name} {demand} {name}')
                actual = tuple(sum(k == i for k, _ in word) for i in range(4))
                require(all(a <= b for a, b in zip(actual, candidates[name])), 'attaining count bound')
                if name.startswith('S') and demand != (0, 0):
                    require(sum(k < 2 for k, _ in word) == 1, 'exactly one nonzero insertion')
                    require(actual == candidates[name], 'sharp single-insertion counts')
                counts['words'] += 1
                counts['basis_forward_inverse'] += 6
        records.append({'ring': r.name, 'order': r.n, 'nonprincipal_demands': nonprincipal})

    # Full graph tests on four distinct coefficient structures, every demand.
    common_prices = [(1, 1, 1, 1), (1, 9, 1, 1), (9, 1, 1, 1),
                     (5, 20, 1, 1), (20, 5, 1, 1), (100, 1000, 1, 1),
                     (Fraction(2, 3), Fraction(7, 5), Fraction(1, 7), Fraction(3, 11))]
    graph_records = []
    for r in (eight, residue(6), cube, field_four()):
        principal, generated = ideals(r)
        edges, targets = affine_graph(r)
        prices_to_check = list(common_prices)
        if r is eight:
            prices_to_check += list(product((1, 3), repeat=4))
            prices_to_check += [(1, 3, 1, 1), (3, 1, 1, 1), (7, 13, 2, 5), (13, 7, 5, 2)]
        prices_to_check = list(dict.fromkeys(prices_to_check))
        bills = {d: candidate_counts(d, principal, generated) for d in targets}
        for prices in prices_to_check:
            dist, scale = shortest_paths(edges, prices)
            counts['dijkstra_runs'] += 1
            for demand, target in targets.items():
                formula = min(price(v, prices) for v in bills[demand].values())
                require(dist[target] == formula*scale, f'tariff mismatch: {r.name} {demand} {prices}')
                counts['optimum_comparisons'] += 1
        graph_records.append({'ring': r.name, 'states': len(edges), 'prices': len(prices_to_check)})

    principal, generated = ideals(eight)
    demand = (2, 4)  # epsilon, eta
    require(generated[demand] == frozenset((0, 2, 4, 6)), 'eight-ring radical')
    require(generated[demand] not in principal, 'nonprincipal obstruction')
    counts['controls'] += 2
    core = words(eight, demand, principal, generated)
    require(set(core) == {'D', 'T0', 'T1'}, 'exclude spurious single-insertion candidates')
    counts['controls'] += 1
    for name, prices in zip(('D', 'T0', 'T1'), common_prices[:3]):
        costs = {k: price(v, prices) for k, v in candidate_counts(demand, principal, generated).items()}
        require(costs[name] < min(v for k, v in costs.items() if k != name), 'each envelope term necessary')
        counts['controls'] += 1
    require(min(price(v, (100, 1000, 1, 1)) for v in candidate_counts(demand, principal, generated).values()) == 202,
            'reject naive residue-ring extension predicting 104')
    counts['controls'] += 1
    for word in core.values():
        for state in product(eight.elements, repeat=3):
            result = execute(eight, word, state)
            target = (eight.add[state[0]][eight.mul[2][state[2]]],
                      eight.add[state[1]][eight.mul[4][state[2]]], state[2])
            require(result == target and execute(eight, inverse(eight, word), result) == state, 'literal dirt and inverse')
            counts['literal_forward_inverse'] += 2
    broken = core['T0'][1:]  # Source column remains correct; dirt does not.
    require(execute(eight, broken, (0, 0, 1)) == (2, 4, 1), 'dirt-only control premise')
    require(not endpoint(eight, broken, demand), 'reject missing dirt-return gate')
    counts['controls'] += 1
    require(not endpoint(eight, [(0, 2), (1, 6)], demand), 'reject wrong source coefficient')
    counts['controls'] += 1
    # Nonunit common generator and incomparable principal demands in a product ring.
    prod = ring_product(eight, binary)
    ps, gs = ideals(prod)
    pair = (2, 8)
    require(pair[1] not in ps[pair[0]] and pair[0] not in ps[pair[1]] and gs[pair] in ps,
            'incomparable principal product-ideal fixture')
    for i in range(2):
        _, beta, _ = witness(prod, pair[i], pair[1-i], ps, gs[pair])
        require(prod.one not in ps[beta] and beta != 0, 'nonunit insertion coefficient')
    counts['controls'] += 1
    # The zero-demand exception is tested by both complete column-orbit searches.
    require((0, 0) not in one_insertion_orbits(eight, 0), 'nonzero insertion cannot vanish')
    counts['controls'] += 1
    print(json.dumps({'fixtures': records, 'graphs': graph_records, 'counts': counts}, sort_keys=True))
    print('PASS_FINITE_COMMUTATIVE_FANOUT no_new_kappa')


if __name__ == '__main__':
    main()
