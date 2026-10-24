"""Independent event replay, bounded query checks, and frozen receipt.

JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
Host integers below belong to the external test oracle, never machine control.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

P = Path(__file__).resolve().parent

def need(value, message):
    if not value: raise ValueError(message)

def load_machine():
    spec = importlib.util.spec_from_file_location('rom_query_machine', P / 'machine.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

def validate_program(m, program):
    registers = set()
    for inst in program:
        op, *a = inst
        if op in ('read', 'write', 'write_reg', 'move'):
            need(a[0] in m.ROLES, 'static role')
        if op in ('write', 'write_reg'):
            need(a[0] not in m.BORROWED, 'borrowed write in program')
        if op == 'move': need(a[1] in (-1, 1), 'unit move in program')
        elif op == 'read': registers.add(a[1])
        elif op == 'write': need(a[1] in 'LR01_', 'tape alphabet')
        elif op == 'write_reg': registers.add(a[1])
        elif op == 'set':
            registers.add(a[0]); need(a[1] in ('0', '1', '=', '<', '>'), 'finite register constant')
        elif op == 'copy': registers.update(a)
        elif op in ('eq', 'eq_reg'):
            registers.add(a[0]); registers.add(a[2])
            if op == 'eq_reg': registers.add(a[1])
            else: need(a[1] in 'LR01_=<>', 'finite equality constant')
        elif op == 'jump': need(type(a[0]) is int and 0 <= a[0] < len(program), 'static jump')
        elif op == 'branch':
            registers.add(a[0]); need(all(type(x) is int and 0 <= x < len(program) for x in a[1:]), 'static branch')
        elif op == 'halt': need(a[0] in ('accept', 'reject'), 'halt state')
        else: need(op == 'move', 'known instruction')
    return sorted(registers)

def audit(m, machine, records, expected_status):
    # Deliberately uses growable cell lists rather than the runner's dictionaries.
    cells = {role: list('L' + records[role] + 'R') if role in records else [] for role in m.ROLES}
    heads = dict.fromkeys(m.ROLES, 0); regs = {}; pc = 0; census = Counter(); halted = False
    for listed_pc, observed in machine.trace:
        need(not halted and listed_pc == pc, 'event PC/control continuity')
        op, *a = machine.program[pc]; pc += 1; census[op] += 1
        if op in ('read', 'write', 'write_reg', 'move'):
            role = a[0]; head = heads[role]; need(head >= 0, 'left boundary')
        if op == 'read':
            actual = cells[role][head] if head < len(cells[role]) else '_'
            need(observed == actual, 'event read content'); regs[a[1]] = actual
        elif op in ('write', 'write_reg'):
            need(role not in m.BORROWED, 'event ownership')
            value = a[1] if op == 'write' else regs[a[1]]
            need(value in 'LR01_' and observed == value, 'event write content')
            while len(cells[role]) <= head: cells[role].append('_')
            cells[role][head] = value
        else:
            need(observed is None, 'noncell event has no readback')
            if op == 'move':
                need(a[1] in (-1, 1), 'unit event move'); heads[role] += a[1]
                need(heads[role] >= 0, 'left boundary after move')
            elif op == 'set': regs[a[0]] = a[1]
            elif op == 'copy': regs[a[1]] = regs[a[0]]
            elif op == 'eq': regs[a[2]] = regs[a[0]] == a[1]
            elif op == 'eq_reg': regs[a[2]] = regs[a[0]] == regs[a[1]]
            elif op == 'branch':
                need(type(regs[a[0]]) is bool, 'Boolean branch register'); pc = a[1] if regs[a[0]] else a[2]
            elif op == 'jump': pc = a[0]
            elif op == 'halt':
                need(a[0] == expected_status, 'expected halt'); halted = True
    need(halted, 'complete halt event')
    need(census == machine.census and pc == machine.pc, 'complete instruction census')
    need(heads == machine.heads and all(h == 0 for h in heads.values()), 'all heads restored')
    need(regs == machine.registers, 'finite-control registers replay')
    for role in m.ROLES:
        expected = {i: x for i, x in enumerate(cells[role]) if x != '_'}
        actual = {i: x for i, x in machine.tapes[role].items() if x != '_'}
        need(actual == expected, 'independent final tape')
    for role in m.BORROWED: need(cells[role] == list('L' + records[role] + 'R'), 'borrowed restoration')
    for role in m.PRIVATE: need(all(x == '_' for x in cells[role]), 'private erasure')
    if expected_status == 'reject': need(all(x == '_' for x in cells['out']), 'rejection output erasure')
    else: need(cells['out'] == ['L', cells['out'][1], 'R'] and cells['out'][1] in '01', 'one-bit output record')
    return dict(sorted(census.items()))

def enc(n): return bin(n)[2:][::-1]

def records(h, s, offset, target, rom):
    return dict(h=enc(h), s=enc(s), offset=enc(offset), target=enc(target), rom=rom)

def execute(m, data, expected, program=None):
    machine = m.Machine(data, trace=True, program=m.PROGRAM if program is None else program)
    status = machine.run()
    need(status == ('reject' if expected is None else 'accept'), 'machine admission')
    counts = audit(m, machine, data, status)
    if expected is not None: need(machine.tapes['out'][1] == expected, 'oracle selected bit')
    return machine, counts

def must_fail(call, message):
    try: call()
    except (ValueError, RuntimeError): return
    raise ValueError('fault control accepted: ' + message)

def verify():
    m = load_machine(); registers = validate_program(m, m.PROGRAM)
    need(m.PROGRAM == m.assemble(), 'same static program')
    cases = []; total_steps = 0; largest_steps = 0; shape_counts = Counter()
    def check(h, s, a, t, rom, family):
        nonlocal total_steps, largest_steps
        x, counts = execute(m, records(h, s, a, t, rom), rom[a * (1 << h) + t])
        steps = sum(counts.values()); w = h + s.bit_length() + 2; M = s * (1 << h)
        need(steps <= 512 * (M + 1) * w * w, 'proved instruction majorant')
        total_steps += steps; largest_steps = max(largest_steps, steps); shape_counts[family] += 1
        cases.append((h, s, a, t, hashlib.sha256(rom.encode()).hexdigest(), steps, counts))
        return x
    # Complete ROM truth tables and addresses for the smallest admissible shape.
    for row in itertools.product('01', repeat=4):
        rom = ''.join(row)
        for a in range(2):
            for t in range(2): check(1, 2, a, t, rom, 'h1_all_roms_all_addresses')
    # Every valid parameter tuple at h=2, under two different ROM patterns.
    for s in range(2, 5):
        for phase in (0, 1):
            rom = ''.join(str(((i * 7) ^ (i // 3) ^ phase) & 1) for i in range(s * 4))
            for a in range(s):
                for t in range(4): check(2, s, a, t, rom, 'h2_all_parameters_two_roms')
    for h in (3, 4, 5):
        for s in (2, (1 << h) - 1, 1 << h):
            rom = ''.join(str(((i * 11) ^ (i // 5)) & 1) for i in range(s * (1 << h)))
            for a, t in ((0, 0), (s - 1, (1 << h) - 1), (s - 1, 1)):
                check(h, s, a, t, rom, 'larger_boundary_parameters')
    fixture = json.loads((P / 'FIXTURE.json').read_text())
    need(fixture['source_commit'] == '26ccde014218f7d906d1251dc295fbc1437ede8a', 'fixture source pin')
    need(hashlib.sha256(bytes(map(int, fixture['rom']))).hexdigest() ==
         'bc0ab563e6d8fdfa24ee89b50dbe3f9a3a6f23681f491e883c6b5aeef07d4104', 'source ROM bytes')
    source_queries = []
    for witness in fixture['witnesses']:
        for q in witness['queries']:
            x = check(5, 17, q['offset'], q['target'], fixture['rom'], 'source_query_epochs')
            need(int(x.tapes['out'][1]) == q['bit'], 'retained source query answer')
            source_queries.append(dict(offset=q['offset'], target=q['target'], bit=q['bit'], instructions=sum(x.census.values())))
    base = records(2, 3, 1, 2, '010101100101')
    rejected = [dict(base, h='0'), dict(base, h=''), dict(base, h='010'), dict(base, s='1'),
                dict(base, s=enc(5)), dict(base, offset=enc(3)), dict(base, target=enc(4)),
                dict(base, offset='00'), dict(base, target='_'), dict(base, rom=base['rom'][:-1]),
                dict(base, rom=base['rom']+'0'), dict(base, rom='01_101100101'), dict(base, rom=''),
                records(65, 2, 0, 0, ''), records(127, (1 << 127) + 1, 0, 0, ''),
                dict(base, h='0' * 129)]
    for data in rejected: execute(m, data, None)
    # Independent ledger checks reject omitted control, changed reads and missing halt.
    x, _ = execute(m, base, base['rom'][6]); original = list(x.trace)
    index = next(i for i, event in enumerate(original) if m.PROGRAM[event[0]][0] == 'eq')
    x.trace = original[:index] + original[index+1:]
    must_fail(lambda: audit(m, x, base, 'accept'), 'omitted equality event')
    x.trace = list(original); index = next(i for i, event in enumerate(original) if m.PROGRAM[event[0]][0] == 'read')
    x.trace[index] = (original[index][0], '1' if original[index][1] != '1' else '0')
    must_fail(lambda: audit(m, x, base, 'accept'), 'wrong read event')
    x.trace = original[:-1]; must_fail(lambda: audit(m, x, base, 'accept'), 'missing halt event')
    bad = list(m.PROGRAM); index = next(i for i, inst in enumerate(bad) if inst[0] == 'move'); bad[index] = ('move', bad[index][1], 0)
    must_fail(lambda: validate_program(m, bad), 'nonunit movement')
    bad = list(m.PROGRAM); index = next(i for i, inst in enumerate(bad) if inst[0] == 'write'); bad[index] = ('write', 'rom', '0')
    must_fail(lambda: validate_program(m, bad), 'borrowed mutation')
    bad = list(m.PROGRAM); index = next(i for i, inst in enumerate(bad) if inst == ('write', 'count', '_')); bad[index] = ('write', 'count', '0')
    must_fail(lambda: execute(m, base, base['rom'][6], bad), 'dirty private cells')
    bad = list(m.PROGRAM); index = next(i for i, inst in enumerate(bad) if inst[0] == 'write_reg' and inst[1] == 'out'); bad[index] = ('write', 'out', '1')
    zero = dict(base, rom='0'*12)
    must_fail(lambda: execute(m, zero, '0', bad), 'wrong selected answer')
    return dict(status='PASS_UNIFORM_ROM_QUERY_COMPONENT', program_instructions=len(m.PROGRAM),
                registers=registers, tapes=len(m.ROLES), accepted_cases=len(cases),
                case_families=dict(sorted(shape_counts.items())), rejected_records=len(rejected),
                fault_controls=7, measured_total_instructions=total_steps, measured_max_instructions=largest_steps,
                source_queries=source_queries, case_digest=hashlib.sha256(json.dumps(cases, sort_keys=True).encode()).hexdigest(),
                machine_sha256=hashlib.sha256((P/'machine.py').read_bytes()).hexdigest(),
                fixture_sha256=hashlib.sha256((P/'FIXTURE.json').read_bytes()).hexdigest(),
                instruction_bound='512*(s*2^h+1)*(h+bit_length(s)+2)^2',
                binary_action_bound='65536*(s*2^h+1)*(h+log2(s)+1)^2',
                excluded=['ROM and header preparation', 'source descriptor serialization adapter', 'CRT reconstruction', 'complete repair/compiler/E tariff', 'host observer overhead'])

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--write-result', action='store_true'); args = parser.parse_args()
    result = verify()
    if args.write_result: (P/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else: need(result == json.loads((P/'RESULT.json').read_text()), 'frozen result receipt')
    print(json.dumps(result, sort_keys=True))

if __name__ == '__main__': main()
