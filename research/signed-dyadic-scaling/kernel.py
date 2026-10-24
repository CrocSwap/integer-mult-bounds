# SPDX-License-Identifier: Apache-2.0
"""Finite signed-dyadic coordinate scaling; no runtime host parameters.

JoyboyBrian with OpenAI Codex assistance. The machine/counter/copy macros
are David Arias's PR2776, retained unchanged and authenticated by loader.py.
"""
SCALES = ((2, 1), (1, 2), (-1, 1), (-2, 1), (-1, 2))
WORK = (2, 3, 8, 9, 10, 11, 12, 13)


def base_program(modules, operation, source=0, output=1):
    if operation not in ('double', 'half', 'negate') or source not in (0, 1) or output not in (0, 1):
        raise ValueError('fixed compile-time scaling/interface choice')
    b, m, c = (modules[k] for k in ('shear', 'machine', 'counters'))
    a = m.Assembler(14)
    fail = a.fresh('invalid_scaling')
    Q_COUNT = 9

    def rewind(tape, prefix):
        c.emit_rewind(a, tape, prefix)

    def walk_record(tape, delta, prefix):
        rewind(b.S_COUNT, prefix + '_S')
        loop, bit, done = (a.fresh(prefix + s) for s in ('_loop', '_bit', '_done'))
        a.label(loop)
        a.branch(b.S_COUNT, {m.UNIT: bit, m.RIGHT: done}, fail)
        a.label(bit)
        a.move(tape, delta)
        a.move(b.S_COUNT, 1)
        a.goto(loop)
        a.label(done)

    def prefixes(body, prefix):
        rewind(b.P_COUNT, prefix + '_P')
        loop, step, done = (a.fresh(prefix + s) for s in ('_loop', '_body', '_done'))
        a.label(loop)
        a.branch(b.P_COUNT, {m.UNIT: step, m.RIGHT: done}, fail)
        a.label(step)
        body()
        a.move(b.P_COUNT, 1)
        a.goto(loop)
        a.label(done)

    def paired(first_source, first_dest, second_source, second_dest, consume, prefix):
        rewind(b.RIGHT_LENGTH, prefix + '_pairs')
        loop, pair, done = (a.fresh(prefix + s) for s in ('_loop', '_pair', '_done'))
        a.label(loop)
        a.branch(b.RIGHT_LENGTH, {m.UNIT: pair, m.RIGHT: done}, fail)
        a.label(pair)
        b._copy_record(a, first_source, first_dest, consume, fail, prefix + '_first')
        b._copy_record(a, second_source, second_dest, consume, fail, prefix + '_second')
        a.move(b.RIGHT_LENGTH, 1)
        a.goto(loop)
        a.label(done)
        b._copy_record(a, first_source, first_dest, consume, fail, prefix + '_last')

    def negative_emit():
        b._copy_record(a, b.SPLIT_A, output, True, fail, 'negative_zero_record')
        rewind(b.LEFT_LENGTH, 'negative_seek_count')
        scan, step, end = (a.fresh(s) for s in ('seek_end_loop', 'seek_end_record', 'seek_end_done'))
        a.label(scan)
        a.branch(b.LEFT_LENGTH, {m.UNIT: step, m.RIGHT: end}, fail)
        a.label(step)
        walk_record(b.SPLIT_A, 1, 'seek_end_of_prefix')
        a.move(b.LEFT_LENGTH, 1)
        a.goto(scan)
        a.label(end)
        rewind(b.LEFT_LENGTH, 'negative_reverse_count')
        loop, record, done = (a.fresh(s) for s in ('reverse_loop', 'reverse_record', 'reverse_done'))
        a.label(loop)
        a.branch(b.LEFT_LENGTH, {m.UNIT: record, m.RIGHT: done}, fail)
        a.label(record)
        walk_record(b.SPLIT_A, -1, 'reverse_to_start')
        b._copy_record(a, b.SPLIT_A, output, True, fail, 'reverse_copy_record')
        walk_record(b.SPLIT_A, -1, 'reverse_return_start')
        a.move(b.LEFT_LENGTH, 1)
        a.goto(loop)
        a.label(done)
        rewind(b.LEFT_LENGTH, 'negative_restore_cursor_count')
        loop, record, done = (a.fresh(s) for s in ('restore_loop', 'restore_record', 'restore_done'))
        a.label(loop)
        a.branch(b.LEFT_LENGTH, {m.UNIT: record, m.RIGHT: done}, fail)
        a.label(record)
        walk_record(b.SPLIT_A, 1, 'restore_bucket_cursor')
        a.move(b.LEFT_LENGTH, 1)
        a.goto(loop)
        a.label(done)

    for tape in WORK + (() if source == output else (output,)):
        good = a.fresh('owned_blank')
        a.branch(tape, {m.BLANK: good}, fail)
        a.label(good)
        a.write(tape, m.LEFT)
        a.move(tape, 1)
    odd = a.fresh('odd_runtime_Q')
    a.branch(b.Q_INPUT, {m.ONE: odd}, fail)
    a.label(odd)
    for src, dst, name in ((b.P_INPUT, b.P_COUNT, 'P'), (b.Q_INPUT, Q_COUNT, 'Q'),
                           (b.S_INPUT, b.S_COUNT, 'S')):
        c.emit_binary_to_unary(a, src, b.BINARY_WORK, dst, 'prepare_' + name)
    if operation == 'negate':
        a.move(Q_COUNT, 1)
        loop, mark, done = (a.fresh(s) for s in ('minus_one_loop', 'minus_one_mark', 'minus_one_done'))
        a.label(loop)
        a.branch(Q_COUNT, {m.UNIT: mark, m.RIGHT: done}, fail)
        a.label(mark)
        a.write(b.LEFT_LENGTH, m.UNIT)
        a.move(b.LEFT_LENGTH, 1)
        a.move(Q_COUNT, 1)
        a.goto(loop)
        a.label(done)
    else:
        even, odd_count, put_a, put_b, done = (a.fresh(s) for s in
                                              ('count_even', 'count_odd', 'count_A', 'count_B', 'count_done'))
        a.label(even)
        a.branch(Q_COUNT, {m.UNIT: put_a}, fail)
        a.label(put_a)
        a.write(b.LEFT_LENGTH, m.UNIT)
        a.move(b.LEFT_LENGTH, 1)
        a.move(Q_COUNT, 1)
        a.goto(odd_count)
        a.label(odd_count)
        a.branch(Q_COUNT, {m.UNIT: put_b, m.RIGHT: done}, fail)
        a.label(put_b)
        a.write(b.RIGHT_LENGTH, m.UNIT)
        a.move(b.RIGHT_LENGTH, 1)
        a.move(Q_COUNT, 1)
        a.goto(even)
        a.label(done)
    for tape in (b.LEFT_LENGTH, b.RIGHT_LENGTH):
        a.write(tape, m.RIGHT)
    rewind(Q_COUNT, 'Q_count_return')
    if operation == 'double':
        def gather():
            b._segment(a, b.LEFT_LENGTH, source, b.SPLIT_A, False, fail, 'gather_A')
            b._segment(a, b.RIGHT_LENGTH, source, b.SPLIT_B, False, fail, 'gather_B')
    elif operation == 'half':
        def gather():
            paired(source, b.SPLIT_A, source, b.SPLIT_B, False, 'gather_even_odd')
    else:
        def gather():
            b._segment(a, Q_COUNT, source, b.SPLIT_A, False, fail, 'gather_negative')
    prefixes(gather, 'gather')
    complete = a.fresh('complete_source')
    a.branch(source, {m.RIGHT: complete}, fail)
    a.label(complete)
    for tape in (b.SPLIT_A, b.SPLIT_B):
        a.write(tape, m.RIGHT)
        rewind(tape, 'bucket_return_' + str(tape))
    if source == output:
        rewind(output, 'original_owner_overwrite_start')
    if operation == 'double':
        def emit():
            paired(b.SPLIT_A, output, b.SPLIT_B, output, True, 'emit_even_odd')
    elif operation == 'half':
        def emit():
            b._segment(a, b.LEFT_LENGTH, b.SPLIT_A, output, True, fail, 'emit_A')
            b._segment(a, b.RIGHT_LENGTH, b.SPLIT_B, output, True, fail, 'emit_B')
    else:
        emit = negative_emit
    prefixes(emit, 'emit')
    for tape in (b.SPLIT_A, b.SPLIT_B):
        complete = a.fresh('complete_bucket')
        a.branch(tape, {m.RIGHT: complete}, fail)
        a.label(complete)
    a.write(output, m.RIGHT)
    rewind(output, 'output_return')
    if source != output:
        rewind(source, 'source_return')
    b._seek_right(a, Q_COUNT, fail, 'Q_erasure_end')
    for tape in WORK:
        b._erase_back_to_origin(a, tape, 'erase_' + str(tape))
    a.halt()
    a.label(fail)
    a.reject('odd positive canonical dimensions and distinct blank owned work tapes')
    return a.finish()


