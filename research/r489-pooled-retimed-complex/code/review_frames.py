"""Independent finite common-frame retiming review (no supplier imports).

Checks actual GF(2) subspaces, fixed scalar payloads/boundaries, raw-to-canonical
transport, and every event in both emitted label ledgers. Does not discharge
Gaussian identities, exact scalar arithmetic, global invoices or asymptotics.
"""
import argparse
import copy
import gzip
import hashlib
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path

if not __debug__:
    raise RuntimeError('This verifier requires Python assertions enabled.')

def read(p):
    return json.load(gzip.open(p))

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',', ':')).encode()).hexdigest()

@lru_cache(None)
def span(vectors):
    s={0}
    for v in vectors:
        assert type(v) is int and 0 <= v < 512
        s |= {u ^ v for u in tuple(s)}
    return frozenset(s)

def sub(vectors):
    return span(tuple(vectors))

ZERO=sub([])
FULL=sub([1 << i for i in range(9)])

def rank(s):
    n=len(s)
    assert n and n & (n-1)==0
    return n.bit_length()-1

def perp(p):
    return frozenset(q for q in range(512) if (p&q).bit_count()%2==0)

def tau(q):
    return q ^ (43 if (q&43).bit_count()%2 else 0)

def transported(s):
    return frozenset(map(tau,s))

def regs(e):
    assert e[0] in ('add','scale')
    return e[1:3] if e[0]=='add' else e[1:2]

def raw_ledger(w):
    v=len(w['ports']); n=2*v+w['report']['R']
    cur=[sub([p]) for p in w['ports']]+[ZERO]*v+[sub(w['start_extra'].get(str(r),[])) for r in range(2*v,n)]
    initial=cur[:]
    final=[FULL]*v+[perp(p) for p in w['ports']]+[FULL]*w['report']['R']
    paid=Counter(); mass=[0]*n; center_mass=0; climbs=0
    def climb(r,f):
        nonlocal climbs
        assert 0 <= r < n and cur[r] <= f, ('non-nested raw climb',r,cur[r],f)
        if cur[r] != f:
            d=rank(f)-rank(cur[r]); assert d>0
            paid[d]+=1; mass[r]+=d; climbs+=1;cur[r]=f
    for part in ('A','B'):
        if part=='B':
            for t in range(v):
                assert cur[v+t]==sub(w['target_levels'].get(str(t),[])), ('target cut',t)
            for r,frame in zip(w['centers'],w['center_frames']):
                assert cur[r]==sub(frame), ('center cut',r)
                served={sub(w['target_levels'].get(str(e[1]-v),[])) for e in w['cut'] if e[2]==r}
                old=cur[r]
                for f in sorted(served,key=rank,reverse=True):
                    assert f <= old
                    if f!=old:
                        d=rank(old)-rank(f);paid[d]+=1;center_mass+=d;old=f
                assert old==ZERO, ('center bottom',r)
        for e in w[part]:
            f=sub(e[-1]); assert len(f)==2**len(e[-1]),'dependent raw frame'
            for r in regs(e):climb(r,f)
            assert all(cur[r]==f for r in regs(e))
    for r,f in enumerate(final):climb(r,f)
    assert mass==[rank(f)-rank(i) for i,f in zip(initial,final)]
    assert dict(paid)=={int(k):v for k,v in w['report']['local_profile'].items()}
    return dict(profile=dict(sorted(paid.items())),rank_mass=sum(k*v for k,v in paid.items()),child_count=sum(paid.values()),climbs=climbs,center_rank_mass=center_mass,per_register_telescoping=True)

def invariants(old,new):
    assert set(old)==set(new)
    changed={}
    for k in old:
        if k in ('A','B'):
            assert [e[:-1] for e in old[k]]==[e[:-1] for e in new[k]], ('scalar payload/order changed',k)
            changed[k]=sum(sub(a[-1])!=sub(b[-1]) for a,b in zip(old[k],new[k]))
        elif k=='report':
            for key in set(old[k])|set(new[k]):
                if key not in ('local_profile','global_profile'):
                    assert old[k].get(key)==new[k].get(key),('report field changed',key)
        else:
            assert old[k]==new[k],('fixed raw field changed',k)
    assert old['A'][:531]==new['A'][:531], 'compensation and kernel prelude changed'
    return dict(changed_gate_frames=changed,unchanged_scalar_gates=len(new['A'])+len(new['B']),unchanged_initial_A_events_including_frames=531,fixed_fields=sorted(set(old)-{'A','B','report'}))

