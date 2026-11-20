#!/usr/bin/env python3
"""Selected #7000 finite predicates for the all-column specialization.

Independent forward scalar interpretation; standard library, explicit checks.
The historical full Clifford catalogue is authenticated, not re-executed.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

HERE = Path(__file__).resolve().parent
INPUT = HERE / 'inputs'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = (INPUT / path).read_bytes()
    pin = next(p for p in json.loads((HERE / 'SOURCE-PINS.json').read_text()) if p['path'] == path)
    need(sha256(raw).hexdigest() == pin['sha256'], 'source hash: ' + path)
    if pin.get('manifest'):
        need(pin['sha256'] == pin['manifest'], 'selected manifest binding: ' + path)
    return json.loads(gzip.decompress(raw) if path.endswith('.gz') else raw)


def digest(x):
    return sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def bit_native(word, mutate=False):
    n = word['public']
    cur = {i: a for i, a in enumerate(word['start'])}
    rows = {i: 1 << i for i in range(n)}
    moves = set()
    used_clear = initialized = 0
    changed = False
    for step, event in enumerate(word['program']):
        op, r = event[:2]
        if op == 'INIT':
            need(r >= n and r not in cur, 'BIT fresh owned label')
            cur[r] = event[2]; rows[r] = 0; initialized += 1
        elif op == 'CLEAR':
            need(r >= n and cur.get(r) == event[2], 'BIT owned return chart')
            used_clear += bool(rows[r]); del cur[r]; del rows[r]
        elif op == 'MOVE':
            _, r, a, b = event
            need(cur.get(r) == a and a != b, 'BIT MOVE entry')
            moves.add((str(a), str(b))); cur[r] = b
        elif op == 'ADD':
            _, r, s, frame = event
            need(r != s and cur.get(r) == cur.get(s) == frame, 'BIT common ADD chart')
            if not (mutate and not changed):
                rows[r] ^= rows[s]
            else:
                changed = True
        elif op == 'SWAP':
            _, r, s = event
            need(r != s and r in rows and s in rows, 'BIT SWAP owners')
            rows[r], rows[s] = rows[s], rows[r]
            cur[r], cur[s] = cur[s], cur[r]
        else:
            raise ValueError('BIT unexpected opcode: ' + op)
    need(set(rows) == set(range(n)), 'BIT complete owner return')
    need([cur[i] for i in range(n)] == word['final'], 'BIT final charts')
    expected = [1 << i for i in range(n)]
    for i in range(111):
        expected[i + 111] ^= 1 << i
    need([rows[i] for i in range(n)] == expected, 'BIT full scalar endpoint')
    # Every native off-diagonal entry lies inside exactly one same-route pair.
    off = [(i, i - 111) for i in range(111, 222)]
    return dict(public=n, coefficient_positions=n*n, events=len(word['program']),
                independent_helper_returns=n-222, off_diagonal_support=off,
                owned_lifetimes=initialized, nonzero_owned_erasure_positions=used_clear,
                moves=sorted(moves))


def complex_native(word, mutant=None):
    n = word['public']
    cur = dict(enumerate(word['initial']))
    rows = {i: {i: F(1)} for i in range(n)}
    paid = set(); lives = nonzero_clear = 0
    for position,event in enumerate(word['program']):
        op, r = event[:2]
        if op == 'INIT':
            need(r >= n and r not in cur, 'complex fresh owned label')
            cur[r] = event[2]; rows[r] = {}; lives += 1
        elif op == 'CLEAR':
            need(r >= n and cur.get(r) == event[2], 'complex owned return chart')
            nonzero_clear += bool(rows[r]); del cur[r]; del rows[r]
        elif op == 'MOVE':
            _, r, a, b, owned = event
            need(cur.get(r) == a and owned == (r >= n), 'complex MOVE owner and entry')
            paid.add((a, b)); cur[r] = b
        elif op == 'SCALE':
            _, r, q, frame = event
            need(cur.get(r) == frame, 'complex SCALE chart')
            q = F(q)*(2 if position == mutant else 1); rows[r] = {i: q*v for i, v in rows[r].items() if q*v}
        elif op in ('ADD', 'COPY'):
            _, r, s, q, frame = event
            need(r != s and cur.get(r) == cur.get(s) == frame, 'complex common scalar chart')
            q = F(q)*(2 if position == mutant else 1)
            if op == 'COPY':
                need(r >= n and not rows[r], 'COPY destination is initialized private zero')
                rows[r] = {i: q*v for i, v in rows[s].items() if q*v}
            else:
                for i, v in rows[s].items():
                    new = rows[r].get(i, F(0)) + q*v
                    if new: rows[r][i] = new
                    else: rows[r].pop(i, None)
        else:
            raise ValueError('complex unexpected opcode: ' + op)
    need(set(rows) == set(range(n)), 'complex complete owner return')
    need([cur[i] for i in range(n)] == word['final'], 'complex final charts')
    target = [{i: F(1)} for i in range(n)]
    hosted = set(word['hosted']['Dports'])
    for pi, x in enumerate(word['live']):
        y = x+112
        if pi in hosted:
            target[y][x] = F(1)
        else:
            target[x][y] = F(-1); target[y] = {x: F(1,2), y: F(1,2)}
    for x, y in zip(word['hosted']['X2'], word['hosted']['Y2']):
        target[x][y] = F(-1)
    need([rows[i] for i in range(n)] == target, 'complex full scalar endpoint')
    mains = set(word['live']) | {x+112 for x in word['live']} | set(word['hosted']['X2']) | set(word['hosted']['Y2'])
    helpers = {(word['initial'][i], word['final'][i]) for i in range(n) if i not in mains}
    catalogue = sorted(paid | helpers)
    return dict(public=n, coefficient_positions=n*n, events=len(word['program']),
                main_fields=len(mains), independent_helper_returns=n-len(mains),
                owned_lifetimes=lives, nonzero_owned_erasure_positions=nonzero_clear,
                catalogue_size=len(catalogue), catalogue_digest=digest(catalogue))


def receipts(catalogue):
    root = 'docs/research/pr-intake-evidence/pr7000-application/'
    ranges = []; boundaries = 0
    for i in range(3):
        receipt = read(root + f'native-catalogue-{i}.json')
        log = INPUT / root / receipt['log']
        need(sha256(log.read_bytes()).hexdigest() == receipt['log_sha256'], 'catalogue receipt log')
        data = json.loads(log.read_text()[log.read_text().index('{'):])
        need(receipt['exit_code'] == 0 and receipt['stop'] is None and receipt['source_unchanged'], 'completed historical catalogue')
        need(data['catalogue_digest'] == catalogue['catalogue_digest'] and data['catalogue_size'] == 3057, 'exact current catalogue census')
        need(data['phase_control_rejected'], 'phase-only rejection receipt')
        need(data['word_sha256'] == sha256((INPUT/'research/shared-wire-split-composition/data/final.json.gz').read_bytes()).hexdigest(), 'complete current word byte binding')
        for engine in ('clifford_exact.py','native_verify.py'):
            path = 'research/shared-wire-split-composition/frozen/'+engine
            need(receipt['source_sha256'][path] == sha256((INPUT/path).read_bytes()).hexdigest(), 'exact executed catalogue engine: '+engine)
        ranges.append([data['slice_start'], data['slice_stop']]); boundaries += data['main_boundary_pairs']
        need(receipt['source_sha256']['docs/research/pr-intake-evidence/pr7000-application/check_native_catalogue.py'] ==
             sha256((INPUT/root/'check_native_catalogue.py').read_bytes()).hexdigest(), 'executed catalogue checker unchanged')
    need(ranges == [[0,1000],[1000,2000],[2000,3057]] and boundaries == 104, 'exhaustive disjoint catalogue coverage')
    return dict(method='reused completed exact signed-Pauli/Gaussian-phase receipts; no catalogue rerun', ranges=ranges, boundary_pairs=boundaries)


def route_source(bit, newer):
    need(bit['frames'] == newer['frames'], 'all 636 rational frame records agree with independently reviewed #7837')
    need(bit['start'][:222] == newer['start'][:222] and bit['final'][:222] == newer['final'][:222], 'all 111 main chart quartets agree')
    caller = read('research/paired-query-only-bit/EFREE-CALLER.json.gz')
    locals_ = [e for e in caller['events'] if e[0] == 'LOCAL']
    need([e[1] for e in locals_] == [s for s in range(1,19) for _ in range(2)], 'paired source chronology')
    for first, second in zip(locals_[::2], locals_[1::2]):
        need(len(set(first[2:] + second[2:])) == 4, 'two native instances use four distinct roots')
    need(bit['public'] == 659 and bit['owned_fields'] == 237, 'selected inventory; do not import grade14 inventory')
    return dict(frame_count=len(bit['frames']), frame_digest=digest(bit['frames']),
                main_chart_pairs=111, native_instances=36, paired_same_route_fields=222,
                complete_ambient=134, copied_grade14_helper_count=False)


def rational_predicates(word, move_pairs):
    frames = word['frames']
    determinants = []
    for label, frame in frames.items():
        b = [[F(x) for x in row] for row in frame['B']]
        a = [[F(x) for x in row] for row in frame['A']]
        need(len(b) == frame['dim'] and len(a) == 8-frame['dim'], 'BIT rational dimensions')
        need(all(len(row) == 8 for row in a+b), 'BIT complete rational basis')
        need(all(sum(x*y for x,y in zip(u,v)) == 0 for u in a for v in b), 'BIT image/kernel orthogonality')
        matrix = [list(row) for row in zip(*(b+a))]
        det = F(1)
        for j in range(8):
            pivot = next((i for i in range(j,8) if matrix[i][j]), None)
            need(pivot is not None, 'BIT split rational frame')
            if pivot != j:
                matrix[pivot], matrix[j] = matrix[j], matrix[pivot]; det = -det
            scale = matrix[j][j]; det *= scale
            matrix[j] = [x/scale for x in matrix[j]]
            for i in range(j+1,8):
                c = matrix[i][j]
                matrix[i] = [x-c*y for x,y in zip(matrix[i],matrix[j])]
        determinants.append([label, str(det)])
    for left, right in move_pairs:
        small, large = sorted([frames[left],frames[right]], key=lambda f:f['dim'])
        need(small['dim'] < large['dim'], 'strict positive MOVE difference')
        need(all(sum(F(x)*F(y) for x,y in zip(u,v)) == 0 for u in small['B'] for v in large['A']), 'every selected MOVE is nested')
    return dict(frames=len(frames), complete_rational_move_pairs=len(move_pairs),
                determinant_digest=digest(determinants),
                proof='Invertible [B^t A^t] and A B^t=0 give self-adjoint split projectors; nested image inclusion gives both product identities.')


def bit_caller(caller):
    # Sixteen-bit exponent lanes cannot carry: every exponent is bounded by
    # the total number of source events, checked below. No D_s^2=D_s is used.
    need(len(caller['events']) < 2**16, 'free body exponent lanes')
    rows = [{(i,0,0)} for i in range(38)]
    def shifted(row, q=0, body=0):
        return {(r,h^q,m+body) for r,h,m in row}
    for event in caller['events']:
        op = event[0]
        if op == 'LOCAL':
            _, stage, src, dst = event
            rows[dst] ^= shifted(rows[src],q=1)
            mon = 1 << (16*(stage-1))
            rows[src] = shifted(rows[src],body=mon)
            rows[dst] = shifted(rows[dst],body=mon)
        elif op == 'ADD':
            _, dst, src = event; rows[dst] ^= rows[src]
        elif op == 'QUERY':
            _, dst, src = event; rows[dst] ^= shifted(rows[src],q=1)
        elif op == 'SWAP':
            _, i, j = event; rows[i],rows[j] = rows[j],rows[i]
        elif op == 'IDLE_ONE':
            _, i, stages = event
            rows[i] = shifted(rows[i],body=sum(1 << (16*(s-1)) for s in stages))
        else:
            raise ValueError('unexpected caller opcode: '+op)
    expected = []
    for i,d in enumerate(caller['diagonal']):
        need(d['q'] == 1 and d['stages'], 'positive nonempty BIT caller target')
        expected.append({(i,1,sum(1 << (16*(s-1)) for s in d['stages']))})
    need(rows == expected, 'full free-polynomial BIT caller diagonal')
    return dict(roles=38, coefficient_positions=1444, events=len(caller['events']),
                body_variables=18, ring='F2[q,D1,...,D18]/(q^2-1)', independent_endpoints=38)


def budgets():
    claim = read('certificates/frontier7000/CLAIM.json')
    rho = F(1,250); covered = F(19262649,5000000000)
    stages = [F(0), F(17,5000), F(38507,10000000), F(12039,3125000)]
    need(F(claim['kappa']) == F(363005817,100000000000), 'unchanged selected kappa')
    need(F(claim['covered_BIT_saving']) == covered, 'exact selected covered saving')
    need([F(v) for v in claim['BIT_bootstrap']] == stages[1:], 'unchanged selected ordinary stages')
    bit_template = next(t for t in claim['uniform_templates'] if t['family'] == 'BIT before cover')
    need(bit_template['rank_encoding'] == '2^296630000000000' and bit_template['ambient'] == 134, 'actual repaired selected template')
    need(F(bit_template['saving']) == covered + F(1,10**10), 'exact selected pre-cover loss')
    need([a['id'] for a in claim['assumptions']] == ['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery'], 'selected record retains all original assumptions')
    out = []
    for b, target in zip(stages, stages[1:]):
        env = (1-rho)*covered+rho*b
        need(target < env and target < rho and target < 1-rho, 'strict full ordinary completion envelope')
        out.append(dict(previous=str(b), target=str(target), envelope=str(env), margin=str(env-target)))
    need(F(296630000000000)*F(1,10**10) == 29663, 'actual repaired selected H_B cover loss')
    need(1+F(64,2**45) < 2, 'cover inflation less than 2 < 2^29663')
    need(F(12039,3125000) > F(376669,100000000), 'completed BIT service supplies selected complex tariff')
    return dict(rho=str(rho), covered_saving=str(covered), stages=out,
                retained_assumptions=claim['assumptions'][1:],
                final_kappa='363005817/100000000000', new_kappa=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-receipt', action='store_true', help='Explicitly regenerate RESULT.json during preparation.')
    args = parser.parse_args()
    pins = json.loads((HERE/'SOURCE-PINS.json').read_text())
    need(len({p['path'] for p in pins}) == len(pins), 'unique extracted source paths')
    for p in pins:
        need(sha256((INPUT/p['path']).read_bytes()).hexdigest() == p['sha256'], 'complete source pin: '+p['path'])
        need(not p.get('manifest') or p['manifest'] == p['sha256'], 'unchanged selected manifest: '+p['path'])
    bit = read('research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz')
    cw = read('research/shared-wire-split-composition/data/final.json.gz')
    # This comparison is a source binding, not a second assumption or a proof
    # that the distinct raw words have identical scalar incidence matrices.
    raw = (INPUT/'research/grade14-native-realization/retained/data/binary.json.gz').read_bytes()
    need(sha256(raw).hexdigest() == 'd28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9', '#7837 word pin')
    newer = json.loads(gzip.decompress(raw))
    binary = bit_native(bit)
    complex_ = complex_native(cw)
    controls = {}
    last_scalar = max(i for i,e in enumerate(cw['program'])
                      if e[0] in ('ADD','COPY','SCALE') and e[1] < cw['public'])
    need(last_scalar == 71260 and cw['program'][last_scalar] == ['ADD',1466,1479,'-1',127], 'actual final public scalar control site')
    try: complex_native(cw,last_scalar)
    except ValueError as err: controls['corrupt_final_complex_scalar_minus1_to_minus2'] = str(err)
    else: raise ValueError('complex scalar negative control accepted')
    try: bit_native(bit, True)
    except ValueError as err: controls['omit_first_BIT_ADD'] = str(err)
    else: raise ValueError('BIT endpoint negative control accepted')
    altered = deepcopy(newer); altered['start'][111] = altered['start'][0]
    try: route_source(bit, altered)
    except ValueError as err: controls['wrong_main_chart'] = str(err)
    else: raise ValueError('main chart negative control accepted')
    result = dict(status='PASS_SELECTED_NATIVE_SOURCE_PREDICATES', authenticated_sources=len(pins), binary=binary,
                  complex=complex_, catalogue=receipts(complex_), route_binding=route_source(bit,newer),
                  rational_frames=rational_predicates(bit,binary['moves']),
                  binary_caller=bit_caller(read('research/paired-query-only-bit/EFREE-CALLER.json.gz')),
                  budget=budgets(), negative_controls=controls,
                  scope='Exact finite source conditions and historical catalogue authentication. Universal proof is separate; no certificate edit or unconditional theorem.')
    # Bind the exact JSON data model: source pair tuples become JSON arrays.
    result = json.loads(json.dumps(result))
    if args.write_receipt:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:
        expected = json.loads((HERE/'RESULT.json').read_text())
        need(result == expected, 'complete frozen finite result')
    print(json.dumps({k:v for k,v in result.items() if k != 'binary'},indent=2))
    print('BIT full endpoint:',binary['coefficient_positions'],'coefficient positions; 111 same-route off-diagonals')


if __name__ == '__main__':
    main()
