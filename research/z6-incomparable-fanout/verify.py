#!/usr/bin/env python3
"""Exact finite corroboration of the written residue-ring fanout theorem.

lee-phys, with substantial OpenAI Codex assistance. Apache-2.0.
The graph oracle uses only primitive transitions, not the tariff formula.
No third-party imports, repository access, file writes or assertions.
"""
from fractions import Fraction
from heapq import heappop, heappush
from itertools import product
from math import gcd
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def domain(n, demand):
    require(type(n) is int and n >= 2, "modulus must be an integer >= 2")
    require(isinstance(demand, tuple) and len(demand) == 2,
            "demand must be a pair")
    require(all(type(x) is int and 0 <= x < n for x in demand),
            "demands must be canonical residues")


def prices_ok(prices):
    require(isinstance(prices, tuple) and len(prices) == 4,
            "prices must be (mu0,mu1,c0,c1)")
    require(all(type(x) in (int, Fraction) and x > 0 for x in prices),
            "executable prices must be positive exact rationals")


def prime_divisors(n):
    result = []
    q = 2
    while q*q <= n:
        if n % q == 0:
            result.append(q)
            while n % q == 0:
                n //= q
        q += 1
    if n > 1:
        result.append(n)
    return result


def generator(n, x, y):
    """Return (a,beta,r) with beta=x-a*y, y=r*beta, via the CRT proof."""
    domain(n, (x, y))
    if x == y == 0:
        return 0, 0, 0
    g = gcd(x, y, n)
    reduced = n // g
    a, period = 0, 1
    for q in prime_divisors(reduced):
        residue = int((x // g) % q == 0)
        a += period * ((residue-a) * pow(period, -1, q) % q)
        period *= q
    beta = (x-a*y) % n
    r = (y // g) * pow(beta // g, -1, reduced) % reduced
    return a, beta, r


def terms(n, demand, prices):
    """Theorem 2: order D,T0,T1,S0,S1; no word construction is used."""
    domain(n, demand)
    prices_ok(prices)
    mu0, mu1, c0, c1 = prices
    result = [sum(prices[i] for i in (0, 1) if demand[i] != 0),
              2*mu0+2*c1, 2*mu1+2*c0]
    for i in (0, 1):
        j = 1-i
        x, y = demand[i], demand[j]
        value = prices[i]
        if y:
            value += 2*prices[2+j]
            if y % gcd(x, n):
                value += 2*prices[2+i]
        result.append(value)
    return tuple(result)


def words(n, demand):
    """Construct the five attaining options, removing zero gates."""
    domain(n, demand)

    def word(gates):
        return tuple((kind, row, k % n) for kind, row, k in gates if k % n)

    result = [word([('P', i, demand[i]) for i in (0, 1)])]
    for i in (0, 1):
        j = 1-i
        result.append(word([('E', j, -1), ('P', i, demand[j]),
                            ('E', j, 1), ('P', i, demand[i]-demand[j])]))
    for i in (0, 1):
        j = 1-i
        x, y = demand[i], demand[j]
        if y == 0:
            gates = [('P', i, x)]
        elif y % gcd(x, n) == 0:
            g = gcd(x, n)
            r = (y // g) * pow(x // g, -1, n // g) % (n // g)
            gates = [('E', j, -r), ('P', i, x), ('E', j, r)]
        else:
            a, beta, r = generator(n, x, y)
            gates = [('E', i, -a), ('E', j, -r), ('P', i, beta),
                     ('E', j, r), ('E', i, a)]
        result.append(word(gates))
    return tuple(result)


def execute(n, word, initial):
    """Literal row values, including the preserved source as coordinate 2."""
    state = list(initial)
    require(len(state) == 3 and
            all(type(x) is int and 0 <= x < n for x in state), "invalid state")
    for kind, row, k in word:
        require(kind in ('P', 'E') and type(row) is int and row in (0, 1)
                and type(k) is int and 0 < k < n, "invalid nonzero gate")
        source = 2 if kind == 'P' else 1-row
        state[row] = (state[row] + k*state[source]) % n
    return tuple(state)


def inverse(n, word):
    return tuple((kind, row, -k % n) for kind, row, k in reversed(word))


def counts(word):
    result = [0]*4
    for kind, row, _ in word:
        result[row + (2 if kind == 'E' else 0)] += 1
    return tuple(result)


def cost(word, prices):
    return sum(a*b for a, b in zip(counts(word), prices))


def endpoint(n, word, demand):
    for basis in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
        expected = ((basis[0]+demand[0]*basis[2]) % n,
                    (basis[1]+demand[1]*basis[2]) % n, basis[2])
        if execute(n, word, basis) != expected:
            return False
    return True


# Independent finite-state oracle. These transitions neither call execute()
# nor use generator(), words(), terms(), or any target-dependent pruning.
def graph(n):
    start = (1, 0, 0, 0, 1, 0)  # rows (a,b,u) and (c,d,v)
    states = [start]
    index = {start: 0}
    edges = []
    for a, b, u, c, d, v in states:
        outgoing = []
        for k in range(1, n):
            neighbors = (
                (a, b, (u+k) % n, c, d, v),
                (a, b, u, c, d, (v+k) % n),
                ((a+k*c) % n, (b+k*d) % n, (u+k*v) % n, c, d, v),
                (a, b, u, (c+k*a) % n, (d+k*b) % n, (v+k*u) % n),
            )
            for kind, neighbor in enumerate(neighbors):
                if neighbor not in index:
                    index[neighbor] = len(states)
                    states.append(neighbor)
                outgoing.append((index[neighbor], kind))
        edges.append(tuple(outgoing))
    # Count all possible determinant-one affine states independently. Since
    # every stored state is distinct and has determinant one, equality proves
    # complete coverage of this entire finite ambient space.
    matrices = sum((a*d-b*c) % n == 1
                   for a, b, c, d in product(range(n), repeat=4))
    require(len(states) == matrices*n*n, "incomplete affine graph")
    require(all((a*d-b*c) % n == 1 for a, b, _, c, d, _ in states),
            "graph contains a wrong dirt determinant")
    targets = {(x, y): index[(1, 0, x, 0, 1, y)]
               for x, y in product(range(n), repeat=2)}
    return edges, targets


def dijkstra(edges, prices):
    distances = [None]*len(edges)
    distances[0] = 0
    queue = [(0, 0)]
    while queue:
        distance, node = heappop(queue)
        if distance != distances[node]:
            continue
        for neighbor, kind in edges[node]:
            candidate = distance+prices[kind]
            old = distances[neighbor]
            if old is None or candidate < old:
                distances[neighbor] = candidate
                heappush(queue, (candidate, neighbor))
    require(all(x is not None for x in distances), "unreached affine state")
    # Bellman inequalities plus attained relaxation paths certify the returned
    # distances. All vertices are explored; no cutoff or formula upper bound.
    require(all(distances[v] <= distances[u]+prices[k]
                for u, row in enumerate(edges) for v, k in row),
            "shortest-path Bellman inequality failed")
    return distances


Z6_WORDS = (
    (('P', 0, 2), ('P', 1, 3)),
    (('E', 1, 5), ('P', 0, 3), ('E', 1, 1), ('P', 0, 5)),
    (('E', 0, 5), ('P', 1, 2), ('E', 0, 1), ('P', 1, 1)),
    (('E', 0, 5), ('E', 1, 3), ('P', 0, 5), ('E', 1, 3), ('E', 0, 1)),
    (('E', 1, 5), ('E', 0, 4), ('P', 1, 1), ('E', 0, 2), ('E', 1, 1)),
)
Z6_COUNTS = ((1, 1, 0, 0), (2, 0, 0, 2), (0, 2, 2, 0),
             (1, 0, 2, 2), (0, 1, 2, 2))
REGIMES = ((1, 1, 1, 1), (1, 9, 1, 1), (9, 1, 1, 1),
           (5, 20, 1, 1), (20, 5, 1, 1))


def rejects(function, *args):
    try:
        function(*args)
    except ValueError:
        return True
    return False


def main():
    evidence = {'claim': 'written all-n proof; bounded exact corroboration',
                'crt_pairs': 0, 'candidate_words': 0,
                'basis_forward_inverse_checks': 0, 'literal_z6_checks': 0,
                'dijkstra_runs': 0, 'optimum_comparisons': 0,
                'affine_states': {}, 'negative_controls': 0}
    check_prices = (Fraction(7, 3), Fraction(19, 2), Fraction(5, 7), 3)
    cases = [(n, (x, y)) for n in range(2, 25)
             for x, y in product(range(n), repeat=2)]
    cases += [(n, pair) for n in (60, 72, 210, 360)
              for pair in ((6, 9), (2, 3), (0, n//2), (n//2, n//3))]
    for n, demand in cases:
        for x, y in (demand, demand[::-1]):
            a, beta, r = generator(n, x, y)
            require((beta+a*y-x) % n == 0 and (r*beta-y) % n == 0
                    and ((1+a*r)*beta-x) % n == 0, "CRT identities failed")
            require(gcd(beta, n) == gcd(x, y, n), "wrong generated ideal")
            evidence['crt_pairs'] += 1
        candidates = words(n, demand)
        bounds = terms(n, demand, check_prices)
        bills = []
        for word, bound in zip(candidates, bounds):
            require(endpoint(n, word, demand), "wrong candidate endpoint")
            require(endpoint(n, inverse(n, word), tuple(-x % n for x in demand)),
                    "wrong inverse endpoint")
            bills.append(cost(word, check_prices))
            require(bills[-1] <= bound, "candidate exceeds its claimed term")
            evidence['candidate_words'] += 1
            evidence['basis_forward_inverse_checks'] += 6
        require(min(bills) == min(bounds), "construction misses envelope")
    for word, vector in zip(Z6_WORDS, Z6_COUNTS):
        require(counts(word) == vector, "wrong displayed Z6 gate counts")
        require(endpoint(6, word, (2, 3)), "wrong displayed Z6 word")
        for initial in product(range(6), repeat=3):
            final = execute(6, word, initial)
            expected = ((initial[0]+2*initial[2]) % 6,
                        (initial[1]+3*initial[2]) % 6, initial[2])
            require(final == expected, "literal dirty/source value failed")
            require(execute(6, inverse(6, word), final) == initial,
                    "literal inverse did not restore inputs")
            evidence['literal_z6_checks'] += 2
    for winner, prices in enumerate(REGIMES):
        values = terms(6, (2, 3), prices)
        require(values[winner] < min(v for i, v in enumerate(values) if i != winner),
                "a displayed term is not uniquely necessary")
        evidence['negative_controls'] += 1  # removing this term changes optimum
    require(terms(6, (2, 3), (2, 100, 1, 1))[1] ==
            terms(6, (2, 3), (2, 100, 1, 1))[3] == 6, "missing price tie")
    require(min(terms(6, (2, 3), (100, 1000, 1, 1))) == 104,
            "wrong one-insertion discriminator")
    require(min(terms(6, (2, 3), (1, 9, 1, 1))) == 4,
            "invalid unit-demand shortcut was not excluded")
    evidence['negative_controls'] += 1
    # Removing the initial E_i leaves the source column unchanged but corrupts
    # the original dirt. This specifically tests the arbitrary-dirty contract.
    missing_return = Z6_WORDS[3][1:]
    require(execute(6, missing_return, (0, 0, 1)) == (2, 3, 1),
            "missing-return control must keep the source demand correct")
    require(not endpoint(6, missing_return, (2, 3)), "missing dirt-return accepted")
    wrong_source = Z6_WORDS[3][:2] + (('P', 0, 2),) + Z6_WORDS[3][3:]
    require(not endpoint(6, wrong_source, (2, 3)), "wrong coefficient accepted")
    evidence['negative_controls'] += 2
    invalid = [(domain, (1, (0, 0))), (domain, (6, (2, 6))),
               (domain, (True, (0, 0))), (domain, (6, (True, 3))),
               (prices_ok, ((0, 1, 1, 1),)), (prices_ok, ((True, 1, 1, 1),)),
               (prices_ok, ((1.0, 1, 1, 1),)), (prices_ok, ((1, 1, 1),))]
    for function, args in invalid:
        require(rejects(function, *args), "invalid domain accepted")
        evidence['negative_controls'] += 1
    for n in range(2, 7):
        edges, targets = graph(n)
        evidence['affine_states'][str(n)] = len(edges)
        vectors = list(REGIMES) + [(2, 100, 1, 1), check_prices]
        if n == 6:
            vectors += list(product((1, 2, 3), repeat=4))
            vectors += [(100, 1000, 1, 1), (1000, 100, 1, 1),
                        (3, 17, 29, 1), (17, 3, 1, 29)]
        vectors = list(dict.fromkeys(vectors))
        for prices in vectors:
            distances = dijkstra(edges, prices)
            evidence['dijkstra_runs'] += 1
            for demand, index in targets.items():
                optimum = min(terms(n, demand, prices))
                require(distances[index] == optimum,
                        f"oracle mismatch n={n}, demand={demand}, prices={prices}")
                require(min(cost(w, prices) for w in words(n, demand)) == optimum,
                        "oracle comparison has no matching witness")
                evidence['optimum_comparisons'] += 1
    print('PASS_RESIDUE_FANOUT ' + json.dumps(evidence, sort_keys=True))


if __name__ == '__main__':
    main()