def canonical_binding(w,c,base_c):
    v=len(w['ports']); n=2*v+w['report']['R'];f=[sub(x) for x in c['frames']]
    assert (v,n,c['h'],c['R'])==(c['v'],len(c['start']),9,w['report']['R'])
    assert f[0]==ZERO and f[1]==FULL and len(set(f))==len(f)
    assert all(len(s)==2**len(b) for s,b in zip(f,c['frames']))
    assert all(tau(tau(x))==x for x in range(512))
    assert all(tau(x^y)==tau(x)^tau(y) and (x&y).bit_count()%2==(tau(x)&tau(y)).bit_count()%2 for x in range(512) for y in range(512))
    assert len(set(c['ports']))==v and set(map(tau,w['ports']))==set(c['ports'])
    mapping={r:c['ports'].index(tau(p)) for r,p in enumerate(w['ports'])}
    mapping.update({r+v:mapping[r]+v for r in range(v)})
    mapping.update({r:r for r in range(2*v,n)})
    assert set(mapping)==set(range(n)) and len(set(mapping.values()))==n
    for k in ('A','B','cut','cleanup','precondition'):
        assert len(w[k])==len(c[k])
        for raw,can in zip(w[k],c[k]):
            x=copy.deepcopy(raw)
            for j in range(1,3 if x[0]=='add' else 2):x[j]=mapping[x[j]]
            assert x[:-1]==can[:-1],('canonical payload',k)
            assert (can[-1] is None) if raw[-1] is None else f[can[-1]]==transported(sub(raw[-1])), ('canonical frame',k)
    starts=[sub([p]) for p in w['ports']]+[ZERO]*v+[sub(w['start_extra'].get(str(r),[])) for r in range(2*v,n)]
    finals=[FULL]*v+[perp(p) for p in w['ports']]+[FULL]*w['report']['R']
    for r in range(n):
        assert f[c['start'][mapping[r]]]==transported(starts[r]), ('canonical start',r)
        assert f[c['final'][mapping[r]]]==transported(finals[r]), ('canonical final',r)
    assert c['centers']==[mapping[r] for r in w['centers']]
    assert [f[i] for i in c['center_frames']]==[transported(sub(x)) for x in w['center_frames']]
    assert {str(mapping[v+int(t)]-v):transported(sub(x)) for t,x in w['target_levels'].items()}=={str(t):f[x] for t,x in c['target_levels'].items()}
    assert c['local_profile']==w['report']['local_profile']
    bf=[sub(x) for x in base_c['frames']]
    for k in ('compensation','precondition','cleanup','cut'):
        assert [e[:-1] for e in c[k]]==[e[:-1] for e in base_c[k]], ('baseline canonical payload',k)
        assert [None if e[-1] is None else f[e[-1]] for e in c[k]]==[None if e[-1] is None else bf[e[-1]] for e in base_c[k]], ('baseline canonical frame',k)
    for k in ('start','final','center_frames'):
        assert [f[i] for i in c[k]]==[bf[i] for i in base_c[k]], ('baseline canonical boundary',k)
    assert c['ports']==base_c['ports'] and c['centers']==base_c['centers']
    return dict(transport_vector=43,transport_exhaustively_orthogonal_and_linear=True,register_permutation_bijective=True,all_raw_canonical_incidences_bound=True,fixed_compensation_operations=len(c['compensation']),actual_frame_count=len(f))

def scalar(e,back):
    x=copy.deepcopy(e[:-1])
    if back:
        if x[0]=='add':x[1],x[2]=x[2],x[1];x[3]=-x[3]
        else:x[2],x[3]=x[3],x[2]
    for j in range(1,3 if x[0]=='add' else 2):x[j]=['L',x[j]]
    return x

