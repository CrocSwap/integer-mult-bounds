#!/usr/bin/env python3
"""Check emitted guide lifecycles with sparse and independent dense execution."""
from hashlib import sha1, sha256
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
import program as p
from machine import Machine, Tape, Program, Rejected, binary


def fixture(n, width):
    length = n * (2 * width + 3)
    ends = [n.bit_length() + 1, width.bit_length() + 1,
            max(n.bit_length(), width.bit_length()) + 1, n + 1, width + 1,
            length + 1, length + 1]
    tapes = [binary(n), binary(width), Tape(), Tape(), Tape(),
             Tape({i: (i + 2) % 7 for i in range(length + 2)}, 0),
             Tape({0: p.LEFT, **{i: (i + 3) % 7 for i in range(1, length + 1)}, length + 1: p.RIGHT}, 0)]
    for tape, end in zip(tapes, ends):
        tape.cells[-2] = p.MARK
        tape.cells[end + 4] = p.ONE
    return tapes, ends


def sparse_snapshot(tapes):
    return [(dict(t.cells), t.head) for t in tapes]


def dense_run(program, initial, ends):
    """Walk the emitted opcodes without the retained machine executor."""
    offset = 3
    cells = [[p.BLANK] * (end + 10) for end in ends]
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
        need(steps < 5000000, 'dense fixture step cap')
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


def check_shape(n, width, programs, independent=True):
    length = n * (2 * width + 3)
    tapes, ends = fixture(n, width)
    initial = sparse_snapshot(tapes)
    outside = [{k: v for k, v in cells.items() if k < 0 or k > end}
               for (cells, _), end in zip(initial, ends)]
    guide = [p.ENCODE[token] for token in p.banks.make_guide(n, 0, width)]
    target_zero = [p.PAYLOAD[c] for _, c in p.banks.make_guide(n, 0, width)[1:-1]]
    c = lambda x: 24 * x - 7 * x.bit_count() + 15 * x.bit_length() + 12
    expected_steps = {'produce': c(n) + c(width) + 22 * n * width + 36 * n + 7 * width + 36,
                      'INIT': 9 * length + 11, 'CLEAR': 9 * length + 11,
                      'retire': 7 * length + 10}
    visited = [set() for _ in tapes]
    charges = {}
    for name in ('produce', 'INIT', 'CLEAR', 'retire'):
        before = sparse_snapshot(tapes)
        machine = Machine(programs[name], tapes).run(5000000)
        charges[name] = machine.steps
        need(machine.steps == expected_steps[name], 'exact instruction ledger')
        after = sparse_snapshot(tapes)
        if independent:
            other, steps = dense_run(programs[name], before, ends)
            need(other == after and steps == machine.steps, 'independent dense execution')
        need(after[:2] == initial[:2], 'preserved binary descriptors and heads')
        need([t.head for t in tapes] == [1, 1, 0, 0, 0, 0, 0], 'complete head return')
        for i, tape in enumerate(tapes):
            need({k: v for k, v in tape.cells.items() if k < 0 or k > ends[i]} == outside[i], 'borrowed exterior cells')
            visited[i].update(machine.visits[i])
        for i in (p.WORK, p.ROWS, p.WIDTH):
            need(tapes[i].cells == outside[i], 'all conversion markers and work retired')
        if name != 'retire':
            need([tapes[p.GUIDE].cells.get(i, p.BLANK) for i in range(length + 2)] == guide, 'exact immutable source guide')
        else:
            need(tapes[p.GUIDE].cells == outside[p.GUIDE], 'complete guide retirement')
        if name == 'produce':
            need(after[p.TARGET] == initial[p.TARGET], 'target untouched during production')
        elif name == 'INIT':
            need([tapes[p.TARGET].cells.get(i, p.BLANK) for i in range(1, length + 1)] == target_zero, 'literal source INIT consumer')
        else:
            need(all(tapes[p.TARGET].cells.get(i, p.BLANK) == p.BLANK for i in range(1, length + 1)), 'literal source CLEAR consumer')
        need(tapes[p.TARGET].cells.get(0) == p.LEFT and tapes[p.TARGET].cells.get(length + 1) == p.RIGHT, 'target guards preserved')
    spans = [max(positions) - min(positions) + 1 for positions in visited]
    expected_span = 2 * length + n + width + n.bit_length() + width.bit_length() + max(n.bit_length(), width.bit_length()) + 14
    need(spans == [end + 1 for end in ends] and sum(spans) == expected_span, 'complete historical visited capacity')
    need(sum(charges.values()) <= 72 * length and sum(spans) <= 7 * length, 'uniform lifecycle bounds')
    return {'records': n, 'width': width, 'payload_extent': length,
            'steps': charges, 'total_steps': sum(charges.values()),
            'visited_spans': spans, 'retained_cells': sum(spans)}


