"""Source-bound rounded-child certificate; no predecessor executable imports."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from arithmetic import execute, need, rotate, wrapper_plan


def inputs():
    root = HERE.parents[1]
    pins = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    data = {}
    for pin in pins['files']:
        if pin['usage'] != 'input':
            continue
        raw = (root / pin['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA256: ' + pin['path'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == pin['git_blob'], 'source blob: ' + pin['path'])
        data[Path(pin['path']).name] = raw
    return json.loads(data['NATIVE.json']), json.loads(data['WORD.json'])


def mul(z, w):
    a, b = z
    c, d = w
    return a * c - b * d, a * d + b * c


def oracle_wrapper(vector, record):
    """Direct phase polynomial; no primary wrapper plan or rotations."""
    result = [(0, 0)] * 512
    for x, (a, b) in enumerate(vector):
        bits = [(x >> j) & 1 for j in range(9)]
        y = record['offset']
        for j, row in enumerate(record['matrix_rows']):
            y ^= (sum(bits[k] * ((row >> k) & 1) for k in range(9)) % 2) << j
        p = record['phase'] + sum(bits[j] * record['linear_Z4'][j] for j in range(9))
        p += 2 * sum(bits[j] * bits[k] * ((record['quadratic_rows'][j] >> k) & 1)
                     for j in range(9) for k in range(j + 1, 9))
        result[y] = mul((a, b), ((1, 0), (0, 1), (-1, 0), (0, -1))[p % 4])
    return result


def oracle(vector, recipe):
    """Closed tensor convolution, denominator 2^rank; no stage recurrence."""
    rank = recipe['rank']
    coefficients = []
    for delta in range(1 << rank):
        z = (1, 0)
        for bit in range(rank):
            z = mul(z, (1, -1 if delta >> bit & 1 else 1))
        coefficients.append(z)
    value = oracle_wrapper(vector, recipe['right'])
    result = [(0, 0)] * 512
    for x, z in enumerate(value):
        if z == (0, 0):
            continue
        for delta, coefficient in enumerate(coefficients):
            a, b = mul(z, coefficient)
            y = x ^ delta
            c, d = result[y]
            result[y] = a + c, b + d
    return oracle_wrapper(result, recipe['left'])


def norm2(vector):
    return sum(a * a + b * b for a, b in vector)


def error_squared(value, F, exact, exact_F):
    common = max(F, exact_F)
    return sum(((a << (common - F)) - (c << (common - exact_F))) ** 2
               for z, w in zip(value, exact) for a, c in zip(z, w)), common


def relative_ok(error_num, error_f, vector, f, b):
    return error_num * (1 << (2 * (b + f))) <= norm2(vector) * (1 << (2 * error_f))


def inverse_wrapper_basis(plan, address=0):
    vector = [(0, 0)] * 512
    x, phase = next((x, phase) for x, (y, phase) in enumerate(plan) if y == address)
    vector[x] = rotate((1, 0), -phase)
    return vector


def fixtures(right):
    basis = inverse_wrapper_basis(right)
    dense = [((x * 104729 + 17) % (1 << 20) - (1 << 19),
              (x * x * 8191 + 31) % (1 << 19) - (1 << 18)) for x in range(512)]
    wide = [((a << 100) + (x % 7), (b << 100) - (x % 11))
            for x, (a, b) in enumerate(dense)]
    child = [(0, 0)] * 512
    child[0], child[1] = (2**20 + 1, 0), (0, 2**20)
    cancel = [(0, 0)] * 512
    for x, (y, phase) in enumerate(right):
        cancel[x] = rotate(child[y], -phase)
    return [('zero', [(0, 0)] * 512), ('unit_basis', basis), ('dense', dense),
            ('wide_dense', wide), ('near_cancellation', cancel)]


def rejected(operation):
    try:
        operation()
    except (ValueError, KeyError):
        return
    raise ValueError('negative control was accepted')


def round_dyadic(value, shift):
    q, rem = divmod(value, 1 << shift)
    twice = 2 * rem
    return q + (twice > 1 << shift or (twice == 1 << shift and q % 2 != 0))


def calculate():
    native, word = inputs()
    bindings, receipts = [], []
    column_digest = hashlib.sha256()
    total_nonzero = 0
    for transport in native['transports']:
        recipe = transport['recipe']
        rank = recipe['rank']
        matches = [(j, e) for j, e in enumerate(word['program'])
                   if e == ['transport', transport['role'], transport['old'], transport['new'], rank]]
        need(len(matches) == 1, 'literal occurrence binding')
        need(rank == len(transport['new']) - len(transport['old']), 'rank dimension gap')
        bindings.append({'role': transport['role'], 'event': matches[0][0], 'rank': rank})
        left, right = wrapper_plan(recipe['left']), wrapper_plan(recipe['right'])
        plans = left, right
        for address in range(512):
            vector = [(0, 0)] * 512
            vector[address] = (1, 0)
            exact = oracle(vector, recipe)
            value, F, defects = execute(vector, 0, rank + 2, recipe, plans)
            err, _ = error_squared(value, F, exact, rank)
            need(err == 0 and not any(defects), 'complete column equality')
            need(norm2(exact) == 1 << (2 * rank), 'unitary column norm')
            column_digest.update(json.dumps(exact, separators=(',', ':')).encode())
        for name, vector in fixtures(right):
            exact = oracle(vector, recipe)
            need(norm2(exact) == norm2(vector) << (2 * rank), 'fixture unitary norm')
            for f in (0, 19, 300):
                for b in (0, 1, 8, 64):
                    value, F, defects = execute(vector, f, b, recipe, plans)
                    need(all(d <= 1024 for d in defects), 'per-stage squared error')
                    err, ef = error_squared(value, F, exact, f + rank)
                    need(relative_ok(err, ef, vector, f, b), 'completed relative bound')
                    total_nonzero += err != 0
                    receipts.append({'role': transport['role'], 'fixture': name, 'f': f, 'b': b,
                                     'F': F, 'error_squared_numerator': err, 'error_squared_scale': ef,
                                     'local_defects4': defects})
        basis = inverse_wrapper_basis(right)
        exact = oracle(basis, recipe)
        for f in (0, 4, 64, 300):
            value, F, _ = execute(basis, f, 1, recipe, plans, forced_precision=f)
            err, ef = error_squared(value, F, exact, f + rank)
            need(not any(a or b for a, b in value), 'same-grid zero witness')
            need(not relative_ok(err, ef, basis, f, 1), 'same-grid relative contract must fail')
        value, F, _ = execute(basis, 0, 8, recipe, plans)
        coarse = [(round_dyadic(a, F), round_dyadic(b, F)) for a, b in value]
        err, ef = error_squared(coarse, 0, exact, rank)
        need(not relative_ok(err, ef, basis, 0, 8), 'final downcast must fail')
        bad = json.loads(json.dumps(recipe))
        bad['left']['phase'] = (bad['left']['phase'] + 1) % 4
        shifted, F, _ = execute(basis, 0, 8, bad)
        err, ef = error_squared(shifted, F, exact, rank)
        need(not relative_ok(err, ef, basis, 0, 8), 'phase mutation must fail')
        bad['left']['matrix_rows'] = [0] * 9
        rejected(lambda: wrapper_plan(bad['left']))
        rejected(lambda: execute(basis, -1, 8, recipe))
    need(total_nonzero > 0, 'fixtures must exercise actual rounding')
    return {'schema_version': 1, 'bindings': bindings, 'exact_columns': 1024,
            'column_stream_sha256': column_digest.hexdigest(), 'rounded_fixtures': len(receipts),
            'nonzero_error_fixtures': total_nonzero, 'fixtures': receipts,
            'same_grid_relative_error': '1 for every f >= 0; violates u=1/2',
            'costs': [{'rank': r, 'butterflies': r * 256, 'signed_integer_additions': r * 256 * 12,
                       'rounded_halves': r * 1024, 'wrapper_moves': 1024} for r in (7, 8)],
            'scope': 'finite reference implementation; no recursive speed, full-word recovery or supplier claim'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result', type=Path)
    args = parser.parse_args()
    result = calculate()
    if args.write_result:
        with args.write_result.open('x', encoding='utf-8', newline='\n') as out:
            json.dump(result, out, indent=2)
            out.write('\n')
    else:
        expected = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))
        need(type(expected) is dict and json.dumps(expected, sort_keys=True) == json.dumps(result, sort_keys=True), 'complete typed receipt')
    print('PASS_P104_ROUNDED_NATIVE_CHILD columns=1024 rounded=' + str(result['rounded_fixtures']) +
          ' nonzero_errors=' + str(result['nonzero_error_fixtures']) + ' no_new_kappa')


if __name__ == '__main__':
    main()
