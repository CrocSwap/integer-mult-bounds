"""Try fusing one first-J and one final-J relative rank-one shear."""
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal

ROOT=Path(__file__).resolve().parent


def dot(a,b):
    return sum(x*y for x,y in zip(a,b,strict=True) if x and y)


def add(a,b,coef):
    return [x+coef*y for x,y in zip(a,b,strict=True)]


def stop(*_):
    raise TimeoutError("40-second triple recombination cap")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(40)
    pins={}
    for line in (ROOT/"PINS").read_text().splitlines():
        h,name=line.split()
        assert name not in pins and sha256((ROOT/name).read_bytes()).hexdigest()==h
        pins[name]=h
    f=run_path(str(ROOT/"forward.py"))
    rank=run_path(str(ROOT/"rank_gate.py"))["rank"]
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
    cases=[p for p in combinations(range(38),3) if p[0]<2 and p[-1]>=36]
    assert len(cases)==140
    proper=[r for r in price["records"] if r["hosts"]!=[1,17]]
    assert len(proper)==152
    assert all(r["rank"]==r["retained_QUERY"]+2*(r["hosts"][1]-r["hosts"][0]+1)
               for r in proper)
    records=[]
    for case in cases:
        transported=[]
        last=case[-1]
        for i in case:
            u,v=factors[i][3:]
            for j in range(i+1,last):
                if j in case:
                    continue
                x,y=factors[j][3:]
                u=add(u,x,dot(y,u))
                v=add(v,y,-dot(v,x))
            assert not dot(u,v)
            transported.append((u,v))
        cols=[]
        for j in range(36):
            basis=unit(j)
            val=basis
            for u,v in transported:
                val=add(val,u,dot(v,val))
            cols.append(add(val,basis,-1))
        piv=rank(cols)
        item={"case":case,"rank":len(piv),"pivots":piv,
              "keys":[factors[i][:3] for i in case]}
        if len(piv)<=2:
            item["transported_factors"]=transported
            item["delta"]=[[i,j,str(x)] for j,v in enumerate(cols) for i,x in enumerate(v) if x]
        records.append(item)
    alarm(0)
    print(dumps({"pins":pins,"factors":len(factors),"old_endpoint":"-I",
                 "upper_gross_with_one_saved_leg":credit,"triple_cap":140,
                 "runner_cap_seconds":40,"records":records,
                 "survivors":[r["case"] for r in records if r["rank"]<=2]},
                indent=2,sort_keys=True,default=str))


if __name__=="__main__":
    main()
