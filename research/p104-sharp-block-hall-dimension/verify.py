#!/usr/bin/env python3
"""Exact source, subspace-inequality and coordinate-witness checks.

Prepared for @CubeJerry with substantial OpenAI GPT-6 Astra Pro assistance.
No optimizer, numerical rank routine, or predecessor verifier is imported.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction
import gzip
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / 'research/p104-designer-toolkit-v2/words/5561.json.gz'
SOURCE_HASH = 'b3701d78bee3661382ebe5414e678dfc9ee292e254cb9dc56339c2d2f45fdf44'
I = frozenset((74, 81, 86, 91))
S = frozenset((62, 63, 69, 99, 67, 68, 95, 100, 101))
P = [61, 62, 63, 67, 68, 69, 95, 99, 100, 101]
OLD = I | S | {57}
NEW = I | set(P)
EXPECTED_PORTS = {57:296, 61:112, 62:176, 63:304, 67:224, 68:352,
                  69:416, 74:478, 81:477, 86:475, 91:471, 95:463,
                  99:415, 100:351, 101:223}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_ports(raw):
    require(hashlib.sha256(raw).hexdigest() == SOURCE_HASH, 'source SHA256')
    ports = json.loads(gzip.decompress(raw))['ports']
    require(len(ports) == 104 and len(set(ports)) == 104, '104 distinct ports')
    require(all(type(p) is int and 0 < p < 512 and p.bit_count() % 2 == 1
                for p in ports), 'odd nine-bit ports')
    require(all(ports[v] == p for v, p in EXPECTED_PORTS.items()), 'port index convention')
    return ports


def zero_relation(ports):
    return lambda u, v: u != v and (ports[u] & ports[v]).bit_count() % 2 == 0


class RankLedger:
    """Formal sum in f(A) and k; rank axioms are checked before use.

    Every inequality is oriented >= 0 and has nonnegative weight. Equalities
    may have signed weights. A zero identity is f(A+v)-f(A)-k = 0.
    Sets contain actual source port IDs, not subset-mask integer variables.
    """
    def __init__(self, vertices, zero):
        self.vertices = frozenset(vertices)
        self.zero_pair = zero
        self.coefficients = defaultdict(Fraction)
        self.k_coefficient = Fraction()
        self.rows = 0

    def term(self, vertices, coefficient):
        vertices = frozenset(vertices)
        require(vertices <= self.vertices, 'rank set outside universe')
        self.coefficients[vertices] += Fraction(coefficient)

    def monotonicity(self, smaller, larger, weight=1):
        weight = Fraction(weight)
        require(weight >= 0 and set(smaller) <= set(larger), 'monotonicity premise/sign')
        self.term(larger, weight)
        self.term(smaller, -weight)
        self.rows += 1

    def submodularity(self, first, second, weight=1):
        weight = Fraction(weight)
        require(weight >= 0, 'submodularity multiplier sign')
        first, second = frozenset(first), frozenset(second)
        self.term(first, weight)
        self.term(second, weight)
        self.term(first | second, -weight)
        self.term(first & second, -weight)
        self.rows += 1

    def zero_additivity(self, base, vertex, weight=1):
        base, weight = frozenset(base), Fraction(weight)
        require(vertex in self.vertices and vertex not in base, 'zero identity vertex')
        require(all(self.zero_pair(vertex, other) for other in base), 'false zero identity')
        self.term(base | {vertex}, weight)
        self.term(base, -weight)
        self.k_coefficient -= weight
        self.rows += 1

    def empty(self, weight=1):
        self.term((), weight)
        self.rows += 1

    def conclude(self, vertices, multiplier, k_bound):
        actual = {a: c for a, c in self.coefficients.items() if c}
        require(actual == {frozenset(vertices): Fraction(multiplier)},
                'rank coefficients do not cancel to stated target')
        require(self.k_coefficient == -k_bound, 'rank certificate k coefficient')
        return self.rows


def check_nine_core(zero):
    """Expand the short proof from PROOF.md, including every monotone step."""
    A = frozenset((62, 69, 99, 68, 100))
    B = frozenset((62, 99, 67, 95, 100))
    C = A | B
    E = frozenset((69, 67, 100))
    F = frozenset((62, 100))
    Q = frozenset((69, 99, 67, 68, 100))
    T = frozenset((62, 69, 67))
    ledger = RankLedger(S, zero)
    ledger.monotonicity(A | {63}, S)
    ledger.zero_additivity(A, 63)
    ledger.monotonicity(B | {101}, S)
    ledger.zero_additivity(B, 101)
    ledger.submodularity(A, B)
    require(A & B == F | {99}, 'short proof intersection')
    ledger.zero_additivity(F, 99)
    ledger.monotonicity(Q | {95}, C)
    ledger.zero_additivity(Q, 95)
    ledger.monotonicity(E | {68}, Q)
    ledger.zero_additivity(E, 68)
    ledger.submodularity(E, F)
    require(E & F == {100}, 'short proof final intersection')
    ledger.monotonicity(T, E | F)
    ledger.zero_additivity((), 62)
    ledger.zero_additivity({62}, 69)
    ledger.zero_additivity({62, 69}, 67)
    ledger.zero_additivity((), 100)
    ledger.empty(2)
    return ledger.conclude(S, 2, 9)


def check_petersen(certificate, zero):
    """Independently translate the lead's bitmask certificate to port sets."""
    require(certificate['vertices'] == P, 'Petersen vertex order')
    ledger = RankLedger(P, zero)
    def subset(mask):
        require(type(mask) is int and 0 <= mask < 2 ** len(P), 'subset mask')
        return frozenset(v for i, v in enumerate(P) if (mask >> i) & 1)
    def vertex(index):
        require(type(index) is int and 0 <= index < len(P), 'vertex index')
        return P[index]
    for descriptor, coefficient in certificate['ub']:
        require(len(descriptor) in (3, 4), 'inequality descriptor length')
        coefficient = -Fraction(coefficient)
        require(coefficient >= 0, 'inequality multiplier sign')
        base = subset(descriptor[1])
        v = vertex(descriptor[2])
        require(v not in base, 'inequality vertex in base')
        if descriptor[0] == 'mono':
            require(len(descriptor) == 3, 'monotonicity descriptor')
            ledger.monotonicity(base, base | {v}, coefficient)
        else:
            require(descriptor[0] == 'submod' and len(descriptor) == 4,
                    'submodularity descriptor')
            w = vertex(descriptor[3])
            require(w not in base and v != w, 'submodularity vertices')
            ledger.submodularity(base | {v}, base | {w}, coefficient)
    for descriptor, coefficient in certificate['eq']:
        if descriptor == ['empty']:
            ledger.empty(coefficient)
        else:
            require(len(descriptor) == 3 and descriptor[0] == 'zero', 'equality descriptor')
            ledger.zero_additivity(subset(descriptor[1]), vertex(descriptor[2]), coefficient)
    return ledger.conclude(P, 1, 5)


