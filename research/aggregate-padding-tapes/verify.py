"""Finite tape semantics and independent rectangle-oracle checks."""
import itertools
import argparse
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tapes


def need(value, message):
    if not value:
        raise ValueError(message)


def mask(shape):
    ranges = [range(1 << (q-1).bit_length()) for q in shape]
    return [all(x < q for x, q in zip(point, shape)) for point in itertools.product(*ranges)]


def oracle_pad(shape, bits):
    iterator = iter(bits)
    result = ''.join(next(iterator) if genuine else '0' for genuine in mask(shape))
    need(next(iterator, None) is None, 'oracle exact source length')
    return result


def execute(shape, bits, restrict=False, origin=0, bad_reset=False, trace=False):
    need(len(shape) == 5 and all(type(q) is int and q >= 1 for q in shape), 'shape domain')
    widths = [(q-1).bit_length() for q in shape]
    genuine, padded = math.prod(shape), 1 << sum(widths)
    in_size, out_size = (padded, genuine) if restrict else (genuine, padded)
    need(len(bits) == in_size and set(bits) <= {'0', '1'}, 'payload domain')
    meter = tapes.Meter(trace)
    coordinates, counters, immutable, intervals = [], [], [], []
    for i, (q, length) in enumerate(zip(shape, widths)):
        description = ''.join(str(((q-1) >> j) & 1) for j in range(length))
        template = tapes.Tape(f'template{i}', '^'+description+'$', meter, origin+7*i, writable=False)
        pc = tapes.Tape(f'padded{i}', '^'+'0'*length+'$', meter, origin-11*i)
        gc = tapes.Tape(f'genuine{i}', '^'+'0'*length+'$', meter, origin+13*i)
        for tape in (template, pc, gc):
            intervals.append((tape, tape.origin, tape.origin+length+1))
            tape.cells[tape.origin-1] = '1'
            tape.cells[tape.origin+length+2] = '1'
        immutable.append((template, dict(template.cells)))
        counters += [(pc, dict(pc.cells)), (gc, dict(gc.cells))]
        coordinates.append(tapes.Coordinate(template, pc, gc))
    if bad_reset:
        # Real semantic mutant: keep old genuine-counter contents across cycles.
        for c in coordinates:
            def faulty_tick(c=c):
                carry = tapes.decrement(c.padded)
                if c.active and tapes.decrement(c.genuine):
                    c.active = False
                if carry:
                    c.active = True
                return carry
            c.tick = faulty_tick
    source = tapes.Tape('source', '^'+bits+'$', meter, origin-71, writable=False)
    target = tapes.Tape('target', '^'+'_'*(out_size+1), meter, origin+97)
    for tape, size in ((source, in_size), (target, out_size)):
        tape.cells[tape.origin-1] = '1'
        tape.cells[tape.origin+size+2] = '1'
        intervals.append((tape, tape.origin, tape.origin+size+1))
    immutable.append((source, dict(source.cells)))
    tapes.scan(coordinates, source, target, restrict)
    need(all(t.cells == expected for t, expected in immutable), 'input/descriptor preservation')
    need(all(t.cells == expected for t, expected in counters), 'owned counter cleanup')
    need(all(t.head == t.origin+1 and t.low >= left and t.high <= right for t, left, right in intervals), 'head restoration/local confinement')
    need(target.cells[target.origin-1] == target.cells[target.origin+out_size+2] == '1', 'output neighbors')
    need(target.cells[target.origin] == '^' and target.cells[target.origin+out_size+1] == '$', 'output delimiters')
    need(meter.steps <= 1024*padded+128*sum(widths)+128, 'uniform charged-step bound')
    result = ''.join(target.cells[target.origin+1+i] for i in range(out_size))
    return result, meter.steps, meter.trace


def reject(fn):
    try:
        fn()
    except ValueError:
        return
    raise ValueError('negative control accepted')


