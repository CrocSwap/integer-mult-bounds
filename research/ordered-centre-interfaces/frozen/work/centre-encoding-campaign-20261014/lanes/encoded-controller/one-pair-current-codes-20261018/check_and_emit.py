#!/usr/bin/env python3
"""Check the three-call current-cut controller and its scalar port codes."""

from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
DATA = LANES / 'oblique-native-20261017/matched-native-involution'
DATA_PIN = '95f11d2b13fc75cb0d07e79ea17afdf3f46b4aca294117ffe1a988779e99f025'
RECEIPT_PIN = '7bc873d627e022d4677b740633c9cd5f86c5e675d84460d538b4b6314c79536c'


def need(test, message):
    if not test:
        raise ValueError(message)


def add(target, source, scalar=F(1)):
    for key, coefficient in source.items():
        value = target.get(key, 0) + scalar * coefficient
        if value:
            target[key] = value
        else:
            target.pop(key, None)


def product(left, right):
    result = []
    for row in left:
        out = {}
        for j, c in row.items():
            add(out, right[j], c)
        result.append(out)
    return result


def apply_gates(gates, size=112):
    rows = [{i: F(1)} for i in range(size)]
    for gate in gates:
        op, target = gate[:2]
        need(0 <= target < size, 'Scalar target range')
        if op == 'scale':
            c = F(*gate[2:])
            rows[target] = {j: c * v for j, v in rows[target].items() if c * v}
        else:
            source = gate[2]
            need(op == 'add' and 0 <= source < size and source != target, 'Scalar source range')
            add(rows[target], rows[source], F(*gate[3:]))
    return rows


def inverse_gates(gates):
    out = []
    for gate in reversed(gates):
        if gate[0] == 'scale':
            c = 1 / F(*gate[2:])
            out.append(['scale', gate[1], c.numerator, c.denominator])
        else:
            c = -F(*gate[3:])
            out.append(['add', gate[1], gate[2], c.numerator, c.denominator])
    return out


def scalar_cost(gates):
    total = 0
    for gate in gates:
        c = F(*gate[-2:])
        a, b = abs(c.numerator), c.denominator
        need(a > 0 and b & (b - 1) == 0, 'Dyadic scalar')
        if gate[0] == 'scale':
            need(a & (a - 1) == 0, 'Dyadic unit scale')
            total += 2 * (abs(a.bit_length() - b.bit_length()) + (c < 0))
        else:
            total += 2 * (3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1)
    return total


def scalar_code(word, response):
    entrance = []
    for pair in word['pair_codes']:
        for op, target, source, value in pair['code']:
            if target >= 112:
                continue
            c = F(value)
            entrance.append([op, target, c.numerator, c.denominator] if op == 'scale'
                            else [op, target, source, c.numerator, c.denominator])
    exit_code = inverse_gates(entrance)
    a, ai = apply_gates(entrance), apply_gates(exit_code)
    identity = [{i: F(1)} for i in range(112)]
    need(product(a, ai) == product(ai, a) == identity, 'Both pair-code inverse orders')
    middle = product(product(a, response), ai)
    need(all(len(row) == 1 and abs(next(iter(row.values()))) == 1 for row in middle),
         'The middle code is a signed permutation')
    permutation = [next(iter(row)) for row in middle]
    signs = [next(iter(row.values())) for row in middle]
    need(sorted(permutation) == list(range(112)), 'Bijective middle code')
    middle_code, cycles, visited = [], [], set()
    for first in range(112):
        if first in visited:
            continue
        cycle, p = [], first
        while p not in visited:
            visited.add(p)
            cycle.append(p)
            p = permutation[p]
        need(p == first, 'Permutation cycle closes')
        cycles.append(cycle)
        for x, y in zip(cycle, cycle[1:]):
            middle_code += [['add', x, y, 1, 1], ['add', y, x, -1, 1],
                            ['add', x, y, 1, 1], ['scale', y, -1, 1]]
    middle_code += [['scale', i, -1, 1] for i, c in enumerate(signs) if c == -1]
    need(apply_gates(middle_code) == middle, 'Every signed permutation input')
    gates = entrance + middle_code + exit_code
    need(apply_gates(gates) == response, 'All112 scalar response columns')
    need(apply_gates(inverse_gates(gates)) == response, 'The actual scalar response is its inverse')
    return gates, {'scalar_gates': len(gates), 'real_scalar_primitives': scalar_cost(gates),
                   'middle_cycles': cycles, 'owned_fields': 0, 'private_fields': 0,
                   'native_children': 0, 'conservative_stage_views': 224}


def reduce_word(word):
    out = []
    for symbol in word:
        if out and out[-1] == -symbol:
            out.pop()
        else:
            out.append(symbol)
    return tuple(out)


