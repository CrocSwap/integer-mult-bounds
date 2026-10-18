#!/usr/bin/env python3
"""Separately implemented symbolic/cost AI audit; not human or formal review.

Apache-2.0.  Only the candidate compiler is imported from backend.py.  This
checker does not import verify.py or use the candidate execution/invoice code.
The symbolic columns represent arbitrary integer input scalars; the routing
temporary has a zero input row and is not admitted as dirty workspace.
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def _require(ok, message):
    if not ok:
        raise ValueError(message)


def _candidate():
    spec = importlib.util.spec_from_file_location(
        'reader_restoration_candidate', HERE / 'backend.py')
    _require(spec is not None and spec.loader is not None,
             'candidate compiler unavailable')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _replay(program, initial):
    """Replay shears on coefficient rows, independently deriving all charges."""
    state = [row[:] for row in initial]
    columns = len(state[0])
    zero = [0] * columns
    accumulator = zero[:]
    invoice = dict(add_instructions=0, scalar_additions=0, source_reads=0,
                   target_reads=0, target_writes=0, tape_word_travel=0)
    peaks = dict(workspace=0, outputs=0, temporary=0, sources=0, accumulator=0)

    def observe():
        # Only the twenty-port wrapper uses this fixture-specific partition.
        if len(state) == 20:
            for kind, indices in [('workspace', range(8)), ('outputs', range(8, 11)),
                                  ('temporary', [11]), ('sources', range(12, 20))]:
                peaks[kind] = max(peaks[kind],
                                  max(sum(map(abs, state[i])) for i in indices))
        peaks['accumulator'] = max(peaks['accumulator'], sum(map(abs, accumulator)))

    observe()
    for instruction in program:
        _require(isinstance(instruction, (tuple, list)) and len(instruction) == 4,
                 'malformed candidate instruction')
        op, destination, source, sign = instruction
        _require(op == 'add', 'unexpected candidate opcode')
        _require(all(type(v) is int for v in (destination, source, sign)),
                 'candidate ports and sign must be integers')
        _require(0 <= destination < len(state) and 0 <= source < len(state),
                 'candidate port out of bounds')
        _require(destination != source and sign in (-1, 1),
                 'invalid or aliased candidate shear')
        # Explicitly model the clean register as a symbolic row as well.
        accumulator = [a + b for a, b in zip(accumulator, state[source])]
        observe()
        state[destination] = [a + sign * b
                              for a, b in zip(state[destination], accumulator)]
        observe()
        accumulator = [a - b for a, b in zip(accumulator, state[source])]
        _require(accumulator == zero, 'symbolic source register not restored')
        observe()
        invoice['add_instructions'] += 1
        invoice['scalar_additions'] += 3
        invoice['source_reads'] += 2
        invoice['target_reads'] += 1
        invoice['target_writes'] += 1
        # Closed-form walk 0 -> source -> destination -> source -> 0;
        # this intentionally does not call the candidate head interpreter.
        invoice['tape_word_travel'] += 2 * source + 2 * abs(destination - source)
    return state, invoice, peaks


def check():
    candidate = _candidate()
    permutation_cases = 0
    for n in range(1, 7):
        basis = [[int(i == j) for j in range(n)] for i in range(n)]
        for permutation in itertools.permutations(range(n)):
            pack = candidate.compile_batch([permutation], [[0] * n], eager=True)
            forwards = [segment for segment in pack['segments']
                        if segment['kind'] == 'forward']
            _require(len(forwards) == 1, 'unexpected forward segment count')
            segment = forwards[0]
            actual, _, _ = _replay(
                pack['program'][segment['start']:segment['stop']],
                basis + [[0] * n, [0] * n])
            expected = [basis[index][:] for index in permutation] + [[0] * n, [0] * n]
            _require(actual == expected, 'candidate gather permutation is incorrect')
            permutation_cases += 1
    _require(permutation_cases == 873, 'incomplete permutation census')

    # Fixed literals, intentionally recreated without importing the verifier.
    permutations = [[1, 0, 3, 2, 5, 4, 7, 6],
                    [3, 0, 1, 2, 7, 4, 5, 6],
                    [4, 5, 6, 7, 0, 1, 2, 3]]
    readers = [[1, 0, 0, 0, 0, 0, 0, 0],
               [1, 1, 0, 0, 0, 0, 0, 0],
               [1, 0, 1, 0, 0, 0, 0, 0]]
    pre_reads = [('add', 8 + i, j, -coefficient)
                 for i, row in enumerate(readers)
                 for j, coefficient in enumerate(row) if coefficient]
    load = [('add', j, 12 + k, 1) for j in range(8)
            for k in (j, (j + 1) % 8)]
    unload = [(op, destination, source, -sign)
              for op, destination, source, sign in reversed(load)]
    initial = [[int(i == j and i != 11) for j in range(20)] for i in range(20)]
    expected = [row[:] for row in initial]
    # Construct y_i += H_i Bx directly; no permutation/compiler result enters
    # the expected map, so both programs must independently meet the contract.
    for i, row in enumerate(readers):
        for j, coefficient in enumerate(row):
            expected[8 + i][12 + j] += coefficient
            expected[8 + i][12 + (j + 1) % 8] += coefficient
    expected_peaks = dict(workspace=3, outputs=5, temporary=3, sources=1, accumulator=3)
    receipt = dict(permutation_cases=permutation_cases, permutation_widths=list(range(1, 7)),
                   arbitrary_input_coordinates=19,
                   symbolic_map_sha256=hashlib.sha256(
                       json.dumps(expected, separators=(',', ':')).encode()).hexdigest())
    for name, eager, count, travel in [('eager', True, 210, 5864),
                                      ('deferred', False, 150, 4504)]:
        program = pre_reads + load + candidate.compile_batch(
            permutations, readers, eager=eager)['program'] + unload
        actual, invoice, peaks = _replay(program, initial)
        _require(actual == expected, f'{name} complete symbolic contract failed')
        _require(invoice['add_instructions'] == count, f'{name} ADD invoice changed')
        _require(invoice['tape_word_travel'] == travel, f'{name} travel invoice changed')
        _require(peaks == expected_peaks, f'{name} symbolic prefix bound changed')
        receipt[name] = dict(invoice=invoice, prefix_coefficient_l1_bounds=peaks)
    return receipt


if __name__ == '__main__':
    result = check()
    print('PASS_INDEPENDENT_READER_AUDIT permutation_cases=873 '
          'wrapped_adds=210->150 word_travel=5864->4504 symbolic_map=exact')
