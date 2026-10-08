#!/usr/bin/env python3
"""Actual h24 signed events, copied centers, reflected frames and paid ranks.
Zhihao Chen / Codex audit of Swapnil Jain's Apache-2.0 pinned round6 producer.
Frame labels are binary subspaces; complex phases use the separately proved
q_U and inverse-rank-one endpoint identities, not XOR cancellation.
"""
import sys,json,time,signal,gzip,hashlib
from pathlib import Path
from collections import Counter
from array import array
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'swapnil-round7/independent/complex-twostage'))
from producer import NStar3,compile_roles
from frames import Checker,echelon,perp_in,ok_res

def main():
    st=time.monotonic()
    def stop(*_):raise TimeoutError('180s event ledger limit')
    signal.signal(signal.SIGALRM,stop);signal.alarm(180)
    h=24;c=NStar3(h);k=compile_roles(c);ch=Checker(c)
    v=len(c.triples);R=k['size'];size=2*v+R;off=2*v;m=h*h
    bases=[];ids={};dims=[]
    def key(b):
        b=tuple(sorted(echelon(b).values()))
        if b not in ids:ids[b]=len(bases);bases.append(b);dims.append(len(b))
        return ids[b]
    zero=key([]);F=key([1<<i for i in range(h)])
    nk={n:key(ch.label(n)) for n in c.active}
    line=[key([sum(1<<i for i in T)]) for T in c.triples]
    hyper=[key(perp_in(bases[F],bases[t])) for t in line]
    cur=line+[zero]*(v+R);initial=cur[:];events=array('i');copies=[]
    H={name:Counter() for name in ('aux','data','center')};geometry=set()
    # kind, dst/register, src/old-frame, numerator/new-frame, denominator/rank.
    def move(reg,f):
        old=cur[reg]
        if old==f:return
        if (old,f) not in geometry:
            assert ch.edge(list(bases[old]),list(bases[f])),('bad actual edge',reg,old,f)
            geometry.add((old,f))
        r=dims[f]-dims[old];assert r>0
        events.extend((0,reg,old,f,r));H['aux' if reg>=off else 'data'][r]+=1;cur[reg]=f
    def add(t,s,n=1,d=1):
        assert cur[t]==cur[s];events.extend((1,t,s,n,d))
    def mix(mode,inverse=False):
        for n,ins,outs in reversed(k['gates']) if inverse else k['gates']:
            f=zero if mode=='low' else F if mode=='high' else nk[n]
            for q in sorted(set(ins+outs)):move(off+q,f)
            if inverse:
                for q in reversed(outs[1:]):add(off+q,off+outs[0],-1)
                if len(ins)==2:add(off+ins[0],off+ins[1],-1)
            else:
                if len(ins)==2:add(off+ins[0],off+ins[1])
                for q in outs[1:]:add(off+q,off+outs[0])
    def inject(sign,high):
        for i,(T,n,cf) in enumerate(c.pieces):
            t=c.tid[T];s=off+k['pout'][i];f=hyper[t] if high else zero
            move(s,f);move(v+t,f);add(v+t,s,sign*cf,2)
    terms={name:[] for name in k['rout']}
    for j,T in enumerate(c.triples):
        if h-1 not in T:
            terms[('*',)].append((v+j,2));selected=T;sg=-1
        else:
            terms[('*',)].append((v+j,5-h));selected=[i for i in range(h-1) if i not in T];sg=1
        for i in selected:terms[('E',i)].append((v+j,sg))
    def center(sign,copied=False):
        for name,sl in k['rout'].items():
            reg=off+sl
            for t,n in terms[name]:assert cur[t]==zero
            if copied:
                # Fresh copy retains its source frame and is moved to zero;
                # original arbitrary-dirty role remains at its live frame.
                f=cur[reg];assert ok_res(list(bases[f]));r=dims[f]
                copies.append(dict(source=reg,frame=f,target_frame=zero,terms=terms[name]))
                events.extend((2,reg,f,len(copies)-1,r));H['center'][r]+=1
            else:
                move(reg,zero)
                for t,n in terms[name]:add(t,reg,sign*n,2)
    def source(sign,high):
        for T,sl in k['src'].items():
            t=c.tid[T];f=F if high else line[t]
            move(off+sl,f);move(t,f);add(off+sl,t,sign)
    mix('low');center(-1);inject(-1,False);mix('low',True)
    source(1,False);mix('label');center(1,True);inject(1,True)
    mix('high',True);source(-1,True)
    for s in range(R):move(off+s,F)
    assert cur[:v]==[F]*v and cur[v:off]==hyper and cur[off:]==[F]*R
    assert sum(r*n for r,n in H['aux'].items())==R*h
    assert sum(r*n for r,n in H['data'].items())==2*v*(h-1)
    assert sum(r*n for r,n in H['center'].items())==(h-1)**2+h
    # Explicit time-reversed signed word with complement labels and bank swap.
    bank=lambda s:s+v if s<v else s-v if s<off else s
    rev=[None]*size
    for s in range(size):rev[bank(s)]=~cur[s]
    RH=Counter();scalar=0
    for j in range(len(events)-5,-1,-5):
        kind,a,b,d,e=events[j:j+5];a=bank(a)
        if kind==0:
            assert rev[a]==~d;rev[a]=~b;RH[e]+=1
        elif kind==1:
            b=bank(b);assert rev[a]==rev[b]
            # Inverse coefficient is -d/e, not d/e.
            scalar+=1
        else:
            cp=copies[d];assert rev[a]==~b
            for t,n in cp['terms']:assert rev[bank(t)]==~zero
            # Fresh copy at complement(source), then moved to full space.
            RH[e]+=1;scalar+=len(cp['terms'])
    assert all(rev[bank(s)]==~initial[s] for s in range(size))
    assert RH==sum(H.values(),Counter())
    # Actual local moves, then global auxiliary endpoints, data connectors,
    # and the inverse rank-one copied correction.
    N=v*v;paid=Counter({r:2*v*n for r,n in RH.items()})
    paid[m-h]+=2*v*R;paid[(h-1)**2]+=2*N;paid[1]+=N
    old=json.loads((HERE/'swapnil-round7/lean/round6-histograms.json').read_text())['cx']; old['hist']=dict(old['hist'])
    assert dict(paid)=={int(r):n for r,n in old['hist'].items()}
    rank=sum(r*n for r,n in paid.items());assert rank==old['s']==119453132304
    outdir=HERE/'round6-complex-literal-ledger';outdir.mkdir(exist_ok=True)
    with gzip.open(outdir/'forward-events.i32.gz','wb') as f:f.write(events.tobytes())
    (outdir/'frames-copies.json').write_text(json.dumps(dict(bases=bases,initial=initial,final=cur,copies=copies),separators=(',',':'))+'\n')
    out=dict(h=h,roles=R,formal_wire_count=size,events=len(events)//5,unique_frames=len(bases),actual_geometric_edges=len(geometry),
      internal_histograms={name:dict(hist) for name,hist in H.items()},copied_center_macros=len(copies),
      literal_scalar_updates_including_copied_scatter=scalar,signed_inverse_coefficient_rule='negate each coefficient and reverse order',
      actual_forward_equal_frames=True,reflected_continuity=True,actual_geometry_passed=True,
      full_histogram=dict(paid),histogram_matches_pinned=True,recursive_rank=rank,maxchild=max(paid),
      elapsed=time.monotonic()-st,limit_seconds=180,
      scope='Full h24 literal frame/event charge replay; exact signed scalar all-h commutator uses prior h24 AMV=I identity and invertible mixers. Prior small full basis and general phase proof reused. This is not a dense h24 physical coefficient replay or proof of all-size precision/tape applicability.',new_multiplication_bound=False)
    (outdir/'result.json').write_text(json.dumps(out,indent=2)+'\n');signal.alarm(0)
    print(json.dumps({k:v for k,v in out.items() if k not in ('internal_histograms','full_histogram')},indent=2))
if __name__=='__main__':main()
