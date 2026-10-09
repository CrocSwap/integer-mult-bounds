#!/usr/bin/env python3
"""Explicit forward and reflected frame/event ledger of pinned round-seven.
Zhihao Chen / Codex audit. Exact nesting of the supplied chains is inherited
from the separately run frame/lifted checkers, not inferred from ranks here.
Copied-center moves are temporary macros, not erased arbitrary scratch.
"""
import sys,json,signal,time,hashlib,gzip
from pathlib import Path
from collections import defaultdict,Counter
from array import array
HERE=Path(__file__).resolve().parent;ROOT=HERE/'swapnil-round7'
sys.path.insert(0,str(ROOT/'independent/deferred-readout'))
import deferred as dr

def main():
    started=time.monotonic()
    def stop(*_):raise TimeoutError('180 second literal ledger limit')
    signal.signal(signal.SIGALRM,stop);signal.alarm(180)
    W,D=dr.load(23);S=dr.Schedule(W,D);v,R,h=S.v,S.R,S.h;size=2*v+R
    co=S.adjoint();sel=S.sel;ops=S.ops;prev={};pred=defaultdict(list);last={}
    for i,op in enumerate(ops):
        for s in S.touch(op):
            if s in prev:pred[i].append(prev[s])
            prev[s]=i;last[s]=i
    ph=set();stack=[last[s] for s in S.ret]
    while stack:
        i=stack.pop()
        if i in ph:continue
        ph.add(i);stack.extend(pred[i])
    assert not any(set(S.touch(ops[i]))&sel for i in ph)
    keys=[];ids={};dims=[]
    def norm(k):
        if k[0]=='out':return ('out',0,tuple(k[2]))
        return k
    def key(k):
        k=norm(k)
        if k not in ids:
            ids[k]=len(keys);keys.append(k);dims.append(S.dim(k))
        return ids[k]
    z,F=key(('0',)),key(('F',))
    paths=[None]*size
    for n,ss in S.xs:paths[n-1]=[key(('n',n))]+[key(('v',s)) for s in ss]+[F]
    y=[[] for _ in range(v)]
    for s in S.readout:
        for t,c in co[s].items():
            if c&1:y[t].append(key(('sigma',s)))
    for t,T in enumerate(S.trip):paths[v+t]=[z]+y[t]+[key(('out',0,T))]
    for s in range(R):paths[2*v+s]=[key(k) for k in S.chain_keys(s)]
    assert all(p and all(dims[b]>=dims[a] for a,b in zip(p,p[1:])) for p in paths)
    pos=[0]*size;current=[p[0] for p in paths];initial=current[:]
    # Fixed-width event records: kind, register/destination, source-or-old,
    # new-or-common, rank. kind=0 move,1 xor,2 temporary copied-center macro.
    events=array('i');rank_hist={k:Counter() for k in ('aux','data','center')}
    bits=[1<<i for i in range(size)]
    def emit(k,a,b,c,r=0):events.extend((k,a,b,c,r))
    def move(s,dst):
        if current[s]==dst:return
        p=paths[s]
        if dst not in p[pos[s]+1:]:
            raise ValueError(dict(register=s,slot=s-2*v,current=keys[current[s]],destination=keys[dst],remaining=[keys[k] for k in p[pos[s]:]],full=[keys[k] for k in p]))
        j=p.index(dst,pos[s]+1)
        while pos[s]<j:
            a=p[pos[s]];b=p[pos[s]+1];r=dims[b]-dims[a];assert r>=0
            emit(0,s,a,b,r);rank_hist['aux' if s>=2*v else 'data'][r]+=1
            pos[s]+=1;current[s]=b
    def xor(t,s):
        assert current[t]==current[s],('gate frames',t,s,keys[current[t]],keys[current[s]])
        emit(1,t,s,current[t]);bits[t]^=bits[s]
    def readout(s):
        aux=2*v+s;f=key(('sigma',s)) if s in sel else z
        assert current[aux]==f
        for t,c in sorted(co[s].items()):
            if c&1:move(v+t,f);xor(v+t,aux)
    def source(s,active):
        frame=key(('v',s)) if active else F
        move(2*v+s,frame);move(S.srcop[s]-1,frame);xor(2*v+s,S.srcop[s]-1)
    reordered_fans=[]
    def operation(i,active):
        op=ops[i]
        if op[0]=='add':
            _,p,o,n=op;frame=key(('n',n)) if active else F
            move(2*v+p,frame);move(2*v+o,frame);xor(2*v+p,2*v+o)
        elif op[0]=='fan':
            # Scalar fan targets commute. The archive groups copies whose
            # physical start frames differ; execute them in frame-chain order.
            targets=sorted(op[2],key=lambda s:S.dim(S.start_key(s))) if active else op[2]
            if active and tuple(targets)!=tuple(op[2]):reordered_fans.append(i)
            for s in targets:
                frame=key(S.start_key(s)) if active else F
                move(2*v+op[1],frame);move(2*v+s,frame);xor(2*v+s,2*v+op[1])
    for s in range(R):
        if s not in sel:readout(s)
    early=sorted(set(S.srcop)-sel,key=lambda s:(S.srcop[s],len(S.vstart[s]),s))
    for s in early:source(s,True)
    first=[i for i in range(len(ops)) if i in ph and ops[i][0]!='src']
    rest=[i for i in range(len(ops)) if i not in ph and ops[i][0]!='src']
    centers={}
    for i in first:operation(i,True)
    for s,c in S.ret.items():
        a=2*v+s;f=key(('ret',c));move(a,f)
        targets=[v+t for t,T in enumerate(S.trip) if c in T]
        assert all(current[t]==z for t in targets)
        centers[a]=targets;emit(2,a,f,z,h-1);rank_hist['center'][h-1]+=1
        for t in targets:bits[t]^=bits[a]
    for s in S.readout:readout(s)
    for s in S.late_v:source(s,True)
    for i in rest:operation(i,True)
    for s,(c,T) in S.out.items():
        t=S.tid[T];f=key(('out',0,T));move(2*v+s,f);move(v+t,f);xor(v+t,2*v+s)
    for i in reversed(first+rest):operation(i,False)
    for s in S.srcop:source(s,False)
    for s in range(R):move(2*v+s,F)
    assert all(bits[i]==((1<<i)^(1<<(i-v)) if v<=i<2*v else 1<<i) for i in range(size))
    assert all(current[i]==F for i in range(v)) and all(current[2*v+s]==F for s in range(R))
    for H in rank_hist.values():H.pop(0,None)
    assert rank_hist['aux']==dr.chain_ranks(S)
    assert sum(r*c for r,c in rank_hist['data'].items())==2*v*(h-1)
    # Actual reflected word: reverse time, complement frames, swap X/Y banks.
    # Center copies are regenerated at the reflected source frame, moved to
    # the reflected target frame, scattered and discarded (same scalar macro).
    bank=lambda s:s+v if s<v else s-v if s<2*v else s
    rev=[None]*size
    for s in range(size):rev[bank(s)]=~current[s]
    reverse_initial=rev[:];bits=[1<<i for i in range(size)];rh=Counter()
    for i in range(len(events)-5,-1,-5):
        k,a,b,c,r=events[i:i+5];a=bank(a)
        if k==0:
            assert rev[a]==~c;rev[a]=~b;rh[r]+=1
        elif k==1:
            b=bank(b);assert rev[a]==rev[b]==~c;bits[a]^=bits[b]
        else:
            assert rev[a]==~b
            for t in centers[a]:
                t=bank(t);assert rev[t]==~c;bits[t]^=bits[a]
            rh[r]+=1
    assert all(rev[bank(s)]==~initial[s] for s in range(size))
    assert all(bits[i]==((1<<i)^(1<<(i+v)) if i<v else 1<<i) for i in range(size))
    rh.pop(0,None);assert rh==sum(rank_hist.values(),Counter())
    # Assemble from ACTUAL events, not the schedule's pre-summed chain table.
    m=h*h;N=v*v;H=Counter()
    for r,c in rh.items():
        for width in dr.inner(r,h):H[width]+=2*v*c
    for s in range(R):
        r=h-S.f[s];H[m-2*r]+=2*v
        for width in dr.inner(r,h):H[width]+=2*v
    H[m-4*h+2]+=2*N
    for width in dr.STAIRCASE_CORNER(h):H[width]+=2*N
    H[1]+=N
    expected=dr.histogram(S,dr.chain_ranks(S),S.ylevels(co),S.xdata(),dr.STAIRCASE_CORNER(h))
    assert dict(H)==expected['hist'];assert sum(w*n for w,n in H.items())==expected['s']
    dest=HERE/'round7-literal-ledger';dest.mkdir(exist_ok=True)
    with gzip.open(dest/'forward-events.i32.gz','wb') as f:f.write(events.tobytes())
    (dest/'frames-and-paths.json').write_text(json.dumps(dict(keys=keys,dims=dims,paths=paths,initial=initial,final=current,centers=centers),separators=(',',':'))+'\n')
    out=dict(h=h,roles=R,formal_basis=size,events=len(events)//5,frame_keys=len(keys),
        rank_histograms={k:dict(vv) for k,vv in rank_hist.items()},
        fan_groups_reordered_internally=reordered_fans,
        complete_forward_F2=True,complete_reflected_F2=True,
        reflected_frame_continuity=True,all_scalar_gates_equal_frame_keys=True,
        exterior_formula='E1=I-I_tensor_Q+sigma_tensor_Q; E2=(I-P)_tensor_I+P_tensor_sigma; rank=m-h+dim(sigma)',
        histogram_matches_external=True,histogram=dict(H),recursive_rank=expected['s'],
        elapsed=time.monotonic()-started,limit_seconds=180,
        exact_chain_geometry='Relies on separately replayed pinned check_frames and check_lifted. Rank labels alone do not prove geometry.',
        scope='Explicit one-axis forward/reflected events, scalar complete basis and exact accounting. Tensor endpoint identities proved separately; full complex/tape/precision and final assembly integration not established.',new_multiplication_bound=False)
    (dest/'result.json').write_text(json.dumps(out,indent=2)+'\n');signal.alarm(0)
    print(json.dumps({k:v for k,v in out.items() if k not in ('histogram','rank_histograms')},indent=2))
if __name__=='__main__':main()
