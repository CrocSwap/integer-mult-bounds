#!/usr/bin/env python3
"""Authenticate and replay the unit-column P104 handoff.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Author-side checks retain the pinned constructor and local replay by Ali Romman
and their credited predecessors; independent.py is a separate implementation.
"""
import argparse
import gzip
import hashlib
import json
import sys
import tempfile
import types
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
compiler = types.ModuleType('_unit_column_compiler')
compiler.__file__ = str(HERE/'compiler.py')
exec(compile((HERE/'compiler.py').read_bytes(), compiler.__file__, 'exec'), compiler.__dict__)

BASE = '2485805a6d47f36ea83ddde6327d453ac82d44dc'
V = {592: Q(5, 16), 593: Q(5, 16), 594: Q(5, 8), 596: Q(3, 8)}
U = {592: Q(-1), 593: Q(1), 594: Q(1), 596: Q(1)}
B = {188: Q(-1), **U}
PAID = {1: 2211, 2: 459, 3: 494, 4: 94, 5: 164, 6: 18, 7: 14}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def digest(x):
    return hashlib.sha256(x).hexdigest()


def blob(x):
    return hashlib.sha1(b'blob ' + str(len(x)).encode() + b'\0' + x).hexdigest()


def source_checks():
    sources = json.loads((HERE/'SOURCES.json').read_bytes())
    need(sources['base_commit'] == BASE, 'Source base')
    result = {}
    for row in sources['files']:
        if row['usage'] != 'input':
            continue
        data = (ROOT/row['path']).read_bytes()
        need(digest(data) == row['sha256'] and blob(data) == row['git_blob'], 'Source bytes: '+row['path'])
        result[row['path']] = digest(data)
    predecessor = json.loads((HERE/'PREDECESSOR.json').read_bytes())
    for row in predecessor['files']:
        data = (HERE/row['path']).read_bytes()
        need(row['head'] == '2fbb316a7bd34fabebed8e47ed40017c150d71b8', 'Pending source head')
        need(digest(data) == row['sha256'] and blob(data) == row['git_blob'], 'Predecessor bytes: '+row['path'])
    return result


def load(path, name):
    # Compile authenticated bytes directly: no preexisting bytecode is imported.
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def dense(events, keys):
    index = {k: i for i, k in enumerate(keys)}
    mat = [[Q(i == j) for j in keys] for i in keys]
    for event in events:
        r = index[event[1]]; q = Q(event[-2])
        if event[0] == 'ADD':
            s = index[event[2]]
            need(r != s, 'Distinct dense operands')
            mat[r] = [x + q*y for x, y in zip(mat[r], mat[s])]
        else:
            need(event[0] == 'SCALE' and compiler.unit(q), 'Dense unit scale')
            mat[r] = [q*x for x in mat[r]]
    return mat


def boundary_check(a, b, pivot, events):
    keys = sorted(a.keys() | b.keys() | {pivot})
    mat = dense(events, keys); p = keys.index(pivot)
    need([sum(a.get(k, 0)*mat[i][j] for i, k in enumerate(keys)) for j in range(len(keys))]
         == [Q(j == p) for j in range(len(keys))], 'Row boundary')
    need([mat[i][p] for i in range(len(keys))] == [b.get(k, Q(0)) for k in keys], 'Column boundary')
    need(dense(events+compiler.inverse(events), keys)
         == [[Q(i == j) for j in keys] for i in keys], 'Exact dirty-input inverse')
    return mat


def rejection(fn):
    try:
        fn()
    except (ValueError, KeyError):
        return 1
    raise ValueError('Defect was not rejected')


