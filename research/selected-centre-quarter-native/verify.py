#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""One native test of PR2199's projected D-only quarter-factor identity.

Aaron Wang / navinor, with help from chatgpt. Native circuit conventions and
source attribution follow Sagar Thakrar's exact Clifford kernel, PR2048's
unpacked statevector method, and the retained bridge/phase convention.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ARCHIVE='research/community-frontier1094-audit/selected-replay.tar.gz'
KERNEL='research/frontier1094-recipes-exact-seed76/clifford.py'
DIM=512
ZERO=((),(),0)
MEMBERS={
 'template':('candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz','2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760'),
 'word':('candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz','16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219'),
 'programs':('candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz','241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a'),
 'recipes':('candidate/strict/global/base/providers/gauge44/CLIFFORD-RECIPES.json','d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731'),
 'residuals':('candidate/strict/global/base/providers/gauge44/RESIDUAL-ADAPTERS.json','383f40aadd00a4ac700dfd0d4c22d6c6c0be9a9863116e4d69c7acd23bafae0c'),
 'phases':('candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json','c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'),
}

def require(ok,why):
    if not ok:
        raise ValueError(why)

def canonical(x):
    return (json.dumps(json.loads(json.dumps(x)),sort_keys=True,indent=2)+'\n').encode()

def sha(b):
    return hashlib.sha256(b).hexdigest()

def reduced(re,im,e):
    bits=0
    for x in re:
        bits|=abs(x)
    for x in im:
        bits|=abs(x)
    if not bits:
        return ZERO
    shift=min(e,(bits & -bits).bit_length()-1)
    return tuple(x>>shift for x in re),tuple(x>>shift for x in im),e-shift

def scale(v,q):
    q=Q(q)
    require(q.denominator & (q.denominator-1)==0,'non-dyadic scalar')
    if not v[0] or not q:
        return ZERO
    return reduced([q.numerator*x for x in v[0]],[q.numerator*x for x in v[1]],
                   v[2]+q.denominator.bit_length()-1)

def add(a,b,q=1):
    b=scale(b,q)
    if not a[0]:
        return b
    if not b[0]:
        return a
    e=max(a[2],b[2])
    return reduced([(x<<(e-a[2]))+(y<<(e-b[2])) for x,y in zip(a[0],b[0])],
                   [(x<<(e-a[2]))+(y<<(e-b[2])) for x,y in zip(a[1],b[1])],e)

def root(v,q,s=1):
    if not v[0]:
        return v
    require(s in (-1,1) and 0<q<DIM,'native root')
    a,b,e=v
    return reduced([a[x]-s*b[x]+a[x^q]+s*b[x^q] for x in range(DIM)],
                   [b[x]+s*a[x]+b[x^q]-s*a[x^q] for x in range(DIM)],e+1)

def apply_columns(columns,x):
    out=0
    for i,c in enumerate(columns):
        if x>>i&1:
            out^=c
    return out

def table_for(m,inverse=False):
    table=[]
    for x in range(DIM):
        y=sum(((r&x).bit_count()%2)<<i for i,r in enumerate(m['matrix_rows'])) ^ m['offset']
        phase=m['phase']+sum(a for i,a in enumerate(m['linear_Z4']) if x>>i&1)
        phase+=2*sum((m['quadratic_rows'][i]>>j)&1 for i in range(9)
                     for j in range(i+1,9) if x>>i&1 and x>>j&1)
        table.append((y,phase%4))
    require(len({y for y,p in table})==DIM,'monomial bijection')
    if not inverse:
        return table
    out=[None]*DIM
    for x,(y,p) in enumerate(table):
        out[y]=(x,-p%4)
    return out

def apply_table(v,table):
    if not v[0]:
        return v
    re,im=[0]*DIM,[0]*DIM
    for x,(y,p) in enumerate(table):
        a,b=v[0][x],v[1][x]
        re[y],im[y]=((a,b),(-b,a),(-a,-b),(b,-a))[p]
    return reduced(re,im,v[2])

