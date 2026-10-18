#!/usr/bin/env python3
"""Exhaust the fixed binary connector interface. Apache-2.0; see NOTICE.md."""
from collections import Counter, deque
import json
from pathlib import Path

SEED = 51
DIM = 2 + SEED % 2
ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def product(factors, source, target, scratch):
    """Literal binary commutator lowering, factors in application order."""
    need(bool(factors), 'empty product')
    need(len(scratch) >= (len(factors)-1).bit_length(), 'insufficient scratch')
    need(len(set([source, target, *scratch])) == 2+len(scratch), 'aliased roles')
    if len(factors) == 1:
        return [[factors[0], source, target]]
    middle = len(factors)//2
    right = product(factors[:middle], source, scratch[0], scratch[1:])
    left = product(factors[middle:], scratch[0], target, scratch[1:])
    # Each binary additive shear is its own inverse; reverse the whole word.
    return right + left + right[::-1] + left[::-1]


def build():
    n = DIM
    size = 1 << (2*n+n*n)
    distance = [-1]*size
    parent = [None]*size
    distance[0] = 0
    queue = deque([0])
    order = list(range(2*n))
    offset = SEED % (2*n)
    order = order[offset:] + order[:offset]
    edges = 0
    while queue:
        state = queue.popleft()
        z = state & ((1 << n)-1)
        for op in order:
            if op < n:
                nxt = state ^ (1 << op)
            else:
                nxt = state ^ (1 << op) ^ (z << (2*n+n*(op-n)))
            edges += 1
            if distance[nxt] < 0:
                distance[nxt] = distance[state]+1
                parent[nxt] = (state, op)
                queue.append(nxt)
    witnesses = {}
    for mask in range(1 << (n*n)):
        node = mask << (2*n)
        word = []
        while node:
            node, op = parent[node]
            word.append(op)
        witnesses[str(mask)] = ''.join(map(str, reversed(word)))
    cycle = 3 + (6 << 3) + (5 << 6)
    factors, next_factor = [], 0
    for length in range(1, 7):
        factors.append(list(range(next_factor, next_factor+length)))
        next_factor += length
    leaves = []
    for char in witnesses[str(cycle)]:
        op = int(char)
        source, target = (op, 6) if op < 3 else (6, op)
        leaves.extend(product(factors[op], source, target, [7, 8, 9]))
    return {
        'format': 'binary-connector-walk-v1',
        'seed': SEED,
        'dimension': n,
        'base_commit': '91a2094f2e022930069e8cfdc810a3ea1b81cd09',
        'search': {'states': size, 'reached': sum(d >= 0 for d in distance),
                   'directed_edges': edges, 'maximum_distance': max(distance),
                   'generator_order': order, 'stopping_rule': 'queue exhausted'},
        'witnesses': witnesses,
        'cycle': {'mask': cycle, 'word': witnesses[str(cycle)],
                  'factor_lists_in_application_order': factors,
                  'lowered_word': leaves,
                  'lowered_factor_multiplicities': dict(sorted(Counter(
                      str(f) for f, _, _ in leaves).items())),
                  'data_arrays': 10, 'dirty_arrays': 4},
    }


if __name__ == '__main__':
    path = ROOT/'CERTIFICATE.json'
    path.write_text(json.dumps(build(), indent=2, sort_keys=True)+'\n')
    print('WROTE_BINARY_CONNECTOR_CERTIFICATE states=32768 targets=512')