def finite_checks():
    cases = preconditioned = 0
    for dimension in range(1, 9):
        for power in range(-2, 3):
            for sign in (-1, 1):
                for phase in (0, 1):
                    pivot = dimension-1
                    u = Q(sign) * (Q(2)**power)
                    a = {i: Q((-1)**(i+phase)*(i+1), 2**((i+phase)%3)) for i in range(pivot)}
                    b = {i: Q((-1)**(i+1+phase)*(i+2), 2**((i+1)%2)) for i in range(pivot)}
                    b[pivot] = u
                    a[pivot] = (1 - sum(a[i]*b[i] for i in range(pivot))) / u
                    boundary_check(a, b, pivot, compiler.compile_basis(a, b, pivot, 0))
                    cases += 1
                    if dimension >= 3:
                        boundary_check(a,b,pivot,compiler.compile_preconditioned(a,b,pivot,0,0,1))
                        preconditioned += 1
    controls = 0
    for a, b, p, f in [
        ({0:Q(1)}, {0:Q(2)}, 0, 0),
        ({0:Q(1,3)}, {0:Q(3)}, 0, 0),
        ({0:Q(1),1:Q(1)}, {0:Q(3),1:Q(-2)}, 0, 0),
        ({0:Q(1)}, {0:Q(1)}, -1, 0),
        ({0:Q(1)}, {0:Q(1)}, True, 0),
        ({0:Q(1)}, {0:Q(1)}, 0, -1),
        ({0:Q(1)}, {0:Q(1)}, 1, 0),
        ({0:Q(1),1:Q(2**16)}, {0:Q(1)}, 0, 0),
        ({0:Q(2**20)}, {0:Q(1,2**20)}, 0, 0),
    ]:
        controls += rejection(lambda a=a,b=b,p=p,f=f: compiler.compile_basis(a,b,p,f))
    for a, b in [(V, U), (V, B)]:
        events = compiler.compile_basis(a, b, 596, 0)
        controls += rejection(lambda a=a,b=b,events=events: boundary_check(a,b,596,list(reversed(events))))
        controls += rejection(lambda a=a,b=b,events=events: boundary_check(a,b,596,events[:-1]))
    controls += rejection(lambda:compiler.compile_preconditioned(V,U,596,0,596,592))
    controls += rejection(lambda:compiler.compile_preconditioned(V,U,596,0,592,592))
    controls += rejection(lambda:compiler.compile_preconditioned(V,U,596,0,591,592))
    return cases, preconditioned, controls


