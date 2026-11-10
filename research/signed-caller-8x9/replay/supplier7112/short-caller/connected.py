"""Optimistic idle invoice bound for the fixed HOST projections of #7002."""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
import hashlib,importlib.util,json,sys
from stage import dot,linear,scale,intersection,rows_of,colrank,trans

ROOT=Path(__file__).resolve().parent
INTERVAL_SHA256="60a743d13f668ef86db4b8215b4d5d04430a671ba6f1fe06d9c1c4c3dfe86da5"
PINS={"root7002.json":"be4a2beed3a40de6d2c5dcc6e4f25f3c2a4375551b70e63fb0e9a03041db6a34",
      "caller7002.json":"f4090329f219edd493b4ca592128521e867a355fb528556b15201e759783568b",
      "invoice7002.json":"87a41b13bdd9248d538805f76a970f51335567845dfc0070698b6979a08b70d6"}

def load(name):
    raw=(ROOT/name).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==PINS[name]
    return json.loads(raw)

def canonical(vectors):
    basis={}
    for v in vectors:
        for k,w in basis.items():
            if k in v:v=linear(v,w,-v[k])
        if v:
            k=min(v); v=scale(v,1/v[k])
            for j,w in basis.items():
                if k in w:basis[j]=linear(w,v,-w[k])
            basis[k]=v
    return tuple(tuple(sorted(basis[k].items())) for k in sorted(basis))

@lru_cache(None)
def meet(A,B):
    return canonical(intersection([dict(x) for x in A],[dict(x) for x in B]))

def projected(c):
    n=c["roles"]
    rows,cols=([{i:F(1)} for i in range(n)] for _ in range(2))
    def add(r,s,q):
        rows[r]=linear(rows[r],rows[s],q)
        cols[s]=linear(cols[s],cols[r],-q)
    hosts={};idles={i:[] for i in range(18)}
    for op,r,*a in c["events"]:
        if op=="HOST":
            y,j,alpha,beta=a
            add(r,y,F(alpha));add(y,r,F(beta))
            assert j not in hosts; hosts[j]=[(cols[k],rows[k]) for k in (r,y)]
        elif op=="QUERY":add(r,a[0],F(1))
        elif op=="ADD":add(r,a[0],F(a[1]))
        elif op=="SWAP":
            j=a[0];rows[r],rows[j]=rows[j],rows[r];cols[r],cols[j]=cols[j],cols[r]
        elif op=="SCALE":
            q=F(a[0]);rows[r]=scale(rows[r],q);cols[r]=scale(cols[r],1/q)
        elif op=="IDLE_ONE":
            for j in a[0]:idles[j].append((cols[r],rows[r]))
        else:assert op=="LAMBDA"
    assert rows==cols==[{i:F(1)} for i in range(n)]
    residuals={}
    for j in range(18):
        total=rows_of(idles[j]+hosts[j],n)
        expected=[{i:F(1)} if mask & (1<<j) else {} for i,mask in enumerate(c["masks"])]
        assert total==expected and len(idles[j])==sum(map(bool,expected))-len(hosts[j])
        residuals[j]=canonical(trans(rows_of(idles[j],n)))
        assert len(residuals[j])==len(idles[j])
    return residuals

def lower_bound(order,residuals):
    result={};hist=Counter()
    for i,stage in enumerate(order):
        R=residuals[stage];spaces={R:0}
        for later in order[i+1:]:
            Q=residuals[later];extra={}
            for V,k in spaces.items():
                W=meet(V,Q)
                if W:extra[W]=max(extra.get(W,0),k+1)
            for V,k in extra.items():spaces[V]=max(spaces.get(V,0),k)
        caps=[len(R)]
        for k in range(1,max(spaces.values())+1):
            caps.append(len(canonical(dict(w) for V,h in spaces.items() if h>=k for w in V)))
        assert all(a>=b for a,b in zip(caps,caps[1:]))
        hist[8]+=len(R)
        for k,capacity in enumerate(caps[1:],1):
            hist[8*(k+1)]+=capacity
            hist[8*k]-=2*capacity
            if k>1:hist[8*(k-1)]+=capacity
        result[stage]={"directions":caps,"distinct_nonzero_intersections":len(spaces)}
    return {r:c for r,c in sorted(hist.items()) if c},result

def main():
    c=load("caller7002.json"); root=load("root7002.json"); native=load("invoice7002.json")
    n=c["roles"];assert n==root["n"]==38
    assert [sum(1<<j for j,s in enumerate(root["stages"]) if i in s["mask"]) for i in range(n)]==c["masks"]
    assert Counter(e[0] for e in c["events"])["IDLE_ONE"]==181
    residuals=projected(c)
    engine=Path(sys.argv[1])
    assert hashlib.sha256(engine.read_bytes()).hexdigest()==INTERVAL_SHA256
    spec=importlib.util.spec_from_file_location("directed_interval",engine)
    g=importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
    target=Counter(1+8*m.bit_count() for m in c["masks"])
    target={r:104*v for r,v in target.items()}
    for r,v in native["helpers"].items():target[int(r)]=target.get(int(r),0)+18*v
    paid=Counter({int(r):18*v for r,v in native["local_paid"].items()})
    paid[1]+=(18+3)*104
    a=F("0.00363166992");b=F("0.01")
    orders={"ascending":tuple(range(18)), "descending":tuple(reversed(range(18))),
            "centre_last":tuple(range(8))+tuple(reversed(range(9,18)))+(8,),
            "large_masks_last":tuple(sorted(range(18),key=lambda i:len(residuals[i])))}
    e0,e1,e2=({i:F(1)} for i in range(3))
    positive={0:canonical([e0,e1]),1:canonical([e0,e2]),2:canonical([e0])}
    assert lower_bound((0,1,2),positive)[0]=={8:2,24:1}
    negative={0:canonical([e0]),1:canonical([e1])}
    assert lower_bound((0,1),negative)[0]=={8:2}
    ans={}
    for label,order in orders.items():
        h,caps=lower_bound(order,residuals)
        lower={r:paid[r]+104*h.get(r,0) for r in paid.keys()|h.keys()}
        mh={r:target.get(r,0)-lower.get(r,0) for r in target.keys()|lower.keys()}
        def derivative(a,b):
            val=(0,0)
            for r,c in mh.items():
                val=g.add(val,g.smul(g.mul(g.power(r,b if c>=0 else a),g.log(r)),-c))
            return val
        price=g.moment(h,a)
        saving=g.sub(g.moment({8:181},a),price)
        margin=g.moment(mh,a)
        slope=derivative(a,b)
        assert sum(r*v for r,v in h.items())==181*8
        assert margin[1]<0 and slope[1]<0
        assert g.add(margin,g.exact(18*104))[0]>0 # omitted-adapter control
        ans[label]={"order":order,"idle_price_bound":h, "caps":caps,
                    "price_at_benchmark":g.show(price),
                    "max_idle_saving_at_benchmark":g.show(saving),
                    "optimistic_margin_at_benchmark":g.show(margin),
                    "upper_derivative_through_001":str(F(slope[1],g.B)),
                    "full_signed_histogram":dict(sorted(mh.items()))}
    print(json.dumps({"pins":PINS,"interval_engine_sha256":INTERVAL_SHA256,"kappa":str(a),
        "window_upper":str(b),"results":ans,"controls":["shared_three_stage_direction",
        "disjoint_one_stage_directions","omitted_adapter_changes_funding_sign"]},sort_keys=True,indent=2))

if __name__=="__main__":main()
