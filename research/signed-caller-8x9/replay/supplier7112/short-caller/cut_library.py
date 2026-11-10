from fractions import Fraction as Q
from collections import Counter
from functools import lru_cache
import json,sys,importlib.util,itertools
from pathlib import Path
from connected import canonical,lower_bound,meet
from stage import one_type,rows_of,trans,prod,dot,colrank
from screen import screen,P

ROOT=Path(__file__).resolve().parent

def gauge(v,x,y,row):
    w={i:a for i,a in v.items() if i not in (x,y)}
    a,b=v.get(x,0),v.get(y,0)
    if a+b:w[x]=(a+b)* (Q(1,2) if row else 1)
    if a-b:w[y]=(a-b)* (Q(1,2) if row else 1)
    return w

def mask_for(h,x,y):
    out=set()
    for a,b in h:
        for v in (a,b):
            out.update(i for i,c in enumerate(v) if i not in (x,y) and c)
            if (v[x]+v[y])%P:out.add(x)
            if (v[x]-v[y])%P:out.add(y)
    return out

@lru_cache(None)
def pairing(v,w):
    return len(colrank([{i:d for i,b in enumerate(w) if (d:=dot(dict(a),dict(b)))} for a in v]))

def block_tuple(A):return tuple(tuple(sorted(v.items())) for v in A)

@lru_cache(None)
def move_space(V, A):
    return canonical(prod([dict(x) for x in V],[dict(x) for x in A]))

class Physical:
    def __init__(self,caller):
        a=one_type(caller,'B',return_cuts=True,phase=1)
        b=one_type(caller,'B',return_cuts=True,phase=-1)
        self.cuts=[]
        for (j,f,fi),(k,g,gi) in zip(a,b):
            assert j==k
            T=prod(trans(gi),f);Ti=prod(trans(fi),g)
            assert prod(T,Ti)==[{i:Q(1)} for i in range(len(T))]
            self.cuts.append((j,block_tuple(T),block_tuple(trans(Ti))))
        assert len(self.cuts)==23
    @lru_cache(None)
    def eligible(self,V):
        ax,ay,bx,by=V
        if not pairing(ax,ay) or not pairing(bx,by):return ()
        avail=[]
        for j,T,Tit in self.cuts:
            x=meet(ax,move_space(bx,Tit))
            if not x:continue
            y=meet(ay,move_space(by,T))
            if y and pairing(x,y):avail.append((j,x,y))
        return tuple(avail)

def coupled_bound(order, domains, physical):
    hist=Counter(); stats=[]
    for index,j in enumerate(order):
        init=domains[j]; spaces={init:0}
        for later in order[index+1:]:
            updates={}
            for V,count in spaces.items():
                R=tuple(meet(a,b) for a,b in zip(V,domains[later]))
                if all(R):updates[R]=max(updates.get(R,0),count+1)
            for R,count in updates.items():spaces[R]=max(spaces.get(R,0),count)
        feasible={V:(count,physical.eligible(V)) for V,count in spaces.items() if count>0}
        feasible={V:(count,a) for V,(count,a) in feasible.items() if a}
        hist[8]+=len(init[0]);before=len(init[0]);caps=[]
        for k in range(1,max((n for n,_ in feasible.values()),default=0)+1):
            bounds=[canonical(dict(v) for count,locations in feasible.values() if count>=k for cut,x,y in locations for v in (x,y)[i]) for i in range(2)]
            cap=pairing(*bounds)
            assert cap<=before;before=cap;caps.append(cap)
            hist[8*(k+1)]+=cap;hist[8*k]-=2*cap
            if k>1:hist[8*(k-1)]+=cap
        stats.append({'stage':j,'shared_space_signatures':sum(count>0 for count in spaces.values()),'physical_signatures':len(feasible),'caps':caps})
    return {r:c for r,c in sorted(hist.items()) if c},stats