def check_petersen_graph(zero):
    # Standard outer pentagon / inner pentagram presentation, with five spokes.
    outer = [61, 69, 100, 62, 95]
    inner = [99, 101, 67, 68, 63]
    expected = set()
    for i in range(5):
        expected.add(frozenset((outer[i], outer[(i+1) % 5])))
        expected.add(frozenset((outer[i], inner[i])))
        expected.add(frozenset((inner[i], inner[(i+2) % 5])))
    actual = {frozenset((u,v)) for u,v in combinations(P, 2) if not zero(u,v)}
    require(actual == expected and len(expected) == 15, 'Petersen graph isomorphism')


def check_isolated_sum(core, zero):
    require(all(zero(i, j) for i, j in combinations(I, 2)), 'four mutually zero ports')
    require(all(zero(i, v) for i in I for v in core), 'isolate/core contact')
    ledger = RankLedger(set(core) | I, zero)
    previous = frozenset(core)
    for i in sorted(I):
        ledger.zero_additivity(previous, i)
        previous = previous | {i}
    require({a:c for a,c in ledger.coefficients.items() if c} ==
            {frozenset(core): Fraction(-1), frozenset(core) | I: Fraction(1)},
            'isolated-sum identity')
    require(ledger.k_coefficient == -4, 'isolated-sum constant')


OLD_ONE = [(74,), (81,), (86,), (91,57), (99,67), (69,100),
           (62,68), (63,95), (101,)]
OLD_TWO = [group for group in [(74,), (81,), (86,), (91,57), (99,67), (69,100)]
           for _ in range(2)] + [(62,68), (62,95), (63,95), (63,101), (68,101)]
NEW_ONE = [(74,), (81,), (86,), (91,), (61,69), (62,95), (63,101), (67,100), (68,99)]


def coordinates(groups, vertices):
    result = {v: [] for v in vertices}
    for coordinate, group in enumerate(groups):
        require(len(group) == len(set(group)), 'duplicate port in coordinate group')
        for v in group:
            require(v in result, 'coordinate uses unknown vertex')
            result[v].append(coordinate)
    return result, len(groups)


def direct_sum(parts, vertices):
    result = {v: [] for v in vertices}
    offset = 0
    for mapping, dimension in parts:
        require(set(mapping) == set(vertices), 'direct-sum coverage')
        for v in vertices:
            result[v].extend(offset + coordinate for coordinate in mapping[v])
        offset += dimension
    return result, offset


def check_coordinate_pairings(mapping, dimension, k, vertices, zero):
    require(set(mapping) == set(vertices), 'upper witness vertex coverage')
    for v in vertices:
        require(len(mapping[v]) == k, 'upper witness row count')
        require(all(type(c) is int and 0 <= c < dimension for c in mapping[v]),
                'upper witness coordinate outside dimension')
        diagonal = [[int(a == b) for b in mapping[v]] for a in mapping[v]]
        require(diagonal == [[int(i == j) for j in range(k)] for i in range(k)],
                'upper witness diagonal is not identity')
    for v, w in product(vertices, repeat=2):
        if zero(v, w):
            require(all(a != b for a in mapping[v] for b in mapping[w]),
                    'upper witness violates a forced zero')


