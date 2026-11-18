#!/usr/bin/env python3
"""Check one physical ruler against complete source bank services."""
from hashlib import sha1, sha256
import gzip
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def authenticate():
    for row in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(sha256((HERE.parents[1] / row['path']).read_bytes()).hexdigest() == row['sha256'], 'retained source hash')
    for row in json.loads((HERE / 'VENDORED.json').read_text())['files']:
        raw = (HERE / row['path']).read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'], 'copied source hash')
        need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'], 'copied source Git blob')


authenticate()
sys.path.insert(0, str(HERE))
import assembly as a
from machine import Machine, Tape, Program, binary
p = a.guide


def counter(x):
    return 24 * x - 7 * x.bit_count() + 15 * x.bit_length() + 12


def service(slot, length):
    return (14 * slot + 9) * length + counter(slot) + 39 * slot + 12 * slot.bit_length() + 47


def fixture(n, width, banks, largest):
    length = n * (2 * width + 3)
    spans = [n.bit_length() + 2, width.bit_length() + 2,
             max(n.bit_length(), width.bit_length(), largest.bit_length()) + 2,
             max(n, largest) + 2, max(width, largest.bit_length()) + 2,
             length + 2, banks * (length + 2)]
    target = {i: (i + 3) % 7 for i in range(spans[-1])}
    for slot in range(banks):
        target[slot * (length + 2)] = p.LEFT
        target[(slot + 1) * (length + 2) - 1] = p.RIGHT
    tapes = [binary(n), binary(width), Tape(), Tape(), Tape(),
             Tape({i: (i + 2) % 7 for i in range(length + 2)}), Tape(target)]
    for tape, span in zip(tapes, spans):
        tape.cells[-2] = p.MARK
        tape.cells[span + 3] = p.ONE
    return tapes, spans


def snapshot(tapes):
    return [(dict(t.cells), t.head) for t in tapes]


def dense_run(program, initial, spans, cap):
    """Execute the fixed table without the retained sparse machine."""
    offset = 3
    cells = [[p.BLANK] * (span + 10) for span in spans]
    heads = []
    for row, (source, head) in zip(cells, initial):
        for index, symbol in source.items():
            row[index + offset] = symbol
        heads.append(head + offset)
    pc, steps = program.entry, 0
    while True:
        instruction = program.instructions[pc]
        op = instruction[0]
        steps += 1
        need(steps <= cap, 'dense external step cap')
        if op == 'branch':
            _, tape, choices, fallback = instruction
            symbol = cells[tape][heads[tape]]
            pc = next((target for value, target in choices if value == symbol), fallback)
        elif op == 'write':
            cells[instruction[1]][heads[instruction[1]]] = instruction[2]
            pc += 1
        elif op == 'move':
            heads[instruction[1]] += instruction[2]
            need(0 <= heads[instruction[1]] < len(cells[instruction[1]]), 'dense fixture extent')
            pc += 1
        elif op == 'goto':
            pc = instruction[1]
        elif op == 'halt':
            break
        else:
            raise ValueError('dense rejection: ' + instruction[1])
    return [({i - offset: symbol for i, symbol in enumerate(row) if symbol != p.BLANK}, head - offset)
            for row, head in zip(cells, heads)], steps