def main(caller_path,base_path,engine_path):
    C=json.loads(caller_path.read_bytes());S=json.loads(base_path.read_bytes());
    sp=importlib.util.spec_from_file_location('gate',engine_path);gate=importlib.util.module_from_spec(sp);sp.loader.exec_module(gate)
    d=C['types']['B']['diagonal'];n=len(d);old={j:{i for i,r in enumerate(d) if r[j+1]} for j in range(1,19)}
    hosts=[one_type(C,'B',return_hosts=True,phase=q) for q in (1,-1)];probes=[];physical=Physical(C)
    for phase in (1,96,22,75):
        H={};screen(C,phase,[1]*18,H);probes.append(H)
    orig_idle=Counter(8*len(e[3]) for e in C['events'] if e[:2]==['B','IDLE_ONE'])
    orig_t=Counter(8*sum(r[2:])+1 for r in d)
    source=json.loads((ROOT/'CROSS-GAUGE.json').read_bytes());pairs=sorted({(x-38,y-38) for j,x,y,*_ in source['possible_one_pair_cross_mask_uses']})
    orders=[tuple(range(1,10))+tuple(range(18,9,-1)),tuple(range(1,19)),tuple(range(18,0,-1))]
    k=Q(S['gate']['claim']);cap=Q(S['gate']['BIT_pin']);full=Counter({int(r):c for r,c in S['invoice']['T'].items()});full.subtract({int(r):c for r,c in S['invoice']['P'].items()})
    records=[]
    for x,y in pairs:
        new={j:set.union(*(mask_for(H[j],x,y) for H in probes)) for j in old}
        assert all(new[j]-{x,y}==old[j]-{x,y} for j in old)
        D={j:[] for j in old}
        for phase_hosts in hosts:
            for j,h in phase_hosts.items():
                rows=rows_of([(gauge(a,x,y,False),gauge(b,x,y,True)) for a,b in h],n)
                assert all(i in new[j] and s in new[j] for i,v in enumerate(rows) for s in v)
                R=[{i:Q(1)} if i in new[j] else {} for i in range(n)]
                for a,b in zip(R,rows):
                    for i,v in b.items():
                        a[i]=a.get(i,0)-v
                        if not a[i]:a.pop(i)
                assert prod(R,R)==R
                D[j].extend([canonical(gauge(a,x,y,True) for a in trans(R)),canonical(gauge(a,x,y,False) for a in R)])
                assert len(D[j][-1])==len(D[j][-2])==len(new[j])-2
        D={j:tuple(v) for j,v in D.items()}
        trial=[(*coupled_bound(o,D,physical),o) for o in orders]
        h,stats,o=max(trial,key=lambda p:gate.moment(p[0],k)[0]);assert sum(r*c for r,c in h.items())==8*sum(len(R[0]) for R in D.values())
        new_t=Counter(8*sum(i in m for m in new.values())+1 for i in range(n))
        delta=Counter(new_t);delta.subtract(orig_t);delta.update(orig_idle);delta.subtract(h)
        assert sum(r*c for r,c in delta.items())==0
        signed=full.copy();signed.update({r:8*c for r,c in delta.items()})
        derivative=(0,0)
        for r,c in signed.items():
            term=gate.mul(gate.power(r,cap if c>=0 else k),gate.log(r));derivative=gate.add(derivative,gate.smul(term,-c))
        signed_margin=gate.moment(signed,k)
        records.append(dict(pair=[x+38,y+38],removed=[[j,i+38] for j in old for i in sorted(old[j]-new[j])],added=[[j,i+38] for j in old for i in sorted(new[j]-old[j])],
          optimistic_paid_hist=h,physical_cut_count=len(physical.cuts),chosen_order=o,cut_screen=stats,upper_delta_hist={r:c for r,c in sorted(delta.items()) if c},optimistic_delta_at_claim=gate.value(gate.moment(delta,k)),
          complete_margin_at_claim=gate.value(signed_margin),complete_derivative_upper=str(Q(derivative[1],gate.B)),uniformly_excluded=signed_margin[1]<0 and derivative[1]<0))
    print(json.dumps({'claim':str(k),'cap':str(cap),'cases':records},indent=2))
if __name__=='__main__':main(*(Path(s) for s in sys.argv[1:]))
