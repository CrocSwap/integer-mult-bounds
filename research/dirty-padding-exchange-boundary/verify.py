#!/usr/bin/env python3
"""Finite corroboration of PROOF.md. Apache-2.0.

Charles Bethin with substantial OpenAI Codex assistance. No predecessor code
is imported. Assertions are not admission checks.
"""
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


# Model 1: literal coordinates and full binary matrix rows. No ring or
# determinant filter appears in this exhaustive traversal.
def rectangle(shape):
    return list(itertools.product(*(range(q) for q in shape)))


def exchange(x):
    return x[0], x[3], x[2], x[1], x[4]


def literal_model(shape):
    true = rectangle(shape)
    padded = rectangle(tuple(1 << (q - 1).bit_length() for q in shape))
    ti = {x: i for i, x in enumerate(true)}
    pi = {x: i for i, x in enumerate(padded)}
    a = len(true)
    identity = tuple(1 << i for i in range(a + len(padded)))
    pairs = [(i, a + pi[x]) for i, x in enumerate(true)]

    def step(state, gate):
        out = list(state)
        if gate == 'p':
            for x, b in pairs:
                out[b] ^= state[x]
        elif gate == 'r':
            for x, b in pairs:
                out[x] ^= state[b]
        elif gate in ('e', 'masked'):
            for x, i in pi.items():
                if gate == 'e' or x in ti:
                    out[a + i] = state[a + pi[exchange(x)]]
        else:
            raise ValueError('unknown gate')
        return tuple(out)

    target = list(identity)
    for x, i in ti.items():
        target[i] = identity[ti[exchange(x)]]
    full_effect = list(target)
    for x, i in pi.items():
        if x not in ti:
            full_effect[a + i] = identity[a + pi[exchange(x)]]
    return identity, tuple(target), tuple(full_effect), step, true, padded


def literal_closure(shape):
    identity, target, dirty_effect, step, true, padded = literal_model(shape)
    seen = {identity}
    queue = [identity]
    edges = 0
    for state in queue:
        for gate in 'pre':
            nxt = step(state, gate)
            edges += 1
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
        require(len(seen) <= 10000, 'closure exceeded declared safety bound')
    word = identity
    for gate in 'prpeprp':
        word = step(word, gate)
    require(word == dirty_effect, 'seven-gate endpoint differs on a basis column')
    has_padding = len(true) != len(padded)
    require((target in seen) == (not has_padding), 'target reachability boundary')
    require((word == target) == (not has_padding), 'dirty restoration boundary')
    # Changed-alphabet positive control: exchange only the genuine cells of B.
    # This is explicitly forbidden in the theorem, and repairs the same word.
    masked = identity
    for gate in ['p', 'r', 'p', 'masked', 'p', 'r', 'p']:
        masked = step(masked, gate)
    require(masked == target, 'masked-exchange escape control')
    # |GL_2(F2[t]/((t+1)^2))| = |GL_2(F2)| * 2^4 = 96.
    # This predicted count does not constrain the traversal or seed its states.
    require(len(seen) == 96 and edges == 288, 'complete closure cardinality')
    fault = None
    if has_padding:
        for index in range(len(true), len(identity)):
            actual = tuple((row >> index) & 1 for row in word)
            wanted = tuple((row >> index) & 1 for row in target)
            if actual != wanted:
                require(actual[:len(true)] == wanted[:len(true)], 'fault touched useful output')
                fault = {'input_cell': list(padded[index - len(true)]),
                         'changed_cells': [list(padded[j - len(true)])
                                           for j in range(len(true), len(identity))
                                           if actual[j] != wanted[j]]}
                break
        require(fault is not None, 'missing dirty basis-column witness')
    return {'shape': list(shape), 'bits': len(identity), 'states': len(seen),
            'edges': edges, 'target_reachable': target in seen, 'fault': fault}


# Model 2: generic matrices over F2[C2]. No literal-coordinate traversal is
# reused. A ring element a+b*t is encoded as a+2*b.
def mul(a, b):
    return (((a & 1) & (b & 1)) ^ ((a >> 1) & (b >> 1))) | (
        (((a & 1) & (b >> 1)) ^ ((a >> 1) & (b & 1))) << 1)