def circuit(v,gates):
    for g in gates:
        if g[0]=='C':
            v=root(v,g[1],g[2])
        elif g[0]=='P':
            v=apply_table(v,[(sum(((r&x).bit_count()%2)<<i for i,r in enumerate(g[1])),0) for x in range(DIM)])
        elif g[0]=='D':
            table=[]
            for x in range(DIM):
                p=sum(a for i,a in enumerate(g[2]) if x>>i&1)
                p+=2*sum((g[1][i]>>j)&1 for i in range(9) for j in range(i+1,9) if x>>i&1 and x>>j&1)
                table.append((x,p%4))
            v=apply_table(v,table)
        elif g[0]=='X':
            v=apply_table(v,[(x^g[1],0) for x in range(DIM)])
        elif g[0]=='PH':
            v=apply_table(v,[(x,g[1]) for x in range(DIM)])
        else:
            raise ValueError('unknown native gate')
    return v

def constant(q=1):
    return scale((tuple([1]*DIM),tuple([0]*DIM),0),q)

def controls():
    v=(tuple([1]+[0]*511),tuple([0]*DIM),0)
    want=(tuple([1,1]+[0]*510),tuple([1,-1]+[0]*510),1)
    require(root(v,1)==want,'hand root amplitudes')
    require(root(root(v,1),1,-1)==v,'root inverse')
    require(root(root(v,1),1)==(tuple([0,1]+[0]*510),tuple([0]*DIM),0),'root square translation')
    require(root(constant(),11)==constant(),'constant root')
    require(scale(add(v,v),Q(1,2))==v and add(v,v,-1)==ZERO,'dyadic addition')
    require(canonical({'rank':{8:1}})==canonical({'rank':{'8':1}}),'rank-key roundtrip')
    require(canonical({'n':1})!=canonical({'n':1.0}) and canonical({'n':1})!=canonical({'n':True}),
            'type-strict receipt')
    swap=[2,1]+[1<<i for i in range(2,73)]
    require(apply_columns(swap,1)==2 and apply_columns(swap,apply_columns(swap,1))==1,
            'independent owner involution')
    return ['hand_root','root_inverse','root_square','constant_root','dyadic_addition',
            'rank_key_and_value_types','owner_involution']

def load():
    pins=json.loads((HERE/'SOURCES.json').read_bytes())['files']
    for p in pins:
        if p['usage']=='input':
            require(sha((ROOT/p['path']).read_bytes())==p['sha256'],'source pin mismatch: '+p['path'])
    out={}
    with tarfile.open(ROOT/ARCHIVE,'r:gz') as t:
        for key,(path,digest) in MEMBERS.items():
            entries=[m for m in t.getmembers() if m.name==path]
            require(len(entries)==1 and entries[0].isfile(),'unique member: '+key)
            raw=t.extractfile(entries[0]).read()
            require(sha(raw)==digest,'member pin: '+key)
            out[key]=json.loads(gzip.decompress(raw) if path.endswith('.gz') else raw)
    spec=importlib.util.spec_from_file_location('pinned_quarter_clifford',ROOT/KERNEL)
    C=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(C)
    return out,C

def native(program,data,initial,seconds=300):
    """Literal one-layer execution; capture private values on both sides of transport."""
    started=time.monotonic()
    word=data['word']
    children={(r['old'],r['new']):r for r in data['recipes']['children']}
    adapters={(r['role'],r['port']):r for r in data['recipes']['endpoint_adapters']}
    state={('L',i):initial.get(i,ZERO) for i in range(704)}
    tables={}
    pre,post={},{}
    def mono(v,m,inv=False):
        if not v[0]:
            return v
        key=(json.dumps(m,sort_keys=True),inv)
        if key not in tables:
            tables[key]=table_for(m,inv)
        return apply_table(v,tables[key])
    def child(v,a,b):
        if not v[0]:
            return v
        r=children[a,b]
        v=mono(v,r['right'])
        for j in range(r['rank']):
            v=root(v,1<<j)
        return mono(v,r['left'])
    for e in program:
        require(time.monotonic()-started<=seconds,'native probe deadline exceeded')
        tag=e[0]
        if tag=='phase':
            continue
        if tag=='climb':
            r,a,b=e[2:5]
            state['L',r]=child(state['L',r],a,b)
        elif tag=='center':
            k,a,b=e[1:4]
            pre[k]=state['C',k]
            state['C',k]=child(state['C',k],a,b)
            post[k]=state['C',k]
        elif tag=='adapter':
            direction,r=e[1:3]
            if direction=='old_to_new' and r<112:
                state['L',r]=mono(state['L',r],adapters['source',r]['left'])
            elif direction=='new_to_old' and 112<=r<224:
                state['L',r]=mono(state['L',r],adapters['target',r-112]['left'],True)
        elif tag=='residual_adapter':
            direction,r,a=e[1:4]
            b=e[4] if len(e)==5 else 1
            m=data['residuals']['recipes'][str(a) if b==1 else f'{a}:{b}']
            state['L',r]=mono(state['L',r],m['right' if direction=='pre' else 'left'],True)
        elif tag=='scalar':
            op=e[1]
            kind,dest=op[0],tuple(op[1])
            if kind=='clear':
                require(dest[0]=='C','ordinary clear')
                state[dest]=ZERO
            elif kind=='copy':
                state[dest]=state[tuple(op[2])]
            elif kind=='scale':
                state[dest]=scale(state[dest],Q(op[2],op[3]))
            elif kind=='add':
                state[dest]=add(state[dest],state[tuple(op[2])],Q(op[3],op[4]))
            else:
                raise ValueError('unknown scalar')
        else:
            raise ValueError('unknown emitted event')
    require(set(pre)==set(post)==set(range(8)),'all eight centre cuts')
    require(all(not v[0] for k,v in state.items() if k[0]=='C'),'private exit')
    require(time.monotonic()-started<=seconds,'native probe deadline exceeded')
    return state,pre,post