def support_count_checks():
    """Finite corroboration of the universal support-activation proof."""
    import itertools
    count = 0
    statuses = set()
    for ai,aj,bi,bj,c in itertools.product(range(-2,3),range(-2,3),range(-2,3),range(-2,3),(-2,-1,1,2)):
        before = [(bool(ai),bool(bi)),(bool(aj),bool(bj))]
        after = [(bool(ai),bool(bi+c*bj)),(bool(aj-c*ai),bool(bj))]
        activated = sum(old==(False,False) and new!=(False,False) for old,new in zip(before,after))
        doubled = sum(old!=(True,True) and new==(True,True) for old,new in zip(before,after))
        need(activated<=1 and (activated==0 or doubled==0), 'Activation/double-creation separation')
        statuses.add(tuple(before));count+=1
    need(len(statuses)==16 and count==2500,'Complete binary support types')
    records=[]
    for a,b in [(V,B),(V,U)]:
        keys=sorted(a.keys()|b.keys());p=596
        aa={k:Q(k==p) for k in keys};bb=aa.copy();seen={p}
        activation=double_events=0;second=set()
        for event in compiler.compile_preconditioned(a,b,p,0,592,593):
            before={k:(bool(aa[k]),bool(bb[k])) for k in keys}
            if event[0]=='ADD':
                _,r,j,c,f=event;c=Q(c)
                aa[j]-=c*aa[r];bb[r]+=c*bb[j]
            else:
                _,r,c,f=event;c=Q(c);aa[r]/=c;bb[r]*=c
            appearing={k for k in keys if (aa[k] or bb[k]) and k not in seen}
            gained={k for k in keys if k!=p and before[k]!=(True,True) and aa[k] and bb[k]}
            need(len(appearing)<=1 and not (appearing and gained),'Attainer event separation')
            activation+=bool(appearing);double_events+=bool(gained)
            seen.update(appearing);second.update(gained)
        need(all(aa[k]==a.get(k,0) and bb[k]==b.get(k,0) for k in keys),'Dual-pair orbit endpoint')
        n=len(set(a)|set(b));m=len(set(a)&set(b))
        lower=n-1+(m-1+1)//2
        actual=len(compiler.compile_preconditioned(a,b,p,0,592,593))
        need(actual==lower and activation==n-1 and double_events==(m//2),'Sharp support count')
        records.append({'union':n,'double_support':m,'lower_bound':lower,'attaining_adds':actual,'activations':activation,'double_creation_gates':double_events})
    return {'transition_cases':count,'support_types':len(statuses),'attainers':records,'four_boundary_minimum_adds':22}


def pairs(values):
    return [[k, str(q)] for k, q in sorted(values.items())]


def build_words():
    where = ROOT/'research/p104-coupled-helper-bases'
    local = load(where/'local.py', '_unit_column_local')
    # The retained constructor imports the original module name.
    sys.modules['local'] = local
    construct = load(where/'construct.py', '_unit_column_construct')
    old = load(ROOT/'research/dyadic-helper-basis-completion/basis.py', '_unit_column_euclidean')
    word = json.loads(gzip.decompress((where/'inputs/pr5580-WORD.json.gz').read_bytes()))
    original_hash = digest(canonical(word))
    step = {'kind':'coupled_handoff','cut':13762,'frame':1053,'group':[3,127],
            'pivot':596,'v':pairs(V),'u':pairs(U),
            'source_functional':pairs(V),'output_direction':pairs(B)}
    need((len(word['program']), word['public']) == (25140,735), 'Source dimensions')
    row, frame = construct.prefix(word,13762)
    cols = construct.suffix_columns(word,13762)
    a,b = {},{}
    for k,q in V.items(): local.add(a,row[k],q)
    for k,q in U.items(): local.add(b,cols[k],q)
    need(a==V and b==B, 'Source-bound exact dual pair')
    need(all(frame[k]==1053 for k in V.keys()|U.keys()), 'Cut frame availability')
    need(not any(compiler.unit(q) for q in V.values()), 'No unit row coordinate')
    need(B[596]==U[596]==1, 'Unit column pivot')
    rejection(lambda:construct.basis(V,U,596,1053))

    def euclidean(a,b,p,f):
        keys = sorted(a.keys()|b.keys()|{p})
        ops = old.compile_basis([a.get(k,Q(0)) for k in keys],[b.get(k,Q(0)) for k in keys],keys.index(p))
        return [['ADD',keys[r],keys[s],str(q),f] if op=='ADD' else ['SCALE',keys[r],str(q),f]
                for op,r,s,q in ops]

    source_old, cut_old = euclidean(V,B,596,3), euclidean(V,U,596,1053)
    source_new = compiler.compile_preconditioned(V,B,596,3,592,593)
    cut_new = compiler.compile_preconditioned(V,U,596,1053,592,593)
    for a,b,ops in [(V,B,source_old),(V,U,cut_old),(V,B,source_new),(V,U,cut_new)]:
        boundary_check(a,b,596,ops)
    need((len(source_old),len(cut_old)) == (36,34), 'Predecessor gate counts')
    need((len(source_new),len(cut_new)) == (6,5), 'Candidate gate counts')
    construct.basis = euclidean
    old_word = construct.handoff(word,step)
    construct.basis = lambda a,b,p,f: compiler.compile_preconditioned(a,b,p,f,592,593)
    new_word = construct.handoff(word,step)
    before, old_result, new_result = map(local.replay,[word,old_word,new_word])
    need(digest(canonical(word))==original_hash,'Original input unchanged')
    need([len(w['program']) for w in [word,old_word,new_word]] == [25140,25280,25162], 'Complete event counts')
    need([r['real_scalar_allowance'] for r in [before,old_result,new_result]] == [217428,218564,217708], 'Complete scalar allowances')
    need(all(r['paid']==PAID for r in [before,old_result,new_result]), 'Identical complete paid profiles')
    need(before['helpers']=={9:424,4:83,5:5,8:15}, 'Original helper profile')
    need(old_result['helpers']==new_result['helpers']=={9:423,4:84,5:6,8:15}, 'Identical productive split')
    need((new_result['public_inputs'],new_result['owned_lifetimes'],new_result['peak_owned_fields'])==(736,8,1), 'Complete lifetime counts')
    need(2*(compiler.allowance(source_old)+compiler.allowance(cut_old))==1136,'Predecessor inserted tariff')
    need(2*(compiler.allowance(source_new)+compiler.allowance(cut_new))==280,'Candidate inserted tariff')
    need(compiler.allowance(source_new)==74 and compiler.allowance(cut_new)==66,'Boundary tariffs')
    # Exactly the original MOVE/COPY/INIT/CLEAR stream remains, modulo the
    # mandated helper split and insertion of a fresh arbitrary public input.
    non_scalar=lambda w:[e for e in w['program'] if e[0] not in ('ADD','SCALE')]
    need(non_scalar(old_word)==non_scalar(new_word),'Identical paid and ownership event stream')

    source_n, cut_n, cut = len(source_new),len(cut_new),13762
    start_cut = source_n+cut+1
    indices = list(range(source_n)) + list(range(start_cut,start_cut+2*cut_n)) + list(range(len(new_word['program'])-source_n,len(new_word['program'])))
    need(len(indices)==22,'Inserted event index coverage')
    failures=0
    for i in indices:
        mutant=deepcopy(new_word);del mutant['program'][i]
        failures+=rejection(lambda mutant=mutant:local.replay(mutant))
    need(failures==22,'All inserted-event omissions reject')
    wrong_frame=deepcopy(new_word);wrong_frame['program'][0][-1]=1053
    failures+=rejection(lambda:local.replay(wrong_frame))
    bad_growth=deepcopy(new_word);bad_growth['program'][0][-2]=str(2**16)
    failures+=rejection(lambda:local.replay(bad_growth))
    return word,old_word,new_word,{'before':before,'predecessor':old_result,'candidate':new_result,
          'complete_events':[25140,25280,25162],'source_events':source_new,'cut_events':cut_new,
          'inserted_allowance':[1136,280],'saved_allowance':856,'full_word_rejections':failures,
          'original_word_sha256':original_hash,'predecessor_word_sha256':digest(canonical(old_word)),
          'candidate_word_sha256':digest(canonical(new_word))}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true')
    parser.add_argument('--emit-word',type=Path)
    args=parser.parse_args()
    sources=source_checks()
    cases,preconditioned,controls=finite_checks()
    original,previous,candidate,result=build_words()
    result['generic_unit_column_cases']=cases
    result['generic_preconditioner_cases']=preconditioned
    result['compiler_rejections']=controls
    result['support_lower_bound']=support_count_checks()
    result['input_sha256']=sources
    independent=load(HERE/'independent.py','_unit_column_independent')
    result['independent']=independent.audit(original,candidate)
    result['independent_rejections']=independent.negative_controls(original,candidate)
    result['package_sha256']={name:digest((HERE/name).read_bytes()) for name in [
        'compiler.py','verify.py','independent.py','PROOF.md','INDEPENDENT-REVIEW.md',
        'README.md','PREDECESSOR.json','SOURCES.json','TASK.json','VERIFY.json']}
    if args.emit_word:
        need(not args.emit_word.resolve().is_relative_to(ROOT),'Emitted word must be outside checkout')
        args.emit_word.write_bytes(canonical(candidate)+b'\n')
    if args.write:
        (HERE/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:
        need(json.loads((HERE/'RESULT.json').read_bytes())==json.loads(canonical(result)),'Exact expected receipt')
    print('PASS_P104_UNIT_COLUMN_HANDOFF cases=%d compiler_controls=%d word_controls=%d saved_allowance=856' % (cases,controls,result['full_word_rejections']))


if __name__=='__main__':
    main()
