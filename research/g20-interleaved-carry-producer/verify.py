"""Check every released column, bit stream, and the physical packet ABI."""
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import importlib.util
import json
from pathlib import Path
import random
import sys

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
    return module


C = load('new_carry_producer', P/'producer.py')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def stream(low, q):
    for bit in range(q.bit_length()):
        yield tuple((x >> bit) & 1 for x in (*low, q))


def decode(packet):
    return sum(bit << i for i, bit in enumerate(packet))-16


def oracle(column, low, q):
    value = sum(x*a for x, a in zip(low, column))
    target = value.numerator*pow(value.denominator, -1, q) % q
    result = 4*(value-target)/q
    C.require(result.denominator == 1, 'integral reference packet')
    return int(result)


def columns(source):
    for basis in ('ports', 'scale_free_ports'):
        C.require([x['port'] for x in source[basis]] == list(range(111)), 'complete port list')
        for record in source[basis]:
            for direction in ('forward', 'inverse'):
                images = []
                for i in range(8):
                    row = [F(i == j) for j in range(8)]
                    for op in record[direction]:
                        if op[0] == 'ADD':
                            row[op[2]] += F(op[-1])*row[op[1]]
                        else:
                            C.require(op[0] == 'SCALE', 'source operation')
                            row[op[1]] *= F(op[-1])
                    images.append(row)
                for j, col in enumerate(zip(*images)):
                    yield (basis, record['port'], direction, j), col


