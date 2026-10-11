"""Portable pure functions extracted from the reviewed complex checks; no historical receipt readers."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
Q=Fraction
from hashlib import sha256
from pathlib import Path
from math import prod
import gzip,json,sys

V,R,H,N,W=1320,9036,22,11676,14316
PHASES=["old_response","ad0","A","centers","B","final","adF","cleanup","done"]
def need(x,s):
    if not x:raise ValueError(s)

def blobhash(p):return sha256(p.read_bytes()).hexdigest()

def digest(x):return sha256(json.dumps(x,separators=(',',':'),sort_keys=True).encode()).hexdigest()

def role(r):return 'X' if r<V else 'Y' if r<2*V else 'S'

def add(t,s,q):return ('add',t,s,q.numerator,q.denominator)

def L(r):return ('L',r)

def T(r):return ('T',r-2*V)

def C(k):return ('C',k)

def clear(t):return ('clear',t)

def copy(t,s):return ('copy',t,s)

def flat(gs):
    for g in gs:
        for r,a,b in g[3]:
            t,s=(r,g[2]) if g[0]=='out' else (g[2],r)
            need(t!=s and role(s)!='Y' and (role(s),role(t))!=('S','X'),'scalar projection shape')
            yield t,s,Q(a,b)

def scal(phase,e,frame):return ('scalar',phase,e,frame)

def lower_scalar(e):
    # The coefficient work stream is disjoint from every live and center role.
    if e[0] in ['copy','clear']:return [e]
    _,t,s,a,b=e;work=('W',0)
    out=[copy(work,s)]
    if abs(a)==2:out.append(('double',work))
    if b%2==0:out.append(('halve',work))
    if b%3==0:out.append(('divide3',work))
    return out+[('accumulate',t,work,1 if a>0 else -1),clear(work)]

def emit(c,ori):
    """Construct the complete local parametric invocation, before cover routing.
    One role stream is its full complete address rectangle. Frame labels denote
    exact canonical representatives, never just rank or binary matrices.
    """
    A=list(flat(c['A']));B=list(flat(c['B']));cur=c['start'].copy()
    K=[]
    for part in (A,None,B):
        if part is None:
            for t,p in enumerate(c['ports']):
                for k,r,f in c['ret']:
                    K.append(add(L(V+t),T(r),Q(*(c['scat']['inside'] if p>>k&1 else c['scat']['outside']))))
        else:
            for t,s,q in part:
                if role(s)=='X':continue
                K.append(add(T(t) if role(t)=='S' else L(t),T(s),q))
    yield ('phase','old_response')
    if ori=='forward':
        for q in range(R):yield scal('old_response',copy(('T',q),L(2*V+q)),'old0')
        for _,t,s,a,b in K:yield scal('old_response',add(t,s,Q(-a if t[0]=='L' else a,b)),'old0')
    else:
        for q in range(R):yield scal('old_response',clear(('T',q)),'old0')
        for _,t,s,a,b in reversed(K):yield scal('old_response',add(s,t,Q(a,b)),'old0')
        for q in range(R):yield scal('old_response',add(L(2*V+q),('T',q),Q(1)),'old0')
    for q in range(R):yield scal('old_response',clear(('T',q)),'old0')
    yield ('phase','ad0')
    for r,f in enumerate(c['start']):yield ('adapter','old_to_new',r,f)
    for part in ['A','centers','B','final']:
        yield ('phase',part)
        if part in ['A','B']:
            for g in c[part]:
                regs=[g[2]]+[x[0] for x in g[3]]+(g[4] if g[0]=='out' else [])
                for r in regs:
                    if cur[r]!=g[1]:
                        old=cur[r];cur[r]=g[1]
                        yield ('climb',part,r,old,g[1],len(c['frames'][g[1]])-len(c['frames'][old]))
                for t,s,q in flat([g]):
                    e=add(L(t),L(s),q) if ori=='forward' else add(L(s),L(t),-q)
                    yield scal('main',e,g[1])
        elif part=='centers':
            for k,r,f in c['ret']:
                yield scal('main',clear(C(k)),f if ori=='forward' else 0)
                if ori=='forward':yield scal('main',add(C(k),L(r),Q(1)),f)
                else:
                    for t,p in enumerate(c['ports']):
                        yield scal('main',add(C(k),L(V+t),Q(*(c['scat']['inside'] if p>>k&1 else c['scat']['outside']))),0)
                yield ('center',k,f if ori=='forward' else 0,0 if ori=='forward' else f,20)
                if ori=='forward':
                    for t,p in enumerate(c['ports']):
                        yield scal('main',add(L(V+t),C(k),Q(*(c['scat']['inside'] if p>>k&1 else c['scat']['outside']))),0)
                else:yield scal('main',add(L(r),C(k),Q(-1)),f)
                yield scal('main',clear(C(k)),0 if ori=='forward' else f)
        else:
            for r,f in enumerate(c['final']):
                if cur[r]!=f:
                    old=cur[r];cur[r]=f
                    yield ('climb','final',r,old,f,len(c['frames'][f])-len(c['frames'][old]))
    yield ('phase','adF')
    for r,f in enumerate(c['final']):yield ('adapter','new_to_old',r,f)
    yield ('phase','cleanup')
    for t,s,q in reversed(A+B):
        if role(t)=='Y':continue
        e=add(L(t),L(s),-q) if ori=='forward' else add(L(s),L(t),q)
        yield scal('cleanup',e,'old1')
    yield ('phase','done')

def contains(U,V):
    for u in U:
        for v in V:
            if u>>(v.bit_length()-1)&1:u^=v
        if u:return False
    return True

def validate(events,c,ori,manifest,bill):
    phase=None;seen=[];cur=c['start'].copy();cent={};dirty=set();initialized=set()
    climbed=Counter();hist=Counter();projection=sha256();whole=sha256();counts=Counter();ad0=[];adF=[]
    pairs=set();states={};all_frame_incidence=0;primitive=sha256();primitive_count=0
    for ev in events:
        whole.update((json.dumps(ev,separators=(',',':'))+'\n').encode())
        tag=ev[0];counts[tag]+=1
        if tag=='phase':
            if phase=='A':states['after_A']=digest(cur)
            if phase=='B':states['after_B']=digest(cur)
            if phase=='final':states['final']=digest(cur)
            phase=ev[1];seen.append(phase)
            need(seen==PHASES[:len(seen)],'strict old/A/copy/B/final/adapter/cleanup chronology')
            if phase=='ad0':need(not dirty,'old-response tableau survived before label recursion')
            if phase=='A':need(ad0==list(enumerate(c['start'])),'missing or reordered exact entry adapter')
            if phase=='adF':need(cur==c['final'],'final climbs omitted before cleanup')
            if phase=='cleanup':need(adF==list(enumerate(c['final'])),'missing or reordered exact final adapter')
            continue
        if tag=='adapter':
            _,which,r,f=ev
            if which=='old_to_new':need(phase=='ad0','entry adapter position');ad0.append((r,f))
            else:need(which=='new_to_old' and phase=='adF','final adapter position');adF.append((r,f))
        elif tag=='climb':
            _,p,r,old,new,d=ev
            need(phase==p and p in ['A','B','final'],'live child outside source label walk')
            need(not dirty and not cent,'new work stock or center active during live child')
            need(cur[r]==old and d==len(c['frames'][new])-len(c['frames'][old]) and d>0,'wrong exact child endpoints/rank')
            pair=(old,new)
            if pair not in pairs:need(contains(c['frames'][old],c['frames'][new]),'nonnested child');pairs.add(pair)
            cur[r]=new;climbed[p]+=1;hist[d]+=1
        elif tag=='center':
            _,k,old,new,d=ev
            need(phase=='centers' and not dirty and set(cent)=={k},'center child ownership')
            need(cent[k]==old and (k,c['ret'][k][1],c['ret'][k][2])==tuple(c['ret'][k]),'center input frame')
            f=c['ret'][k][2]
            need((old,new,d)==((f,0,20) if ori=='forward' else (0,f,20)),'center child direction/rank')
            cent[k]=new;hist[d]+=1
            projection.update((json.dumps(('main',('recursive_center',k,d)),separators=(',',':'))+'\n').encode())
        elif tag=='scalar':
            _,p,e,f=ev
            need(p==('main' if phase in ['A','centers','B'] else phase),'scalar phase binding')
            need(e[0] in ['add','copy','clear'],'unpaid scalar operation')
            target=e[1];source=e[2] if e[0] in ['add','copy'] else None
            for x in [target]+([source] if source else []):
                bank,r=x
                if bank=='T':need(phase=='old_response' and 0<=r<R,'tableau outside old response')
                elif bank=='C':need(phase=='centers' and 0<=r<H,'center outside copied block')
                elif bank=='L':
                    need(0<=r<N,'live register range')
                    if phase=='old_response':need(role(r) in ['S','Y'] and f=='old0','old response not at common old0')
                    elif phase=='cleanup':need(role(r) in ['X','S'] and f=='old1' and cur[r]==1,'cleanup not at common old1')
                    else:need(cur[r]==f,'scalar incidence uses wrong exact label');all_frame_incidence+=1
                else:raise ValueError('unknown stream namespace')
            if source and source[0]=='T':need(source[1] in initialized,'read before tableau initialization')
            if source and source[0]=='C':need(cent.get(source[1])==f,'center source frame')
            if target[0]=='T':
                if e[0]=='add':need(target[1] in initialized,'tableau accumulation before initialization')
                initialized.add(target[1])
                if e[0]=='clear':dirty.discard(target[1])
                else:dirty.add(target[1])
            if target[0]=='C':
                if e[0]=='clear':
                    if target[1] in cent:del cent[target[1]]
                else:
                    need(not cent or set(cent)=={target[1]},'overlapping center lifetimes')
                    need(cent.get(target[1],f)==f,'center target frame');cent[target[1]]=f
            if e[0]=='add':need(e[4] in [1,2,3,6] and abs(e[3]) in [1,2],'unrecorded coefficient')
            projection.update((json.dumps((p,e),separators=(',',':'))+'\n').encode())
            lowered=lower_scalar(e)
            if e[0]=='add':need(lowered[-1]==('clear',('W',0)),'coefficient work survives scalar macro')
            for op in lowered:
                primitive.update((json.dumps((p,op),separators=(',',':'))+'\n').encode())
                primitive_count+=1
        else:raise ValueError('unknown physical event')
    need(seen==PHASES and not dirty and not cent,'incomplete invocation or dirty temporary')
    need(dict(climbed)=={'A':18012,'B':41182,'final':9036},'live transition count/partition')
    need(counts['center']==22 and counts['climb']==68230,'paid children omitted or doubled')
    need({str(k):v for k,v in sorted(hist.items())}==manifest['checks']['invocation_histogram'],'paid source histogram changed')
    need(states=={k:v for k,v in manifest['checks']['phase_state_sha256'].items() if k!='start'},'exact label states differ')
    need(projection.hexdigest()==bill[ori]['schedule_sha256'],'complete scalar program differs from checked bill')
    need(2*primitive_count==bill[ori]['totals']['real_component_primitive_steps'],'independent primitive expansion bill')
    return dict(events=sum(counts.values()),event_counts=dict(counts),program_sha256=whole.hexdigest(),
        scalar_projection_sha256=projection.hexdigest(),live_transition_partition=dict(climbed),
        paid_children=counts['climb']+counts['center'],final_climbs_before_cleanup=True,
        exact_common_label_live_incidences=all_frame_incidence,distinct_nested_pairs=len(pairs),
        exact_label_state_sha256=states,old_response_erased_before_all_children=True,
        entry_and_exit_old_new_adapters=2*N,Gaussian_primitives=primitive_count,
        real_component_primitives=2*primitive_count,scalar_primitive_sha256=primitive.hexdigest())

def global_contract(manifest):
    return dict(family='baseline5stageComplex',m=110,live=14316,physical=23375,
        stage_recipe=[dict(stage=j,window=f'G{j}',orientation=o,active_pair=p,
            bank_owner='d' if j==0 else f'r{j}(t)^(-1)(d)',helper_owner='d' if j==0 else f's{j}(d)',
            exterior_subset='empty' if j==0 else f'qS bs{j} l',
            native_frame=f'(G{j} d).X.Phi(frames[f])',old_frame=f'(G{j} d).Xm.Phi(P)')
            for j,(o,p) in enumerate([('forward',1),('backward',1),('forward',1),('backward',2),('forward',2)])],
        chronology=manifest['chronology'],exact_frame_bindings=manifest['source_frame_equalities'],
        scratch_namespace=dict(centers=[14316,14338],tableau=[14338,23374],coefficient=[23374,23375]),
        recursive_volume_denominator=14316,primitive_policy='charged_fixed_tape_complete_streams',
        label_policy='identical_exact_representative_and_paid_rank_zero_reconciliation',
        helper_policy='arbitrary_input; inherited_dirty_lift; Z5=kernel',
        odd_grid='2^(-P)3^(-G(D+1)); no return rounding',local_bound_exponent=48,
        global_bound_exponent=6050,maintained_guard_changed=False,
        primitive_recipe=dict(scalar='copy source to W; optional double/halve/divide3; signed accumulate; clear W',
            live_child='exact target representative times inverse current representative; two rank-zero factors around one C tensor child',
            center_forward='copy at retained frame; exact residual to frame zero; scatter; erase',
            center_backward='zero at frame zero; accumulate transpose scatter; exact residual to retained frame; subtract into original; erase',
            entry_exit='WinB.old_to_new and WinB.new_to_old, lowered as paid exact rank-zero Clifford operators',
            rank_zero='binary Gaussian elimination; affine bit flips; Z4 linear phases and even cross terms; exact scalar fourth root',
            cross_phase='i^(2xy) = i^x i^y i^(-(x xor y)); at most three parity-phase scans',
            selected_bit='compact-control-movement proposition, complete restored borrowed fields, paid repair, no RAM lookup',
            phase_scan='evaluate fixed Z4 quadratic descriptors per record, multiply by fourth root, record suffix pays descriptor arithmetic',
            role_route='permutation on all complete live/work roles, at most W_physical^2 complete-stream exchanges on fixed tapes',
            row_stock='split only live complete rows; scalar-only work creates no row coordinate or recursive branch'))

def validate_global(g,m):
    need(g==global_contract(m),'five-window exact source/tape/namespace contract changed')
    # Injective embedding of each invocation and its disjoint temporary stock.
    for s in g['stage_recipe']:
        p=s['active_pair'];offset=2*V*(p-1)
        live=[offset+r for r in range(2*V)]+[4*V+q for q in range(R)]
        work=list(range(14316,23375))
        need(len(set(live+work))==len(live+work),'global workstream aliases a live role')
        need(all(0<=r<W for r in live),'global live embedding')
    return True

def controls(events,c,ori,m,b):
    def rejected(name,fn):
        x=list(events);fn(x)
        try:validate(x,c,ori,m,b)
        except ValueError as e:return dict(name=name,rejected=True,reason=str(e))
        raise ValueError('mutation accepted: '+name)
    out=[]
    out.append(rejected('drop_final_climb',lambda x:x.pop(next(i for i,e in enumerate(x) if e[:2]==('climb','final')))))
    def move_cleanup(x):
        a=next(i for i,e in enumerate(x) if e==('phase','final'))
        b=next(i for i,e in enumerate(x) if e==('phase','cleanup'))
        x[a:b]=x[b:-1]+x[a:b];x[b:]=[('phase','done')]
    out.append(rejected('cleanup_before_final_climbs',move_cleanup))
    out.append(rejected('drop_final_frame_adapter',lambda x:x.pop(next(i for i,e in enumerate(x) if e[:2]==('adapter','new_to_old')))))
    def wrong_frame(x):
        i=next(i for i,e in enumerate(x) if e[0]=='scalar' and e[1]=='main' and isinstance(e[3],int))
        e=x[i];x[i]=e[:3]+(-1,)
    out.append(rejected('wrong_common_exact_gate_label',wrong_frame))
    out.append(rejected('drop_center_child',lambda x:x.pop(next(i for i,e in enumerate(x) if e[0]=='center'))))
    out.append(rejected('tableau_not_erased_before_child',lambda x:x.pop(max(i for i,e in enumerate(x) if e[0]=='scalar' and e[1]=='old_response' and e[2]==('clear',('T',0))))))
    def wrong_sign(x):
        i=next(i for i,e in enumerate(x) if e[0]=='scalar' and e[1]=='cleanup')
        z=x[i];e=z[2];x[i]=z[:2]+(e[:3]+(-e[3],e[4]),z[3])
    out.append(rejected('wrong_cleanup_sign',wrong_sign))
    for entry in out:entry['orientation']=ori
    return out
