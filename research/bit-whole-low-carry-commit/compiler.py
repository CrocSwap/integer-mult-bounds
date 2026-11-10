# SPDX-License-Identifier: Apache-2.0
"""Whole-low carry/commit program. Compilation receives no runtime Q,Z or data.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Retained
#5332/#5849/#5487 algorithms are imported unchanged and linked by local jumps.
"""
from fractions import Fraction
import json

from source import aliases, frontend, require


def rational_inverse(matrix):
    n = len(matrix)
    rows = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        require(pivot is not None, 'invertible source matrix')
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = rows[j][j]
        rows[j] = [x / scale for x in rows[j]]
        for i in range(n):
            if i != j:
                scale = rows[i][j]
                rows[i] = [x - scale*y for x, y in zip(rows[i], rows[j])]
    return tuple(tuple(row[n:]) for row in rows)


def source_matrix(raw, lanes=1, inverse=False):
    require(type(lanes) is int and lanes >= 1 and type(inverse) is bool, 'fixed source parameters')
    path = 'research/kappa-rebuild/bit/sources/pr589-regenerated/records/frames.json'
    frame = json.loads(raw[path])['frames']['506']
    require(frame['dim'] == 4 and len(frame['A']) == len(frame['B']) == 4, 'actual frame506')
    basis = frame['B'] + frame['A']
    small = tuple(tuple(Fraction(basis[j][i]) for j in range(8)) for i in range(8))
    if inverse:
        small = rational_inverse(small)
    return tuple(tuple(small[i//lanes][j//lanes] if i % lanes == j % lanes else Fraction(0)
                       for j in range(8*lanes)) for i in range(8*lanes))


def column_specs(matrix):
    """Eight source reads, padded only by owned zero control digits if n<8."""
    n = len(matrix)
    require(n >= 2 and all(len(row) == n for row in matrix), 'fixed square source of dimension at least two')
    extra = max(0, 8-n)
    specs = []
    for row in range(n):
        for col in range(n):
            indices = [i for i in range(n) if matrix[i][col]]
            require(len(indices) <= 8, 'source column support at most eight')
            for i in range(n):
                if len(indices) == min(8, n):
                    break
                if i not in indices:
                    indices.append(i)
            indices.sort()
            weights = [4*Fraction(matrix[i][col]) for i in indices] + [Fraction(0)]*extra
            require(all(x.denominator == 1 for x in weights), 'quarter-integral source')
            weights = tuple(int(x) for x in weights)
            require(len(weights) == 8 and sum(abs(x) for x in weights) <= 16, 'retained source decoder envelope')
            positions = tuple(row*n+i for i in indices) + tuple(n*n+i for i in range(extra))
            specs.append((weights, positions))
    return tuple(specs), n*n+extra


def compile_program(modules, q, matrix, inverse=False, mutant=None):
    """Emit one finite local machine for B_A. q and matrix are compile-time."""
    require(type(inverse) is bool, 'fixed source route direction')
    matrix = tuple(tuple(Fraction(x) for x in row) for row in matrix)
    if inverse:
        matrix = rational_inverse(matrix)
    specs, local_cells = column_specs(matrix)
    n, d = len(matrix), len(matrix)**2
    low_types, permutation, cache_bits = modules['types'].compile_types(q, matrix)
    t, bits = len(low_types), (q-1).bit_length()
    if mutant == 'wrong_cache_type':
        shift = d*bits
        cache_bits = cache_bits[shift:]+cache_bits[:shift]
    m, c, shear = (modules[k] for k in ('machine', 'counters', 'shear'))
    qloops = tuple(range(23, 23+d))
    zloop, binary_work, tloop = 23+d, 24+d, 25+d
    tapes = 26+d
    a = m.Assembler(tapes)
    fail = a.fresh('invalid_whole_low_boundary')
    commit_entry, carry_entry = a.fresh('commit'), a.fresh('all_carries')
    boundaries = {}

    def checked(tape, symbols, name):
        good = a.fresh(name)
        a.branch(tape, {s: good for s in symbols}, fail)
        a.label(good)

    def append(program, continuation, mapping=None, tag='component'):
        mapping = mapping or {}
        labels = [a.fresh(tag) for _ in program.instructions]
        a.goto(labels[program.entry])
        for label, row in zip(labels, program.instructions):
            a.label(label)
            op = row[0]
            if op == 'branch':
                a.branch(mapping.get(row[1], row[1]), {s: labels[pc] for s, pc in row[2]}, labels[row[3]])
            elif op == 'goto':
                a.goto(labels[row[1]])
            elif op == 'write':
                a.write(mapping.get(row[1], row[1]), row[2])
            elif op == 'move':
                a.move(mapping.get(row[1], row[1]), row[2])
            elif op == 'halt':
                a.goto(continuation)
            elif op == 'reject':
                a.reject(row[1])
            else:
                raise ValueError('unrecognized linked instruction')

    def blank_mark(tape, name):
        checked(tape, (m.BLANK,), name)
        a.write(tape, m.LEFT)
        a.move(tape, 1)

    def erase_marked(tape, name):
        loop, move, end = (a.fresh(name+'_'+s) for s in ('seek', 'move', 'end'))
        a.label(loop)
        a.branch(tape, {m.ZERO: move, m.ONE: move, m.UNIT: move, m.RIGHT: end}, fail)
        a.label(move); a.move(tape, 1); a.goto(loop)
        a.label(end)
        shear._erase_back_to_origin(a, tape, name+'_erase')

    def loops(counters, body, name):
        labels = []
        for tape in counters:
            loop, run, end = (a.fresh(name+'_'+s) for s in ('loop', 'run', 'end'))
            labels.append((tape, loop, end))
            a.label(loop)
            a.branch(tape, {m.UNIT: run, m.RIGHT: end}, fail)
            a.label(run)
        body()
        for tape, loop, end in reversed(labels):
            a.move(tape, 1)
            a.goto(loop)
            a.label(end)
            c.emit_rewind(a, tape, name+'_rewind')

    def binary_increment(tape):
        loop, zero, one, end, done = (a.fresh('increment_'+s) for s in ('loop', 'zero', 'one', 'end', 'done'))
        a.label(loop)
        a.branch(tape, {m.ZERO: zero, m.ONE: one, m.RIGHT: end}, fail)
        a.label(one); a.write(tape, m.ZERO); a.move(tape, 1); a.goto(loop)
        a.label(zero); a.write(tape, m.ONE); a.goto(done)
        a.label(end); a.write(tape, m.ONE); a.move(tape, 1); a.write(tape, m.RIGHT)
        a.label(done); c.emit_rewind(a, tape, 'increment_return')

    def binary_product(tape, counters, name):
        blank_mark(tape, name+'_blank')
        a.write(tape, m.ZERO); a.move(tape, 1); a.write(tape, m.RIGHT)
        c.emit_rewind(a, tape, name+'_zero')
        loops(counters, lambda: binary_increment(tape), name)

    def copy_payload(source, target, counter=22, consume=False):
        loop, run, end = (a.fresh('payload_'+s) for s in ('loop', 'run', 'end'))
        a.label(loop); a.branch(counter, {m.UNIT: run, m.RIGHT: end}, fail); a.label(run)
        zero, one, advance = (a.fresh('payload_'+s) for s in ('zero', 'one', 'advance'))
        a.branch(source, {m.ZERO: zero, m.ONE: one}, fail)
        a.label(zero); a.write(target, m.ZERO); a.goto(advance)
        a.label(one); a.write(target, m.ONE)
        a.label(advance)
        if consume:
            a.write(source, m.BLANK)
        a.move(source, 1); a.move(target, 1); a.move(counter, 1); a.goto(loop)
        a.label(end); c.emit_rewind(a, counter, 'payload_counter_return')

    after_cache = a.fresh('cache_initialized')
    append(modules['commit'].compile_cache(m, cache_bits, tapes), after_cache, {4: 21}, 'cache_init')
    a.label(after_cache)
    if mutant == 'early_commit':
        early_return = a.fresh('early_commit_return')
        early = modules['commit'].compile_commit(m, c, permutation, d, cache_bits)
        early_map = {0: 0, 1: 1, 2: 5, 3: 20, 4: 21, 5: binary_work, 6: 22,
                     **{7+i: tape for i, tape in enumerate(qloops+(zloop,))}}
        append(early, early_return, early_map, 'premature_commit')
        a.label(early_return)
    # Q=1 has zero high carry, but the low permutation and its cache lifecycle
    # are still executed. The valid input contract supplies canonical odd Q.
    checked(5, (m.ONE,), 'odd_Q'); a.move(5, 1)
    unit, nonunit = a.fresh('unit_Q'), a.fresh('nonunit_Q')
    a.branch(5, {m.RIGHT: unit, m.ZERO: nonunit, m.ONE: nonunit}, fail)
    a.label(unit); a.move(5, -1); a.goto(commit_entry)
    a.label(nonunit); a.move(5, -1); a.goto(carry_entry)

    a.label(carry_entry)
    boundaries['carry_entry'] = len(a.instructions)
    for tape in (22, binary_work, tloop) + qloops + (zloop,):
        blank_mark(tape, 'private_extent')
    for tape in qloops:
        c.emit_binary_to_unary(a, 5, binary_work, tape, 'Q_extent')
    c.emit_binary_to_unary(a, 20, binary_work, zloop, 'Z_extent')
    loops(qloops+(zloop,), lambda: (a.write(22, m.UNIT), a.move(22, 1)), 'fiber_length')
    a.write(22, m.RIGHT); c.emit_rewind(a, 22, 'fiber_length_return')
    for _ in range(t):
        a.write(tloop, m.UNIT); a.move(tloop, 1)
    a.write(tloop, m.RIGHT); c.emit_rewind(a, tloop, 'type_counter_return')

    outer, body, finished = (a.fresh('low_'+s) for s in ('loop', 'body', 'finished'))
    a.label(outer); a.branch(tloop, {m.UNIT: body, m.RIGHT: finished}, fail); a.label(body)
    boundaries['fiber_entry'] = len(a.instructions)
    blank_mark(19, 'owned_fiber')
    copy_payload(0, 19)
    a.write(19, m.RIGHT); c.emit_rewind(a, 19, 'owned_fiber_return')
    loops((22,), lambda: a.move(0, -1), 'parent_fiber_return')
    # Copy this complete old-low control block, preserving the full cache.
    for _ in range(d*bits):
        zero, one, advance = (a.fresh('cache_copy_'+s) for s in ('zero', 'one', 'advance'))
        a.branch(21, {m.ZERO: zero, m.ONE: one}, fail)
        a.label(zero); a.write(17, m.ZERO); a.goto(advance)
        a.label(one); a.write(17, m.ONE)
        a.label(advance); a.move(21, 1); a.move(17, 1)
    for _ in range((local_cells-d)*bits):
        a.write(17, m.ZERO); a.move(17, 1)
    a.write(17, m.RIGHT)
    for _ in range(local_cells*bits):
        a.move(17, -1)

    kernel = modules['rotation'].build(modules, inverse=(mutant == 'negative_carries'))
    cleanup = modules['descriptor'].erase(modules)
    for coordinate, (weights, positions) in enumerate(specs):
        binary_product(4, qloops[:coordinate], 'prefix_extent')
        binary_product(7, qloops[coordinate+1:]+(zloop,), 'suffix_extent')
        done = a.fresh('frontend_return')
        append(frontend(modules, q, weights, positions, local_cells, tapes), done, tag='source_frontend')
        a.label(done)
        if mutant == 'erase_cache_early' and coordinate == 0:
            a.write(17, m.BLANK)
        done = a.fresh('rotation_return')
        if mutant != 'omit_first_carry' or coordinate != 0:
            append(kernel, done, {0: 0 if mutant == 'alias_carry_owner' else 19}, 'carry_rotation')
        a.label(done)
        done = a.fresh('descriptor_erased')
        append(cleanup, done, tag='descriptor_retirement'); a.label(done)
        for _ in range(bits):
            a.write(18, m.BLANK); a.move(18, 1)
        for _ in range(bits):
            a.move(18, -1)
        erase_marked(4, 'prefix_retirement')
        erase_marked(7, 'suffix_retirement')

    boundaries['local_cache_last_use_boundary'] = len(a.instructions)
    for _ in range(local_cells*bits):
        a.write(17, m.BLANK); a.move(17, 1)
    a.write(17, m.BLANK)
    for _ in range(local_cells*bits):
        a.move(17, -1)
    if mutant != 'omit_installation':
        copy_payload(19, 0, consume=True)
    else:
        loops((22,), lambda: (a.move(0, 1), a.move(19, 1)), 'missing_installation')
    checked(19, (m.RIGHT,), 'whole_fiber_return')
    a.write(19, m.BLANK); c.emit_rewind(a, 19, 'consumed_fiber_return')
    a.move(19, -1); a.write(19, m.BLANK)
    a.move(tloop, 1); a.goto(outer)
    a.label(finished)
    checked(0, (m.RIGHT,), 'complete_original_owner')
    checked(21, (m.RIGHT,), 'complete_old_cache')
    c.emit_rewind(a, 0, 'original_owner_return')
    c.emit_rewind(a, 21, 'old_cache_return')
    for tape in (22, tloop) + qloops + (zloop,):
        erase_marked(tape, 'extent_retirement')
    a.move(binary_work, -1); checked(binary_work, (m.LEFT,), 'binary_work_return'); a.write(binary_work, m.BLANK)
    a.goto(commit_entry)

    a.label(commit_entry)
    boundaries['commit_entry'] = len(a.instructions)
    if mutant == 'wrong_low_direction':
        permutation = [permutation.index(i) for i in range(t)]
    commit = modules['commit'].compile_commit(m, c, permutation, d, cache_bits)
    mapping = {0: 0, 1: 1, 2: 5, 3: 20, 4: 21, 5: binary_work, 6: 22,
               **{7+i: tape for i, tape in enumerate(qloops+(zloop,))}}
    done = a.fresh('complete_carry_commit')
    append(commit, done, mapping, 'low_commit'); a.label(done)
    if mutant == 'extra_work':
        a.move(5, 1); a.move(5, -1)
    a.halt()
    a.label(fail); a.reject('whole-low source shape, old-cache lifetime and owned workspace')
    program = a.finish()
    return program, dict(n=n, d=d, q=q, inverse=inverse, types=low_types,
                         permutation=permutation, cache_bits=cache_bits, local_cells=local_cells,
                         matrix=matrix, tapes=tapes, boundaries=boundaries)
