#!/usr/bin/env python3
"""Exact cycle-fanout certificate, without predecessor executable imports."""
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

IDENTITY = 1 | (2 << 4) | (4 << 8)
SOURCE_BITS = (8, 128, 2048)
CYCLE = ((1, 0), (2, 1), (0, 2))
TARGET = (2, 4, 14)
MAX_LAYER = 200_000


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def multiply(a, b):
    require(0 <= a < 16 and 0 <= b < 16, 'ring element outside R16')
    return (a & 1) * b ^ (b & 1) * (a & 14)


def independent(demand):
    basis = ()
    for value in demand:
        if value == 0 or value & 1:
            return False
        basis = extend(basis, value)
    return len(basis) == 3


def extend(basis, vector):
    for pivot in basis:
        vector = min(vector, vector ^ pivot)
    if not vector:
        return basis
    high = 1 << (vector.bit_length() - 1)
    result = [x ^ vector if x & high else x for x in basis]
    return tuple(sorted(result + [vector], reverse=True))


def contains(basis, vector):
    for pivot in basis:
        vector = min(vector, vector ^ pivot)
    return vector == 0


def row_add(matrix, receiver, sender):
    return matrix ^ (((matrix >> (4 * sender)) & 15) << (4 * receiver))


def symbolic_step(state, basis, gate):
    kind, receiver, sender, residue = gate
    if kind == 'E':
        generator = ((state >> (4 * sender)) & 15) << (4 * receiver)
        if residue:
            state = row_add(state, receiver, sender)
            changed = ()
            for vector in basis:
                changed = extend(changed, row_add(vector, receiver, sender))
            basis = changed
    else:
        generator = SOURCE_BITS[receiver]
        state ^= residue * generator
    return state, extend(basis, generator)


def symbolic_solution(sequence):
    state, basis = IDENTITY, ()
    for gate in sequence:
        state, basis = symbolic_step(state, basis, gate)
    return state == IDENTITY and all(contains(basis, x) for x in SOURCE_BITS)


def exclude_five():
    """Every residue skeleton with <=5 ADDs and exactly two unit insertions."""
    additions = tuple(('E', a, b, u) for a, b in CYCLE for u in (0, 1))
    insertions = tuple(('P', a, -1, 1) for a in range(3))
    layer = {(IDENTITY, (), 0, 0)}
    sizes, finals, transitions = [1], 0, 0
    for _depth in range(7):
        following = set()
        for state, basis, inserted, added in layer:
            moves = (additions if added < 5 else ())
            moves += insertions if inserted < 2 else ()
            for gate in moves:
                ns, nb = symbolic_step(state, basis, gate)
                ni = inserted + (gate[0] == 'P')
                na = added + (gate[0] == 'E')
                transitions += 1
                if ni == 2 and ns == IDENTITY:
                    finals += 1
                    require(not all(contains(nb, x) for x in SOURCE_BITS),
                            'two-insertion five-ADD counterexample')
                key = (ns, nb, ni, na)
                require(key in following or len(following) < MAX_LAYER,
                        'exhaustion, no certificate')
                following.add(key)
        layer = following
        sizes.append(len(layer))
    return {'layer_sizes': sizes, 'transitions': transitions,
            'closing_transitions': finals}


def word(demand, root):
    require(independent(demand) and root in range(3), 'invalid demand or root')
    i, j, k = root, (root + 1) % 3, (root + 2) % 3
    q = [('E', j, i, 1 ^ demand[j]), ('E', k, j, demand[k]),
         ('E', j, i, 1)]
    return [('P', i, -1, 1 ^ demand[i])] + q + [('P', i, -1, 1)] + q


def matrix(word_gates):
    require(len(word_gates) <= 8, 'word exceeds eight gates')
    rows = [[int(i == j) for j in range(4)] for i in range(3)]
    for kind, a, b, coefficient in word_gates:
        require(0 < coefficient < 16, 'zero or invalid coefficient')
        require(a in range(3), 'invalid receiver')
        if kind == 'P':
            rows[a][3] ^= coefficient
        else:
            require(kind == 'E' and (a, b) in CYCLE, 'noncycle ADD')
            rows[a] = [x ^ multiply(coefficient, y)
                       for x, y in zip(rows[a], rows[b], strict=True)]
    return rows


def target(demand):
    return [[int(i == j) for j in range(3)] + [demand[i]] for i in range(3)]


