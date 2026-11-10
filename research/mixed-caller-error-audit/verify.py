"""Independent source-bound field-error audit; no author modules are executed.

Prefixes use elementary row operations. Suffixes use explicit right-column
operations. This is a finite algebraic audit under the retained unitary and
per-primitive defect hypotheses, not a physical rounding implementation.
"""
import argparse
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = '8ef153f281be3784f7dacffc5f02b9e04406344ec7b759fa1b4adc22bb48f591'
N, D = 34, 18
ZERO = (0,) * D
ONE = (F(1), F(0))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def pairs(items):
    out = {}
    for key, value in items:
        need(key not in out, 'duplicate JSON key')
        out[key] = value
    return out


def strict(data):
    def bad(value):
        raise ValueError('nonfinite JSON constant: ' + value)
    return json.loads(data, object_pairs_hook=pairs, parse_constant=bad)


def typed(value):
    need(type(value) in (dict, list, str, int, type(None)), 'untyped receipt value')
    if isinstance(value, dict):
        need(all(type(k) is str for k in value), 'non-string key')
        for child in value.values():
            typed(child)
    elif isinstance(value, list):
        for child in value:
            typed(child)


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def authenticate():
    raw = (HERE / 'SOURCE-PINS.json').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == MANIFEST, 'SOURCE-PINS digest')
    pins = strict(raw)
    need(type(pins['schema_version']) is int and pins['schema_version'] == 1, 'pin schema')
    need(len(pins['files']) == 5, 'all five source files')
    files = {}
    for row in pins['files']:
        path = row['path']
        need(type(path) is str and path.startswith('inputs/') and '..' not in path, 'source path')
        need(path not in files, 'duplicate source path')
        data = (HERE / path).read_bytes()
        need(type(row['bytes']) is int and len(data) == row['bytes'], 'source byte length')
        need(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256')
        blob = b'blob ' + str(len(data)).encode() + b'\0' + data
        need(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'source Git blob')
        files[path] = data
    return files


def rational(value):
    need(type(value) in (int, str), 'exact rational grammar')
    out = F(value)
    need(type(value) is int or str(out) == value, 'canonical rational')
    return out


def validate(word):
    need(type(word['roles']) is int and word['roles'] == N, '34 roles')
    need(type(word['stages']) is int and word['stages'] == D, '18 stages')
    need(type(word['events']) is list and len(word['events']) == 570, '570 events')
    for e in word['events']:
        need(type(e) is list and e, 'event record')
        op = e[0]
        lengths = {'ADD': 4, 'SCALE': 3, 'SWAP': 3, 'QUERY': 4,
                   'LOCAL': 4, 'Q_POWER': 3, 'LAMBDA': 3, 'IDLE': 4, 'IDLE_ONE': 3}
        need(op in lengths and len(e) == lengths[op], 'opcode grammar')
        roles = e[2:4] if op == 'LOCAL' else e[1:3] if op in ('ADD','SWAP','QUERY','IDLE') else e[1:2]
        need(all(type(r) is int and 0 <= r < N for r in roles), 'role grammar')
        if len(roles) == 2:
            need(roles[0] != roles[1], 'distinct operands')
        if op in ('ADD','SCALE'):
            rational(e[-1])
        if op in ('QUERY','Q_POWER','LAMBDA'):
            need(type(e[-1]) is int, 'central exponent integer')
        if op == 'LAMBDA':
            need(e[-1] in (-1,1), 'normalizer sign')
        stages = [e[1]] if op == 'LOCAL' else e[-1] if op in ('IDLE','IDLE_ONE') else []
        need(type(stages) is list and len(set(stages)) == len(stages), 'stage set')
        need(all(type(s) is int and 1 <= s <= D for s in stages), 'stage grammar')
    need(len(word['diagonal']) == N, 'full endpoint declarations')
    for row in word['diagonal']:
        need(len(row) == D + 2 and all(type(v) is int for v in row), 'target monomial')
        need(row[1] == 0, 'unused stage zero slot')
    return word['events']


def cmul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def phase(power):
    return ((F(1),F(0)), (F(0),F(1)), (F(-1),F(0)), (F(0),F(-1)))[power % 4]


def combine(a, b, scalar=ONE):
    out = dict(a)
    for key, value in b.items():
        u, v = cmul(value, scalar)
        old = out.get(key, (F(0), F(0)))
        value = old[0] + u, old[1] + v
        if value != (0, 0):
            out[key] = value
        else:
            out.pop(key, None)
    return out


def multiply(poly, scalar=ONE, stages=()):
    if scalar == (0,0):
        return {}
    shift = tuple(int(j + 1 in stages) for j in range(D))
    return {tuple(a+b for a,b in zip(key, shift)): cmul(value, scalar)
            for key, value in poly.items()}


def identity():
    return [{i: {ZERO: ONE}} for i in range(N)]


def row_scale(matrix, role, scalar=ONE, stages=()):
    matrix[role] = {j: multiply(p, scalar, stages) for j,p in matrix[role].items()}


def row_add(matrix, dst, src, scalar):
    out = dict(matrix[dst])
    for j, poly in matrix[src].items():
        value = combine(out.get(j, {}), poly, scalar)
        if value:
            out[j] = value
        else:
            out.pop(j, None)
    matrix[dst] = out


def col_scale(matrix, role, scalar=ONE, stages=()):
    for row in matrix:
        if role in row:
            row[role] = multiply(row[role], scalar, stages)


def col_add(matrix, dst, src, scalar):
    for row in matrix:
        value = combine(row.get(dst, {}), row.get(src, {}), scalar)
        if value:
            row[dst] = value
        else:
            row.pop(dst, None)


def forward(matrix, e, q):
    op = e[0]
    if op == 'ADD':
        row_add(matrix, e[1], e[2], (rational(e[3]), F(0)))
    elif op == 'SCALE':
        row_scale(matrix, e[1], (rational(e[2]), F(0)))
    elif op == 'SWAP':
        matrix[e[1]], matrix[e[2]] = matrix[e[2]], matrix[e[1]]
    elif op == 'QUERY':
        row_add(matrix, e[1], e[2], phase(q*e[3]))
    elif op == 'LOCAL':
        row_scale(matrix, e[2], stages=[e[1]])
        row_scale(matrix, e[3], stages=[e[1]])
        row_add(matrix, e[3], e[2], phase(-q))
    elif op == 'Q_POWER':
        row_scale(matrix, e[1], phase(q*e[2]))
    elif op == 'LAMBDA':
        row_scale(matrix, e[1], ONE if q % 2 == 0 else (F(0), F(e[2])))
    else:
        roles = e[1:3] if op == 'IDLE' else e[1:2]
        for role in roles:
            row_scale(matrix, role, stages=e[-1])


def right(matrix, e, q):
    """In-place S <- S E, using explicit columns; no matrix transpose."""
    op = e[0]
    if op == 'ADD':
        col_add(matrix, e[2], e[1], (rational(e[3]), F(0)))
    elif op == 'SCALE':
        col_scale(matrix, e[1], (rational(e[2]), F(0)))
    elif op == 'SWAP':
        for row in matrix:
            a, b = row.pop(e[1], {}), row.pop(e[2], {})
            if a:
                row[e[2]] = a
            if b:
                row[e[1]] = b
    elif op == 'QUERY':
        col_add(matrix, e[2], e[1], phase(q*e[3]))
    elif op == 'LOCAL':
        col_add(matrix, e[2], e[3], phase(-q))
        col_scale(matrix, e[2], stages=[e[1]])
        col_scale(matrix, e[3], stages=[e[1]])
    elif op == 'Q_POWER':
        col_scale(matrix, e[1], phase(q*e[2]))
    elif op == 'LAMBDA':
        col_scale(matrix, e[1], ONE if q % 2 == 0 else (F(0), F(e[2])))
    else:
        roles = e[1:3] if op == 'IDLE' else e[1:2]
        for role in roles:
            col_scale(matrix, role, stages=e[-1])


def cell_size(poly):
    return sum((abs(a)+abs(b) for a,b in poly.values()), F(0))


def merge_envelope(table, boundary, matrix):
    target = table[boundary]
    for i, row in enumerate(matrix):
        for j, poly in row.items():
            target[i][j] = max(target[i][j], cell_size(poly))


def envelope(events, backward=False):
    table = [[[F(0) for _ in range(N)] for _ in range(N)] for _ in range(571)]
    for q in range(4):
        matrix = identity()
        boundary = 570 if backward else 0
        merge_envelope(table, boundary, matrix)
        indices = range(569,-1,-1) if backward else range(570)
        for t in indices:
            (right if backward else forward)(matrix, events[t], q)
            merge_envelope(table, t if backward else t+1, matrix)
    return table


def check_endpoint(events, word):
    for q in range(4):
        matrix = identity()
        for event in events:
            forward(matrix, event, q)
        for i, row in enumerate(matrix):
            target = word['diagonal'][i]
            need(row == {i: {tuple(target[2:]): phase(q*target[0])}}, 'all-stage endpoint')


def sites(e, normalizers=True):
    op = e[0]
    if op in ('ADD','SCALE'):
        return 'scalar', e[1:2], F(1)
    if op == 'LAMBDA':
        return 'scalar', e[1:2] if normalizers else [], F(9,2)
    if op == 'LOCAL':
        return 'local', e[2:4], F(1)
    if op == 'QUERY':
        return 'query', e[1:2], F(1)
    if op in ('IDLE','IDLE_ONE'):
        return 'idle', e[1:3] if op == 'IDLE' else e[1:2], F(1)
    return 'scalar', [], F(0)


def error_arrays(events, suffix, skip=None):
    out = {key: [F(0)]*N for key in ('scalar','local','query','idle')}
    for t, event in enumerate(events):
        if t == skip:
            continue
        kind, roles, weight = sites(event)
        for i in range(N):
            out[kind][i] += weight * sum((suffix[t+1][i][r] for r in roles), F(0))
    return out


def real_event(state, e, dual=False):
    op = e[0]
    if op in ('ADD','QUERY','LOCAL'):
        dst, src, c = (e[1],e[2],rational(e[3])) if op == 'ADD' else (e[1],e[2],F(1)) if op == 'QUERY' else (e[3],e[2],F(1))
        if dual:
            dst, src = src, dst
        state[dst] += c * state[src]
    elif op == 'SCALE':
        state[e[1]] *= rational(e[2])
    elif op == 'SWAP':
        state[e[1]], state[e[2]] = state[e[2]], state[e[1]]


def lower_witness(events, output):
    dual = [F(int(i == output)) for i in range(N)]
    chosen = [[] for _ in events]
    total = F(0)
    for t in range(569,-1,-1):
        _, roles, _ = sites(events[t], False)
        for role in roles:
            sign = (dual[role] > 0) - (dual[role] < 0)
            chosen[t].append([role, sign])
            total += abs(dual[role])
        real_event(dual, events[t], True)
    state = [F(0)] * N
    for event, errors in zip(events, chosen):
        real_event(state, event)
        for role, value in errors:
            state[role] += value
    need(state[output] == total, 'dual choice attains independent forward error')
    return total, chosen, state


def gauss_add(a, b):
    return a[0]+b[0], a[1]+b[1]


def normalizer_circuit(x, y, sign, errors):
    x = gauss_add(gauss_add(x, cmul((F(0),F(-sign)), y)), errors[0])
    x = gauss_add(cmul((F(1,2),F(sign,2)), x), errors[1])
    y = gauss_add(cmul((F(1),F(sign)), y), errors[2])
    y = gauss_add(gauss_add(y, cmul((F(0),F(-sign)), x)), errors[3])
    return [x[0],x[1],y[0],y[1]]


def normalizer():
    zero = (F(0), F(0))
    result = []
    for sign in (-1,1):
        columns, error_columns = [], []
        for j in range(4):
            v = [F(int(i == j)) for i in range(4)]
            x, y = (v[0],v[1]), (v[2],v[3])
            got = normalizer_circuit(x,y,sign,[zero]*4)
            a, b = (F(1,2),F(sign,2)), (F(1,2),F(-sign,2))
            expected = gauss_add(cmul(a,x),cmul(b,y)) + gauss_add(cmul(b,x),cmul(a,y))
            need(got == list(expected), 'both signs literal four-operation matrix')
            columns.append(list(map(str,got)))
            errors = [zero]*4
            errors[j] = ONE
            error_columns.append(normalizer_circuit(zero,zero,sign,errors))
        norms = [sum(v*v for v in col) for col in error_columns]
        need(norms == [1,2,1,1], 'all four primitive error columns')
        result.append({'sign':sign,'columns':columns,'error_columns':[[str(v) for v in col] for col in error_columns], 'error_squared_norms':list(map(str,norms))})
    need(F(3,2)**2 > 2, 'strict normalizer 9/2 majorant')
    return result


def first_difference(a, b):
    for i in range(N):
        for j in range(N):
            x, y = a[i].get(j, {}), b[i].get(j, {})
            for key in sorted(set(x) | set(y)):
                if x.get(key,(0,0)) != y.get(key,(0,0)):
                    return {'output':i,'input':j,'stage_exponents':list(key),
                            'expected':list(map(str,x.get(key,(0,0)))), 'actual':list(map(str,y.get(key,(0,0))))}
    raise ValueError('countercontrol did not change an actual coefficient')


def mathematical_toys():
    # Two central spectral summands and two unit input fields. Each character
    # row sum is1, while orthogonal projections can sum to output norm sqrt2.
    character_rows = [[F(1),F(0)],[F(0),F(1)]]
    wrong = max(sum(row) for row in character_rows)
    cell_bound = sum(max(row[j] for row in character_rows) for j in range(2))
    inputs = [[F(1),F(0)],[F(0),F(1)]]
    output = [character_rows[0][0]*inputs[0][0], character_rows[1][1]*inputs[1][1]]
    squared = sum(v*v for v in output)
    need(all(sum(v*v for v in x) == 1 for x in inputs), 'unit toy field inputs')
    need(wrong == 1 and cell_bound == 2 and squared > wrong*wrong, 'max-before-sum toy underbound')
    a, b = list(ZERO), list(ZERO)
    a[0], b[1] = 1, 1
    poly = combine({tuple(a):ONE},{tuple(b):ONE},(F(-1),F(0)))
    collapsed = sum(value[0] for value in poly.values())
    signed = sum(value[0] * ((-1)**key[1]) for key,value in poly.items())
    need(len(poly) == 2 and cell_size(poly) == 2 and collapsed == 0 and signed == 2, 'independent-stage collapse toy')
    return ({'cell_majorant_sum':str(cell_bound),'max_character_row_sum':str(wrong),'attainable_squared_norm':str(squared)},
            {'polynomial':'D1-D2','distinct_monomial_bound':str(cell_size(poly)),'all_stages_one':str(collapsed),'D1_plus_D2_minus':str(signed)})


def controls(events, suffix, arrays):
    t = next(i for i,e in enumerate(events) if e[0] == 'ADD')
    changed = [list(e) for e in events]
    changed[t][3] = str(-rational(changed[t][3]))
    old, new = identity(), identity()
    for e, f in zip(events, changed):
        forward(old,e,0)
        forward(new,f,0)
    sign_fault = {'event':t,'witness':first_difference(old,new)}
    t = next(i for i,e in enumerate(events) if e[0] == 'LAMBDA')
    wrong = error_arrays(events,suffix,t)
    row = next(i for i in range(N) if wrong['scalar'][i] != arrays['scalar'][i])
    left, right_matrix = identity(), identity()
    row_scale(left,0,(F(2),F(0)))
    row_scale(left,1,(F(3),F(0)))
    row_scale(right_matrix,0,(F(2),F(0)))
    row_scale(right_matrix,1,(F(3),F(0)))
    event = ['ADD',0,1,'3/2']
    forward(left,event,0)
    right(right_matrix,event,0)
    need(left[0][1] == {ZERO:(F(9,2),F(0))} and right_matrix[0][1] == {ZERO:(F(3),F(0))}, 'right-column orientation control')
    maximum_toy, stage_toy = mathematical_toys()
    return {'actual_ADD_sign_flip':sign_fault,
            'omitted_normalizer_accounting':{'event':t,'output':row,'expected':str(arrays['scalar'][row]),'actual':str(wrong['scalar'][row])},
            'orientation_toy':{'input_diagonal':['2','3'],'cell':[0,1],'left_coefficient':'9/2','right_coefficient':'3'},
            'max_before_sum_toy':maximum_toy,
            'stage_collapse_toy':stage_toy}


def build(files):
    word = strict(files['inputs/CONTROLLER.json'])
    events = validate(word)
    prefix, suffix = envelope(events), envelope(events,True)
    check_endpoint(events,word)
    rows = lambda table: [[sum(row,F(0)) for row in matrix] for matrix in table]
    prow, srow = rows(prefix), rows(suffix)
    maximum = max((v,t,i) for t,row in enumerate(prow) for i,v in enumerate(row))
    arrays = error_arrays(events,suffix)
    common = max(sum((arrays[k][i] for k in arrays),F(0)) for i in range(N))
    lowers = [lower_witness(events,i) for i in range(N)]
    best, output = max((row[0],i) for i,row in enumerate(lowers))
    need(256 < best <= common < 512, 'sharp uniform integer nine-bit guard')
    result = {'schema_version':1,'source_manifest_sha256':MANIFEST,'roles':N,'stages':D,'events':570,
              'prefix':[str(maximum[0]),maximum[1],maximum[2]],
              'errors':{k:list(map(str,v)) for k,v in arrays.items()},
              'maxima':{k:str(max(v)) for k,v in arrays.items()},'common_error':str(common),
              'prefix_row_envelopes':[[str(v) for v in row] for row in prow],
              'suffix_row_envelopes':[[str(v) for v in row] for row in srow],
              'prefix_cell_envelope_sha256':hashlib.sha256(encode([[[str(v) for v in row] for row in matrix] for matrix in prefix])).hexdigest(),
              'suffix_cell_envelope_sha256':hashlib.sha256(encode([[[str(v) for v in row] for row in matrix] for matrix in suffix])).hexdigest(),
              'lower_all_outputs':[str(v[0]) for v in lowers],
              'lower_witness':{'amplification':str(best),'output':output,'Q':'I','stages':'I','normalizer_error':0,
                               'errors':lowers[output][1],'final_state':list(map(str,lowers[output][2]))},
              'normalizer':normalizer(),'sufficient_guard_bits':9,'insufficient_guard_bits':8,
              'boundary_signal_bound':'18*M+8487*epsilon','controls':controls(events,suffix,arrays),
              'scope':'Exact finite field-error contract; no native rounding, physical cleanup, precision price or kappa.'}
    author = strict(files['inputs/AUTHOR-RESULT.json'])
    for key in ('prefix','errors','maxima','common_error','boundary_signal_bound','sufficient_guard_bits','insufficient_guard_bits'):
        need(result[key] == author[key], 'author receipt discrepancy: '+key)
    for key in ('amplification','output','Q','stages','normalizer_error'):
        need(result['lower_witness'][key] == author['lower_witness'][key], 'lower author discrepancy')
    need([[int(v) for v in row['error_squared_norms']] for row in result['normalizer']] == author['normalizer_error_squared_norms'], 'normalizer author discrepancy')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    files = authenticate()
    result = build(files)
    typed(result)
    if args.emit:
        print(encode(result).decode(),end='')
    else:
        retained = strict((HERE / 'RESULT.json').read_bytes())
        typed(retained)
        need(retained == result, 'retained RESULT mismatch')
        print('PASS_MIXED_CALLER_ERROR_AUDIT')


if __name__ == '__main__':
    main()