def build_program(modules, coefficient=(2, 1), inplace=False):
    if (type(coefficient) is not tuple or len(coefficient) != 2
            or not all(type(v) is int for v in coefficient)
            or coefficient not in SCALES or type(inplace) is not bool):
        raise ValueError('fixed signed-dyadic coefficient/interface')
    numerator, denominator = coefficient
    output = 0 if inplace else 1
    operation = 'negate' if coefficient == (-1, 1) else ('double' if denominator == 1 else 'half')
    programs = [base_program(modules, operation, 0, output)]
    if numerator < 0 and coefficient != (-1, 1):
        programs.append(base_program(modules, 'negate', output, output))
    rows, starts = [], []
    for program in programs:
        starts.append(len(rows))
        rows.extend(program.instructions)
    linked = []
    for index, (program, start) in enumerate(zip(programs, starts)):
        for row in program.instructions:
            if row[0] == 'branch':
                linked.append(('branch', row[1], tuple((s, pc + start) for s, pc in row[2]), row[3] + start))
            elif row[0] == 'goto':
                linked.append(('goto', row[1] + start))
            elif row[0] == 'halt' and index + 1 < len(programs):
                linked.append(('goto', starts[index + 1]))
            else:
                linked.append(row)
    return modules['machine'].Program(tuple(linked), 14)