def physical_packets(fixtures):
    base = ROOT/'research/runtime-quarter-carry'
    modules = {}
    try:
        for name in ('machine', 'counters', 'shear'):
            modules[name] = load(name, base/'inputs'/f'{name}.py')
            sys.modules[name] = modules[name]
        dense = load('carry_dense', base/'inputs/independent.py')
        descriptor = load('carry_descriptor', base/'inputs/descriptor.py')
        quarter = load('carry_quarter', base/'inputs/offset.py')
        kernel = load('carry_kernel', base/'kernel.py')
    finally:
        for name in modules:
            sys.modules.pop(name, None)
    calls = largest = 0
    for inverse in (False, True):
        program = kernel.quarter_program(modules, descriptor, quarter, inverse)
        table = dict(tapes=program.tapes, entry=program.entry, instructions=program.instructions)
        for label, column, low, q, width in fixtures:
            packet = C.produce(C.compile_column(column), stream(low, q))
            code = decode(packet)
            high = q**width
            shape = (1, high, 2)
            payload = [int((i*i+3*i+1) % 7 < 3) for i in range(2*high)]
            origins = [7*t-39 for t in range(19)]
            bank = [({o-4:dense.ONE, o:dense.MARK, o+6:dense.RIGHT}, o) for o in origins]
            bank[0] = dense.marked([dense.ONE if b else dense.ZERO for b in payload], origins[0])
            for tape, extent in zip((4, 5, 7), shape):
                bank[tape] = dense.binary(extent, origins[tape])
            for tape in (*kernel.WORK, 14):
                bank[tape] = ({}, origins[tape])
            bank[16] = dense.marked([dense.ONE if b else dense.ZERO for b in packet], origins[16])
            states, steps = dense.execute(table, bank, 468*len(payload))
            offset = code*pow(4, -1, high) % high
            sign = -1 if inverse else 1
            expected = [payload[((i//2-sign*offset) % high)*2+i%2] for i in range(len(payload))]
            cells, head = dense.marked([dense.ONE if b else dense.ZERO for b in expected], origins[0])
            C.require(states[0].snapshot() == cells and states[0].head == head, 'physical output owner')
            for tape, state in enumerate(states[1:], 1):
                if tape in (*kernel.WORK, 14):
                    C.require(not state.snapshot() and state.head == bank[tape][1], 'physical cleanup')
                else:
                    C.require(state.snapshot() == bank[tape][0] and state.head == bank[tape][1], 'physical spectator')
            C.require(steps <= 468*len(payload), 'retained consumer tariff')
            largest = max(largest, steps)
            calls += 1
    return calls, largest


def reject(name, function):
    try:
        function()
    except ValueError:
        return name
    raise ValueError('accepted control: '+name)


def run():
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            C.require(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'source hash '+row['path'])
    source = json.loads((ROOT/'research/g20-fused-qadic-carries/inputs/source-RESULT.json').read_text())
    records = list(columns(source))
    C.require(len(records) == 3552, 'all 444 routes and 3552 columns')
    unique = sorted({col for _, col in records})
    rng = random.Random(6456)
    digest = sha256()
    cases = exhaustive = long_cases = 0
    physical = {}
    maximum_bits = maximum_comparisons = 0
    for label, col in records:
        plan = C.compile_column(col)
        maximum_bits = max(maximum_bits, C.state_bits(plan))
        maximum_comparisons = max(maximum_comparisons, len(plan[3]))
        for q in (1, 3, 5, 25, 2**89-1):
            lows = [[rng.randrange(q) for _ in range(8)],
                    [q-1 if a < 0 else 0 for a in col],
                    [q-1 if a > 0 else 0 for a in col]]
            for low in lows:
                packet = C.produce(plan, stream(low, q))
                code = decode(packet)
                C.require(code == oracle(col, low, q), 'independent inverse-based oracle')
                digest.update(canonical([label, q, low, packet]))
                cases += 1
                if q == 5 and code not in physical:
                    physical[code] = (label, col, low, q, 1 if code != -3 else 3)
    for col in unique:
        plan = C.compile_column(col)
        support = [i for i, a in enumerate(col) if a]
        for values in product(range(3), repeat=len(support)):
            low = [0]*8
            for i, value in zip(support, values):
                low[i] = value
            C.require(decode(C.produce(plan, stream(low, 3))) == oracle(col, low, 3), 'complete active low domain')
            exhaustive += 1
    for col in unique[::120]:
        q = 2**4097-1
        low = [rng.randrange(q) for _ in range(8)]
        C.require(decode(C.produce(C.compile_column(col), stream(low, q))) == oracle(col, low, q), 'long bounded-state input')
        long_cases += 1
    C.require(-3 in physical, 'nonintegral physical carry fixture')
    calls, largest = physical_packets([physical[k] for k in sorted(physical)])
    col = (F(1, 4), F(1), F(0), F(0), F(0), F(0), F(0), F(0))
    plan = C.compile_column(col)
    valid = list(stream([1, 0, 0, 0, 0, 0, 0, 0], 5))
    controls = [reject('even radix', lambda:C.produce(plan, stream([0]*8, 4))),
        reject('noncanonical low', lambda:C.produce(plan, stream([5]+[0]*7, 5))),
        reject('empty stream', lambda:C.produce(plan, [])),
        reject('leading zero radix', lambda:C.produce(plan, valid+[(0,)*9])),
        reject('bad symbol', lambda:C.produce(plan, [(0,)*8+(2,)])),
        reject('truncated tuple', lambda:C.produce(plan, [(0,)*8])),
        reject('wrong denominator', lambda:C.compile_column([F(1, 8)]+[0]*7)),
        reject('outside packet envelope', lambda:C.compile_column([5]+[0]*7)),
        reject('omit correction', lambda:C.require(oracle(col, [1]+[0]*7, 5) == 0, 'nonzero carry')),
        reject('wrong source sign', lambda:C.require(oracle(col, [1]+[0]*7, 5) ==
            oracle(tuple(-x for x in col), [1]+[0]*7, 5), 'signed packet'))]
    return dict(routes=444, columns=len(records), distinct_columns=len(unique), source_cases=cases,
        exhaustive_active_cases=exhaustive, long_bit_cases=long_cases, largest_input_bits=4097,
        state_encoding_bits=maximum_bits, maximum_threshold_comparisons=maximum_comparisons,
        physical_consumer_calls=calls, physical_codes=sorted(physical), maximum_consumer_steps=largest,
        transcript_sha256=digest.hexdigest(), rejected_controls=controls,
        scope='One-pass interleaved producer and actual packet consumer. Physical low-cache access and complete caller remain open.')


if __name__ == '__main__':
    C.require(sys.argv[1:] in ([], ['--write']), 'supported arguments')
    result = run()
    if sys.argv[1:] == ['--write']:
        (P/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        C.require(result == json.loads((P/'RESULT.json').read_text()), 'complete recorded result')
    print('PASS_G20_INTERLEAVED_CARRY_PRODUCER')
    print(json.dumps(result, sort_keys=True))
