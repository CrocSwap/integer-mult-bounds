"""Independent exact four-edit endpoint gate at q=-1 and body=1."""
from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from math import lcm
from pathlib import Path
from time import monotonic

CALLER_HEAD = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
COMPARATOR = '9d0119eb12fbd9fa534b48cd37b68e7099757b91'
CALLER_SHA = '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'
ADMISSION_SHA = '41b8a189dffeb768e5843446cdc469f9cc2f0aa038d0a593cf2be43aa009a9a3'
CASE_LIMIT = 1950
SECONDS = 27


def no_duplicates(rows):
    value = dict(rows)
    if len(value) != len(rows):
        raise ValueError('duplicate input key')
    return value


def authenticated_json(path, expected):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != expected:
        raise ValueError('changed input: ' + path.name)
    return json.loads(raw, object_pairs_hook=no_duplicates)


def unit_vector(n, i):
    value = [Fraction(0)] * n
    value[i] = Fraction(1)
    return value


def signed(power):
    return 1 if power % 2 == 0 else -1


def decode(event, offset):
    if event[0] == 'J':
        a, b, left, right = event[3]
        return ('shears', a - offset, b - offset, -Fraction(left), -Fraction(right))
    if event[0] != 'B':
        return None
    op, field, *args = event[1:]
    role = field - offset
    if op == 'ADD':
        return ('add', role, args[0] - offset, Fraction(args[1]))
    if op == 'QUERY':
        return ('add', role, args[0] - offset, signed(args[1]))
    if op == 'SWAP':
        return ('swap', role, args[0] - offset)
    if op == 'SCALE':
        return ('scale', role, Fraction(args[0]))
    if op == 'IDLE_ODD':
        return ('scale', role, signed(args[1]))
    assert op in ('IDLE_ONE', 'LAMBDA')
    return None


def update(vector, gate):
    if gate is None:
        return
    opcode, a, b, *extra = gate
    if opcode == 'add':
        vector[a] += extra[0] * vector[b]
    elif opcode == 'scale':
        vector[a] *= b
    elif opcode == 'swap':
        vector[a], vector[b] = vector[b], vector[a]
    else:
        assert opcode == 'shears'
        left, right = extra
        vector[a] += left * vector[b]
        vector[b] += right * vector[a]


def old_trajectories(gates, sites, n, old_diagonal=None):
    # Keep literal chronological forwards separate from per-case edit evaluation.
    rows = {clock: [] for clock in sites}
    for col in range(n):
        vector = unit_vector(n, col)
        for clock, gate in enumerate(gates):
            update(vector, gate)
            if clock in sites:
                rows[clock].append(vector[sites[clock]])
        if old_diagonal is not None:
            expected = unit_vector(n, col)
            expected[col] *= old_diagonal[col]
            assert vector == expected, ('old endpoint column', col)

    gains, ends = {}, {}
    for origin, role in sites.items():
        vector = unit_vector(n, role)
        for clock in range(origin + 1, len(gates)):
            update(vector, gates[clock])
            if clock in sites:
                gains[origin, clock] = vector[sites[clock]]
        ends[origin] = vector

    denominator = lcm(*(x.denominator for row in rows.values() for x in row),
                      *(x.denominator for x in gains.values()),
                      *(x.denominator for row in ends.values() for x in row))
    rows = {k: tuple(int(v * denominator) for v in row) for k, row in rows.items()}
    gains = {k: int(v * denominator) for k, v in gains.items()}
    ends = {k: tuple(int(v * denominator) for v in row) for k, row in ends.items()}
    return denominator, rows, gains, ends


def differences(data, clocks, col):
    d, rows, gains, ends = data
    powers = [d ** i for i in range(len(clocks) + 2)]
    injected = []
    for j, clock in enumerate(clocks):
        arrived = rows[clock][col] * powers[j]
        for i, previous in enumerate(clocks[:j]):
            arrived += injected[i] * gains[previous, clock] * powers[j - i - 1]
        injected.append(-2 * arrived)
    if not any(injected):
        return
    weights = [v * powers[len(clocks) - i - 1] for i, v in enumerate(injected)]
    denominator = powers[len(clocks) + 1]
    for row, endpoint in enumerate(zip(*(ends[c] for c in clocks))):
        numerator = sum(a * b for a, b in zip(weights, endpoint))
        if numerator:
            yield row, Fraction(numerator, denominator)


def first_difference(data, clocks, n):
    for col in range(n):
        for row, value in differences(data, clocks, col):
            return col, row, value
    return None


def direct(gates, sites, clocks, col, n):
    old = unit_vector(n, col)
    changed = old.copy()
    for clock, gate in enumerate(gates):
        update(old, gate)
        update(changed, gate)
        if clock in clocks:
            changed[sites[clock]] *= -1
    return {i: value - before for i, (before, value) in enumerate(zip(old, changed)) if value != before}


