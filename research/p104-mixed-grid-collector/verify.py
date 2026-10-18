#!/usr/bin/env python3
"""Exact mixed-grid collector certificate, Apache-2.0.

Prepared for ywz65 with substantial OpenAI Codex assistance. The independent
matrix construction uses a closed seven-factor formula and integer arithmetic.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
N, ZERO = 512, (0, 0)
SOURCES = ['D31', 'D30', 'D29', 'D28', 'D27']
FRAME = [256, 136, 64, 40, 16, 4, 2, 1]
QUERY_FRAME = [364]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)


def same(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def load():
    # Check every external executable and scientific byte before import.
    for pin in read_json(HERE / 'SOURCES.json')['vendored_files']:
        raw = (HERE / pin['local']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA256 ' + pin['local'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == pin['git_blob'], 'source Git blob ' + pin['local'])
    spec = importlib.util.spec_from_file_location('rounded_predecessor', HERE/'vendor/pr2665/verify.py')
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    local, recipes = old.load_inputs()
    word = read_json(HERE/'vendor/pr2665/inputs/WORD.json')
    need(word['chart'] == 'Delta_W = conjugate(Gamma_W) = Gamma_W^(-T)', 'physical chart')
    frames = copy.deepcopy(word['initial_frames'])
    for event in word['program'][:2025]:
        op, target = event[:2]
        if op == 'transport':
            need(frames[target] == event[2], 'prefix transport frame')
            frames[target] = event[3]
        elif op == 'add':
            need(frames[target] == frames[event[2]] == event[4], 'prefix common ADD frame')
        elif op == 'sign':
            need(frames[target] == event[3] and event[2] in ('-1', '1'), 'prefix sign frame')
        else:
            raise ValueError('unexpected prefix allocation')
    need(all(frames[s] == FRAME for s in SOURCES), 'all five physical entrance frames')
    need(frames['Q7'] == QUERY_FRAME, 'query current chart')
    need(local[0] == ['zero','C',FRAME] and local[14] == ['erase','C',FRAME], 'collector lifecycle')
    need(local[6] == ['transport','C',FRAME,QUERY_FRAME,7]
         and local[8] == ['transport','C',QUERY_FRAME,FRAME,7], 'literal chart change')
    return old, local, recipes


def turn(value, phase):
    a, b = value
    for _ in range(phase % 4):
        a, b = -b, a
    return a, b


def action(record, address):
    image = record['offset']
    for j, mask in enumerate(record['matrix_rows']):
        if (mask & address).bit_count() & 1:
            image ^= 1 << j
    phase = record['phase']
    for j in range(9):
        if address >> j & 1:
            phase += record['linear_Z4'][j]
            phase += 2 * (record['quadratic_rows'][j] & address & ~((1 << (j+1))-1)).bit_count()
    return image, phase % 4


def columns(recipe):
    need(recipe['rank'] == 7, 'closed formula rank')
    for side in ('left','right'):
        need(sorted(action(recipe[side], x)[0] for x in range(N)) == list(range(N)), 'permutation')
    result = []
    for source in range(N):
        middle, p = action(recipe['right'], source)
        col = {}
        for low in range(128):
            target, q = action(recipe['left'], (middle & ~127) | low)
            distance = ((middle & 127) ^ low).bit_count()
            # (1+i)^7 (-i)^distance /2^7 = (1-i)(-i)^distance /16.
            col[target] = turn((1,-1), p + q - distance)
        need(len(col) == 128 and all(abs(a) == abs(b) == 1 for a,b in col.values()), 'flat column')
        result.append(col)
    return result


def matvec(cols, vector):
    """Numerator product for matrix cols/16; caller tracks denominator."""
    real, imag = [0]*N, [0]*N
    for col, (a,b) in zip(cols, vector):
        if a or b:
            for row, (c,d) in col.items():
                real[row] += c*a-d*b
                imag[row] += c*b+d*a
    return list(zip(real,imag))


def literal(old, local, recipes, initial, bits, guard=4, coarse_query=False):
    state, child, defects = copy.deepcopy(initial), 0, []
    for event in local:
        op, target = event[:2]
        if op == 'zero':
            need(target not in state, 'fresh private register')
            state[target] = ([ZERO]*N,0)
        elif op == 'transport':
            exact = old.native(*state[target], recipes[child])
            state[target] = old.quantize(*exact, bits+guard if child == 0 else bits)
            defects.append(old.subtract(state[target],exact))
            child += 1
        elif op == 'add':
            coefficient = int(event[3])
            need(coefficient in (-1,1), 'unit coefficients only')
            vector, exponent = state[event[2]]
            state[target] = old.subtract(state[target], ([(-coefficient*a,-coefficient*b) for a,b in vector],exponent))
            if coarse_query and target == 'Q7':
                state[target] = old.quantize(*state[target],bits)
        elif op == 'erase':
            residue = state.pop(target)
        else:
            raise ValueError('unexpected local instruction')
    need(child == 2 and all(state[s] == initial[s] for s in SOURCES), 'children and dirty restoration')
    return residue, state['Q7'], defects


def verify():
    old, local, recipes = load()
    u,v = [columns(recipe) for recipe in recipes]
    need({sum(row in col for col in u) for row in range(N)} == {128}, 'row support for magnitude bill')
    for matrix, recipe in zip((u,v),recipes):
        for x,col in enumerate(matrix):
            dense = [col.get(y,ZERO) for y in range(N)]
            need(old.native(*old.basis(x),recipe) == (dense,4), 'closed formula vs butterfly')
    for x,col in enumerate(u):
        product = matvec(v,[col.get(y,ZERO) for y in range(N)])
        need(product == old.basis(x,256)[0], 'independent VU column')
    need(same(old.verify((local,recipes)),read_json(HERE/'vendor/pr2665/RESULT.json')), 'predecessor receipt')
    zero, grids = ([ZERO]*N,0), [0,1,4,17,64]
    for bits in grids:
        initial = {name:old.normalize([(((x+3)*(j+5))%31-15,((x*x+7)*(j+2))%29-14) for x in range(N)],bits)
                   for j,name in enumerate(SOURCES+['Q7'])}
        numerators = [tuple(sum(initial[s][0][x][k]*(1 << (bits-initial[s][1])) for s in SOURCES) for k in (0,1)) for x in range(N)]
        ideal = old.normalize(matvec(u,numerators),bits+4)
        expected = old.subtract(initial['Q7'],([(-a,-b) for a,b in ideal[0]],ideal[1]))
        residue,query,defects = literal(old,local,recipes,initial,bits)
        need(residue == zero and query == expected and defects == [zero,zero], 'all-five dirty fixture')
        residue,coarse,_ = literal(old,local,recipes,initial,bits,coarse_query=True)
        need(residue == zero, 'coarse one-way query leaves cleanup exact')
        error,exponent = old.subtract(coarse,expected)
        need(sum(a*a+b*b for a,b in error)*(1 << (2*bits)) <= 256*(1 << (2*exponent)), 'query error <=16h')
    for guard in range(4):
        initial = {s:zero for s in SOURCES+['Q7']}
        initial['D31'] = old.basis(0,1,9)
        residue,query,_ = literal(old,local,recipes,initial,9,guard)
        need(query == zero and residue == old.basis(0,-1,9), 'insufficient guard witness')
        for bits in (5,8,17):
            initial['D31'] = old.basis(0,(1<<bits)+1,bits)
            residue,query,defects = literal(old,local,recipes,initial,bits,guard)
            need(residue == old.basis(0,-1,bits) and query == old.native(*old.basis(0),recipes[0]), 'scaled guard witness')
            error,exponent = defects[0]
            need(sum(a*a+b*b for a,b in error)*(1 << (2*bits)) == 1 << (2*exponent), 'scaled defect norm h')
            need(defects[1] == zero, 'scaled exact return')
    initial = {s:zero for s in SOURCES+['Q7']}
    initial['D31'] = old.basis(0,1,9)
    wrong_cleanup = copy.deepcopy(local); wrong_cleanup[13][3] = '1'
    need(literal(old,wrong_cleanup,recipes,initial,9)[0] != zero, 'wrong cleanup control')
    wrong_return = copy.deepcopy(recipes); wrong_return[1]['left']['phase'] += 2
    need(literal(old,local,wrong_return,initial,9)[0] != zero, 'wrong inverse control')
    arbitrary_return = old.native(*old.basis(0,1,13),recipes[1])
    need(old.quantize(*arbitrary_return,9) != arbitrary_return, 'arbitrary finer-grid return control')
    need(literal(old,local,recipes,initial,9,coarse_query=True)[1] != literal(old,local,recipes,initial,9)[1], 'coarse query changes endpoint')
    return dict(status='PASS_P104_MIXED_GRID_COLLECTOR',source_pr=2665,
                source_head='f9e96e979b7630b7a70705c9774d00fc07014110',events=[2025,2039],native_events=[2031,2033],
                physical_chart='Delta_W = conjugate(Gamma_W) = Gamma_W^(-T)',
                gather_frame=FRAME,query_frame=QUERY_FRAME,dirty_sources=SOURCES,
                independent_native_columns=1024,independent_inverse_columns=512,
                column_denominator=16,support_per_column=128,support_per_row=128,
                all_input_contract='b>=0; five D and Q7 real/imaginary coordinates in 2^-b Z; exact ADD; completed U on 2^-(b+4), V on 2^-b; exact fine-grid Q7',
                minimum_outbound_extra_fractional_bits=4,private_extra_fractional_storage_bits=4096,
                exact_query_extra_fractional_storage_bits=4096,
                component_magnitude_bounds={'private':'80B','query':'81B','assumption':'all six entrance real/imaginary components <= B'},
                local_bill={'rank_seven_children':2,'rank_mass':14,'unit_adds':11,'fresh_zero':1,'strict_zero_erase':1},
                dense_all_source_grids=grids,insufficient_guards=[0,1,2,3],scaled_guard_cases=12,
                controls=['wrong cleanup','wrong inverse phase','arbitrary fine-grid inverse entrance','coarse query endpoint'],
                predecessor_receipt_unchanged=True,
                scope='Completed-operation local grid contract; no internally rounded child, rounded prefix, hosting, full supplier or kappa.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path)
    args = parser.parse_args()
    if args.out:
        need(not args.out.exists(),'output already exists')
    result = verify()
    need(same(result,read_json(HERE/'RESULT.json')),'complete typed receipt equality')
    if args.out:
        with args.out.open('x',encoding='utf-8') as stream:
            stream.write(json.dumps(result,indent=2)+'\n')
    print('PASS_P104_MIXED_GRID_COLLECTOR columns=1024 inverse=512 sharp_guard=4')


if __name__ == '__main__':
    main()
