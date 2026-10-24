#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact finite checks for the A5 carrier; no predecessor program is imported."""
from collections import Counter
from hashlib import sha256
from itertools import product
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
IDENTITY = (1, 0, 0, 1)
X = (1, 1, 0, 1)
Y = (0, 2, 3, 1)
X_WORD = ((2, 0), (3, 1))
Y_WORD = ((0, 1), (1, 2), (2, 1), (3, 1), (0, 3), (3, 0))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(a, b):
    """F4=F2[w]/(w^2+w+1), with a+b*w encoded as a+2*b."""
    value = (a if b & 1 else 0) ^ (a << 1 if b & 2 else 0)
    return value ^ (7 if value & 4 else 0)


def matrix_product(a, b):
    return tuple(multiply(a[2*i], b[j]) ^ multiply(a[2*i+1], b[j+2])
                 for i in range(2) for j in range(2))


def determinant(a):
    return multiply(a[0], a[3]) ^ multiply(a[1], a[2])


def vector_action(a, value):
    u, v = value & 3, value >> 2
    return ((multiply(a[0], u) ^ multiply(a[1], v))
            | ((multiply(a[2], u) ^ multiply(a[3], v)) << 2))


def address_action(a, value, copies):
    return sum(vector_action(a, (value >> (4*j)) & 15) << (4*j)
               for j in range(copies))


def permutation_product(a, b):
    return tuple(a[b[j]] for j in range(5))


def identified_group():
    """Generate paired A5 permutations and matrices with a fixed 120-step cap."""
    start = (tuple(range(5)), IDENTITY)
    generators = (((1, 0, 3, 2, 4), X), ((2, 1, 4, 3, 0), Y))
    seen, queue = {start}, [start]
    for index in range(120):
        if index == len(queue):
            break
        p, a = queue[index]
        for q, b in generators:
            state = (permutation_product(q, p), matrix_product(b, a))
            if state not in seen:
                seen.add(state)
                queue.append(state)
        need(len(queue) <= 60, 'generator identification is inconsistent')
    need(len(queue) == 60, 'paired group must have order sixty')
    need(len({p for p, _ in queue}) == 60, 'permutation projection not injective')
    matrices = tuple(a for _, a in queue)
    all_sl2 = {a for a in product(range(4), repeat=4) if determinant(a) == 1}
    need(set(matrices) == all_sl2, 'matrix projection must equal SL2(F4)')
    return tuple(queue)


def cnot_action(value, word):
    for control, target in word:
        value ^= ((value >> control) & 1) << target
    return value


def cycles_of(permutation):
    need(sorted(permutation) == list(range(len(permutation))), 'not a permutation')
    seen, cycles = set(), []
    for start in range(len(permutation)):
        if start in seen:
            continue
        cycle, value = [], start
        for _ in range(len(permutation)):
            if value in seen:
                break
            seen.add(value)
            cycle.append(value)
            value = permutation[value]
        need(value == start, 'cycle did not close')
        cycles.append(tuple(cycle))
    return tuple(cycles)


def swap_word(permutation):
    swaps = tuple((cycle[0], value) for cycle in cycles_of(permutation)
                  for value in cycle[1:])
    # Symbolic rows carry every possible dirty data input, without a clean bit.
    rows = [1 << j for j in range(len(permutation))]
    for a, b in swaps:
        rows[a] ^= rows[b]
        rows[b] ^= rows[a]
        rows[a] ^= rows[b]
    need(all(rows[permutation[j]] == 1 << j for j in range(len(rows))),
         'XOR-swap program has the wrong complete endpoint')
    return len(swaps)


def orbit_inventory(matrices, copies):
    remaining = set(range(1 << (4*copies)))
    lengths = []
    for start in range(1 << (4*copies)):
        if start not in remaining:
            continue
        orbit = {address_action(a, start, copies) for a in matrices}
        need(orbit <= remaining, 'orbits overlap without coinciding')
        remaining.difference_update(orbit)
        lengths.append(len(orbit))
    need(not remaining, 'orbit inventory incomplete')
    return dict(sorted(Counter(lengths).items()))