def scalar_run(gates, values):
    rows, source = list(values[:3]), values[3]
    for kind, a, b, coefficient in gates:
        rows[a] ^= multiply(coefficient, source if kind == 'P' else rows[b])
    return tuple(rows) + (source,)


def check_words():
    demands = [d for d in product(range(0, 16, 2), repeat=3) if independent(d)]
    checked = 0
    for demand in demands:
        for root in range(3):
            gates = word(demand, root)
            require(matrix(gates) == target(demand), 'forward matrix')
            require(matrix(gates[::-1]) == target(demand), 'inverse matrix')
            require(sum(g[0] == 'P' for g in gates) == 2, 'insertion count')
            require(sum(g[0] == 'E' for g in gates) == 6, 'ADD count')
            sequence = [(t, a, b, c & 1) for t, a, b, c in gates]
            require(symbolic_solution(sequence), 'positive symbolic control')
            checked += 1
    require(len(demands) == 168 and checked == 504, 'demand enumeration')
    return checked


def check_scalars():
    checked = 0
    for root in range(3):
        gates = word(TARGET, root)
        for values in product(range(16), repeat=4):
            expected = tuple(values[i] ^ multiply(TARGET[i], values[3])
                             for i in range(3)) + (values[3],)
            actual = scalar_run(gates, values)
            require(actual == expected, 'literal forward input')
            require(scalar_run(gates[::-1], actual) == values, 'literal inverse')
            checked += 2
    return checked


def check_controls():
    gates = word(TARGET, 0)
    mutations = [gates[:i] + gates[i + 1:] for i in range(8)]
    changed = list(gates)
    changed[2] = ('E', 2, 1, 2)
    mutations.append(changed)
    changed = list(gates)
    changed[0] = ('P', 0, -1, 2)
    mutations.append(changed)
    for altered in mutations:
        require(matrix(altered) != target(TARGET), 'mutant escaped')
    require(not independent((2, 4, 6)), 'dependent demand accepted')
    require(not independent((3, 4, 14)), 'unit demand accepted')
    require(not symbolic_solution([('P', 0, -1, 1)]), 'open residue accepted')
    require(not symbolic_solution([]), 'empty basis accepted')
    for gates_bad in ([('E', 0, 1, 1)], [('P', 0, -1, 0)]):
        try:
            matrix(gates_bad)
        except RuntimeError:
            continue
        raise RuntimeError('invalid gate accepted')
    return len(mutations) + 6


def check_prices():
    checked = 0
    for c in (1, 2, 5):
        for extra in (0, 1, 17):
            prices = (6 * c + extra, 9 * c + extra, 11 * c + extra)
            optimum = 2 * min(prices) + 6 * c
            require(3 * min(prices) >= optimum, 'three-insertion price gate')
            require(2 * min(prices) + 6 * c == optimum, 'reverse-edge price gate')
            for root in range(3):
                cost = sum(prices[a] if kind == 'P' else c
                           for kind, a, _b, _x in word(TARGET, root))
                require(cost == 2 * prices[root] + 6 * c, 'complete word bill')
            checked += 1
    example = sum(100 if kind == 'P' else 1
                  for kind, _a, _b, _x in word(TARGET, 0))
    require(example == 206 and min(300, 200 + 4) == 204, 'displayed prices')
    return checked + 1


def main():
    # R16 multiplication independently checked against the monomial definition.
    for a, b in product(range(16), repeat=2):
        expanded = ((a & 1) & (b & 1))
        for bit in (2, 4, 8):
            expanded ^= (a & 1) * (b & bit) ^ (b & 1) * (a & bit)
        require(multiply(a, b) == expanded, 'ring multiplication')
    evidence = {'exclusion': exclude_five(), 'words': check_words(),
                'literal_forward_inverse': check_scalars(),
                'controls': check_controls(), 'price_fixtures': check_prices()}
    package = Path(__file__).resolve().parent
    hashes = {}
    for name in ('README.md', 'PROOF.md', 'TASK.json', 'SOURCES.json',
                 'VERIFY.json', 'verify.py'):
        path = package / name
        require(path.stat().st_size <= 1_048_576, 'package-file size bound')
        data = path.read_bytes()
        hashes[name] = sha256(data).hexdigest()
    print(json.dumps({'result': 'PASS_R16_INDEPENDENT_CYCLE_TARIFF',
                      'evidence': evidence, 'sha256': hashes}, sort_keys=True))


if __name__ == '__main__':
    main()
