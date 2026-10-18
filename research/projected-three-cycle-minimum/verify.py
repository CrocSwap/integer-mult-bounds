#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact projected three-cycle verification, standard library only.

Prepared for Andrey Mas with substantial ChatGPT GPT-6 Pro
research assistance. Prior elementary loops and SWAP are credited to Gareth
Davidson (@bitplane), PR1420; @woklerx's PR1105 is the earlier lineage.

Default: all semantic fixtures, the complete five-register radius-six search
in TWO representations, an exact set comparison, and the lower-bound test.
There are no downloads, third-party dependencies, assertions, random tests,
symmetry pruning, timeouts, or external certificate inputs used to prune.

Usage:
    python3 -I -B verify.py
    python3 -I -O -B verify.py
    python3 -I -B verify.py --receipt certificate.json  # write a fresh receipt

The --receipt option does not skip any checks. With no option, an adjacent
certificate.json is compared if present; the search is still recomputed.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import sys


class VerificationError(RuntimeError):
    """An essential mathematical or implementation check failed."""


def need(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


# Registers 0,1,2 are the three named helpers; register 3 is the sole target.
# Embed this word by mapping register 3 to k and leaving extra helpers idle.
WORD = (
    (0, 1), (0, 2), (1, 0), (2, 3), (3, 1), (1, 3), (2, 1),
    (0, 2), (3, 0), (1, 3), (3, 1), (1, 2), (0, 1),
)
EXPECTED_LAYERS = [1, 20, 260, 2670, 22988, 174676, 1221368]
N = 5
Y = 4
RADIUS = 6


def identity(n: int) -> tuple[int, ...]:
    return tuple(1 << j for j in range(n))


def cycle_rows(n: int) -> tuple[int, ...]:
    need(n >= 4, 'three helpers and one target required')
    return (2, 4, 1) + identity(n)[3:]


def check_word(n: int, y: int, word: tuple) -> None:
    need(type(n) is int and n >= 2 and type(y) is int and 0 <= y < n,
         'invalid register specification')
    for gate in word:
        need(isinstance(gate, (list, tuple)) and len(gate) == 2, 'invalid gate')
        d, s = gate
        need(type(d) is int and type(s) is int and 0 <= d < n and
             0 <= s < n and d != s, 'invalid XOR endpoints')


def rows_pair(n: int, y: int, word: tuple) -> tuple[tuple, tuple]:
    """Formal input coefficients; projection is a separately executed word."""
    check_word(n, y, word)
    raw, projected = list(identity(n)), list(identity(n))
    for d, s in word:
        raw[d] ^= raw[s]
        if d != y:
            projected[d] ^= projected[s]
    return tuple(raw), tuple(projected)


def literal_pair(n: int, y: int, word: tuple, value: int) -> tuple[int, int]:
    """Literal Boolean execution, with a separately filtered projected program."""
    check_word(n, y, word)
    need(type(value) is int and 0 <= value < 1 << n, 'invalid Boolean input')
    kept = tuple((d, s) for d, s in word if d != y)
    outputs = []
    for program in (word, kept):
        bits = [(value >> j) & 1 for j in range(n)]
        for d, s in program:
            bits[d] = (bits[d] + bits[s]) % 2
        outputs.append(sum(b << j for j, b in enumerate(bits)))
    return tuple(outputs)


def rows_value(rows: tuple, value: int) -> int:
    return sum(((row & value).bit_count() & 1) << j
               for j, row in enumerate(rows))


def cycle_value(value: int) -> int:
    # Direct output-bit specification, not obtained from a matrix product.
    return (value & ~7) | ((value >> 1) & 3) | ((value & 1) << 2)


def pack_rows(rows: tuple) -> int:
    n = len(rows)
    return sum(row << (n * i) for i, row in enumerate(rows))


def rank(rows: tuple) -> int:
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def fixtures() -> dict:
    n, y = 4, 3
    unit, target = identity(n), cycle_rows(n)
    raw, projected = rows_pair(n, y, WORD)
    need(len(WORD) == 13 and raw == unit and projected == target,
         'thirteen-gate witness is incorrect')
    need(Counter(d for d, _ in WORD) == {0: 4, 1: 4, 2: 2, 3: 3},
         'witness write counts')
    need(rank(tuple(a ^ b for a, b in zip(unit, target))) == 2,
         'cycle defect rank')
    for x in range(1 << n):
        need(literal_pair(n, y, WORD, x) == (x, cycle_value(x)),
             'dirty truth-table witness failure')

    # Already-known fixtures: NOT new minimum claims or predecessor censuses.
    elementary = ((0, y), (y, 1), (0, y), (y, 1), (0, 1))
    sole_target = ((0, y), (y, 0)) * 3
    swap = ((0, 1), (1, 0), (1, y), (y, 0), (1, y), (y, 0), (0, 1))
    prior_fixtures = (
        ('PR1420 five-gate elementary', elementary, (3, 2, 4, 8)),
        ('PR1420 six-gate sole-target', sole_target, (9, 2, 4, 8)),
        ('PR1420 seven-gate SWAP', swap, (2, 1, 4, 8)),
    )
    for name, word, expected in prior_fixtures:
        need(rows_pair(n, y, word) == (unit, expected), name)
        for x in range(1 << n):
            need(literal_pair(n, y, word, x) == (x, rows_value(expected, x)),
                 name + ' literal failure')

    # Wrongly extracting the raw helper block would report I, not the cycle.
    need(tuple(r & 7 for r in raw[:3]) == (1, 2, 4), 'raw-block control')
    need(tuple(r & 7 for r in projected[:3]) == (2, 4, 1),
         'syntactic projection control')

    # A dirty-target error invisible on EVERY assignment with y=0.
    contaminated = WORD + ((0, y),)
    cr, cp = rows_pair(n, y, contaminated)
    need(cr != unit and cp != target, 'dirty-target mutation was not detected')
    for x in range(1 << y):
        need(literal_pair(n, y, contaminated, x) == (x, cycle_value(x)),
             'zero-target control should pass its restricted tests')
    need(literal_pair(n, y, contaminated, 1 << y) != (1 << y, 1 << y),
         'dirty-target distinguishing input was lost')

    # Delete step 11, the last target restoration: P is STILL exactly the cycle;
    # all raw helper rows are restored, but the raw target row is not restored.
    missing = WORD[:10] + WORD[11:]
    mr, mp = rows_pair(n, y, missing)
    need(len(missing) == 12 and mp == target and mr[:3] == unit[:3]
         and mr[y] != unit[y], 'missing-restoration negative control')
    failure_input = next((x for x in range(1 << n)
                          if literal_pair(n, y, missing, x)[0] != x), None)
    need(failure_input is not None, 'missing restoration lacked a dirty witness')

    # Reversal fixes raw identity but reverses the requested cycle orientation.
    reverse_projection = rows_pair(n, y, WORD[::-1])[1]
    need(reverse_projection == (4, 1, 2, 8) and reverse_projection != target,
         'cycle orientation control')

    # Independent basis-column replay, including every extra dirty input.
    dimensions = [4, 5, 6, 18, 65]
    for dim in dimensions:
        target_index = dim - 1
        embedded = tuple((target_index if d == 3 else d,
                          target_index if s == 3 else s) for d, s in WORD)
        need(rows_pair(dim, target_index, embedded) ==
             (identity(dim), cycle_rows(dim)), 'larger embedding row failure')
        for j in range(dim):
            x = 1 << j
            need(literal_pair(dim, target_index, embedded, x) ==
                 (x, cycle_value(x)), 'larger embedding column failure')

    rejected = 0
    for illegal in (((0, 0),), ((0, 4),), ((-1, 0),)):
        try:
            rows_pair(n, y, illegal)
        except VerificationError:
            rejected += 1
    need(rejected == 3, 'invalid primitive accepted')
    return {
        'witness_length': 13,
        'witness_chronological_destination_source': [list(g) for g in WORD],
        'witness_registers': ['z0', 'z1', 'z2', 'y'],
        'raw_rows': list(raw), 'projected_rows': list(projected),
        'witness_all_boolean_inputs_checked': 16,
        'prior_positive_fixtures_checked': 3,
        'embedding_register_counts': dimensions,
        'projection_vs_raw_block_control': 'passed',
        'zero_target_false_positive_control': 'passed',
        'missing_target_restoration_control': 'passed',
        'missing_restoration_raw_rows': list(mr),
        'missing_restoration_distinguishing_input': failure_input,
        'reversed_cycle_control': 'passed', 'illegal_gate_controls': rejected,
    }


def row_ball() -> tuple[set[int], list[int], int]:
    """All paired endpoints through radius six; row-major packed matrices.

    All twenty generators are expanded at EVERY vertex of distance <=5.
    No endpoint, word, register-usage or cancellation pruning is used.
    """
    n, nn, y = N, N * N, Y
    rowmask = (1 << n) - 1
    unit = pack_rows(identity(n))
    start = unit | (unit << nn)
    operations = [(d * n, s * n, d != y)
                  for d in range(n) for s in range(n) if d != s]
    seen, frontier, layers = {start}, [start], [1]
    edges = 0
    for _ in range(RADIUS):
        following = []
        for state in frontier:
            for d, s, keep in operations:
                nxt = state ^ (((state >> s) & rowmask) << d)
                if keep:
                    nxt ^= ((state >> (nn + s)) & rowmask) << (nn + d)
                if nxt not in seen:
                    seen.add(nxt)
                    following.append(nxt)
        edges += len(frontier) * len(operations)
        frontier = following
        layers.append(len(frontier))
    return seen, layers, edges


def column_ball() -> tuple[set[int], list[int], int]:
    """Separate engine: each n-bit block is the image of one dirty basis input.

    A gate changes the destination bit in EVERY input image having source bit 1.
    This engine does not use row extraction, row XORs, or the row transition.
    """
    n, nn = N, N * N
    basis_images = sum((1 << j) << (j * n) for j in range(n))
    root = basis_images | (basis_images << nn)
    every_column_bit_zero = sum(1 << (n * j) for j in range(n))
    operations = []
    for dst in range(n):
        for src in range(n):
            if dst == src:
                continue
            selection = every_column_bit_zero << src
            if dst != Y:
                selection |= selection << nn
            operations.append((selection, dst - src))
    reached = {root}
    boundary = [root]
    counts = [1]
    expanded = 0
    for _ in range(RADIUS):
        new_boundary = []
        for current in boundary:
            for selection, shift in operations:
                donor_bits = current & selection
                moved = donor_bits << shift if shift >= 0 else donor_bits >> (-shift)
                image = current ^ moved
                if image not in reached:
                    reached.add(image)
                    new_boundary.append(image)
        expanded += len(boundary) * len(operations)
        counts.append(len(new_boundary))
        boundary = new_boundary
    return reached, counts, expanded


def column_translation(state: int) -> int:
    """Right multiplication by (I,C) in basis-image/column representation.

    C sends input basis e0 to e2, e1 to e0, e2 to e1. Thus the new P columns
    are old columns [2,0,1,3,4]. R is left untouched.
    """
    nn = N * N
    lowmask = (1 << nn) - 1
    raw, p = state & lowmask, state >> nn
    block = (1 << N) - 1
    p0 = p & block
    p1 = (p >> N) & block
    p2 = (p >> (2 * N)) & block
    permuted = (p & ~((1 << (3 * N)) - 1)) | p2 | (p0 << N) | (p1 << (2 * N))
    return raw | (permuted << nn)


def finite_lower_bound() -> dict:
    row_states, row_layers, row_edges = row_ball()
    need(row_layers == EXPECTED_LAYERS, 'unexpected complete row BFS layers')
    need(len(row_states) == sum(EXPECTED_LAYERS), 'row ball cardinality')
    need(row_edges == 20 * sum(EXPECTED_LAYERS[:-1]), 'row expansion count')
    print('Row search complete: 1,421,983 states through radius 6.', file=sys.stderr)

    # Direct P*C column permutation inside every packed row: [p2,p0,p1,...].
    # The raw matrix and ALL projected columns beyond 0,1,2 remain unchanged.
    nn = N * N
    base = sum(1 << (N * j + nn) for j in range(N))
    selected = 7 * base
    row_hits = 0
    for state in row_states:
        translated = (state & ~selected) | ((state & (3 * base)) << 1) | \
                     ((state & (4 * base)) >> 2)
        if translated in row_states:
            row_hits += 1
    need(row_hits == 0, 'a word of length at most twelve exists')

    # Receipt hash is diagnostic ONLY: every mathematical check is recomputed.
    digest = hashlib.sha256()
    for state in sorted(row_states):
        digest.update(struct.pack('<Q', state))

    column_states, column_layers, column_edges = column_ball()
    need(column_layers == EXPECTED_LAYERS, 'unexpected complete column BFS layers')
    need(len(column_states) == len(row_states), 'column ball cardinality')
    need(column_edges == row_edges, 'column expansion count')
    print('Column search complete; comparing every represented endpoint.', file=sys.stderr)

    # Exact bijective representation comparison, NOT just matching hashes.
    # Precompute the contribution of one row to a transposed 5x5 bit array.
    tables = [[sum(((row >> j) & 1) << (j * N + i) for j in range(N))
               for row in range(1 << N)] for i in range(N)]
    equal_states, column_hits = 0, 0
    rowmask = (1 << N) - 1
    for state in row_states:
        converted = 0
        for i in range(N):
            converted |= tables[i][(state >> (i * N)) & rowmask]
            converted |= tables[i][(state >> (nn + i * N)) & rowmask] << nn
        need(converted in column_states, 'the two exact balls disagree')
        equal_states += 1
        if column_translation(converted) in column_states:
            column_hits += 1
    need(column_hits == 0, 'column representation found a short word')
    need(equal_states == len(column_states), 'incomplete exact set comparison')

    # Identity checks the chosen cycle, but cannot distinguish product side.
    unit = pack_rows(identity(N))
    start = unit | (unit << nn)
    goal = unit | (pack_rows(cycle_rows(N)) << nn)
    translated_start = (start & ~selected) | ((start & (3 * base)) << 1) | \
                       ((start & (4 * base)) >> 2)
    need(translated_start == goal, 'row translation is not the requested cycle')
    literal_columns = sum(cycle_value(1 << j) << (j * N) for j in range(N))
    need(column_translation(start) == unit | (literal_columns << nn),
         'column translation is not the requested cycle')

    # Separate Pro review's noncommuting fixture: T=T_01, T*C != C*T.
    # Exercise the same packed translation used above, keeping raw T fixed.
    t = pack_rows((3, 2, 4, 8, 16))
    noncommuting = t | (t << nn)
    right = (noncommuting & ~selected) | ((noncommuting & (3 * base)) << 1) | \
            ((noncommuting & (4 * base)) >> 2)
    need(right == t | (pack_rows((6, 4, 1, 8, 16)) << nn),
         'noncommuting row right-translation control')
    need(right != t | (pack_rows((2, 4, 3, 8, 16)) << nn),
         'row translation confused left and right products')
    t_columns = pack_rows((1, 3, 4, 8, 16))
    need(column_translation(t_columns | (t_columns << nn)) ==
         t_columns | (pack_rows((4, 1, 3, 8, 16)) << nn),
         'noncommuting column right-translation control')
    return {
        'registers': N, 'helpers': 4, 'targets': 1, 'radius': RADIUS,
        'all_generators_per_vertex': N * (N - 1),
        'exact_distance_layers_both_engines': EXPECTED_LAYERS,
        'ball_states_each_engine': len(row_states),
        'expanded_states_each_engine': sum(EXPECTED_LAYERS[:-1]),
        'expanded_directed_edges_each_engine': row_edges,
        'row_ball_right_translate_intersection': row_hits,
        'column_ball_right_translate_intersection': column_hits,
        'exact_transposed_state_memberships_checked': equal_states,
        'row_ball_sha256_sorted_little_endian_u64': digest.hexdigest(),
        'full_paired_group_census_claimed': False,
        'excluded_word_lengths': '0 through 12 inclusive',
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', type=Path,
                        help='write a deterministic JSON receipt after ALL checks')
    args = parser.parse_args()
    result = {
        'schema': 'projected-three-cycle-exact-v1',
        'license': 'Apache-2.0',
        'theorem': {
            'minimum': 13, 'helpers': 'every finite k >= 3', 'targets': 1,
            'uniform_reduction': 'rank defect 2 forces at least 3 target writes; '
                                 'length <=12 has at most 4 written helpers; '
                                 'delete read-only-input contributions and pad to 5 registers',
            'proof_status': 'computer-assisted lower bound with written all-dimension reduction',
        },
        'semantic_checks': fixtures(),
        'lower_bound': finite_lower_bound(),
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.receipt is not None:
        args.receipt.write_text(encoded, encoding='utf-8')
    else:
        receipt = Path(__file__).resolve().with_name('certificate.json')
        if receipt.exists():
            need(json.loads(receipt.read_text(encoding='utf-8')) == result,
                 'recomputed result differs from the adjacent receipt')
    print(encoded, end='')
    print('PASS: minimum 13 for every finite k >= 3 (see proof.md for the reduction).',
          file=sys.stderr)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (VerificationError, OSError, ValueError) as exc:
        print('FAIL: ' + str(exc), file=sys.stderr)
        raise SystemExit(1)