def controls():
    gates = [('scale', 0, -1), None, ('scale', 0, -1), None]
    sites = {0: 0, 1: 1, 2: 0, 3: 1}
    data = old_trajectories(gates, sites, 2, (1, 1))
    assert first_difference(data, (0, 1), 2) == (0, 0, Fraction(-2))
    assert first_difference(data, (2, 3), 2) == (0, 0, Fraction(-2))
    assert first_difference(data, (0, 1, 2, 3), 2) is None
    gates = [('scale', 0, -1), ('shears', 0, 1, Fraction(-1, 2), Fraction(1, 3)), None,
             ('swap', 0, 2), ('scale', 1, -1), ('add', 0, 2, Fraction(-3, 5)), None]
    sites = {0: 0, 2: 1, 4: 1, 6: 2}
    data = old_trajectories(gates, sites, 3)
    edits = [(0,), (0, 2), (0, 2, 4, 6)]
    for clocks, col in product(edits, range(3)):
        assert dict(differences(data, clocks, col)) == direct(gates, sites, clocks, col, 3)
    return {'two_individually_failing_pairs_cancel': True, 'fractional_noncommuting_direct_columns': 9}


def run(caller, control_result, price, price_sha, started):
    assert caller['stages'] == 17
    block = caller['types']['B']
    offset, n = block['offset'], block['roles']
    assert (offset, n, len(block['ports'])) == (36, 36, 8)
    old, new = {}, {}
    for clock, event in enumerate(caller['events']):
        if event[:2] == ['B', 'IDLE_ODD']:
            assert len(event[3]) == 1 and event[4:] == [-1]
            old[clock] = (event[2] - offset, event[3])
        elif event[:2] == ['B', 'IDLE_ONE'] and len(event[3]) > 1:
            new[clock] = (event[2] - offset, event[3])
    assert len(old) == 4 and len(new) == 26
    stock = old | new
    assert all(0 <= role < n and len(set(mask)) == len(mask) and all(1 <= s <= 17 for s in mask)
               for role, mask in stock.values())
    cases = sorted(tuple(sorted(odd + even)) for odd in combinations(old, 2) for even in combinations(new, 2))
    assert len(cases) == len(set(cases)) == CASE_LIMIT
    priced = []
    for item in price['keys']:
        assert len(item['odd']) == len(item['even']) == 2
        assert all(clock in old for clock in item['odd']) and all(clock in new for clock in item['even'])
        shape = sorted(len(new[clock][1]) for clock in item['even'])
        assert item['price'] == ','.join(map(str, shape)) and item['price'] in price['prices']
        priced.append(tuple(sorted(item['odd'] + item['even'])))
    assert sorted(priced) == cases, 'price scope differs from literal caller'
    gates = [decode(event, offset) for event in caller['events']]
    data = old_trajectories(gates, {c: x[0] for c, x in stock.items()}, n,
                            [signed(x[0]) for x in block['diagonal']])
    records = []
    for key in cases:
        if monotonic() - started >= SECONDS:
            break
        mismatch = first_difference(data, key, n)
        if mismatch is None:
            records.append({'key': key, 'first_difference': None})
        else:
            col, row, value = mismatch
            records.append({'key': key, 'first_difference': [col + offset, row + offset, str(value)]})
    unvisited = cases[len(records):]
    return {'status': 'HIT_TIME_CAP' if unvisited else 'EXHAUSTED', 'cases': CASE_LIMIT,
            'comparator_head': COMPARATOR, 'caller_head': CALLER_HEAD, 'caller_sha256': CALLER_SHA,
            'admission_sha256': ADMISSION_SHA, 'price_sha256': price_sha, 'controls': control_result,
            'odd_clocks': sorted(old), 'even_clocks': sorted(new), 'old_endpoint_columns': n,
            'common_denominator': data[0], 'records': records, 'tested': len(records),
            'survivors': [r['key'] for r in records if r['first_difference'] is None], 'unvisited': unvisited}


def main():
    started = monotonic()
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, default=Path('inputs'))
    parser.add_argument('--price', type=Path)
    parser.add_argument('--price-sha')
    parser.add_argument('--controls-only', action='store_true')
    args = parser.parse_args()
    assert __debug__
    control_result = controls()
    if args.controls_only:
        print(json.dumps(control_result, sort_keys=True))
        return
    if args.price is None or args.price_sha is None:
        parser.error('authenticate the price-before-decoding receipt first')
    price = authenticated_json(args.price, args.price_sha)
    assert price['head'] == COMPARATOR and price['caller_head'] == CALLER_HEAD and price['copies'] == 17
    assert price['input_sha256']['inputs/7113/CALLER.json'] == CALLER_SHA
    admission = authenticated_json(args.inputs / 'ADMITTED.json', ADMISSION_SHA)
    assert admission['status'] == 'independently_reproduced_comparable'
    assert admission['head'] == COMPARATOR and admission['caller_sha256'] == CALLER_SHA
    caller = authenticated_json(args.inputs / 'CALLER.json', CALLER_SHA)
    print(json.dumps(run(caller, control_result, price, args.price_sha, started), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