def check_case(n, width, banks, schedule, compiled=None, independent=True):
    program, blocks = a.build(schedule) if compiled is None else compiled
    largest = max(slot for _, slot, _ in schedule)
    need(0 < largest < banks, 'complete reserved bank array')
    tapes, spans = fixture(n, width, banks, largest)
    initial = snapshot(tapes)
    outside = [{k: v for k, v in cells.items() if k < 0 or k >= span}
               for (cells, _), span in zip(initial, spans)]
    length = n * (2 * width + 3)
    literal = p.banks.make_guide(n, 0, width)
    expected_guide = {**outside[p.GUIDE], **{i: p.ENCODE[token] for i, token in enumerate(literal) if p.ENCODE[token] != p.BLANK}}
    zero = [p.PAYLOAD[c] for _, c in literal[1:-1]]
    expected_target = dict(initial[p.TARGET][0])
    production = counter(n) + counter(width) + 22 * n * width + 36 * n + 7 * width + 36
    retirement = 7 * length + 10
    total = production + sum(service(slot, length) for _, slot, _ in schedule) + retirement
    machine = Machine(program, tapes)

    def boundary(retired=False):
        need([t.head for t in tapes] == [1, 1, 0, 0, 0, 0, 0], 'complete head return')
        need(snapshot(tapes[:2]) == initial[:2], 'preserved input descriptors')
        for index in (p.WORK, p.ROWS, p.WIDTH):
            need(tapes[index].cells == outside[index], 'complete counter retirement')
        need(tapes[p.GUIDE].cells == (outside[p.GUIDE] if retired else expected_guide), 'immutable ruler or complete retirement')
        need(tapes[p.TARGET].cells == expected_target, 'selected payload and all parked cells')

    def advance(end):
        while machine.pc != end:
            need(not machine.halted and machine.steps < total + 10000, 'sparse external step cap')
            machine.step()

    advance(blocks[0]['start'])
    boundary()
    need(machine.steps == production, 'exact producer bill')
    for block in blocks:
        before = machine.steps
        start = block['slot'] * (length + 2)
        for offset, value in enumerate(zero, 1):
            value = value if block['operation'] == 'INIT' else p.BLANK
            if value == p.BLANK:
                expected_target.pop(start + offset, None)
            else:
                expected_target[start + offset] = value
        advance(block['end'])
        boundary()
        need(machine.steps - before == service(block['slot'], length), 'exact selected service bill')
    before = machine.steps
    machine.run(total + 10000)
    boundary(retired=True)
    need(machine.steps - before == retirement and machine.steps == total, 'complete instruction bill')
    actual_spans = [max(v) - min(v) + 1 for v in machine.visits]
    need(actual_spans[:6] == spans[:6] and actual_spans[6] <= spans[6], 'historical visited spans')
    for visits, span in zip(machine.visits, spans):
        need(min(visits) == 0 and max(visits) < span, 'owned access windows')
    if independent:
        other, steps = dense_run(program, initial, spans, total)
        need(other == snapshot(tapes) and steps == total, 'independent dense execution')
    return {'records': n, 'width': width, 'reserved_banks': banks, 'largest_slot': largest,
            'payload_extent': length, 'reset_services': len(schedule), 'steps': total,
            'visited_spans': actual_spans, 'reserved_spans': spans,
            'retained_cells': sum(spans), 'independent_dense': independent}


def controls():
    schedule = [(0, 2, 'INIT'), (1, 2, 'CLEAR')]
    program, blocks = a.build(schedule)
    block = blocks[0]
    region = range(block['start'], block['end'])
    table = program.instructions
    forward = next(i for i in region if table[i] == ('move', p.TARGET, 1))
    turn = next(i for i in region if i > forward and table[i] == ('move', p.TARGET, 1))
    backward = max(i for i in region if table[i] == ('move', p.TARGET, -1))
    guide_return = next(i for i in region if table[i] == ('move', p.GUIDE, -1) and table[i - 1] == ('move', p.GUIDE, 1))
    consumer_step = next(i for i in region if i > guide_return and table[i] == ('move', p.TARGET, 1))
    work_erase = max(i for i in region if table[i] == ('write', p.WORK, p.BLANK))
    faults = [('omit slot right cell', turn, ('goto', turn + 1)),
              ('reverse outward travel', forward, ('move', p.TARGET, -1)),
              ('write shared ruler', consumer_step + 1, ('write', p.GUIDE, p.MARK)),
              ('omit payload return step', backward, ('goto', backward + 1)),
              ('omit ruler return step', guide_return, ('goto', guide_return + 1)),
              ('retain counter marker', work_erase, ('goto', work_erase + 1))]
    result = []
    for label, pc, row in faults:
        changed = list(table)
        changed[pc] = row
        mutant = Program(tuple(changed), 7)
        try:
            check_case(2, 2, 4, schedule, (mutant, blocks), independent=False)
        except ValueError as error:
            need(str(error) in ('complete head return', 'selected payload and all parked cells',
                                'immutable ruler or complete retirement', 'complete counter retirement',
                                'complete immutable ruler and unary bank counter', 'current flat zero guide'), 'semantic fault cause')
            result.append({'fault': label, 'rejected_by': str(error)})
        else:
            raise ValueError('instruction fault accepted')
    return result


