"""Try fusing one first-J and one final-J relative rank-one shear."""
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal

ROOT=Path(__file__).resolve().parents[1]


def dot(a,b):
    return sum(x*y for x,y in zip(a,b,strict=True) if x and y)


def add(a,b,coef):
    return [x+coef*y for x,y in zip(a,b,strict=True)]


def stop(*_):
    raise TimeoutError("45-second four-factor cap")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(45)
    pins={}
    for line in (ROOT/"receipts/LEAD-PINS.txt").read_text().splitlines():
        h,name=line.split()
        assert name not in pins and sha256((ROOT/(name if name.startswith("inputs/") else "engines/"+name)).read_bytes()).hexdigest()==h
        pins[name]=h
    f=run_path(str(ROOT/"engines/forward.py"))
    rank=run_path(str(ROOT/"engines/rank_gate.py"))["rank"]
    assert pins["inputs/CALLER.json"]==f["PINS"]["inputs/CALLER.json"]
    unit,apply=f["unit"],f["apply"]
    tape=loads((ROOT/"inputs/CALLER.json").read_bytes())["events"]
    price=loads((ROOT/"inputs/R193.json").read_bytes())
    credit=[Q(x)-96 for x in price["per_host_before_new_A_channels"]]
    assert credit[0]>0 and credit[1]<96
    factors=[]
    for clock,e in enumerate(tape):
        if e[0]=="J":
            a,b,c,d=e[2]
            shears=[(b,a,1),(c,d,-1)]
        elif e[:2]==["A","QUERY"]:
            assert e[-1]==-1
            shears=[(e[2],e[3],1)]
        else:
            continue
        prefix=tape[:clock]
        columns=[apply(prefix,unit(i),-1) for i in range(36)]
        for dst,src,coefficient in shears:
            u=apply(prefix,unit(dst),-1,inverse=True)
            v=[2*coefficient*column[src] for column in columns]
            assert not dot(u,v) and apply(prefix,u,-1)==unit(dst)
            factors.append((clock,dst,src,u,v))
    assert len(factors)==38 and [p[0] for p in factors[:2]+factors[-2:]]==[43,43,4691,4691]
    for i in range(36):
        x=unit(i)
        for _,_,_,u,v in factors:
            x=add(x,u,dot(v,x))
        assert x==[-v for v in unit(i)]
        assert apply(tape,unit(i),1)==unit(i)
        assert apply(tape,unit(i),-1)==[-v for v in unit(i)]
    from itertools import combinations
    cases=[p for p in combinations(range(38),4) if p[0]<2 and p[-1]>=36]
    assert len(cases)==2381
    proper=[r for r in price["records"] if r["hosts"]!=[1,17]]
    assert len(proper)==152 and all(r["rank"]==r["retained_QUERY"]+2*(r["hosts"][1]-r["hosts"][0]+1)
                                   for r in proper)
    prime=65521
    assert all(prime%d for d in range(2,256))
    def mod(v):
        assert all(x.denominator%prime for x in v)
        return [x.numerator*pow(x.denominator,-1,prime)%prime for x in v]
    def minus_add(a,b,c):
        return [(x+c*y)%prime for x,y in zip(a,b,strict=True)]
    def modrank(rows):
        piv={}
        for v in rows:
            r=v.copy()
            for k,p in sorted(piv.items()):
                if r[k]:
                    r=minus_add(r,p,-r[k])
            k=next((j for j,x in enumerate(r) if x),None)
            if k is not None:
                m=pow(r[k],-1,prime)
                piv[k]=[(x*m)%prime for x in r]
        return sorted(piv)
    mf=[(mod(u),mod(v)) for _,_,_,u,v in factors]
    records=[]
    capped=False
    try:
        for case in cases:
            last=case[-1]
            us,vs=[],[]
            for i in case:
                u,v=mf[i]
                for j in range(i+1,last):
                    if j in case:
                        continue
                    a,b=mf[j]
                    u=minus_add(u,a,dot(b,u)%prime)
                    v=minus_add(v,b,-dot(v,a)%prime)
                assert not dot(u,v)%prime
                us.append(u)
                vs.append(v)
            up,vp=modrank(us),modrank(vs)
            out={"case":case,"image_pivots":up,"covector_pivots":vp,"rank":4}
            if min(len(up),len(vp))<4:
                transported=[]
                for i in case:
                    u,v=factors[i][3:]
                    for j in range(i+1,last):
                        if j in case:
                            continue
                        _,_,_,a,b=factors[j]
                        u=add(u,a,dot(b,u))
                        v=add(v,b,-dot(v,a))
                    assert not dot(u,v)
                    transported.append((u,v))
                cols=[]
                for j in range(36):
                    base=unit(j)
                    val=base
                    for u,v in transported:
                        val=add(val,u,dot(v,val))
                    cols.append(add(val,base,-1))
                out["exact_fallback_rank"]=out["rank"]=len(rank(cols))
                if out["rank"]<4:
                    out["factors"]=transported
            records.append(out)
    except TimeoutError:
        capped=True
    finally:
        alarm(0)
    print(dumps({"pins":pins,"factors":len(factors),"old_endpoint":"-I",
                 "upper_gross_with_one_saved_leg":credit,"case_cap":2381,
                 "runner_cap_seconds":45,"modulus":prime,"records":records,
                 "capped":capped,"unvisited":len(cases)-len(records),
                 "survivors":[r["case"] for r in records if r["rank"]<4]},
                indent=2,sort_keys=True,default=str))
    if capped:
        raise SystemExit(2)


if __name__=="__main__":
    main()