def check_full_characteristic_two(ports):
    """Literal 9-bit rows; integer parity checks certify every Gram entry."""
    rows = [[(p >> bit) & 1 for bit in range(9)] for p in ports]
    for i, j in product(range(104), repeat=2):
        entry = sum(x*y for x, y in zip(rows[i], rows[j])) % 2
        expected = (ports[i] & ports[j]).bit_count() % 2
        require(entry == expected, 'binary Gram entry')
        require(i != j or entry == 1, 'binary diagonal')
    # Exact binary elimination is a consistency check, not the lower proof.
    basis = {}
    for value in ports:
        while value:
            bit = value.bit_length() - 1
            if bit in basis:
                value ^= basis[bit]
            else:
                basis[bit] = value
                break
    require(len(basis) == 9, 'binary port rank')


def rejects(call, label):
    try:
        call()
    except ValueError:
        return label
    raise ValueError('negative control was accepted: ' + label)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=SOURCE)
    args = parser.parse_args()
    raw = args.source.read_bytes()
    ports = source_ports(raw)
    zero = zero_relation(ports)
    cert = json.loads((HERE / 'petersen-dual.json').read_text())
    short_rows = check_nine_core(zero)
    petersen_rows = check_petersen(cert, zero)
    check_petersen_graph(zero)
    check_isolated_sum(S, zero)
    check_isolated_sum(P, zero)
    require([v for v in range(104) if all(zero(v, i) for i in I)] == P,
            'common forced-zero neighborhood')
    one, two, new = coordinates(OLD_ONE, OLD), coordinates(OLD_TWO, OLD), coordinates(NEW_ONE, NEW)
    for k in range(1, 13):
        q, r = divmod(k, 2)
        old_map, old_d = direct_sum([two] * q + [one] * r, OLD)
        require(old_d == (17*k + 1)//2, 'old dimension formula')
        check_coordinate_pairings(old_map, old_d, k, OLD, zero)
        new_map, new_d = direct_sum([new] * k, NEW)
        require(new_d == 9*k, 'new dimension formula')
        check_coordinate_pairings(new_map, new_d, k, NEW, zero)
    check_full_characteristic_two(ports)
    controls = []
    controls.append(rejects(lambda: source_ports(raw[:-1] + bytes((raw[-1] ^ 1,))), 'source-byte mutation'))
    controls.append(rejects(lambda: check_nine_core(lambda u,v: zero(u,v) and {u,v} != {62,63}),
                            'missing zero in short proof'))
    controls.append(rejects(lambda: check_nine_core(lambda u,v: u != v and not zero(u,v)),
                            'reversed parity convention'))
    bad = deepcopy(cert); bad['ub'][0][1] = '1/2'
    controls.append(rejects(lambda: check_petersen(bad, zero), 'reversed inequality multiplier'))
    bad = deepcopy(cert); bad['ub'].pop()
    controls.append(rejects(lambda: check_petersen(bad, zero), 'deleted inequality'))
    bad = deepcopy(cert); bad['eq'][-1][1] = '3/2'
    controls.append(rejects(lambda: check_petersen(bad, zero), 'altered equality multiplier'))
    bad = deepcopy(cert)
    row = next(row for row in bad['eq'] if row[0][0] == 'zero')
    v = P[row[0][2]]
    row[0][1] = 1 << next(j for j,w in enumerate(P) if w != v and not zero(v,w))
    controls.append(rejects(lambda: check_petersen(bad, zero), 'false zero premise'))
    bad_map = deepcopy(two[0]); bad_map[63][0] = bad_map[62][0]
    controls.append(rejects(lambda: check_coordinate_pairings(bad_map, 17, 2, OLD, zero),
                            'forced-zero collision in upper witness'))
    bad_map = {v: [c for c in cs if c != 16] for v,cs in two[0].items()}
    controls.append(rejects(lambda: check_coordinate_pairings(bad_map, 16, 2, OLD, zero),
                            'deleted seventeenth coordinate'))
    bad_map = deepcopy(two[0]); bad_map[62][1] = bad_map[62][0]
    controls.append(rejects(lambda: check_coordinate_pairings(bad_map, 17, 2, OLD, zero),
                            'singular diagonal in upper witness'))
    print(json.dumps({'source_sha256': SOURCE_HASH, 'short_proof_axiom_rows': short_rows,
                      'petersen_certificate_rows': petersen_rows,
                      'original_14_minimum_all_fields': 'ceil(17k/2)',
                      'replacement_14_minimum_all_fields': '9k',
                      'full_104_lower_all_fields': '9k',
                      'full_104_minimum_characteristic_two': '9k',
                      'coordinate_block_sizes_executed': list(range(1,13)),
                      'negative_controls_rejected': controls}, indent=2))
    print('PASS_P104_SHARP_BLOCK_HALL_DIMENSION')


if __name__ == '__main__':
    main()