def left(symbol, row):
    out = {}
    for (source, word), value in row.items():
        add(out, {(source, reduce_word((symbol,) + word)): value})
    return out


PROGRAM = [
    ['forward', 0], ['code_X', 0, 1],
    ['code_Y', 1, 1], ['backward', 1], ['code_X', 1, 1],
    ['code_Y', 2, 1], ['forward', 2], ['code_X', 1, -1],
]


def replay(program, raw=False):
    x = {(0, (-4,) if raw else ()): F(1)}
    y = {(1, ()): F(1)}
    for event in program:
        kind, stage = event[:2]
        symbol = stage + 1
        if kind == 'forward':
            add(y, left(symbol, x))
        elif kind == 'backward':
            add(x, left(-symbol, y), -1)
        elif kind == 'code_X':
            x = left(event[2] * symbol, x)
        else:
            need(kind == 'code_Y', 'Known controller event')
            y = left(event[2] * symbol, y)
    return x, y


def main():
    raw = gzip.decompress((DATA / 'MATCHED-NATIVE-PROGRAM.json.gz').read_bytes())
    need(sha256(raw).hexdigest() == DATA_PIN, 'Frozen data word')
    need(sha256((DATA / 'MATCHED-NATIVE-RECEIPT.json').read_bytes()).hexdigest() == RECEIPT_PIN,
         'Frozen native receipt')
    source = json.loads(raw)
    response = [{int(j): F(v) for j, v in row.items()} for row in source['response']]
    identity = [{i: F(1)} for i in range(112)]
    need(product(response, response) == identity, 'Actual full response involution')
    need(all(response[i].get(j, 0) == response[j].get(i, 0) for i in range(112) for j in range(112)),
         'Actual response symmetry')
    payload = {'schema': 'one-pair-current-code-controller-v1', 'data_payload_pin': DATA_PIN,
               'program': PROGRAM, 'providers': {}}
    receipt = {'status': 'PASS_ONE_PAIR_CURRENT_CODES', 'providers': {}}
    for provider, item in source['providers'].items():
        gates, bill = scalar_code(item['forward'], response)
        profile = Counter(e[4] for e in item['forward']['events'] if e[0] == 'native')
        need(sum(k * v for k, v in profile.items()) == 1792, 'Data call mass')
        payload['providers'][provider] = {'scalar_E_code': gates, 'scalar_E_inverse_code': inverse_gates(gates)}
        receipt['providers'][provider] = {'one_code': bill, 'three_call_native_profile':
                                         dict(sorted((k, 3 * v) for k, v in profile.items())),
                                         'three_call_native_mass': 5376,
                                         'local_and_five_code_real_scalar': 3 * 3032 + 5 * bill['real_scalar_primitives'],
                                         'old_terminal_real_scalar': 2688,
                                         'five_code_view_bound': 1120,
                                         'naive_terminal_extra_rank_one_children': 224,
                                         'naive_terminal_scalar_inverse_codes': 3,
                                         'new_borrowed_or_owned_fields': 0}
    x, y = replay(PROGRAM)
    need(x == {(1, ()): -1} and y == {(0, (3, 2, 1)): 1}, 'Ordered generic three-call endpoint')
    xr, yr = replay(PROGRAM, raw=True)
    # q acts on Y before the retained Q^2 terminal. No E is moved through Q.
    preterminal_y = left(-4, yr)
    final_x = left(4, left(4, preterminal_y))
    final_y = {k: -v for k, v in xr.items()}
    need(final_x == {(0, (4, 3, 2, 1, -4)): 1} and final_y == {(1, ()): 1},
         'Physical Q T Q^-1 endpoint')
    decoded = final_x
    for symbol in (-4, -3, -2, -1, 4):
        decoded = left(symbol, decoded)
    need(decoded == {(0, ()): 1}, 'Ordered two-pass terminal inverse')
    rejected = []
    for i, event in enumerate(PROGRAM):
        if event[0].startswith('code_'):
            xx, yy = replay(PROGRAM[:i] + PROGRAM[i+1:])
            need((xx, yy) != (x, y), 'Omitted current code changes the endpoint')
            rejected.append(i)
    receipt.update({'generic_ordered_endpoint': ['-y', 'E2 E1 E0 x'],
                    'physical_raw_output_code': ['Q E2 E1 E0 Q^-1', 'I'],
                    'omitted_code_controls': rejected,
                    'future_X_codes': 0, 'past_Y_codes': 0,
                    'scope': 'Current-cut code circuit and exact residual. Full terminal access, global hosting, and complete kappa cost are separate.'})
    data = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    (HERE / 'PROGRAM.json').write_bytes(data + b'\n')
    receipt['payload_sha256'] = sha256(data + b'\n').hexdigest()
    receipt['checker_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    (HERE / 'CHECKS.json').write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
