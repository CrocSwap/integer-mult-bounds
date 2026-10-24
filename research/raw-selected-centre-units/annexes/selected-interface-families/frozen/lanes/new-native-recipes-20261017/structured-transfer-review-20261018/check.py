#!/usr/bin/env python3
"""Review the structured S24 transfer with reverse ordered columns."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json
import shutil


HERE = Path(__file__).resolve().parent
REVIEW = HERE.parent
LANES = REVIEW.parent
SOURCE = LANES / 'new-core-transfer-20261017/structured-centres-transfer-20261018'
CENTRES = LANES / 'controller-followthrough-20261017/structured-centres'
PINS = {
    'transfer': 'e0cd1e8a7c99e7aecf663e735e56a5b7e98b4bff4f696e6b0339463ccad4c280',
    'centre': '5e762396d55ac47b34bbe60e30c62a429ddd6fc1f018cb4b4b94d3670d374a19',
    'scaled': 'deea4844f2327a73129c213df915819ec845fb9c97a30498d43f231a2267e733',
    'clean': 'a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa',
    'phase_review': '924b898621dd25ea9d3330563fdf7acf6c3b63dc99526e15faaee682f4bdd94d',
    'algebra': 'c6ba81bd2e382e021b2c2ea853f75576dc101400a7cce3408003fe365c7e7bef',
}
INPUTS = {}


def need(condition, label):
    if not condition:
        raise ValueError(label)


def read(path, pin=None, zipped=False):
    raw = path.read_bytes()
    content = gzip.decompress(raw) if zipped else raw
    record = {'sha256': sha256(raw).hexdigest()}
    if zipped:
        record['decompressed_sha256'] = sha256(content).hexdigest()
    INPUTS[str(path.relative_to(LANES.parent))] = record
    need(pin is None or sha256(content).hexdigest() == pin, 'Input pin: ' + str(path))
    return json.loads(content)


def frozen(folder, name, pin):
    manifest = read(folder / name, pin)
    for path, digest in manifest['artifacts'].items():
        raw = (folder / path).read_bytes()
        need(sha256(raw).hexdigest() == digest, 'Frozen artifact: ' + path)
        INPUTS[str((folder / path).relative_to(LANES.parent))] = {'sha256': digest}
    return manifest


path = REVIEW / 'check_raw_selected.py'
need(sha256(path.read_bytes()).hexdigest() == PINS['algebra'], 'Pinned independent algebra')
INPUTS[str(path.relative_to(LANES.parent))] = {'sha256':PINS['algebra']}
spec = importlib.util.spec_from_file_location('s24_independent_algebra', path)
alg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alg)
add, atom, left = alg.acc, alg.atom, alg.op_left


def wire(token, private):
    kind, index = token
    if kind == 'L':
        need(0 <= index < 632, 'Live field range')
        return index
    if kind == 'C':
        need(0 <= index < 8, 'Owned field range')
        return 632 + index
    need(kind == 'Z' and index in private, 'Private field range')
    return private[index]


def boundary(events, frame):
    frames = [frame] * 224 + [0] * 8
    operations, price = [], 0
    for event in events:
        kind, target, declared = event['kind'], event['target'], event['frame']
        need(0 <= target < 224 or target == 632, 'Boundary touches only data and C0')
        slot = target if target < 224 else 224
        if kind == 'clear':
            need(target == 632, 'Boundary CLEAR is owned')
            frames[slot] = declared
            operations.append(('clear', target))
            price += alg.price(kind)
            continue
        need(frames[slot] == declared == frame, 'Physical boundary target frame')
        if kind == 'scale':
            coefficient = Q(event['coefficient'])
            operations.append(('scale', target, coefficient))
            price += alg.price(kind, coefficient)
            continue
        source = event['source']
        need(0 <= source < 224 or source == 632, 'Boundary source range')
        other = source if source < 224 else 224
        need(source != target and frames[other] == declared, 'Physical boundary source frame')
        if kind == 'copy':
            need(target == 632, 'Only owned boundary COPY')
            operations.append(('copy', target, source))
            price += alg.price(kind)
        else:
            need(kind == 'add', 'Boundary scalar opcode')
            coefficient = Q(event['coefficient'])
            operations.append(('add', target, source, coefficient))
            price += alg.price(kind, coefficient)
    need(frames[224:] == [0] * 8, 'Boundary owned frame exit')
    return operations, price


def core(events, c, direction):
    private = {key: 640+i for i, key in enumerate(c['zero_buffers'])}
    frames = c['start'][:] + [0] * 8 + [None] * len(private)
    active, allocated, returned = set(), set(), set()
    allowed_warps = set(map(tuple, c['warp_edges']))
    operations, invoice, profile = [], 0, Counter()
    for event in events:
        tag = event[0]
        if tag == 'scalar':
            gate, declared = event[1:]
            kind, target = gate[0], wire(gate[1], private)
            need(target < 640 or target in active, 'Active core target')
            if kind == 'clear':
                need(632 <= target < 640, 'Only owned core CLEAR')
                frames[target] = declared
                operations.append(('clear', target))
                invoice += alg.price(kind)
            elif kind == 'scale':
                need(frames[target] == declared, 'Core SCALE frame')
                coefficient = Q(*gate[2:])
                operations.append(('scale', target, coefficient))
                invoice += alg.price(kind, coefficient)
            else:
                need(kind == 'add', 'Core ADD grammar')
                source = wire(gate[2], private)
                need(source < 640 or source in active, 'Active core source')
                need(source != target and frames[source] == frames[target] == declared, 'Core ADD frame')
                coefficient = Q(*gate[3:])
                operations.append(('add', target, source, coefficient))
                invoice += alg.price(kind, coefficient)
        elif tag == 'climb':
            _, _, target, old, new, rank = event
            before, after = c['frames'][old], c['frames'][new]
            need(frames[target] == old, 'Native input frame')
            need(alg.rank(before + after) == len(after) and rank == len(after)-len(before) > 0,
                 'Nested native child and exact rank')
            frames[target] = new
            profile[rank] += 1
        elif tag == 'warp':
            target, symbol, old, new = wire(event[1], private), *event[2:]
            need(target < 640 or target in active, 'Active warp target')
            need(frames[target] == old and (1 if symbol > 0 else -1, abs(symbol), old, new) in allowed_warps,
                 'Actual signed warp class')
            frames[target] = new
            letter = (abs(symbol) + (10000 if direction == 'forward' else 20000)) * (1 if symbol > 0 else -1)
            operations.append(('operator', target, letter))
        elif tag == 'zero_buffer':
            target = private[event[2]]
            if event[1] == 'alloc':
                need(target not in allocated, 'Single private allocation')
                active.add(target)
                allocated.add(target)
                frames[target] = 1
                operations.append(('zero', target))
            else:
                need(event[1] == 'free' and target in active and frames[target] == 1, 'Private return at FULL')
                active.remove(target)
                returned.add(target)
        elif tag == 'adapter':
            _, side, target, frame = event
            need(side in ('old_to_new', 'new_to_old'), 'Adapter orientation')
            endpoint = c['start'] if side == 'old_to_new' else c['final']
            need(endpoint[target] == frame, 'Ordinary adapter endpoint')
        elif tag == 'residual_adapter':
            _, side, target, entry, *end = event
            need(side in ('pre', 'post') and c['start'][target] == entry and
                 c['final'][target] == (end[0] if end else 1), 'Residual wrapper endpoints')
        else:
            need(tag == 'phase', 'Known core event')
    need(not active and allocated == returned == set(private.values()), 'All private lifetimes close')
    need(frames[:640] == c['final'] + [0] * 8, 'Every native endpoint frame')
    need(invoice == 87360 and profile == {1:2433,2:724,3:228,4:102,5:20}, 'Core invoice and native profile')
    return operations, {'dyadic_real_primitives': invoice, 'native_children': 3507,
                        'native_mass': 5073, 'private_returns': 91, 'profile': dict(profile)}


def reverse(operations, expected, private=False, coherent=True):
    total = 731 if private else 640
    columns = [atom(i) for i in range(total)]
    probes, admitted = {}, set()
    for position, event in enumerate(operations):
        kind, target = event[:2]
        if kind == 'clear':
            if target in admitted:
                probes[position] = total + len(probes)
            admitted.add(target)
        elif kind == 'copy':
            need(target in admitted, 'Owned COPY follows admission')
            probes[position] = total + len(probes)
    if not coherent:
        probes = {}
    for position in range(len(operations)-1, -1, -1):
        event = operations[position]
        kind, target = event[:2]
        if kind in ('clear', 'zero'):
            columns[target] = {}
        elif kind == 'copy':
            add(columns[event[2]], columns[target])
            columns[target] = {}
        elif kind == 'add':
            add(columns[event[2]], columns[target], event[3])
        elif kind == 'scale':
            columns[target] = {key: value * event[2] for key, value in columns[target].items()}
        else:
            need(kind == 'operator', 'Reverse operator grammar')
            letter, moved = event[2], {}
            for (word, output), value in columns[target].items():
                result = word[:-1] if word and word[-1] == -letter else word + (letter,)
                add(moved, {(result, output): value})
            columns[target] = moved
        if position in probes:
            add(columns[target], atom(probes[position]))
    wanted = [{} for _ in range(total)]
    for output, row in enumerate(expected):
        for (word, source), value in row.items():
            add(wanted[source], {(word, output): value})
    for index, (actual, goal) in enumerate(zip(columns, wanted)):
        need(actual == goal, ('Reverse input column or coherent zero observable', index))
    return {'arbitrary_input_columns': 640, 'private_columns': total-640,
            'zero_before_later_CLEAR_or_COPY_observables': len(probes)}


def matrix_apply(matrix, values):
    result = []
    for row in matrix:
        out = {}
        for p, coefficient in row.items():
            add(out, values[p], coefficient)
        result.append(out)
    return result


def matrix_product(a, b):
    result = []
    for row in a:
        out = {}
        for i, x in row.items():
            for j, y in b[i].items():
                value = out.get(j, 0) + x*y
                if value:
                    out[j] = value
                else:
                    out.pop(j, None)
        result.append(out)
    return result


def derive(source, receipt, selected):
    response = [{int(k): Q(v) for k, v in row.items()} for row in source['response']]
    K = [{int(k): Q(v) for k, v in row.items()} for row in source['centre_rows']]
    centre = set(receipt['centre_support_ports'])
    ordinary = set(range(112)) - set(selected)
    hadamard = set(range(112)) - centre
    need(len(centre) == 48 and len(hadamard) == 64 and len(selected) == 24, 'Actual split dimensions')
    minors = receipt['orthogonal_minor_ports']
    need(len(minors) == 6 and sorted(p for m in minors for p in m) == sorted(centre), 'Six disjoint centre minors')
    need(sorted(selected) == sorted(p for m in minors[:3] for p in m), 'Actual first-three-minor selection')
    for minor in minors:
        need([[sum(a.get(p,0)*b.get(p,0) for p in minor) for b in K] for a in K] ==
             [[Q(2*(i==j)) for j in range(8)] for i in range(8)], 'Every minor Gram identity')
    need(all(len(row) == 12 and set(row.values()) <= {Q(-1),Q(1)} for row in K), 'Actual signed centre rows')
    gram = [{q: sum(row.get(p,0)*row.get(q,0) for row in K) for q in centre} for p in range(112)]
    gram = [{q:v for q,v in row.items() if v} for row in gram]
    for p in range(112):
        need(all(response[p].get(q,0) == response[q].get(p,0) for q in range(112)), 'Symmetric actual response')
        if p in centre:
            desired = {p:Q(-1)}
            for q,v in gram[p].items():
                desired[q] = desired.get(q,0)+v/2
            need(response[p] == {q:v for q,v in desired.items() if v}, 'Actual centre response formula')
        else:
            need(set(response[p]) <= hadamard, 'Separate Hadamard response support')
    J = [{q:-v for q,v in row.items()} for row in response]
    identity = [{p:Q(1)} for p in range(112)]
    H, Hi, A, Ai = (deepcopy(identity) for _ in range(4))
    sign = {p: -1 if p in selected else 1 for p in range(112)}
    for p in ordinary:
        H[p] = {q:v for q,v in J[p].items() if q in ordinary}
    for p in centre & ordinary:
        for q,v in gram[p].items():
            if q in ordinary:
                Hi[p][q] = Hi[p].get(q,0)-v/4
    for p in centre:
        A[p], Ai[p] = {p:Q(sign[p])}, {p:Q(sign[p])}
        for q,v in gram[p].items():
            A[p][q] = A[p].get(q,0)-v/4
            Ai[p][q] = Ai[p].get(q,0)+sign[p]*sign[q]*v/4
    H64, Hi64 = deepcopy(identity), deepcopy(identity)
    for p in hadamard:
        H64[p] = dict(J[p])
        Hi64[p] = {q:v/4 for q,v in J[p].items()}
        Hi[p], A[p], Ai[p] = dict(Hi64[p]), dict(Hi64[p]), dict(H64[p])
    for matrix in (H,Hi,A,Ai):
        for p,row in enumerate(matrix):
            matrix[p] = {q:v for q,v in row.items() if v}
    for first, second in ((H,Hi),(Hi,H),(A,Ai),(Ai,A),(H64,Hi64),(Hi64,H64)):
        need(matrix_product(first,second) == identity, 'Exact complete scalar inverse order')
    return J,H,Hi,A,Ai,H64,Hi64,ordinary,hadamard


def expected_maps(selected, J, H, Hi, A, Ai, ordinary):
    identity = [atom(i) for i in range(640)]
    selected = set(selected)
    x = identity[:112]
    y = identity[112:224]
    qa = [left(x[p],p,1) if p in selected else {} for p in range(112)]
    qb = [left(y[p],p,-1) if p in selected else {} for p in range(112)]
    back_query = [qa[p] if p in selected else y[p] for p in range(112)]
    forward_query = [qb[p] if p in selected else x[p] for p in range(112)]
    jb, jf = matrix_apply(J,back_query), matrix_apply(J,forward_query)
    raw_b, raw_f = deepcopy(identity), deepcopy(identity)
    for p in range(112):
        if p in selected:
            raw_b[p], raw_b[112+p] = dict(qb[p]), dict(qa[p])
            add(raw_f[p],left(jf[p],p,-1))
        add(raw_b[p],jb[p],-1)
        if p in ordinary:
            add(raw_f[112+p],jf[p])
    balanced_b, balanced_f = deepcopy(raw_b), deepcopy(raw_f)
    hi_x = matrix_apply(Hi,raw_b[:112])
    hv = matrix_apply(H,y)
    for p in ordinary:
        balanced_b[p] = hi_x[p]
        balanced_f[112+p] = dict(hv[p])
        add(balanced_f[112+p],jf[p])
    lx = [left(x[p],p,1) if p in selected else x[p] for p in range(112)]
    dy = [left(y[p],p,-1) if p in selected else {key:-v for key,v in y[p].items()} for p in range(112)]
    diagonal, normalized = deepcopy(raw_b), deepcopy(raw_b)
    alx, aidy = matrix_apply(A,lx), matrix_apply(Ai,dy)
    for p in range(112):
        diagonal[p] = alx[p]
        add(diagonal[p],dy[p])
        normalized[p] = dict(lx[p])
        add(normalized[p],aidy[p])
    result = dict(raw_backward=raw_b,balanced_backward=balanced_b,diagonal_backward=diagonal,
                  normalized_backward=normalized,raw_forward=raw_f,balanced_forward=balanced_f)
    for rows in result.values():
        rows[632:] = [{} for _ in range(8)]
    return result


def selected_exchange(selected, frame):
    events = []
    for p in selected:
        for kind,t,s,value in (('add',p,112+p,1),('add',112+p,p,-1),('add',p,112+p,1),('scale',112+p,None,-1)):
            e = {'kind':kind,'target':t,'coefficient':str(value),'frame':frame}
            if s is not None:
                e['source'] = s
            events.append(e)
    return events


def hadamard_inventory(pairs, gauges, hadamard):
    need(len(pairs) == 8 and sorted(p for pair in pairs for side in ('left','right')
                                  for p in pair[side]) == sorted(hadamard),
         'Eight disjoint Hadamard group pairs')
    events = []

    def emit(kind, target, coefficient, source=None):
        event = {'kind':kind,'target':target,'coefficient':str(coefficient),'frame':1}
        if source is not None:
            event['source'] = source
        events.append(event)

    for pair in pairs:
        for side in ('left','right'):
            fields = pair[side]
            need(len(fields) == 4, 'Four fields per Hadamard group')
            for i,j,d in ((0,1,-1),(2,3,1),(0,2,-1),(1,3,1)):
                a,b = fields[i],fields[j]
                emit('add',a,d,b)
                emit('scale',b,2)
                emit('add',b,-d,a)
            for i in (1,2):
                emit('scale',fields[i],-1)
        for a,b in zip(pair['left'],pair['right']):
            emit('add',a,1,b)
            emit('add',b,-1,a)
            emit('add',a,1,b)
            emit('scale',b,-1)
    inverse = []
    for event in reversed(events):
        inverse.append(dict(event,coefficient=str(-Q(event['coefficient']) if event['kind']=='add'
                                                 else 1/Q(event['coefficient']))))
    need(gauges['hadamard_X'] == events and gauges['hadamard_inverse_X'] == inverse,
         'Literal sixteen Hadamard kernels, 32 physical exchanges, and complete inverse')
    return {'four_port_kernels':16,'physical_exchanges':32,'scalar_events':len(events),
            'literal_complete_inverse_checked':True}


def native(event):
    return event[0] in ('climb','center','warp','adapter','residual_adapter')


def check_core_edit(provider, source, clean):
    originals = source['programs']
    need(len(originals['forward']) == len(originals['backward']), 'Paired source index domain')
    sites = []
    for i,e in enumerate(originals['forward']):
        if e[0] == 'scalar' and e[1][0] == 'add':
            target, origin = e[1][1:3]
            is_y = lambda f: f[0]=='L' and 112<=f[1]<224
            if is_y(target) and not is_y(origin):
                sites.append(i)
                need(originals['backward'][i][1][1:3] == [origin,target], 'Paired transposed transfer site')
    need(len(sites) == 184 and provider['negative_transfer_sites'] == sites, 'Exactly 184 changed transfer signs')
    for direction in ('forward','backward'):
        desired = deepcopy(originals[direction])
        for i in sites:
            desired[i][1][3] *= -1
        actual = next(p['retained_core'] for p in provider['programs'].values() if p['orientation']==direction)
        need(actual == desired, 'Exact complete sign edit')
        need([e for e in actual if native(e)] == [e for e in clean['programs'][direction] if native(e)],
             'Exact native record bridge to reviewed current source')
        need(all(p['retained_core']==actual for p in provider['programs'].values() if p['orientation']==direction),
             'One exact core for every variant')


def physical_frames(c):
    need(len(c['start'])==632 and c['start'][112:224]==[0]*112 and c['final'][:112]==[1]*112,
         'Actual source and target endpoint types')
    for p,port in enumerate(c['ports']):
        need(c['frames'][c['start'][p]] == [port], 'Actual intrinsic input line')
        hole = c['frames'][c['final'][112+p]]
        need(len(hole)==alg.rank(hole)==8 and all((v & port).bit_count()%2==0 for v in hole),
             'Actual intrinsic output hole')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    need(not args.out.exists(), 'New output directory')
    need(shutil.disk_usage(HERE).free>=3*1024**3, 'At least 3 GiB free disk')
    transfer=frozen(SOURCE,'FREEZE.json',PINS['transfer'])
    frozen(CENTRES,'FREEZE.json',PINS['centre'])
    frozen(CENTRES,'GAUGES-V2-FREEZE.json',PINS['scaled'])
    source=read(CENTRES/'STRUCTURED-CENTRES-PROGRAM.json.gz','2b9de1454c2025ae4e230bd64de36b4f6c937628c63fc5afede6640dd3c0e1e1',True)
    source_receipt=read(CENTRES/'STRUCTURED-CENTRES.json')
    clean=read(LANES/'new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz',PINS['clean'],True)
    read(LANES/'independent-review-20261017/NEW-CORE-NATIVE-REVIEW.json',PINS['phase_review'])
    bridge=read(SOURCE/'NATIVE-GEOMETRY-BRIDGE.json')
    for name,pin in bridge['phase_inputs'].items():
        read(LANES/name,pin) if name.endswith('.json') else need(sha256((LANES/name).read_bytes()).hexdigest()==pin,'Phase proof pin')
    reports={}
    wrong_Q_order=[]
    for implementation in ('original','scaled'):
        packet=read(SOURCE/(implementation+'-normal')/'STRUCTURED-TRANSFER-PROGRAMS.json.gz',transfer['payload_decompressed_sha256'][implementation],True)
        selected=packet['selected_S']
        J,H,Hi,A,Ai,H64,Hi64,ordinary,hadamard=derive(source,source_receipt,selected)
        need(packet['ordinary_U']==sorted(ordinary) and packet['hadamard_ports']==sorted(hadamard), 'Exact packet partition')
        expected=expected_maps(selected,J,H,Hi,A,Ai,ordinary)
        reports[implementation]={}
        for provider,item in packet['providers'].items():
            c=item['canonical']
            canonical_path=REVIEW/provider/'CANONICAL-WORD.json.gz'
            native_c=read(canonical_path,zipped=True)
            need(sha256(canonical_path.read_bytes()).hexdigest() ==
                 bridge['providers'][provider]['phase_canonical_compressed_sha256'],
                 'Exact compressed canonical phase input')
            need(c==native_c==source['providers'][provider]['canonical']==clean['providers'][provider]['canonical'],
                 'Semantic canonical equality to all pinned phase providers')
            physical_frames(c)
            check_core_edit(item,source['providers'][provider],clean['providers'][provider])
            gauges=item['gauge_words']
            inventory=hadamard_inventory(item['hadamard_pairs'],gauges,hadamard)
            gauge_checks={}
            matrices=dict(ordinary_Y=H,ordinary_inverse_X=Hi,data_X=A,data_inverse_X=Ai,
                          hadamard_X=H64,hadamard_inverse_X=Hi64)
            compiled={}
            for name,events in gauges.items():
                compiled[name]=boundary(events,0 if name=='ordinary_Y' else 1)
                identity=[atom(i) for i in range(640)]
                wanted=deepcopy(identity)
                if name=='fused_inverse_X':
                    changed=matrix_apply(Hi,identity[:112])
                    for p in selected:
                        for q in ordinary:
                            if J[p].get(q,0):
                                add(changed[p],changed[q],-J[p][q])
                else:
                    offset=112 if name=='ordinary_Y' else 0
                    changed=matrix_apply(matrices[name],identity[offset:offset+112])
                offset=112 if name=='ordinary_Y' else 0
                wanted[offset:offset+112]=changed
                if any(e['kind']=='clear' for e in events):
                    wanted[632]={}
                check=reverse(compiled[name][0],wanted)
                check['dyadic_real_primitives']=compiled[name][1]
                gauge_checks[name]=check
            identity=[atom(i) for i in range(640)]
            zero_c=deepcopy(identity);zero_c[632]={}
            for a,b in (('hadamard_X','hadamard_inverse_X'),('hadamard_inverse_X','hadamard_X'),
                        ('data_X','data_inverse_X'),('data_inverse_X','data_X')):
                reverse(compiled[a][0]+compiled[b][0],identity if a.startswith('hadamard') else zero_c)
            need(compiled['hadamard_X'][1]==compiled['hadamard_inverse_X'][1]==2048,'Priced64-port words')
            input_exchange=selected_exchange(selected,0)
            output_exchange=selected_exchange(selected,1)
            need(boundary(input_exchange,0)[1]==boundary(output_exchange,1)[1]==624,'Priced24 physical exchanges')
            costs={'raw_backward':87984,'raw_forward':88608}
            costs.update(dict(zip(('balanced_backward','diagonal_backward','normalized_backward','balanced_forward'),
                                 (91368,91944,96684,91894) if implementation=='original' else (91208,91592,96012,91830))))
            checks={}
            for name,program in item['programs'].items():
                direction=program['orientation']
                prefix=gauges['ordinary_Y'] if name=='balanced_forward' else []
                suffix={'raw_backward':[], 'balanced_backward':gauges['ordinary_inverse_X'],
                        'diagonal_backward':gauges['fused_inverse_X'],
                        'normalized_backward':gauges['fused_inverse_X']+gauges['data_inverse_X'],
                        'raw_forward':output_exchange,'balanced_forward':output_exchange}[name]
                need(program['prefix']==prefix and program['input_exchange']==input_exchange and program['suffix']==suffix,
                     'Exact complete boundary composition')
                need(program['events']==prefix+input_exchange+program['retained_core']+suffix,'Complete serialized word')
                pre_ops,pre_cost=boundary(prefix+input_exchange,0)
                post_ops,post_cost=boundary(suffix,1)
                native_ops,native_bill=core(program['retained_core'],c,direction)
                operations=[('operator',p,p+1) for p in range(112)]+pre_ops
                operations += [('operator',p,-p-1) for p in range(112)]+native_ops
                operations += [('operator',112+p,-p-1) for p in range(112)]+post_ops
                operations += [('operator',112+p,p+1) for p in range(112)]
                check=reverse(operations,expected[name],private=True)
                bill=pre_cost+native_bill['dyadic_real_primitives']+post_cost
                need(bill==costs[name],'Complete independently counted invoice')
                if direction=='backward':
                    need(all(left(expected[name][112+p],p,-1)==atom(p) for p in selected),
                         'Selected productive physical Y is original X')
                if name=='normalized_backward':
                    for p in range(112):
                        x_part={key:v for key,v in expected[name][p].items() if key[1]<112}
                        need(x_part==(left(atom(p),p,1) if p in selected else atom(p)),
                             'Exact ordered original-X normalization')
                    mistaken=deepcopy(expected[name])
                    ai_y=matrix_apply(Ai,[atom(112+p) for p in range(112)])
                    for p in range(112):
                        mistaken[p]=left(atom(p),p,1) if p in selected else atom(p)
                        add(mistaken[p],left(ai_y[p],p,-1) if p in selected else
                            {key:-v for key,v in ai_y[p].items()})
                    need(mistaken!=expected[name], 'The actual Q order is material')
                    try:
                        reverse(operations,mistaken,private=True)
                    except ValueError:
                        wrong_Q_order.append(implementation+'/'+provider)
                    else:
                        raise ValueError('Wrong borrowed-source order D A^-1 was accepted')
                check.update(dyadic_real_primitives=bill,native_mass=5073,native_children=3507,
                             helpers_restored_under_inherited_wrappers=408,owned_zero_outputs=8,
                             exact_Q_order_checked=True,physical_input_line_and_output_hole_checked=True)
                checks[name]=check
            reports[implementation][provider]={'programs':checks,'gauges':gauge_checks,
                                               'hadamard_inventory':inventory,'literal_inverse_orders':4}
            print(implementation,provider,'six complete ordered words and seven gauges PASS',flush=True)
        if implementation=='scaled':
            retained_packet=packet
    # A hidden residual can preserve the endpoint but must fail the zero check.
    events=deepcopy(retained_packet['providers']['base']['gauge_words']['ordinary_inverse_X'])
    position=next(i for i,e in enumerate(events) if e['kind']=='clear' and i)
    events.insert(position,{'kind':'add','target':632,'source':0,'coefficient':'1','frame':1})
    bad,_=boundary(events,1)
    wanted=[atom(i) for i in range(640)];wanted[:112]=matrix_apply(Hi,wanted[:112]);wanted[632]={}
    reverse(bad,wanted,coherent=False)
    try:
        reverse(bad,wanted,coherent=True)
    except ValueError as error:
        mutation=str(error)
    else:
        raise ValueError('Hidden query erasure was accepted')
    out={'status':'PASS_INDEPENDENT_STRUCTURED_S24_PHYSICAL_TRANSFER','implementations':reports,
         'complete_native_words_checked':24,'hidden_query_erasure_rejected':mutation,
         'hidden_query_erasure_endpoint_still_correct':True,
         'wrong_Q_order_rejected':wrong_Q_order,
         'scope':'Complete local words and coherent scalar gauges. Native phases use exact unchanged orientation-specific source records. No global route, caller exterior phase, hosting, recursive precision, or supplier claim.',
         'checker_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}
    args.out.mkdir(parents=True)
    (args.out/'REVIEW.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    (args.out/'INPUTS.json').write_text(json.dumps(INPUTS,indent=2,sort_keys=True)+'\n')
    print(out['status'],flush=True)


if __name__=='__main__':
    main()