def ledger(c,events,back):
    v=c['v'];n=2*v+c['R'];f=[sub(x) for x in c['frames']]
    cur=[f[i] for i in c['start']]; initial=cur[:]
    phases=['zero_frame_precondition','entry_adapters','A','centers','B','final','exit_adapters','full_frame_cleanup','done']
    phases_seen=[];phase=None;scalars={p:[] for p in phases}; center_events=[]
    paid=Counter();mass=[0]*n;wrappers=Counter();adapters=Counter();touched=set();active=None;private={};private_life=Counter();center_mass=Counter();event_counts=Counter();actual_edges=set()
    entering={r for r in range(2*v,n) if cur[r]!=ZERO}
    for index,e in enumerate(events):
        tag=e[0];event_counts[tag]+=1
        if tag=='phase':
            assert active is None
            if phase=='centers':
                assert set(private)==set(range(len(c['centers'])))
            phase=e[1];phases_seen.append(phase)
            assert phases_seen==phases[:len(phases_seen)]
            if phase=='centers':
                assert all(cur[v+t]==f[c.get('target_levels',{}).get(str(t),0)] for t in range(v))
                assert all(cur[r]==f[q] for r,q in zip(c['centers'],c['center_frames']))
            if phase=='exit_adapters':assert cur==[f[i] for i in c['final']]
            continue
        assert phase in phases
        if tag=='climb':
            _,part,r,a,b,d=e
            assert phase==part and phase in ('A','B','final') and active is None
            assert cur[r]==f[a] and f[a] < f[b] and d==rank(f[b])-rank(f[a]),('emitted climb',back,index)
            assert r not in entering or wrappers['pre',r]==1
            actual_edges.add((a,b))
            cur[r]=f[b];paid[d]+=1;mass[r]+=d;touched.add(r)
        elif tag=='center':
            _,k,a,b,d=e
            assert phase=='centers' and active==k and private[k]==f[a]
            assert f[a]<f[b] if back else f[b]<f[a]
            assert d==abs(rank(f[a])-rank(f[b]))>0
            actual_edges.add((a,b))
            private[k]=f[b];paid[d]+=1;center_mass[k]+=d;center_events.append(e)
        elif tag=='adapter':
            _,kind,r,q=e
            assert 0<=r<n and cur[r]==f[q]
            assert (kind=='old_to_new' and phase=='entry_adapters' and r not in entering) or (kind=='new_to_old' and phase=='exit_adapters')
            adapters[kind,r]+=1
        elif tag=='residual_adapter':
            _,kind,r,q=e
            assert r in entering and q==c['start'][r]
            if kind=='pre':assert phase=='entry_adapters' and r not in touched
            else:assert kind=='post' and phase=='full_frame_cleanup' and len(scalars[phase])==len(c['cleanup'])
            wrappers[kind,r]+=1
        elif tag=='scalar':
            _,op,q=e; frame=f[q];kind=op[0];rs=[tuple(op[1])]+([tuple(op[2])] if kind in ('add','copy') else [])
            assert phase in ('zero_frame_precondition','A','centers','B','full_frame_cleanup')
            if phase=='centers':center_events.append(e)
            if kind=='clear':
                assert phase=='centers' and op[1][0]=='C'
                k=op[1][1]
                if private_life[k]==0:
                    assert active is None and k==len(private)
                    private[k]=frame;active=k
                else:
                    assert active==k and private_life[k]==1 and private[k]==frame
                    active=None
                private_life[k]+=1
            for typ,r in rs:
                if typ=='L':
                    assert cur[r]==frame, ('scalar label',back,index,r)
                    assert r not in entering or wrappers['pre',r]==1
                    assert wrappers['post',r]==0
                    touched.add(r)
                else:
                    assert typ=='C' and private[r]==frame and (active==r or kind=='clear')
            scalars[phase].append([op,q])
        else:raise AssertionError(('unexpected event',e))
    assert phases_seen==phases and active is None
    assert cur==[f[i] for i in c['final']]
    assert mass==[rank(f[q])-rank(a) for a,q in zip(initial,c['final'])]
    assert adapters==Counter({('old_to_new',r):1 for r in range(n) if r not in entering})+Counter({('new_to_old',r):1 for r in range(n)})
    assert wrappers==Counter({(kind,r):1 for kind in ('pre','post') for r in entering})
    for phase,source in [('zero_frame_precondition',c['precondition']+c['compensation']),('A',c['A']),('B',c['B']),('full_frame_cleanup',c['cleanup'])]:
        assert scalars[phase]==[[scalar(e,back),e[-1]] for e in source],('scalar phase binding',back,phase)
    assert all(f[q]==ZERO for _,q in scalars['zero_frame_precondition'])
    assert all(f[q]==FULL for _,q in scalars['full_frame_cleanup'])
    expected_center=[]
    for k,r in enumerate(c['centers']):
        cf=c['center_frames'][k];terms=[e for e in c['cut'] if e[2]==r]
        levels={c.get('target_levels',{}).get(str(e[1]-v),0) for e in terms}
        path=[cf]+sorted(levels-{cf},key=lambda q:rank(f[q]),reverse=True)
        assert f[path[-1]]==ZERO
        assert all(f[b] < f[a] for a,b in zip(path,path[1:]))
        order=list(reversed(path)) if back else path
        expected_center.append(['scalar',['clear',['C',k]],order[0]])
        if not back:expected_center.append(['scalar',['copy',['C',k],['L',r]],cf])
        for j,q in enumerate(order):
            if j:expected_center.append(['center',k,order[j-1],q,abs(rank(f[order[j-1]])-rank(f[q]))])
            for e in terms:
                if c.get('target_levels',{}).get(str(e[1]-v),0)==q:
                    op=['add',['C',k],['L',e[1]],e[3],e[4]] if back else ['add',['L',e[1]],['C',k],e[3],e[4]]
                    expected_center.append(['scalar',op,q])
        if back:expected_center.append(['scalar',['add',['L',r],['C',k],-1,1],cf])
        expected_center.append(['scalar',['clear',['C',k]],order[-1]])
        assert private_life[k]==2 and center_mass[k]==rank(f[cf])
    assert center_events==expected_center, ('center stream binding',back)
    assert dict(paid)=={int(k):v for k,v in c['local_profile'].items()}
    available_edges=set(map(tuple,c['edges']))|{(a,b) for q in c['center_frames'] for a,b in [(q,0),(0,q)]}
    assert actual_edges<=available_edges, 'actual edge missing from phase interface'
    return dict(events=len(events),event_counts=dict(event_counts),event_sha256=digest(events),profile=dict(sorted(paid.items())),rank_mass=sum(k*v for k,v in paid.items()),per_register_telescoping=True,private_center_paths=len(c['centers']),entering_helpers=len(entering),scalar_operations=sum(map(len,scalars.values())),all_actual_labels_checked=True,actual_directed_edges=len(actual_edges),all_actual_edges_covered_by_canonical_phase_interface=True)

