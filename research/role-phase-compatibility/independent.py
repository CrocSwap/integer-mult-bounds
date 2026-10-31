#!/usr/bin/env python3
"""Independent integer-dyadic column replay and relaxed event-gauge graph.

No primary verifier, Fraction arithmetic, Clifford compiler, or pricing routine
is imported. Native phase values are the separately dense-checked certificate.
"""
from collections import deque
from hashlib import sha256
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research/p104-helper470-twin-rung-removal/WORD.json.gz'
WORD_HASH = '7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f'
CONTACTS = {8255:(229,227,1,1), 9031:(225,227,-1,1),
            9034:(231,225,1,-1), 9916:(229,87,1,1),
            9924:(231,27,1,1), 9982:(229,238,1,1),
            9983:(231,7,1,1), 9997:(231,81,1,1)}
PHASES = {9901:1,9904:1,9938:0,9955:1,9987:0,9994:0}


def demand(ok, reason):
    if not ok:
        raise ValueError(reason)


def normalize(numerator, exponent):
    if numerator == 0:
        return (0, 0)
    while exponent and numerator % 2 == 0:
        numerator //= 2
        exponent -= 1
    return numerator, exponent


def coefficient(text):
    parts = text.split('/')
    demand(len(parts) in (1,2), 'Rational text')
    numerator = int(parts[0])
    denominator = int(parts[1]) if len(parts) == 2 else 1
    demand(denominator > 0 and denominator & (denominator-1) == 0, 'Dyadic coefficient')
    return normalize(numerator, denominator.bit_length()-1)


def addition(a, b):
    exponent = max(a[1], b[1])
    return normalize((a[0] << (exponent-a[1])) + (b[0] << (exponent-b[1])), exponent)


def multiplication(a, b):
    return normalize(a[0]*b[0], a[1]+b[1])


def column_replay(program):
    columns = sorted({column for row in CONTACTS.values() for column in row[:2]})
    samples = {event:{} for event in CONTACTS}
    for column in columns:
        values = [(0,0)] * 799
        values[column] = (1,0)
        for event, instruction in enumerate(program[:9998]):
            operation, target = instruction[:2]
            if event in CONTACTS:
                source = instruction[2]
                samples[event][column] = (values[target], values[source])
            if operation in ('INIT','CLEAR'):
                values[target] = (0,0)
            elif operation == 'SCALE':
                values[target] = multiplication(values[target], coefficient(instruction[2]))
            elif operation in ('ADD','COPY'):
                source, q = instruction[2:4]
                values[target] = addition(values[target], multiplication(coefficient(q), values[source]))
            else:
                demand(operation == 'MOVE', 'Known operation')
    for event, (x, y, first, second) in CONTACTS.items():
        demand(samples[event][x] == ((first,0),(0,0)), 'First independent coordinate')
        demand(samples[event][y] == ((0,0),(second,0)), 'Second independent coordinate')
    return len(columns), samples


def graph(program, width, omit=None, phases=None):
    """Every other event is a free new gauge: this only relaxes compatibility."""
    phases = PHASES if phases is None else phases
    nodes = list(range(799))
    adjacent = {}
    for index, instruction in enumerate(program[:9998]):
        operation, target = instruction[:2]
        previous, fresh = nodes[target], 799+index
        if index in CONTACTS and index != omit:
            source = nodes[instruction[2]]
            constraints = ((previous,fresh,0),(source,fresh,0))
        elif index in phases:
            constraints = ((previous,fresh,-width*phases[index]),)
        else:
            constraints = ()
        for u,v,difference in constraints:
            adjacent.setdefault(u,[]).append((v,difference % 4))
            adjacent.setdefault(v,[]).append((u,(-difference) % 4))
        nodes[target] = fresh
    return adjacent


def consistent(adjacent):
    labels = {}
    for root in adjacent:
        if root in labels:
            continue
        labels[root] = 0
        queue = deque([root])
        while queue:
            current = queue.popleft()
            for other, difference in adjacent[current]:
                proposed = (labels[current]+difference) % 4
                if other in labels:
                    if labels[other] != proposed:
                        return False
                else:
                    labels[other] = proposed
                    queue.append(other)
    return True


def main():
    raw = SOURCE.read_bytes()
    demand(sha256(raw).hexdigest() == WORD_HASH, 'Exact source bytes')
    word = json.loads(gzip.decompress(raw))
    program = word['program']
    columns, samples = column_replay(program)
    for width in range(1,33):
        demand(consistent(graph(program,width)) == (width % 4 == 0), 'Relaxed graph criterion')
        demand(consistent(graph(program,width,omit=9997)), 'Missing final ADD opens cycle')
        repaired = dict(PHASES)
        repaired[9955] = 0
        demand(consistent(graph(program,width,phases=repaired)), 'Altered native phase opens cycle')
    # Verify the emitted primary table against these independently computed columns.
    receipt = json.loads((HERE/'RESULT.json').read_text())
    for event, (x,y,a,b) in CONTACTS.items():
        row = receipt['independent_adds'][str(event)]
        demand(row == {'columns':[x,y], 'matrix':[[str(a),'0'],['0',str(b)]],
                       'determinant':str(a*b)}, 'Independent retained minor')
    demand(receipt['native_move_phases'] == {str(k):v for k,v in PHASES.items()}, 'Phase certificate agreement')
    print(json.dumps({'integer_dyadic_columns':columns,'column_events':columns*9998,
                      'independent_minors':len(samples),'width_graphs':32,
                      'opened_cycle_controls':64},sort_keys=True))
    print('PASS_INDEPENDENT_ROLE_PHASE columns=9 contacts=8 relaxed_graphs=32')


if __name__ == '__main__':
    main()
