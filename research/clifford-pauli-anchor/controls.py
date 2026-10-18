#!/usr/bin/env python3
"""Independent matrix checks of every signed Pauli image and anchor.
Tekalign / OpenAI Codex, Apache-2.0. Oracle: Sagar Thakrar's packed kernel.
"""
import json
from pathlib import Path
import random
import types

PACKAGE = Path(__file__).resolve().parent


def load(path, name):
    m = types.ModuleType(name)
    m.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), m.__dict__)
    return m


def check():
    R = load(PACKAGE / 'replay.py', 'source_replay')
    E = load(PACKAGE / 'engine.py', 'anchor_controls_engine')
    raw = R.capture()[R.KERNEL]
    C = R.module(raw, 'packed_oracle', R.KERNEL)
    rng = random.Random(86)
    circuits = paulis = matrix_columns = comparisons = 0
    for n in range(1, 5):
        C.N_AXES, C.DIM = n, 1 << n
        for _ in range(24):
            word = []
            for _ in range(12):
                kind = rng.choice(('P', 'D', 'C', 'X', 'PH'))
                if kind == 'P':
                    rows = [1 << j for j in range(n)]
                    if n > 1:
                        for _ in range(2 * n):
                            a, b = rng.sample(range(n), 2)
                            rows[a] ^= rows[b]
                    g = (kind, rows)
                elif kind == 'D':
                    g = (kind, [rng.randrange(1 << n) for _ in range(n)], [rng.randrange(4) for _ in range(n)])
                elif kind == 'C':
                    g = (kind, rng.randrange(1, 1 << n), rng.choice((-1, 1)))
                else:
                    g = (kind, rng.randrange(4 if kind == 'PH' else 1 << n))
                word.append(g)
            frozen = E.freeze(word, n)
            k = C.c_gates(word)
            cols = C.columns(C.run(word, C.radix(k)), C.radix(k))
            state, denominator = E.anchor(frozen, n)
            R.need(state == cols.get(0, {}) and denominator == k, 'anchor/full-matrix disagreement')
            for index, (p, x, z) in enumerate(E.pauli_action(frozen, n)):
                x0, z0 = (1 << index, 0) if index < n else (0, 1 << (index - n))
                for column in range(1 << n):
                    # Check U P = image(P) U directly on EVERY input column.
                    left = {y: E.rotate(v, 2 * ((column & z0).bit_count() % 2))
                            for y, v in cols[column ^ x0].items()}
                    right = {y ^ x: E.rotate(v, p + 2 * ((y & z).bit_count() % 2))
                             for y, v in cols[column].items()}
                    R.need(left == right, 'signed Pauli image disagrees with full matrix')
                    matrix_columns += 1
                paulis += 1
            before = json.dumps(word)
            for other in (word, word + C.adjoint(word), [], word + [('PH', 1)], word + [('X', 1)]):
                R.need(E.same_operator(word, other, n) == C.same_operator(word, other), 'differential comparator')
                comparisons += 1
            R.need(json.dumps(word) == before, 'input mutation')
            circuits += 1
    identity = E.freeze([], 2)
    phase = E.freeze([('PH', 1)], 2)
    character = E.freeze([('D', [0, 0], [2, 0])], 2)
    R.need(E.pauli_action(identity, 2) == E.pauli_action(phase, 2) and
           not E.same_operator([], [('PH', 1)], 2), 'Pauli-only phase blindness control')
    R.need(E.anchor(identity, 2) == E.anchor(character, 2) and
           not E.same_operator([], [('D', [0, 0], [2, 0])], 2), 'zero-column-only blindness control')
    bad = [('T', 0), ('C', 0, 1), ('C', 1, 0), ('PH', True), ('X', 4),
           ('P', [1, 1]), ('D', [0, 0], [0, 4]), ('PH', 1, 2)]
    for gate in bad:
        try:
            E.same_operator([('X', 1), gate], [], 2)
        except ValueError:
            pass
        else:
            raise ValueError('invalid gate accepted: ' + repr(gate))
    # Cache keys include full immutable operands; caller mutation cannot reuse an old gate.
    mutable = [('D', [0, 0], [0, 0])]
    R.need(E.same_operator(mutable, [], 2), 'cache positive')
    mutable[0][2][0] = 2
    R.need(not E.same_operator(mutable, [], 2), 'cache operand mutation')
    R.need(E.tables.cache_info().currsize <= 64, 'bounded gate cache')
    return {'seed': 86, 'circuits': circuits, 'signed_pauli_images': paulis,
            'matrix_column_relations': matrix_columns, 'differential_comparisons': comparisons,
            'invalid_gates_rejected': len(bad), 'phase_only_and_column_only_blindness_controls': 2,
            'cache_operand_mutation_rejected': True}


if __name__ == '__main__':
    print(json.dumps(check(), sort_keys=True))