def controls(w,c,events,old,base_c):
    rejected=[]
    def reject(name,fn):
        try:fn()
        except (AssertionError,KeyError,IndexError,TypeError,ValueError):rejected.append(name)
        else:raise AssertionError(('negative control survived',name))
    x=copy.deepcopy(w);x['A'][0][3]+=1
    reject('raw_scalar_payload_change',lambda:invariants(old,x))
    x=copy.deepcopy(w);x['start_extra'][next(iter(x['start_extra']))]=[]
    reject('changed_helper_entrance',lambda:invariants(old,x))
    x=copy.deepcopy(w);x['A'][0][-1]=[]
    reject('downward_raw_retiming',lambda:raw_ledger(x))
    x=copy.deepcopy(c);x['A'][0][-1]=0
    reject('canonical_frame_mismatch',lambda:canonical_binding(w,x,base_c))
    for name,back,mutator in [
        ('missing_forward_climb',False,lambda es:es.pop(next(i for i,e in enumerate(es) if e[0]=='climb'))),
        ('wrong_forward_climb_rank',False,lambda es:es[next(i for i,e in enumerate(es) if e[0]=='climb')].__setitem__(5,99)),
        ('wrong_backward_dual_sign',True,lambda es:es[next(i for i,e in enumerate(es) if e[0]=='scalar' and e[1][0]=='add')][1].__setitem__(3,99)),
        ('wrong_center_label',False,lambda es:es[next(i for i,e in enumerate(es) if e[0]=='scalar' and e[1][0]=='copy')].__setitem__(2,0)),
        ('missing_entering_pre_wrapper',False,lambda es:es.pop(next(i for i,e in enumerate(es) if e[:2]==['residual_adapter','pre']))),
        ('missing_entering_post_wrapper',True,lambda es:es.pop(next(i for i,e in enumerate(es) if e[:2]==['residual_adapter','post']))),
        ('wrong_exit_frame',True,lambda es:es[next(i for i,e in enumerate(es) if e[:2]==['adapter','new_to_old'])].__setitem__(3,0)),
        ('wrong_center_rank',True,lambda es:es[next(i for i,e in enumerate(es) if e[0]=='center')].__setitem__(4,99)),
    ]:
        es=copy.deepcopy(events['backward' if back else 'forward']);mutator(es)
        reject(name,lambda:ledger(c,es,back))
    return rejected

def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    wp=a.candidate/'FULL-WORD.json.gz';cp=a.candidate/'CANONICAL-WORD.json.gz';ep=a.candidate/'LOCAL-PROGRAMS.json.gz';op=a.baseline/'FULL-WORD.json.gz';bp=a.baseline/'CANONICAL-WORD.json.gz'
    w,c,events,old,base_c=map(read,[wp,cp,ep,op,bp])
    report=dict(status='PASS_INDEPENDENT_FIXED_SCALAR_RETIMING_AND_BOTH_ACTUAL_FRAME_LEDGERS',bindings={str(q):sha(q) for q in [wp,cp,ep,op,bp]},reviewer_sha256=sha(__file__),invariants=invariants(old,w),original_raw_ledger=raw_ledger(old),retimed_raw_ledger=raw_ledger(w),canonical_binding=canonical_binding(w,c,base_c),emitted_ledgers={name:ledger(c,events[name],name=='backward') for name in ('forward','backward')},negative_controls_rejected=controls(w,c,events,old,base_c),scope='Finite source and emitted-label retiming check only. Gaussian phase identities, exact all-column scalar arithmetic, complete global paid invoice, and inherited all-size/analytic interfaces are separate obligations.')
    a.out.write_text(json.dumps(report,indent=2)+'\n')
    print(report['status']);print('profile',report['retimed_raw_ledger']['profile']);print('rank mass',report['retimed_raw_ledger']['rank_mass'],'negative controls',len(report['negative_controls_rejected']))

if __name__=='__main__':main()