def scalar(program):
    """Only supplies the proposal/control; native acceptance uses literal recipes."""
    state={('L',i):{i:Q(1)} for i in range(704)}
    rows={}
    def combine(target,source,q):
        for j,v in list(source.items()):
            x=target.get(j,0)+q*v
            if x:
                target[j]=x
            else:
                target.pop(j,None)
    for e in program:
        if e[0]=='center':
            rows[e[1]]=dict(state['C',e[1]])
        elif e[0]=='scalar':
            op=e[1]
            name,d=op[0],tuple(op[1])
            if name=='clear':
                state[d]={}
            elif name=='copy':
                state[d]=dict(state[tuple(op[2])])
            elif name=='scale':
                state[d]={j:Q(op[2],op[3])*v for j,v in state[d].items()}
            elif name=='add':
                combine(state[d],state[tuple(op[2])],Q(op[3],op[4]))
            else:
                raise ValueError('unknown projected scalar')
    require(set(rows)==set(range(8)),'projected cuts')
    return [rows[k] for k in range(8)],state

def rho1(record):
    """Columns of the actual orthogonal involution, no payload permutation."""
    axes=[1<<i for i in range(73)]
    basis=record['idle_children'][0]['orthogonal_axes'][:8]
    require(len(basis)==8 and all(0<x<512 for x in basis),'actual chart basis')
    local=[record['q']]+basis
    require(all((a&b).bit_count()%2==(i==j) for i,a in enumerate(local) for j,b in enumerate(local)),
            'orthonormal actual local chart')
    swaps=[b^(1<<(9+i)) for i,b in enumerate(basis)]
    columns=tuple(x ^ apply_columns(swaps,sum(((x&s).bit_count()%2)<<i for i,s in enumerate(swaps)))
                  for x in axes)
    require(all(apply_columns(columns,apply_columns(columns,x))==x for x in axes),
            'rho involution')
    require(all((a&b).bit_count()%2==(i==j) for i,a in enumerate(columns) for j,b in enumerate(columns)),
            'rho orthogonal')
    require(apply_columns(columns,record['q'])==record['q'],'rho fixes port')
    beta=sum(((b.bit_count()-1)//2%2)<<i for i,b in enumerate(basis))
    b_beta=apply_columns(basis,beta)
    require(record['stage_alignment'][0]==dict(entry_X=0,entry_Y=0,exit_X=0,exit_Y=0),
            'stage0 translations')
    require(record['stage_alignment'][1]==dict(entry_X=record['q']^b_beta,
                entry_Y=record['q']^b_beta,exit_X=b_beta^(beta<<9),exit_Y=b_beta^(beta<<9)),
            'stage1 translations')
    return columns

def component(v,address=0):
    return ['0','0'] if not v[0] else [str(Q(v[0][address],1<<v[2])),str(Q(v[1][address],1<<v[2]))]

def routed_entrance(call,global_values,source_cover,routes):
    """Read actual family/cover pairs; payload translations fix this constant input."""
    answer={}
    for i,(family,route) in enumerate(call['owners']):
        if family not in global_values:
            continue
        require(i<224 and route==[1,1,i%112],'live input must be a stage1 data route')
        if routes[i%112]==source_cover:
            answer[i]=global_values[family]
    return answer

def build():
    checks=controls()
    data,C=load()
    programs=data['programs']
    rows,endpoint=scalar(programs['forward'])
    R=[{p:q for p,q in row.items() if p<112} for row in rows]
    # Discovery used the known PR1918 source minor; replay needs only this
    # four-column exact witness and its independently checked native response.
    weights={0:Q(1),1:Q(-1),6:Q(-1),7:Q(-1)}
    require(all(sum(row.get(p,0)*q for p,q in weights.items())==0 for row in R),'all eight source sums')
    require(all(q.denominator&(q.denominator-1)==0 for q in weights.values()),'dyadic source witness')
    calls=sorted(data['template']['calls'],key=lambda c:c['time'])
    require([(c['time'],c['stage'],c['replica'],c['orientation']) for c in (calls[0],calls[4])]
            ==[(0,0,0,'forward'),(4,1,0,'backward')],'selected calls0/4')
    for c in calls[:5]:
        require(c['local_program_sha256']==sha(json.dumps(programs[c['orientation']],sort_keys=True,separators=(',',':')).encode()),
                'bound program')
        require(len(c['owners'])==len({r[0] for r in c['owners']})==704,'injective owner roles')
    require(calls[0]['owners'][:224]==[[p,[1,0,p%112]] for p in range(224)],'stage0 owner/chart binding')
    require(calls[4]['owners'][:224]==[[p,[1,1,p%112]] for p in range(224)],'stage1 owner/chart binding')
    support=set(weights)|{p+112 for p in weights}
    for c in calls[1:4]:
        require(not support&{r[0] for r in c['owners']},'intervening call touches witness family')
    schedule=data['template']['execution_schedule']
    require([e['kind'] for e in schedule[:5]]==['local_cover_sweep']*5,'uninterrupted initial call sweeps')
    require([(e['time'],e['replica'],e['stage']) for e in schedule[:5]]
            ==[(c['time'],c['replica'],c['stage']) for c in calls[:5]],'schedule binding')
    records=data['phases']['recipes']
    routes={p:rho1(records[p]) for p in weights}
    g=routes[0]
    identity=tuple(1<<i for i in range(73))
    require(g!=identity and all(routes[p]!=g for p in weights if p!=0),'distinct active port owner routes')
    initial={p:constant(q) for p,q in weights.items()}
    result,pre,post=native(programs['forward'],data,initial)
    require(all(not v[0] for v in pre.values()) and all(not v[0] for v in post.values()),
            'native forward transcript did not vanish')
    for i in range(704):
        expected=initial.get(i%112,ZERO) if i<224 else ZERO
        require(result['L',i]==expected,'literal complete first-call endpoint')
    # At common owner I, stage1 reads physical class rho1(p) at port p.
    # Only port0 has its live values at that class. The whole 73-axis
    # payload is constant, so all entry translations and exterior roots fix it.
    global_values={i:result['L',i] for i in support}
    second=routed_entrance(calls[4],global_values,g,routes)
    require(set(second)=={0,112},'actual routed live input roles')
    end,bpre,bpost=native(programs['backward'],data,second)
    require(bpre[0]==constant(Q(1,4)),'literal backward pre-transport query')
    require(all(end['L',i]==(constant() if i==112 else ZERO) for i in range(704)),
            'literal backward completion')
    before=C.canonical_frame(data['word']['frames'][data['word']['center_frames'][0]])
    require(circuit(bpost[0],C.adjoint(before))==bpre[0],
            'inverse-normalized backward transport')
    native_controls=[]
    invariant={p:constant(q) for p,q in weights.items()}
    invariant.update({p+112:constant(q) for p,q in weights.items()})
    _,ipre,ipost=native(programs['backward'],data,invariant)
    require(all(not v[0] for v in ipre.values()) and all(not v[0] for v in ipost.values()),
            'cover-invariant positive control')
    native_controls.append('cover_invariant_kernel_positive')
    wrong=routed_entrance(calls[4],global_values,identity,routes)
    _,wpre,_=native(programs['backward'],data,wrong)
    require(not wrong and wpre[0]==ZERO,'wrong-owner fixture did not remove signal')
    native_controls.append('wrong_owner_location_rejected')
    changed=dict(data)
    changed['recipes']=dict(data['recipes'])
    changed['recipes']['children']=list(data['recipes']['children'])
    key=(0,data['word']['center_frames'][0])
    at=next(i for i,r in enumerate(changed['recipes']['children']) if (r['old'],r['new'])==key)
    r=deepcopy(changed['recipes']['children'][at])
    r['left']['phase']=(r['left']['phase']+1)%4
    changed['recipes']['children'][at]=r
    _,mpre,mpost=native(programs['backward'],changed,second)
    require(mpre[0]==bpre[0] and circuit(mpost[0],C.adjoint(before))!=bpre[0],
            'transport global-phase mutant accepted')
    native_controls.append('backward_transport_phase_rejected')
    mutated=deepcopy(programs['backward'])
    at=next(i for i,e in enumerate(mutated) if e[0]=='scalar' and e[1][0]=='add'
            and e[1][1]==['C',0] and e[1][2]==['L',112])
    mutated[at][1][3]*=2
    _,mpre,_=native(mutated,data,second)
    require(mpre[0]!=bpre[0],'changed gather coefficient accepted')
    native_controls.append('backward_gather_coefficient_rejected')
    # Projection positive control on these same data columns: compose all
    # 704 first-call endpoint columns into the backward centre rows.
    brows,_=scalar(programs['backward'])
    for k in range(8):
        for p in range(112):
            v=sum(brows[k].get(i,0)*endpoint['L',i].get(p,0) for i in range(704))
            require(v==R[k].get(p,0)/4,'PR2199 scalar quarter-factor positive control')
    return dict(status='PASS_SELECTED_CENTRE_QUARTER_NATIVE_COUNTEREXAMPLE',
                base_commit='0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2',
                calls=[0,4],replica=0,channel=0,
                payload='constant1 on every physical tensor/spectator address at one cover owner; zero elsewhere',
                source_weights={str(p):str(q) for p,q in sorted(weights.items())},
                source_columns=[[str(row.get(p,0)) for p in weights] for row in R],
                source_cover_matrix_columns=list(g),
                source_cover_matrix_sha256=sha(canonical(list(g))),
                active_port_route_sha256={str(p):sha(canonical(list(r))) for p,r in routes.items()},
                input_families=sorted(weights),target_families_held_fixed='all112..223; arbitrary same baseline in two executions',
                scalar_positive_control='quarter factor exact on all8x112 D coefficients',
                native_witness=dict(all_forward_centre_inputs_zero=True,all_forward_centre_outputs_zero=True,
                    first_call_complete_endpoint_checked=True,intervening_calls_touch_no_live_witness_family=True,
                    backward_pre_channel0=component(bpre[0]),backward_post_channel0=component(bpost[0]),
                    backward_post_sha256=sha(canonical(bpost[0])),
                    backward_post_inverse_normalized_channel0=component(circuit(bpost[0],C.adjoint(before))),
                    forward_output_owner='every cover owner',backward_observed_owner='identity',
                    physical_output_address=0),
                literal_events={o:len(p) for o,p in programs.items()},
                controls=checks,native_controls=native_controls,
                archive_members={k:dict(path=p,sha256=h) for k,(p,h) in MEMBERS.items()},
                scope='One actual native kernel counterexample, not all addresses, all channels, global rank, '
                      'a tariff, supplier or kappa change. No decoder of the first eight saved centre fields alone '
                      'can recover this later query; additional information/changed schedule remains open.')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--controls',action='store_true')
    p.add_argument('--probe',action='store_true')
    p.add_argument('--write',type=Path)
    p.add_argument('--receipt',type=Path,default=HERE/'RESULT.json')
    args=p.parse_args()
    checks=controls()
    if args.controls:
        print('PASS_QUARTER_NATIVE_CONTROLS count='+str(len(checks)))
        return
    result=build()
    if args.probe:
        print(json.dumps(result,indent=2))
    elif args.write:
        with args.write.open('xb') as f:
            f.write(canonical(result))
    else:
        require(canonical(json.loads(args.receipt.read_bytes()))==canonical(result),'receipt mismatch')
    print(result['status']+' first_transcript=0 later_query=1/4 no_new_kappa')

if __name__=='__main__':
    try:
        main()
    except (ValueError,KeyError,OSError) as e:
        raise SystemExit('FAIL_QUARTER_NATIVE: '+str(e))
