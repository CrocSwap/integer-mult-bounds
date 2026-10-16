#!/usr/bin/env python3
"""Exact P104 dual with 280 persistent registers and no private allocation.

Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
Read-only; all inherited executable inputs authenticated before import.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
BASE = 'research/p104-native-channel/'
MAIN_INPUTS = {BASE+x for x in ('inputs/LOWRANK-WITNESS.json', 'inputs/P104-FIXTURE.json',
                               'NATIVE-RECIPES.json.gz', 'check_native.py', 'vendor/native_verify.py')}
RETAINED = {'source/pr2479/'+x for x in ('README.md','verify.py','SOURCES.json','WORD.json','RESULT.json')}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def unique(pairs):
    out = {}
    for k,v in pairs:
        need(k not in out, 'duplicate JSON key')
        out[k] = v
    return out


def read(path):
    return json.loads(path.read_text(encoding='utf8'), object_pairs_hook=unique)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'))


def authenticate(records, root, inventory):
    need(len(records)==len(inventory) and {r['path'] for r in records}==inventory,'source inventory')
    for r in records:
        raw=(root/r['path']).read_bytes()
        need(sha256(raw).hexdigest()==r['sha256'],'source SHA256: '+r['path'])
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==r['git_blob'],
             'source Git blob: '+r['path'])


def source_word():
    main=[x for x in read(HERE/'SOURCES.json')['files'] if x['usage']=='input']
    retained=read(HERE/'PREDECESSORS.json')['files']
    authenticate(main,ROOT,MAIN_INPUTS)
    authenticate(retained,HERE,RETAINED)
    spec=importlib.util.spec_from_file_location('retained_private_dual',HERE/'source/pr2479/verify.py')
    p=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(p)
    p.ROOT=ROOT
    receipt,dual=p.compute()
    need(canonical(receipt)==canonical(read(HERE/'source/pr2479/RESULT.json')),'retained receipt drift')
    need(canonical(dual)==canonical(read(HERE/'source/pr2479/WORD.json')),'retained complete word drift')
    checker,original,fixture,cert,_=p.load()
    return p,checker,original,cert,dual


def span(vectors):
    out={0}
    for x in vectors:
        need(type(x) is int and 0<=x<512,'binary generator')
        out|={x^y for y in tuple(out)}
    return frozenset(out)


def build(dual):
    """Only replace the eight authenticated complete accumulator intervals."""
    old=dual['program']
    starts={m['dual_interval'][0]:m for m in dual['private_macros']}
    old_bindings={b['dual_event']:b for b in dual['native_bindings']}
    program,bindings,macros=[],[],[]
    i=0
    while i<len(old):
        if i in starts:
            m=starts[i]
            end=m['dual_interval'][1]
            q,a,b,readers=m['query'],m['cap'],m['line'],m['readers']
            need(old[i:end+1]==[['zero','C',b]]+[['add','C',d,1,b] for d in readers]+
                 [['transport','C',b,a,7],['add',q,'C',-1,a],['erase','C',a]],'exact source macro')
            begin=len(program)
            source=old_bindings[end-2]['original_event']
            program.append(['transport',q,a,b,7])
            bindings.append({'event':begin,'original_event':source,'mode':'conjugate','macro':len(macros)})
            program.extend(['add',q,d,-1,b] for d in readers)
            bindings.append({'event':len(program),'original_event':source,'mode':'transpose','macro':len(macros)})
            program.append(['transport',q,b,a,7])
            macros.append({'source_interval':[i,end],'interval':[begin,len(program)-1],
                           'query':q,'cap':a,'line':b,'readers':readers})
            i=end+1
        else:
            e=deepcopy(old[i])
            need(e[0] in ('add','transport') and 'C' not in e[1:3],'persistent public event')
            if e[0]=='transport':
                binding=old_bindings[i]
                need(binding['mode']=='conjugate','public native mode')
                bindings.append({'event':len(program),'original_event':binding['original_event'],
                                 'mode':'conjugate','macro':None})
            program.append(e)
            i+=1
    need(len(macros)==8,'macro inventory')
    return {'schema_version':1,'initial_frames':dual['initial_frames'],'final_frames':dual['final_frames'],
            'program':program,'native_bindings':bindings,'macros':macros,
            'chart_contract':'Delta_V = Gamma_V^(-T); all 280 registers persistent; no private storage'}


def add(dst,src,a):
    for k,v in src.items():
        z=dst.get(k,F(0))+a*v
        if z: dst[k]=z
        else: dst.pop(k,None)


def replay(program,initial,final,*,starts=None,cuts=(),allow_private=False):
    rows=deepcopy(starts) if starts is not None else {r:{r:F(1)} for r in initial}
    frames={r:span(v) for r,v in initial.items()}
    snapshots={}
    counts,profile=Counter(),Counter()
    for i,e in enumerate(program):
        op=e[0]
        counts[op]+=1
        if op=='add':
            _,dst,src,a,v=e
            need(dst!=src and dst in frames and src in frames and
                 frames[dst]==frames[src]==span(v),'common chart at '+str(i))
            add(rows[dst],rows[src],F(a))
        elif op=='transport':
            _,r,a,b,rank=e
            x,y=span(a),span(b)
            need(r in frames and frames[r]==x and (x<y or y<x),'transport frame at '+str(i))
            need(type(rank) is int and rank==abs(len(x).bit_length()-len(y).bit_length()),'rank')
            frames[r]=y
            profile[rank]+=1
        elif allow_private and op=='zero':
            _,r,v=e
            need(r=='C' and r not in rows,'source owned allocation')
            rows[r],frames[r]={},span(v)
        elif allow_private and op=='erase':
            _,r,v=e
            need(r=='C' and frames[r]==span(v),'source owned discard')
            del rows[r],frames[r]
        else:
            raise ValueError('nonpersistent operation')
        if i+1 in cuts:
            snapshots[i+1]=(deepcopy(rows),deepcopy(frames))
    need(frames=={r:span(v) for r,v in final.items()},'final register/frame boundary')
    return rows,dict(sorted(counts.items())),{str(k):v for k,v in sorted(profile.items())},snapshots


def inverse(program):
    out=[]
    for e in reversed(program):
        if e[0]=='add': out.append(['add',e[1],e[2],str(-F(e[3])),e[4]])
        else:
            need(e[0]=='transport','inverse persistent gate')
            out.append(['transport',e[1],e[3],e[2],e[4]])
    return out


def encoded(rows):
    return {r:{k:str(v) for k,v in sorted(row.items())} for r,row in sorted(rows.items())}


def positive_inverse(actual,native,rank):
    """Move the inverse standard child back to a positive child plus one X."""
    adj=native.adjoint(actual)
    positions=[i for i,g in enumerate(adj) if g[0]=='C']
    need(len(positions)==rank and positions==list(range(positions[0],positions[0]+rank)),
         'contiguous inverse child')
    child=[adj[i] for i in positions]
    need(all(g[2]==-1 for g in child) and {g[1] for g in child}=={1<<j for j in range(rank)},
         'standard inverse child')
    return adj[:positions[0]]+(('X',(1<<rank)-1),)+native.fourier(rank)+adj[positions[-1]+1:]


def native_check(p,checker,original,cert,new):
    n=checker.N
    iso=cert['label_isometry']
    gram=tuple(iso['compressed_dual_gram'])
    orth=iso['orthonormal_basis_compressed']
    def key(raw):
        return span(sum(((x & n.mul(gram,b)).bit_count()%2)<<j for j,b in enumerate(orth)) for x in raw)
    sources={}
    for r in cert['transports']:
        for e in r['events']:
            need(e not in sources,'unique original occurrence')
            sources[e]=r
    bindings={b['event']:b for b in new['native_bindings']}
    need(len(bindings)==len(new['native_bindings']),'unique new occurrence')
    checked,recipes={},[]
    macro_columns=0
    for i,e in enumerate(new['program']):
        if e[0]!='transport':
            need(i not in bindings,'binding on ADD')
            continue
        b=bindings[i]
        r=sources[b['original_event']]
        source=original['program'][b['original_event']]
        mode=b['mode']
        old,end=(r['old'],r['new']) if mode=='conjugate' else (r['new'],r['old'])
        need(key(e[2])==span(old) and key(e[3])==span(end) and e[4]==r['rank']==source[4],
             'literal native source/target/rank binding')
        if b['macro'] is None:
            need(e[1]==source[1] and mode=='conjugate','ordinary register binding')
        else:
            m=new['macros'][b['macro']]
            need(source[1]=='C' and e[1]==m['query'] and i in (m['interval'][0],m['interval'][1]),
                 'excursion register and boundary binding')
        identity=(tuple(r['old']),tuple(r['new']),mode)
        if identity not in checked:
            actual=p.native_dual(r['recipe'],mode,n)
            expected=n.adjoint(p.conjugate(n.frame(tuple(old),9)))+p.conjugate(n.frame(tuple(end),9))
            need(sum(g[0]=='C' for g in actual)==r['rank'] and
                 all(g[2]==1 for g in actual if g[0]=='C'),'positive child normalization')
            n.equal(actual,expected,'persistent forward native phase')
            inverse_actual=positive_inverse(actual,n,r['rank'])
            need(sum(g[0]=='C' for g in inverse_actual)==r['rank'] and
                 all(g[2]==1 for g in inverse_actual if g[0]=='C'),'positive inverse child normalization')
            n.equal(inverse_actual,n.adjoint(expected),'persistent inverse native phase')
            checked[identity]=(actual,expected)
            recipes.append([list(r['old']),list(r['new']),mode,actual,inverse_actual])
        actual,expected=checked[identity]
        if b['macro'] is not None:
            for basis in range(512):
                need(n.state(actual,basis)==n.state(expected,basis),'excursion complete Gaussian column')
                macro_columns+=1
    need(set(bindings)=={i for i,e in enumerate(new['program']) if e[0]=='transport'},'complete native bindings')
    for m in new['macros']:
        first,last=(bindings[i] for i in m['interval'])
        r=sources[first['original_event']]
        need(first['original_event']==last['original_event'],'same source macro')
        down=checked[(tuple(r['old']),tuple(r['new']),'conjugate')][0]
        up=checked[(tuple(r['old']),tuple(r['new']),'transpose')][0]
        n.equal(down+up,(),'native Q round trip is identity')
    return {'occurrences':len(bindings),'distinct_edges':len(checked),'inverse_edges':len(checked),
            'macro_gaussian_columns':macro_columns,'intrinsic_adapters_inherited_checked':208,
            'recipe_sha256':sha256(canonical(recipes).encode()).hexdigest()},checked


def controls(p,checker,original,cert,new,expected,checked):
    passed=[]
    def rejected(program,label):
        try:
            rows,_,_,_=replay(program,new['initial_frames'],new['final_frames'])
            need(rows==expected,'endpoint rows')
        except ValueError:
            passed.append(label)
        else: raise ValueError('accepted fault: '+label)
    m=new['macros'][0]
    for label,value in [('missing reader',0),('wrong subtraction sign',1)]:
        bad=deepcopy(new['program']);bad[m['interval'][0]+1][3]=value
        rejected(bad,label)
    bad=deepcopy(new['program']);bad.pop(m['interval'][1]);rejected(bad,'omitted Q return')
    bad=deepcopy(new['program']);bad[m['interval'][0]],bad[m['interval'][0]+1]=bad[m['interval'][0]+1],bad[m['interval'][0]]
    rejected(bad,'read before common line')
    bad=deepcopy(new['program']);bad.insert(0,['zero','C',[]]);rejected(bad,'private allocation forbidden')
    n=checker.N
    key=next(k for k in checked if k[2]=='transpose')
    actual,expected_native=checked[key]
    phased=actual+(('phase',1),)
    need(n.tableau(phased)==n.tableau(actual) and n.state(phased)!=n.state(expected_native),'phase-only control')
    passed.append('phase-only fault detected')
    r=next(r for r in cert['transports'] if tuple(r['old'])==key[0] and tuple(r['new'])==key[1])
    wrong=n.adjoint(n.recipe(r['recipe']))
    need(n.tableau(wrong)!=n.tableau(expected_native) or n.state(wrong)!=n.state(expected_native),'adjoint/transpose control')
    passed.append('adjoint is not ordinary-transpose return')
    wrong_word=deepcopy(new)
    wrong_word['program'][m['interval'][0]][1]='Q1'
    try: native_check(p,checker,original,cert,wrong_word)
    except ValueError: passed.append('wrong native occurrence register rejected')
    else: raise ValueError('wrong Q source binding accepted')
    permuted=deepcopy(new['program'])
    for e in permuted:
        for position in ((2,3) if e[0]=='transport' else (4,)):
            e[position]=list(reversed(e[position]))
    rows,_,_,_=replay(permuted,new['initial_frames'],new['final_frames'])
    need(rows==expected,'equivalent frame bases')
    passed.append('equivalent frame basis positive control')
    return passed


def compute():
    p,checker,original,cert,dual=source_word()
    new=build(dual)
    old_cuts=[m['source_interval'][1]+1 for m in new['macros']]
    new_cuts=[m['interval'][1]+1 for m in new['macros']]
    expected,old_counts,old_profile,old_snapshots=replay(dual['program'],dual['initial_frames'],dual['final_frames'],
                                                       cuts=old_cuts,allow_private=True)
    rows,counts,profile,new_snapshots=replay(new['program'],new['initial_frames'],new['final_frames'],cuts=new_cuts)
    need(rows==expected,'all 280 endpoint columns')
    for a,b in zip(old_cuts,new_cuts):
        need(old_snapshots[a]==new_snapshots[b],'all public rows/frames at macro boundary')
    identity={r:{r:F(1)} for r in new['initial_frames']}
    reverse=inverse(new['program'])
    restored,rc,rp,_=replay(reverse,new['final_frames'],new['initial_frames'],starts=rows)
    need(restored==identity and rc==counts and rp==profile,'reverse after forward on all columns')
    reverse_rows,_,_,_=replay(reverse,new['final_frames'],new['initial_frames'])
    restored2,_,_,_=replay(new['program'],new['initial_frames'],new['final_frames'],starts=reverse_rows)
    need(restored2==identity,'forward after reverse on independent endpoint columns')
    need(counts=={'add':2624,'transport':1418} and len(new['program'])==4042,'persistent invoice')
    predicted=dict(old_profile);predicted['7']+=8
    need(profile==predicted,'exact extra eight H7')
    native,checked=native_check(p,checker,original,cert,new)
    checks=controls(p,checker,original,cert,new,expected,checked)
    return {'schema_version':1,'claim':'finite P104 inverse-transpose using only persistent registers; no private allocation/discard',
            'inputs':len(rows),'events':len(new['program']),'operations':counts,'rank_profile':profile,
            'rank_mass':sum(int(k)*v for k,v in profile.items()),'extra_H7':8,'extra_rank_mass':56,
            'macro_boundary_coefficient_comparisons':8*280*280,'macro_boundary_frame_comparisons':8*280,
            'forward_endpoint_coefficients':280*280,'inverse_composition_coefficients_each_order':280*280,
            'native':native,'controls':checks,'word_sha256':sha256(canonical(new).encode()).hexdigest(),
            'endpoint_rows':encoded(rows),'reverse_endpoint_rows':encoded(reverse_rows),
            'limits':'no I-G/2 correction, scalar/tape lowering, global owners, complete moment, changed-word precision, all-size or new kappa'},new


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    result,word=compute()
    need(canonical(result)==canonical(read(HERE/'RESULT.json')),'complete receipt mismatch')
    need(canonical(word)==canonical(read(HERE/'WORD.json')),'complete word mismatch')
    if args.out:
        with args.out.open('x',encoding='utf8') as f:
            json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    print('PASS_P104_PERSISTENT_DUAL inputs=280 native=1418 rank_mass=2424 private=0 controls='+str(len(result['controls']))+' no_new_kappa')


if __name__=='__main__':
    main()
