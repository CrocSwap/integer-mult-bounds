"""Faithful primitive-stream oracle; no formal projector products.

JoyboyBrian, with OpenAI Codex assistance; Apache-2.0.
"""
import importlib.util
import json
from pathlib import Path
import random


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_compiler():
    path = Path(__file__).with_name('verify.py')
    spec = importlib.util.spec_from_file_location('clean_compiler', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.authenticate()
    return module


def shift(value, addresses=2):
    mask = (1 << addresses) - 1
    return ((value << 1) & mask) | (value >> (addresses - 1))


def execute(word, state, addresses=2):
    tape = list(state)
    for gate in word:
        need(gate[0] in ('xor', 'reflect'), 'unknown primitive')
        if gate[0] == 'xor':
            _, dest, source = gate
            need(0 <= source < len(tape) and 0 <= dest < len(tape)
                 and dest != source, 'invalid scalar CNOT')
            tape[dest] ^= tape[source]
        else:
            _, role = gate
            need(0 <= role < len(tape), 'invalid reflection role')
            tape[role] = shift(tape[role], addresses)
    return tuple(tape)


def expected(matrix, state, clean_shift=False, addresses=2):
    output = list(state)
    for i, row in enumerate(matrix):
        for j in range(len(matrix)):
            if row >> j & 1:
                output[i] ^= state[j] ^ shift(state[j], addresses)
    if clean_shift:
        output[-1] = shift(state[-1], addresses)
    return tuple(output)


def basis_states(width, active=None, addresses=2):
    if active is None:
        active = width
    for role in range(active):
        for bit in range(addresses):
            state = [0] * width
            state[role] = 1 << bit
            yield tuple(state)


def check_literal(matrix, compiler):
    q, _, _, word, _ = compiler.compile_matrix(matrix)
    columns = 0
    for state in basis_states(len(matrix) + 1):
        need(execute(word, state) == expected(matrix, state, q > 0 and not q & 1),
             'literal full-input endpoint')
        columns += 1
    return columns


def small_and_conjugated(compiler):
    fixtures, columns = 0, 0
    for n in range(1, 5):
        for bits in range(1 << (n * n)):
            matrix = tuple((bits >> (n * i)) & ((1 << n) - 1) for i in range(n))
            # Independent scalar square-zero decision, rather than compiler.apply.
            if any(sum(((matrix[k] >> j) & 1) for k in range(n) if matrix[i] >> k & 1) & 1
                   for i in range(n) for j in range(n)):
                continue
            columns += check_literal(matrix, compiler)
            fixtures += 1
    random_columns = 0
    for q in range(1, 9):
        n = 2 * q + 2
        matrix = [(1 << (q + i)) if i < q else 0 for i in range(n)]
        rng = random.Random(2400 + q)
        for _ in range(4 * n):
            dest, source = rng.sample(range(n), 2)
            matrix[dest] ^= matrix[source]
            # Right multiplication by the same involutory elementary matrix.
            for i, row in enumerate(matrix):
                if row >> dest & 1:
                    matrix[i] ^= 1 << source
        columns += check_literal(tuple(matrix), compiler)
        _, _, _, word, _ = compiler.compile_matrix(tuple(matrix))
        for _ in range(20):
            state = tuple(rng.randrange(4) for _ in range(n)) + (0,)
            need(execute(word, state) == expected(tuple(matrix), state),
                 'literal dense dirty data / clean return')
            random_columns += 1
        fixtures += 1
    return {'fixtures': fixtures, 'faithful_input_basis_columns': columns,
            'dense_dirty_states': random_columns}


def independent_shortest():
    result = []
    for q in (1, 2):
        data, width = 2 * q, 2 * q + 1
        basis = list(basis_states(width, data))
        changes = set()
        for x in range(1, 1 << width):
            for y in range(1 << width):
                if (x & y).bit_count() % 2 != 1:
                    continue
                encoded = 0
                for col, state in enumerate(basis):
                    source = 0
                    for j in range(width):
                        if y >> j & 1:
                            source ^= state[j]
                    delta = source ^ shift(source)
                    for role in range(width):
                        if x >> role & 1:
                            encoded ^= delta << (2 * (role + width * col))
                changes.add(encoded)
        matrix = tuple((1 << (q + i)) if i < q else 0 for i in range(data))
        target = 0
        for col, state in enumerate(basis):
            output = expected(matrix, state)
            for role in range(width):
                target ^= (output[role] ^ state[role]) << (2 * (role + width * col))
        need(target not in changes, 'faithful single-call minimum')
        if q == 2:
            need(not any((target ^ delta) in changes for delta in changes),
                 'faithful two-call minimum')
        result.append({'rank': q, 'full_action_changes': len(changes),
                       'shorter_than': q + 1})
    return result


def omission_and_boundary_controls(compiler):
    omissions, all_dirty_failures, noninvolutory = 0, 0, 0
    for q in range(1, 9):
        data = 2 * q
        matrix = tuple((1 << (q + i)) if i < q else 0 for i in range(data))
        _, _, _, word, _ = compiler.compile_matrix(matrix)
        states = list(basis_states(data + 1, data))
        for index, gate in enumerate(word):
            if gate[0] != 'reflect':
                continue
            mutant = word[:index] + word[index + 1:]
            need(any(execute(mutant, state) != expected(matrix, state) for state in states),
                 'omitted paid reflection accepted')
            omissions += 1
        if not q & 1:
            helper = (0,) * data + (1,)
            need(execute(word, helper) != expected(matrix, helper),
                 'dirty helper falsely restored')
            all_dirty_failures += 1
            three_states = list(basis_states(data + 1, data, 3))
            need(any(execute(word, state, 3) != expected(matrix, state, addresses=3)
                     for state in three_states), 'noninvolution falsely admitted')
            noninvolutory += 1
            old = compiler.lower_projectors(compiler.canonical_projectors(q, data, False),
                                           data + 1)
            need(all(execute(old, state) == expected(matrix, state)
                     for state in basis_states(data + 1)), 'matched dirty baseline endpoint')
    return {'omitted_reflections_rejected': omissions,
            'dirty_ancilla_rejected': all_dirty_failures,
            'noninvolutory_labels_rejected': noninvolutory}


def main():
    compiler = load_compiler()
    report = small_and_conjugated(compiler)
    report['independent_shortest'] = independent_shortest()
    report['controls'] = omission_and_boundary_controls(compiler)
    print(json.dumps(report, sort_keys=True))
    print('PASS_CLEAN_SQUARE_ZERO_LITERAL scalar_cnots_and_address_swaps no_new_kappa')


if __name__ == '__main__':
    main()