def controls(programs):
    table = programs['produce'].instructions
    first_zero = next(i for i, row in enumerate(table) if row == ('write', p.GUIDE, p.ZERO))
    blank_write = next(i for i, row in enumerate(table) if row == ('write', p.GUIDE, p.BLANK))
    last_return = max(i for i, row in enumerate(table) if row == ('move', p.GUIDE, -1))
    retirement = programs['retire'].instructions
    final_erase = max(i for i, row in enumerate(retirement) if row == ('write', p.GUIDE, p.BLANK))
    faults = [('wrong zero bit', 'produce', first_zero, ('write', p.GUIDE, p.ONE)),
              ('missing represented blank write', 'produce', blank_write, ('goto', blank_write + 1)),
              ('premature right marker', 'produce', first_zero, ('write', p.GUIDE, p.RIGHT)),
              ('missing guide origin return', 'produce', last_return, ('goto', last_return + 1)),
              ('retained guide left marker', 'retire', final_erase, ('goto', final_erase + 1))]
    results = []
    for label, phase, index, row in faults:
        changed = list(programs[phase].instructions)
        changed[index] = row
        mutant = dict(programs, **{phase: Program(tuple(changed), 7, programs[phase].entry)})
        try:
            check_shape(3, 2, mutant, independent=False)
        except ValueError as error:
            need(str(error) in ('exact immutable source guide', 'complete head return', 'complete guide retirement'), 'semantic mutation rejection')
            results.append({'fault': label, 'rejected_by': str(error)})
        else:
            raise ValueError('instruction fault accepted')
    tapes, _ = fixture(3, 2)
    tapes[p.N].cells[3] = p.ZERO
    tapes[p.N].cells[4] = p.RIGHT
    try:
        Machine(programs['produce'], tapes).run(10000)
    except Rejected as error:
        need(str(error) == 'positive canonical binary extent and empty conversion workspace', 'noncanonical descriptor cause')
        results.append({'fault': 'redundant high zero in binary N', 'rejected_by': str(error)})
    else:
        raise ValueError('noncanonical descriptor accepted')
    return results


def main():
    programs = p.build()
    tables = {name: {'tapes': obj.tapes, 'entry': obj.entry, 'instructions': obj.instructions}
              for name, obj in programs.items()}
    cases = [check_shape(n, width, programs) for n in (1, 2, 3, 4, 7, 8, 15, 16, 31, 32) for width in (1, 2, 3, 17)]
    cases.extend(check_shape(n, width, programs) for n, width in ((512, 1), (1024, 3)))
    result = {'cases': cases, 'controls': controls(programs), 'tapes': 7,
              'table_rows': {name: len(obj.instructions) for name, obj in programs.items()},
              'tables_sha256': sha256(encoded(tables)).hexdigest(),
              'all_cases_dense_checked': True, 'lifecycle_step_bound': '72L',
              'historical_visited_cell_bound': '7L'}
    files = {'TABLES.json': tables, 'RESULT.json': result}
    if sys.argv[1:] == ['--write']:
        need(all(not (HERE / file).exists() for file in files), 'do not replace checked receipts')
        for file, value in files.items():
            (HERE / file).write_text(json.dumps(value, indent=2) + '\n')
    else:
        need(not sys.argv[1:], 'unexpected arguments')
        for file, value in files.items():
            need(encoded(value) == encoded(json.loads((HERE / file).read_text())), 'complete emitted receipt')
    print('PASS_CURRENT_FLAT_GUIDE_LIFECYCLE ' + json.dumps({k: v for k, v in result.items() if k != 'cases'}, sort_keys=True))


if __name__ == '__main__':
    main()