def run():
    cases, rows, steps, maximum_ratio = 0, 0, 0, 0
    for p, q, g, s in itertools.product(range(1, 5), repeat=4):
        shape = (p, q, g, q, s)
        bits = ''.join(str((i*7+i//3+q) % 2) for i in range(math.prod(shape)))
        expected = oracle_pad(shape, bits)
        origin = (-19, 0, 41)[cases % 3]
        actual, cost1, _ = execute(shape, bits, origin=origin)
        need(actual == expected, 'independent mixed-radix padding')
        restored, cost2, _ = execute(shape, actual, restrict=True, origin=origin+3)
        need(restored == bits, 'complete dirty round trip')
        # Indexed oracle for an external completed exchange; not a fast callee.
        dimensions = [1 << (x-1).bit_length() for x in shape]
        coordinates = list(itertools.product(*(range(r) for r in dimensions)))
        locations = {v: i for i, v in enumerate(coordinates)}
        exchanged = ''.join(actual[locations[(x[0], x[3], x[2], x[1], x[4])]] for x in coordinates)
        result, cost3, _ = execute(shape, exchanged, restrict=True, origin=origin)
        ordinary = list(itertools.product(*(range(r) for r in shape)))
        lookup = {v: i for i, v in enumerate(ordinary)}
        expected_exchange = ''.join(bits[lookup[(x[0], x[3], x[2], x[1], x[4])]] for x in ordinary)
        need(result == expected_exchange, 'completed exchange composition')
        cases += 1
        rows += len(actual)
        steps += cost1+cost2+cost3
        maximum_ratio = max(maximum_ratio, (cost1+len(actual)-1)//len(actual))
    shape = (1, 2, 3, 2, 1)
    for value in range(1 << 12):
        bits = format(value, '012b')
        padded, _, _ = execute(shape, bits)
        need(padded == oracle_pad(shape, bits), 'all-payload padding')
        need(execute(shape, padded, restrict=True)[0] == bits, 'all-payload restriction')
    micro = 0
    for width in range(8):
        for value in range(1 << width):
            meter = tapes.Meter()
            contents = ''.join(str((value >> j) & 1) for j in range(width))
            tape = tapes.Tape('micro', '^'+contents+'$', meter, origin=-37)
            borrow = tapes.decrement(tape)
            got = sum(int(tape.cells[tape.origin+1+j]) << j for j in range(width))
            need(got == (value-1) % (1 << width) and borrow == (value == 0), 'independent decrement oracle')
            need(tape.head == tape.origin+1 and tape.low >= tape.origin and tape.high <= tape.origin+width+1, 'micro head confinement')
            micro += 1
    for width in (16, 64, 257):
        for value in (0, 1, 1 << (width-1), (1 << width)-1):
            meter = tapes.Meter()
            contents = ''.join(str((value >> j) & 1) for j in range(width))
            tape = tapes.Tape('long-micro', '^'+contents+'$', meter, origin=129)
            borrow = tapes.decrement(tape)
            got = sum(int(tape.cells[tape.origin+1+j]) << j for j in range(width))
            need(got == (value-1) % (1 << width) and borrow == (value == 0), 'long carry chain')
            need(meter.steps <= 8*width+12 and tape.head == tape.origin+1, 'long carry charged/head bound')
            micro += 1
    reject(lambda: execute((2, 2, 3, 2, 1), '1'*24, bad_reset=True))
    reject(lambda: execute((1, 2, 0, 2, 1), ''))
    reject(lambda: execute(shape, '0'*11))
    reject(lambda: execute(shape, '0'*11+'x'))
    changed = oracle_pad((1, 2, 2, 2, 1), '1'*8)
    need(changed != oracle_pad(shape, '1'*12), 'changed shape must not be admitted as same contract')
    a, cost, trace = execute(shape, '101011001101', origin=-123, trace=True)
    b, cost0, _ = execute(shape, '101011001101', origin=0)
    need(a == b and cost == cost0 and trace and len(trace) == cost, 'translated trace and cost')
    return dict(status='PASS_AGGREGATE_PADDING_TAPES',shape_cases=cases,padded_rows=rows,
                all_boolean_payloads=4096,decrement_cases=micro,semantic_controls=5,
                measured_steps_shape_cases=steps,max_padding_steps_per_row_rounded=maximum_ratio,
                tapes=17,primitive_bound='1024*N+128*sum(L_i)+128',
                limits='Fixed-tape scan only; indexed exchange oracle is not a fast callee or joined supplier.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.out and args.out.exists():
        raise ValueError('output already exists')
    saved = None if args.out else json.loads((HERE/'RESULT.json').read_text())
    result = run()
    if args.out:
        with args.out.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(json.dumps(result,indent=2)+'\n')
    else:
        need(json.dumps(result,sort_keys=True) == json.dumps(saved,sort_keys=True), 'typed result receipt')
    print(json.dumps(result,indent=2))