def norm_column(matrices, start, copies):
    value = 0
    for a in matrices:
        value ^= 1 << address_action(a, start, copies)
    return value


def semantic_controls(matrices):
    count = 0
    # Every literal address CNOT matters, on both copies.
    for a, word in ((X, X_WORD), (Y, Y_WORD)):
        for omitted in range(len(word)):
            mutant = word[:omitted] + word[omitted+1:]
            need(any(cnot_action(z, mutant) != vector_action(a, z)
                     for z in range(16)), 'omitted CNOT escaped')
            count += 1
    need(matrix_product(X, Y) != matrix_product(Y, X), 'labels commute')
    count += 1
    # A group-faithful single copy still kills the nonzero formal norm element.
    need(all(norm_column(matrices, z, 1) == 0 for z in range(16)),
         'single-copy obstruction was lost')
    count += 1
    need(norm_column(matrices, 65, 2).bit_count() == 60,
         'regular orbit must detect the formal norm element')
    count += 1
    return count


def build_result():
    paired = identified_group()
    matrices = tuple(a for _, a in paired)
    # All multiplication pairs check the explicit isomorphism, not a word census.
    correspondence = dict(paired)
    for p, a in paired:
        for q, b in paired:
            need(correspondence[permutation_product(p, q)] == matrix_product(a, b),
                 'generator correspondence fails multiplication')
    need(len({tuple(vector_action(a, z) for z in range(16)) for a in matrices})
         == 60, 'single-copy group action not faithful')
    # Identity matrix has columns (1,0) and (0,1), encoded as 1+16*4=65.
    images = tuple(address_action(a, 65, 2) for a in matrices)
    need(len(set(images)) == 60, 'identity orbit must be regular')
    need({tuple((z >> (2*j)) & 3 for j in (0, 2, 1, 3)) for z in images}
         == set(matrices), 'regular orbit must be the determinant-one matrices')
    invoices = {}
    for name, a, word in (('x', X, X_WORD), ('y', Y, Y_WORD)):
        need(all(cnot_action(z, word) == vector_action(a, z) for z in range(16)),
             'four-bit address circuit incorrect')
        doubled = word + tuple((c+4, t+4) for c, t in word)
        permutation = tuple(address_action(a, z, 2) for z in range(256))
        need(all(cnot_action(z, doubled) == permutation[z] for z in range(256)),
             'eight-bit address circuit incorrect')
        swaps = swap_word(permutation)
        invoices[name] = {'address_cnots': len(doubled), 'data_swaps': swaps,
                          'data_xors': 3*swaps,
                          'cycle_lengths': dict(sorted(Counter(map(len, cycles_of(permutation))).items()))}
    return {'group_order': 60, 'multiplication_pairs': 3600,
            'single_copy_orbits': orbit_inventory(matrices, 1),
            'double_copy_orbits': orbit_inventory(matrices, 2),
            'regular_orbit_seed': 65, 'faithful_formal_basis_columns': len(images),
            'invoices': invoices, 'semantic_controls': semantic_controls(matrices)}


def source_hashes():
    return {name: sha256((HERE/name).read_bytes()).hexdigest() for name in
            ('README.md', 'TASK.json', 'SOURCES.json', 'VERIFY.json', 'verify.py', 'OVERLAP.json')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='explicitly regenerate RESULT.json')
    args = parser.parse_args()
    receipt = {'result': build_result(), 'source_sha256': source_hashes()}
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + '\n'
    if args.write:
        (HERE/'RESULT.json').write_text(encoded)
    else:
        need((HERE/'RESULT.json').read_text() == encoded, 'receipt mismatch; do not overwrite during replay')
    print('PASS_A5_EIGHT_BIT_CARRIER ' + json.dumps(receipt['result'], sort_keys=True))


if __name__ == '__main__':
    main()