def unit(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def product(a, b):
    n = len(a)
    out = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for z in range(n):
                out[i][j] ^= mul(a[i][z], b[z][j])
    return out


def determinant(matrix):
    # Leibniz works with zero divisors. Signs vanish in characteristic two.
    total = 0
    for perm in itertools.permutations(range(len(matrix))):
        term = 1
        for i, j in enumerate(perm):
            term = mul(term, matrix[i][j])
        total ^= term
    return total


def bank_generators(g, k):
    n = g + k
    result = []
    for target in range(n):
        for source in range(n):
            if target == source:
                continue
            a, c = unit(n), unit(k)
            a[target][source] = 1
            if target >= g and source >= g:
                c[target-g][source-g] = 1
            result.append((a, c, 0))
    for bank in range(k):
        a, c = unit(n), unit(k)
        a[g+bank][g+bank] = c[bank][bank] = 2
        result.append((a, c, 1))
    return result


def ring_checks():
    require(mul(2, 2) == 1 and 2 != 1, 'ring involution distinction')
    rng = random.Random(3)
    words = primitives = 0
    for g, k in [(1, 0), (1, 1), (2, 1), (2, 2), (2, 3), (2, 4)]:
        generators = bank_generators(g, k)
        for a, c, parity in generators:
            require(determinant(a) == determinant(c) == (2 if parity else 1),
                    'primitive determinant mismatch')
            primitives += 1
        target = unit(g+k)
        target[0][0] = 2
        require(determinant(target) == 2 and determinant(unit(k)) == 1,
                'target determinant distinction')
        for _ in range(32 if generators else 1):
            a, c, parity = unit(g+k), unit(k), 0
            for _ in range(64 if generators else 0):
                ga, gc, flip = rng.choice(generators)
                a, c, parity = product(ga, a), product(gc, c), parity ^ flip
            require(determinant(a) == determinant(c) == (2 if parity else 1),
                    'word determinant mismatch')
            words += 1
    require(determinant(unit(2)) != determinant([[2]]),
            'padding-only correction must break the invariant')
    return {'bank_pairs': 6, 'primitives': primitives, 'words': words,
            'max_word_length': 64, 'seed': 3}


def orbit_checks():
    # Enumerate actual orbits, without using the proof's two-case construction.
    checked = 0
    for p, q, gap, suffix in itertools.product(range(1, 6), range(2, 6), range(1, 6), range(1, 6)):
        shape = (p, q, gap, q, suffix)
        a = set(rectangle(shape))
        omega = set(rectangle(tuple(1 << (x-1).bit_length() for x in shape)))
        c = omega - a
        require(all(exchange(x) in a for x in a), 'A not invariant')
        require(all(exchange(x) in c for x in c), 'C not invariant')
        require(any(exchange(x) != x for x in a), 'missing genuine two-cycle')
        if c:
            require(any(exchange(x) != x for x in c), 'missing padded two-cycle')
        checked += 1
    return checked


def sources():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for entry in pins['files']:
        if entry['usage'] == 'input':
            digest = hashlib.sha256((ROOT / entry['path']).read_bytes()).hexdigest()
            require(digest == entry['sha256'], 'source pin changed: ' + entry['path'])


def main():
    sources()
    identity, target, _, step, _, _ = literal_model((3, 1, 1, 1, 1))
    require(identity == target == step(identity, 'e'), 'Q=1 identity exception')
    fixtures = [literal_closure(x) for x in [
        (1, 3, 1, 3, 1), (3, 2, 1, 2, 1), (1, 2, 3, 2, 1),
        (1, 2, 1, 2, 3), (1, 2, 1, 2, 1)]]
    report = {'literal_closures': fixtures, 'ring': ring_checks(),
              'shape_orbits_checked': orbit_checks(),
              'sys_version': sys.version, 'sys_executable': sys.executable}
    print(json.dumps(report, indent=2))
    print('PASS_DIRTY_PADDING_EXCHANGE_BOUNDARY')


if __name__ == '__main__':
    main()
