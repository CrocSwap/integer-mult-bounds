#!/usr/bin/env python3
"""QQ16 L2 in the accumulated frame. William Lawyer / OpenAI Codex. Apache-2.0."""
import argparse
import ast
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AXES = tuple(1 << i for i in range(73))
OLD = tuple((v, 1) for v in AXES[:9])
STAGE = tuple((v, 1) for v in AXES[9:17])
CURRENT = OLD + STAGE


def require(ok, why):
    if not ok:
        raise ValueError(why)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def act(g, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= g[bit.bit_length() - 1]
        vector ^= bit
    return result


@lru_cache(None)
def product(g, h):
    return tuple(act(g, v) for v in h)


@lru_cache(None)
def phase(terms):
    """Full Z/4 multilinear polynomial; XOR expands mod 4 through degree 2."""
    linear, quadratic = [0] * 73, [0] * 73
    for v, c in terms:
        bits = [i for i in range(73) if v >> i & 1]
        for i in bits:
            linear[i] = (linear[i] + c) % 4
            if c % 2:
                for j in bits:
                    if i < j:
                        quadratic[i] ^= 1 << j
    return tuple(linear), tuple(quadratic)


def transport(terms, g, shift):
    return tuple((act(g, v), c) for v, c in terms) + ((shift, 2),)


def preserving_shift(g):
    linear, quadratic = phase(tuple((g[i], 1) for i in range(17)))
    require(not any(quadratic), 'quadratic frame residual')
    delta = [((i < 17) - linear[i]) % 4 for i in range(73)]
    require(all(x % 2 == 0 for x in delta), 'odd frame residual')
    return sum((x // 2) << i for i, x in enumerate(delta))


def load_sources():
    sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    raw = {}
    for item in sources['files']:
        if item['usage'] == 'input':
            data = (ROOT / item['path']).read_bytes()
            require(digest(data) == item['sha256'], 'source hash: ' + item['path'])
            raw[item['path']] = data
    p = json.loads(gzip.decompress(raw['research/joint-query/certificate.json.gz']))
    R = [[Q(row.get(str(i), 0)) for i in range(112)] for row in p['R_rows']]
    A, T, U = (tuple(p[k + '_ports']) for k in ('A', 'T', 'U'))
    require(A == (0,7,20,27,36,46,57,111) and T == (21,37,47,76,81,87,92,110), 'selected partition')
    require(U == tuple(i for i in range(112) if i not in A + T), 'ordinary partition')
    require(all(v in (-1,0,1) for row in R for v in row), 'signed centre matrix')
    require(all(sum(R[i][t]*R[j][t] for t in T) == 4*(i == j)
                for i in range(8) for j in range(8)), 'selected Gram')
    require(all(sum(R[k][t]**2 for k in range(8)) == 4 for t in U+T), 'column norms')
    records = {}
    registry = p['map_registry']
    for port in U + T:
        names = [e[2] for e in p['programs']['B_1_2'] if e[0] == 'cover_map' and e[1] == ['L',112+port]]
        require(len(names) == 4, 'current route inventory')
        entry, leave = (registry[n] for n in names[-2:])
        g = tuple(entry['owner_right_matrix_columns'])
        require(len(g) == 73 and product(g,g) == AXES, 'involutive route')
        require(all((g[i]&g[j]).bit_count()%2 == (i == j)
                    for i in range(73) for j in range(73)), 'orthogonal route')
        require(all(g[i] == AXES[i] for i in range(17,73)) and all(v < 1<<17 for v in g[:17]), 'spectator support')
        old = entry['payload_translation_at_identity_owner']
        require(tuple(leave['owner_right_matrix_columns']) == g and
                leave['payload_translation_at_identity_owner'] == act(g,old), 'registered inverse')
        basis = g[9:17]
        require(all(v < 512 for v in basis), 'local chart basis')
        normals = [q for q in range(1,512) if all((q&v).bit_count()%2 == 0 for v in basis)]
        require(len(normals) == 1 and normals[0].bit_count()%2 == 1, 'unique odd normal')
        q = normals[0]
        require(act(g,q) == q, 'route fixes normal')
        if 'positive_'+str(port) in p['native_line_recipes']:
            require(p['native_line_recipes']['positive_'+str(port)]['label'] == q, 'selected normal binding')
        require(phase(transport(OLD+((q,-1),),g,old)) == phase(STAGE), 'inherited old-cut bridge')
        shift = preserving_shift(g)
        inv = act(g,shift)
        require(phase(transport(CURRENT,g,shift)) == phase(CURRENT), 'accumulated lift')
        require(phase(transport(CURRENT,g,inv)) == phase(CURRENT), 'inverse accumulated lift')
        matches = sorted(n for n,r in registry.items() if tuple(r['owner_right_matrix_columns']) == g
                         and r['payload_translation_at_identity_owner'] == shift)
        records[port] = dict(q=q,g=g,shift=shift,inverse_shift=inv,old_shift=old,registered_matches=matches)
    return R,U,T,records,{n:digest(v) for n,v in raw.items()}


def program(R,U,T,records):
    word = []
    def emit(op,**kw):
        word.append(dict(op=op,**kw))
    for p in U:
        emit('clear',field=f'Z{p}',frame='Y',port=p)
        emit('add',dst=f'Z{p}',src=f'Y{p}',coefficient='1')
        emit('line',field=f'Z{p}',port=p,sign=1)
        emit('add',dst=f'Z{p}',src=f'X{p}',coefficient='1')
    for p in T:
        emit('stage',field=f'T{p}',sign=1,rank=8)
    for side,ports in (('Z',U),('T',T)):
        for p in ports:
            emit('map',field=f'{side}{p}',port=p,inverse=False,owner_columns=list(records[p]['g']),shift=records[p]['shift'])
    emit('private_begin')
    for k in range(8):
        emit('clear',field='C',frame='current')
        for p in T:
            if R[k][p]:
                emit('add',dst='C',src=f'T{p}',coefficient=str(R[k][p]))
        for p in U:
            if R[k][p]:
                emit('add',dst=f'Z{p}',src='C',coefficient=str(-R[k][p]/4))
    emit('clear',field='C',frame='identity')
    emit('private_end')
    for side,ports in (('T',T),('Z',U)):
        for p in ports:
            emit('map',field=f'{side}{p}',port=p,inverse=True,owner_columns=list(records[p]['g']),shift=records[p]['inverse_shift'])
    for p in T:
        emit('stage',field=f'T{p}',sign=-1,rank=8)
    return word


def add_rows(a,b,c):
    result = dict(a)
    for k,v in b.items():
        result[k] = result.get(k,Q(0)) + c*v
    return {k:v for k,v in result.items() if v}


def replay(word,R,U,T,records,output_frame=CURRENT):
    original = {f'X{p}':CURRENT for p in U}
    original.update({f'Y{p}':CURRENT+((records[p]['q'],-1),) for p in U})
    original.update({f'T{p}':OLD for p in T})
    frames = dict(original)
    frames.update({f'Z{p}':() for p in U})
    frames['C'] = ()
    rows = {f:{(f,AXES):Q(1)} for f in frames}
    private = False
    for i,e in enumerate(word):
        op = e['op']
        if op == 'clear':
            f = e['field']
            require(f == 'C' or f.startswith('Z'), 'only owned fields may clear')
            require(f != 'C' or private, 'private clear outside owner body')
            rows[f] = {(f,AXES):Q(1)} if e.get('keep_dirty') else {}
            frames[f] = CURRENT+((records[e['port']]['q'],-1),) if e['frame'] == 'Y' else CURRENT if e['frame'] == 'current' else ()
        elif op == 'add':
            dst,src = e['dst'],e['src']
            require(dst == 'C' or dst.startswith('Z'), 'borrowed scalar target')
            require(phase(frames[dst]) == phase(frames[src]), 'ADD frame mismatch at '+str(i))
            require('C' not in (dst,src) or private, 'scratch outside owner body')
            rows[dst] = add_rows(rows[dst],rows[src],Q(e['coefficient']))
        elif op == 'line':
            frames[e['field']] += ((records[e['port']]['q'],e['sign']),)
        elif op == 'stage':
            frames[e['field']] += tuple((v,e['sign']) for v,_ in STAGE)
        elif op == 'map':
            f,g = e['field'],tuple(e['owner_columns'])
            frames[f] = transport(frames[f],g,e['shift'])
            rows[f] = {(v,product(g,h)):c for (v,h),c in rows[f].items()}
        elif op == 'private_begin':
            require(not private,'nested private sweep')
            private = True
        else:
            require(op == 'private_end' and private,'private boundary')
            require(not rows['C'] and phase(frames['C']) == phase(()),'unclean private scratch')
            private = False
    require(not private and not rows['C'] and phase(frames['C']) == phase(()),'final scratch cleanup')
    for f,terms in original.items():
        require(rows[f] == {(f,AXES):Q(1)},'source content restoration: '+f)
        require(phase(frames[f]) == phase(terms),'source frame restoration: '+f)
    result = {}
    for p in U:
        expected = {(f'X{p}',AXES):Q(1),(f'Y{p}',AXES):Q(1)}
        for t in T:
            c = -sum(R[k][p]*R[k][t] for k in range(8))/4
            if c:
                expected = add_rows(expected,{(f'T{t}',product(records[p]['g'],records[t]['g'])):c},1)
        require(rows[f'Z{p}'] == expected,'ordered L2 output: '+str(p))
        require(phase(frames[f'Z{p}']) == phase(output_frame),'declared output frame')
        result[f'Z{p}'] = [[v,list(g),str(c)] for (v,g),c in sorted(expected.items())]
    return digest(canonical(result))


def controls(word,R,U,T,records):
    mutations = {}
    for name,predicate,last in (
        ('missing_output_line',lambda e:e['op']=='line',False),
        ('missing_T_raise',lambda e:e['op']=='stage' and e['sign']==1,False),
        ('missing_T_restore',lambda e:e['op']=='stage' and e['sign']==-1,False),
        ('missing_scratch_cleanup',lambda e:e['op']=='clear' and e['field']=='C',True)):
        mutant = deepcopy(word)
        indices = [i for i,e in enumerate(mutant) if predicate(e)]
        del mutant[indices[-1] if last else indices[0]]
        mutations[name] = mutant
    for name in ('dirty_output','old_translation','missing_translation','payload_only','wrong_correction','wrong_line_sign'):
        mutant = deepcopy(word)
        if name == 'dirty_output':
            next(e for e in mutant if e['op']=='clear')['keep_dirty'] = True
        elif name in ('old_translation','missing_translation','payload_only'):
            e = next(e for e in mutant if e['op']=='map' and e['field']==f'Z{U[0]}')
            if name == 'old_translation':
                e['shift'] = records[U[0]]['old_shift']
            elif name == 'missing_translation':
                e['shift'] = 0
            else:
                e['owner_columns'] = list(AXES)
                e['shift'] = 0
        elif name == 'wrong_correction':
            e = next(e for e in mutant if e['op']=='add' and e['src']=='C')
            e['coefficient'] = str(-Q(e['coefficient']))
        else:
            next(e for e in mutant if e['op']=='line')['sign'] = -1
        mutations[name] = mutant
    errors = {}
    for name,mutant in mutations.items():
        try:
            replay(mutant,R,U,T,records)
        except ValueError as error:
            errors[name] = str(error)
        else:
            raise ValueError('ineffective control: '+name)
    return errors


def scalar_invoice(word):
    source = ROOT/'research/joint-query/verify_scalar.py'
    functions = [n for n in ast.parse(source.read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name=='scalar_cost']
    require(len(functions)==1,'source scalar-cost function')
    env = {'F':Q,'need':require}
    exec(compile(ast.Module(body=functions,type_ignores=[]),str(source),'exec'),env)
    cost,coefficients = 0,Counter()
    for e in word:
        if e['op']=='clear':
            cost += env['scalar_cost'](['clear'])
        elif e['op']=='add':
            c = Q(e['coefficient'])
            coefficients[str(abs(c))] += 1
            cost += env['scalar_cost'](['add',None,None,c.numerator,c.denominator])
    require(dict(coefficients)=={'1':224,'1/4':384} and cost==6610,'scalar invoice')
    return cost,dict(coefficients)


def native_kernels(records):
    columns_checked = 0
    for r in records.values():
        q = r['q']
        pivot = (q&-q).bit_length()-1
        columns = (q,)+tuple(1<<i for i in range(9) if i!=pivot)
        images = {act(columns,x):x for x in range(512)}
        require(len(images)==512,'invertible rank-one wrapper')
        for x in range(512):
            middle = images[x]
            require(act(columns,middle)==x and act(columns,middle^1)==x^q,'rank-one kernel support')
            # The positive child coefficients are (1+i)/2, (1-i)/2.
            actual = {act(columns,middle):(1,1),act(columns,middle^1):(1,-1)}
            require(actual=={x:(1,1),x^q:(1,-1)},'rank-one Gaussian coefficients')
            columns_checked += 1
    def mul(a,b):
        return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
    pairs = 0
    for sign in (1,-1):
        for source in range(256):
            for target in range(256):
                difference = source^target
                actual = expected = (1,0)
                for i in range(8):
                    bit = ((difference^(255 if sign==-1 else 0))>>i)&1
                    actual = mul(actual,(1,-1) if bit else (1,1))
                    bit = (difference>>i)&1
                    expected = mul(expected,(1,-sign) if bit else (1,sign))
                require(actual==expected,'signed rank-eight kernel')
                pairs += 1
    wrapper = list(AXES)
    for i in range(8):
        wrapper[i],wrapper[i+9] = wrapper[i+9],wrapper[i]
    require(product(tuple(wrapper),tuple(wrapper))==AXES,'stage wrapper inverse')
    return dict(rank_one_basis_columns=columns_checked,signed_rank_eight_coefficients=pairs,
                stage_inverse_translation=sum(AXES[9:17]),stage_denominator=256)


def calculate():
    R,U,T,records,pins = load_sources()
    word = program(R,U,T,records)
    operator = replay(word,R,U,T,records)
    failures = controls(word,R,U,T,records)
    counts = dict(Counter(e['op'] for e in word))
    require(counts==dict(clear=105,add=608,line=96,stage=16,map=208,private_begin=1,private_end=1),'literal invoice')
    scalar,coefficients = scalar_invoice(word)
    kernels = native_kernels(records)
    maps = {str(p):dict(owner_columns=list(r['g']),translation=r['shift'],inverse_translation=r['inverse_shift'],
                        registered_matches=r['registered_matches']) for p,r in records.items()}
    invoice = dict(rank_one_children=96,rank_eight_children=16,native_rank_mass=224,native_wrappers=224,
                   full_cover_maps=208,scalar_real_primitives=scalar,ADD_coefficients=coefficients,
                   owned_outputs=96,local_owned_scratch=1,restored_sources=200,read_only_XY_sources=192,
                   retained_F0_T_arrays=8,literal_events=len(word))
    tail = [dict(op='stage',field=f'Z{p}',sign=-1,rank=8) for p in U]
    require(replay(word+tail,R,U,T,records,OLD)==operator,'old-frame variant content')
    require(Counter(e['op'] for e in word+tail)==Counter(dict(clear=105,add=608,line=96,stage=112,map=208,private_begin=1,private_end=1)),
            'old-frame literal invoice')
    legacy = dict(rank_one_children=96,rank_eight_children=112,native_rank_mass=992,native_wrappers=416,
                  full_cover_maps=208,scalar_real_primitives=scalar,literal_events=len(word)+len(tail),
                  output_frame='F_L',saved_rank_mass_vs_PR2492=176)
    receipt = dict(status='PASS_QQ16_ACCUMULATED_FRAME_L2',source_sha256=pins,invoice=invoice,trace=counts,
                   operator_sha256=operator,controls=failures,native_kernels=kernels,phase_routes=len(records),
                   registered_route_matches=sum(bool(r['registered_matches']) for r in records.values()),
                   output_frame='F_(L+E1)',old_frame_variant=legacy,
                   scope='local native construction; no full decoder, supplier or kappa')
    return receipt,word,maps,tail


def serialized(name,value):
    # One literal event/route per line keeps generated data reviewable.
    compact = lambda v:json.dumps(v,sort_keys=True,separators=(',',':'))
    if isinstance(value,list):
        return '[\n'+',\n'.join('  '+compact(e) for e in value)+'\n]\n'
    if name=='MAPS.json':
        return '{\n'+',\n'.join('  '+json.dumps(k)+':'+compact(v) for k,v in sorted(value.items()))+'\n}\n'
    return json.dumps(value,sort_keys=True,indent=2)+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='create new receipts, refusing overwrite')
    args = parser.parse_args()
    receipt,word,maps,tail = calculate()
    for name,value in (('RESULT.json',receipt),('WORD.json',word),('MAPS.json',maps),('OLD-FRAME-TAIL.json',tail)):
        path = HERE/name
        if args.write:
            with path.open('x',encoding='utf-8',newline='\n') as stream:
                stream.write(serialized(name,value))
        else:
            require(json.loads(path.read_text(encoding='utf-8'))==value,'committed '+name+' differs')
    print('PASS_QQ16_ACCUMULATED_FRAME_L2 sources=200 outputs=96 rank_mass=224 controls=10 no_new_kappa')


if __name__=='__main__':
    main()
