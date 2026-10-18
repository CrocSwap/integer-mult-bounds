"""Source-bound adaptive-rounding collision. Arham Tahir/Codex, Apache-2.0."""
import argparse
import gzip
import hashlib
import json
from math import comb
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WIDTH = 512
ZERO = (0, 0)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs)


def inputs(root=ROOT):
    """Authenticate every live input before executing the one arithmetic module."""
    pins = read_json((HERE / 'SOURCES.json').read_bytes())
    data = {}
    for pin in pins['files']:
        if pin['usage'] != 'input':
            continue
        raw = (root / pin['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA256: ' + pin['path'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == pin['git_blob'], 'source blob: ' + pin['path'])
        data[pin['path']] = raw
    module = types.ModuleType('authenticated_adaptive_arithmetic')
    source = 'research/p104-rounded-native-child/arithmetic.py'
    exec(compile(data[source], source, 'exec'), module.__dict__)
    word = read_json(data['research/p104-rounded-collector/inputs/WORD.json'])
    native = read_json(gzip.decompress(data['research/p104-rounded-collector/inputs/NATIVE.json.gz']))
    local, recipes = bind(word, native)
    return module, local, recipes


def bind(word, native):
    need(len(word['program']) == 5398, 'event count')
    need(all(e[0] in ('transport', 'add', 'sign') and
             (e[0] != 'add' or e[1] != e[2]) for e in word['program'][:2025]), 'invertible prefix')
    local = word['program'][2025:2040]
    frame = local[0][2]
    sources = ['D31', 'D30', 'D29', 'D28', 'D27']
    need(local[0] == ['zero', 'C', frame] and len(frame) == 8, 'private allocation')
    need(local[1:6] == [['add', 'C', s, 1, frame] for s in sources], 'five gathers')
    need(local[7] == ['add', 'Q7', 'C', '1', local[6][3]], 'one-way query')
    need(local[9:14] == [['add', 'C', s, '-1', frame] for s in reversed(sources)], 'source cleanup')
    need(local[14] == ['erase', 'C', frame], 'private erase')
    frames = prefix_frames(word)
    need(all(frames[s] == frame for s in sources) and frames['Q7'] == local[6][3],
         'actual collector cut frames')
    recipes = []
    for index in (2031, 2033):
        matches = [t for t in native['transports'] if index in t['events']]
        need(len(matches) == 1, 'unique native binding')
        t = matches[0]
        need(word['program'][index] == ['transport', 'C', t['old'], t['new'], 7], 'literal native event')
        need(t['recipe']['rank'] == 7, 'rank seven')
        recipes.append(t['recipe'])
    need(local[6][2:4] == list(reversed(local[8][2:4])), 'inverse endpoint frames')
    return local, recipes


def prefix_frames(word):
    frames = dict(word['initial_frames'])
    for event in word['program'][:2025]:
        op, reg = event[:2]
        if op == 'transport':
            need(frames[reg] == event[2], 'prefix transport frame')
            need(event[4] == abs(len(event[2])-len(event[3])), 'prefix transport rank')
            frames[reg] = event[3]
        elif op == 'add':
            need(frames[reg] == frames[event[2]] == event[4], 'prefix common ADD frame')
        elif op == 'sign':
            need(frames[reg] == event[3], 'prefix sign frame')
        else:
            raise ValueError('noninvertible prefix')
    return frames


def rotate(z, phase):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def multiply(z, w):
    a, b = z
    c, d = w
    return a*c-b*d, a*d+b*c


def monomial(vector, record):
    """Independent explicit bit/phase formula, with no primary address plan."""
    result = [ZERO] * WIDTH
    targets = []
    for x, z in enumerate(vector):
        bits = [(x >> j) & 1 for j in range(9)]
        y = record['offset']
        for j, row in enumerate(record['matrix_rows']):
            y ^= (sum(bits[k] * ((row >> k) & 1) for k in range(9)) % 2) << j
        phase = record['phase'] + sum(bits[j] * record['linear_Z4'][j] for j in range(9))
        phase += 2 * sum(bits[j]*bits[k]*((record['quadratic_rows'][j] >> k) & 1)
                         for j in range(9) for k in range(j+1, 9))
        result[y] = rotate(z, phase)
        targets.append(y)
    need(sorted(targets) == list(range(WIDTH)), 'oracle wrapper bijection')
    return result


def oracle(vector, recipe):
    """Closed tensor-convolution numerator with denominator 2^rank."""
    rank = recipe['rank']
    coefficients = []
    for delta in range(1 << rank):
        z = (1, 0)
        for bit in range(rank):
            z = multiply(z, (1, -1 if delta >> bit & 1 else 1))
        coefficients.append(z)
    inner = monomial(vector, recipe['right'])
    result = [ZERO] * WIDTH
    for x, z in enumerate(inner):
        if z == ZERO:
            continue
        for delta, coefficient in enumerate(coefficients):
            a, b = multiply(z, coefficient)
            c, d = result[x ^ delta]
            result[x ^ delta] = c+a, d+b
    return monomial(result, recipe['left'])


def add(dst, src, coefficient=1):
    a, af = dst
    b, bf = src
    F = max(af, bf)
    return ([((x << (F-af)) + coefficient*(u << (F-bf)),
               (y << (F-af)) + coefficient*(v << (F-bf)))
             for (x, y), (u, v) in zip(a, b)], F)


def equal(a, b):
    return all(z == ZERO for z in add(a, b, -1)[0])


def norm2(vector):
    return sum(a*a+b*b for a, b in vector)


def squared_error(actual, exact):
    delta, F = add(actual, exact, -1)
    return norm2(delta), F


def relative_ok(actual, exact, entrance, b):
    error, F = squared_error(actual, exact)
    vector, f = entrance
    return error * (1 << (2*(b+f))) <= norm2(vector) * (1 << (2*F))


def inverse_basis(module, recipe):
    right = module.wrapper_plan(recipe['right'])
    x, phase = next((x, p) for x, (y, p) in enumerate(right) if y == 0)
    vector = [ZERO] * WIDTH
    vector[x] = rotate((1, 0), -phase)
    need(monomial(vector, recipe['right']) == [(1, 0)] + [ZERO]*(WIDTH-1), 'entrance basis')
    return vector


def collector(module, local, recipes, dirty, b, strict=False):
    zero = ([ZERO] * WIDTH, 0)
    state = {s: zero for s in ('D31', 'D30', 'D29', 'D28', 'D27', 'Q7')}
    state['D31'] = dirty
    calls = []
    for event in local:
        op, reg = event[:2]
        if op == 'zero':
            need(reg not in state, 'fresh private state')
            state[reg] = zero
        elif op == 'add':
            coefficient = int(event[3])
            need(coefficient in (-1, 1), 'unit scalar coefficient')
            state[reg] = add(state[reg], state[event[2]], coefficient)
        elif op == 'transport':
            recipe = recipes[len(calls)]
            before = state[reg]
            value, F, defects = module.execute(*before, b, recipe)
            exact = oracle(before[0], recipe), before[1]+recipe['rank']
            need(relative_ok((value, F), exact, before, b), 'completed relative defect')
            state[reg] = value, F
            calls.append({'grid': F, 'defects4': defects, 'error': squared_error(state[reg], exact)})
        elif op == 'erase':
            residue = state[reg]
            need(not strict or not any(z != ZERO for z in residue[0]), 'strict private zero')
            del state[reg]
        else:
            raise ValueError('unsupported local instruction')
    need(len(calls) == 2 and state['D31'] == dirty, 'calls and immutable dirty source')
    need(all(equal(state[s], zero) for s in ('D30', 'D29', 'D28', 'D27')), 'other sources unchanged')
    return residue, state['Q7'], calls


def fixture(module, local, recipes, b, f):
    basis = inverse_basis(module, recipes[0])
    A = 1 << (b+7)
    low = [(A*a, A*c) for a, c in basis]
    high = [((A+1)*a, (A+1)*c) for a, c in basis]
    out0, F0, d0 = module.execute(low, f, b, recipes[0])
    out1, F1, d1 = module.execute(high, f, b, recipes[0])
    need(low != high and (out0, F0) == (out1, F1), 'field and metadata collision')
    need(F0 == f and not any(d0) and d1 == [4]+[0]*6, 'first-stage tie collision')
    need(equal((out0, F0), (oracle(low, recipes[0]), f+7)), 'exact low outbound')
    need(squared_error((out1, F1), (oracle(high, recipes[0]), f+7)) == (1 << 14, f+7),
         'unit-quantum outbound error')
    clean, query0, calls0 = collector(module, local, recipes, (low, f), b, strict=True)
    residual, query1, calls1 = collector(module, local, recipes, (high, f), b)
    expected = [(-a, -c) for a, c in basis], f
    need(equal(residual, expected) and equal(query0, query1), 'literal collector residual/query')
    need(not any(z != ZERO for z in clean[0]), 'exact low cleanup')
    need(calls1[1]['grid'] == f+4 and calls1[1]['error'][0] == 0, 'retained finer return grid')
    fine, _, _ = collector(module, local, recipes, (high, f), b+7, strict=True)
    need(not any(z != ZERO for z in fine[0]), 'fixed-input finer-policy positive control')
    return {'b': b, 'f': f, 'A': str(A), 'outbound_grid': F1,
            'return_grid': calls1[1]['grid'], 'outbound_defects4': d1,
            'residual_norm2_numerator': 1, 'residual_grid': f,
            'low_calls': calls0, 'high_calls': calls1}


def check_inverse(module, recipes):
    digest = hashlib.sha256()
    for x in range(WIDTH):
        v = [ZERO] * WIDTH
        v[x] = (1, 0)
        out, F, defects = module.execute(v, 0, 16, recipes[0])
        need(not any(defects), 'exact inverse fixture outbound')
        need(equal((out, F), (oracle(v, recipes[0]), 7)), 'oracle complete outbound column')
        back, B, defects = module.execute(out, F, 16, recipes[1])
        need(not any(defects) and equal((back, B), (v, 0)), 'complete native inverse column')
        digest.update(json.dumps(out, separators=(',', ':')).encode())
    return digest.hexdigest()


def cube_input(module, recipe, A, mask):
    """Independently selectable low bits in all 256 first-stage pairs."""
    inner = [ZERO]*WIDTH
    for j in range(256):
        inner[2*j] = A + ((mask >> j) & 1), 0
    right = module.wrapper_plan(recipe['right'])
    vector = [rotate(inner[y], -phase) for y, phase in right]
    need(monomial(vector, recipe['right']) == inner, 'cube entrance wrapper')
    return vector


def check_cube(module, local, recipes):
    masks = ((1 << 128)-1, ((1 << 128)-1) << 128)
    fixtures = []
    for b, f in ((0, 0), (8, 19), (64, 300), (256, 0)):
        A = 1 << (b+7)
        vectors = [cube_input(module, recipes[0], A, mask) for mask in masks]
        outputs = [module.execute(vector, f, b, recipes[0]) for vector in vectors]
        need(vectors[0] != vectors[1] and outputs[0] == outputs[1], 'collision including diagnostics')
        need(outputs[0][1:] == (f, [512]+[0]*6), 'fixed-weight cube diagnostics')
        base = cube_input(module, recipes[0], A, 0)
        for mask, vector in zip(masks, vectors):
            residue, _, calls = collector(module, local, recipes, (vector, f), b)
            need(equal(residue, add((base, f), (vector, f), -1)), 'cube collector residual')
            need(calls[1]['error'][0] == 0, 'cube exact return')
        fixtures.append({'b': b, 'f': f, 'diagnostics4': outputs[0][2],
                         'retained_grid': outputs[0][1], 'weight': masks[0].bit_count()})
    states = comb(256, 128)
    need((1 << 251) < states <= (1 << 252), 'diagnostic-preserving history bits')
    return {'independent_bits': 256, 'same_field_and_grid_states': str(1 << 256),
            'minimum_history_bits': 256, 'same_diagnostics_weight': 128,
            'same_diagnostics_states': str(states), 'minimum_extra_bits_given_diagnostics': 252,
            'fixtures': fixtures}


def calculate():
    module, local, recipes = inputs()
    digest = check_inverse(module, recipes)
    fixtures = [fixture(module, local, recipes, b, f)
                for b in (0, 1, 8, 64, 256) for f in (0, 19, 300)]
    return {'status': 'PASS_P104_ADAPTIVE_ROUNDING_COLLISION', 'native_events': [2031, 2033],
            'local_events_inclusive': [2025, 2039], 'exact_inverse_columns': WIDTH,
            'outbound_column_digest': digest, 'fixtures': fixtures,
            'collision_cube': check_cube(module, local, recipes),
            'family': 'b,f>=0; A=2^(b+7); x0=A*e*2^-f; x1=(A+1)*e*2^-f',
            'scope': 'One local collision/cleanup obstruction under the specified adaptive kernel; no supplier or kappa.'}


def compare(actual, expected):
    need(type(actual) is type(expected), 'typed receipt mismatch')
    if isinstance(actual, dict):
        need(actual.keys() == expected.keys(), 'receipt keys')
        for key in actual:
            compare(actual[key], expected[key])
    elif isinstance(actual, (list, tuple)):
        need(len(actual) == len(expected), 'receipt length')
        for a, b in zip(actual, expected):
            compare(a, b)
    else:
        need(actual == expected, 'receipt value')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', type=Path)
    args = parser.parse_args()
    result = read_json(json.dumps(calculate()))
    if args.write_result is not None:
        with args.write_result.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(json.dumps(result, indent=2)+'\n')
    else:
        compare(result, read_json((HERE / 'RESULT.json').read_bytes()))
    print(result['status'] + ' inverse_columns=512 sparse=15 cube_bits=256 diagnostic_extra_bits=252 no_new_kappa')


if __name__ == '__main__':
    main()