def main():
    schedule = a.source_schedule()
    program, blocks = a.build(schedule)
    need(len(schedule) == 468 and {k for _, k, _ in schedule} == set(range(234, 468)), 'literal lifetime inventory')
    _, word = a.word.words()
    reverse, live = [], {}
    ordinal = 233
    for clock in range(len(word['program']) - 1, -1, -1):
        event = word['program'][clock]
        if event[0] == 'CLEAR':
            need(event[1] not in live, 'reverse lifetime overlap')
            live[event[1]] = clock
        elif event[0] == 'INIT':
            need(event[1] in live, 'reverse lifetime closure')
            reverse.extend([(clock, 234 + ordinal, 'INIT'), (live.pop(event[1]), 234 + ordinal, 'CLEAR')])
            ordinal -= 1
    need(not live and ordinal == -1 and sorted(reverse) == schedule, 'independent reverse source census')
    for block in blocks:
        need(not any(row[:2] == ('write', p.GUIDE) for row in program.instructions[block['start']:block['end']]), 'read-only shared ruler in every service')
    table = {'tapes': program.tapes, 'entry': program.entry,
             'instructions': program.instructions, 'blocks': blocks}
    cases = [check_case(n, w, k + 2, [(0, k, 'INIT'), (1, k, 'CLEAR')])
             for n, w, k in [(1, 1, 1), (2, 3, 2), (3, 2, 5), (7, 1, 8), (8, 7, 15), (1, 2, 31)]]
    cases.append(check_case(1, 1, 468, schedule, (program, blocks)))
    cases.append(check_case(512, 1, 468, [(0, 467, 'INIT'), (1, 467, 'CLEAR')]))
    result = {'source_word_sha256': a.word.CANDIDATE, 'tapes': 7,
              'schedule_sha256': sha256(encoded(schedule)).hexdigest(),
              'tables_sha256': sha256(encoded(table)).hexdigest(),
              'table_rows': len(program.instructions), 'cases': cases, 'controls': controls(),
              'full_schedule_linear': sum(14 * k + 9 for _, k, _ in schedule),
              'full_schedule_constant': sum(counter(k) + 39 * k + 12 * k.bit_length() + 47 for _, k, _ in schedule),
              'small_storage': {'shared_total': cases[-2]['retained_cells'], 'previous_two_arrays': 6552},
              'native_storage': {'shared_total': cases[-1]['retained_cells'], 'previous_two_arrays': 2398032}}
    if sys.argv[1:] == ['--write']:
        need(not (HERE / 'TABLES.json.gz').exists() and not (HERE / 'RESULT.json').exists(), 'do not replace checked receipts')
        (HERE / 'TABLES.json.gz').write_bytes(gzip.compress(encoded(table), mtime=0))
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    else:
        need(not sys.argv[1:], 'unexpected arguments')
        need(encoded(table) == gzip.decompress((HERE / 'TABLES.json.gz').read_bytes()), 'complete emitted table')
        need(encoded(result) == encoded(json.loads((HERE / 'RESULT.json').read_text())), 'complete result receipt')
    print('PASS_CURRENT_SHARED_GUIDE_BANKS ' + json.dumps({k: v for k, v in result.items() if k != 'cases'}, sort_keys=True))


if __name__ == '__main__':
    main()
