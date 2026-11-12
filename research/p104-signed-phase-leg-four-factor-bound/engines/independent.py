"""Exact rational rank of selected four-factor words crossing both extreme hosts."""
from collections import Counter
from fractions import Fraction as Q
from functools import reduce
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from math import gcd, lcm
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/R194.json": "49b7dbd3d08c56b16dc43f23bd6f410dde0b98040d922cee6f617786eb474834",
    "inputs/R195.json": "f6091c7c63b21145077808bbdacc61431f641d0da37f9fa648aea4b7ead3b472",
    "inputs/R193.json": "4926019203f511866cf327128ebcd291561ebc03b6d77a6816361d7128d4664c",
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
N, SECONDS = 36,45


def unique(items):
    obj = dict(items)
    assert len(items) == len(obj)
    return obj


def read(name):
    raw = (ROOT/name).read_bytes()
    assert sha256(raw).hexdigest() == PINS[name], name
    return loads(raw,object_pairs_hook=unique)


def dot(a,b):
    return sum(x*y for x,y in zip(a,b,strict=True) if x and y)


def add(a,b,z):
    return [x+z*y for x,y in zip(a,b,strict=True)] if z else a


def unit(i):
    return [Q(i==j) for j in range(N)]


def factors(tape):
    # Maintain the q=-1 prefix rows and its inverse columns independently.
    g, inv = [unit(i) for i in range(N)], [unit(i) for i in range(N)]
    result,labels = [],[]
    for t,e in enumerate(tape):
        if e[0]=="B":
            continue
        if e[0]=="J":
            _,stage,(x,y,u,v),_ = e
            legs = [(y,x,1),(u,v,-1)]
        elif e[:2]==["A","QUERY"]:
            _,_,d,s,exp = e
            assert exp==-1
            stage,legs = 0,[(d,s,1)]
        else:
            op,d = e[1:3]
            if op=="ADD":
                s,k = e[3],Q(e[4])
                g[d],inv[s] = add(g[d],g[s],k),add(inv[s],inv[d],-k)
            elif op=="SCALE":
                k = Q(e[3])
                g[d],inv[d] = [k*x for x in g[d]],[x/k for x in inv[d]]
            elif op=="SWAP":
                s = e[3]
                g[d],g[s] = g[s],g[d]
                inv[d],inv[s] = inv[s],inv[d]
            else:
                assert op in ("LAMBDA","IDLE_ONE")
            continue
        for n,(d,s,sgn) in enumerate(legs):
            u,v = [2*sgn*x for x in inv[d]],g[s].copy()
            assert not dot(u,v)
            result.append((u,v))
            labels.append([t,stage,n,d,s,sgn])
            g[d],inv[s] = add(g[d],g[s],-sgn),add(inv[s],inv[d],sgn)
    for i in range(N):
        x = unit(i)
        for u,v in result:
            x = add(x,u,dot(v,x))
        assert x == [-a for a in unit(i)]
        assert [dot(row,inv[i]) for row in g] == unit(i)
    return result,labels


def packed(factors):
    out = []
    for u,v in factors:
        du,dv = lcm(*(x.denominator for x in u)),lcm(*(x.denominator for x in v))
        out.append(([int(x*du) for x in u],[int(y*dv) for y in v],du*dv))
    return out


def shift_integer(w, u, v, d):
    z = dot(v,w)
    if not z:
        return w
    w = [d*x+z*y for x,y in zip(w,u,strict=True)]
    g = reduce(gcd,w)
    assert g
    return [x//g for x in w] if g!=1 else w


def integer_transports(core, chosen):
    output = []
    chosen_set = set(chosen)
    for i in chosen:
        u,v,_ = core[i]
        for j in range(i+1,chosen[-1]):
            if j not in chosen_set:
                x,y,d = core[j]
                u = shift_integer(u,x,y,d)
                v = shift_integer(v,y,[-a for a in x],d)
        assert not dot(u,v)
        output.append((u,v))
    return output


def pivot_columns(rows):
    work = [row.copy() for row in rows]
    selected = []
    for j in range(len(work[0])):
        i = len(selected)
        k = next((k for k in range(i,len(work)) if work[k][j]),None)
        if k is None:
            continue
        work[i],work[k] = work[k],work[i]
        a = work[i][j]
        for k in range(i+1,len(work)):
            b = work[k][j]
            if b:
                work[k] = [a*y-b*x for x,y in zip(work[i],work[k],strict=True)]
        selected.append(j)
        if len(selected)==len(work):
            break
    return selected


def det(m):
    if len(m)==1:
        return m[0][0]
    return sum((-1)**i * v * det([row[:i]+row[i+1:] for row in m[1:]])
               for i,v in enumerate(m[0]) if v)


def exact_deficient(core, chosen):
    # Replay the product for any case in which the rank-four sufficient test fails.
    shifted = []
    for i in chosen:
        u,v = core[i]
        for j in range(i+1,chosen[-1]):
            if j not in chosen:
                x,y = core[j]
                u,v = add(u,x,dot(y,u)),add(v,y,-dot(v,x))
        shifted.append((u,v))
    columns = []
    for i in range(N):
        e = unit(i)
        x = e
        for u,v in shifted:
            x = add(x,u,dot(v,x))
        columns.append(add(x,e,-1))
    return pivot_columns(columns),shifted


def stop(*_):
    raise TimeoutError("45-second four-factor cap")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(SECONDS)
    r194,r195,r193,c = [read("inputs/"+x+".json") for x in ("R194","R195","R193","CALLER")]
    for old in (r194,r195,r193):
        assert (old["head"],old["caller"]) == (HEAD,CALLER)
    assert r194["factor_count"] == r195["factor_count"] == 38
    assert not r194["survivors"] and not r195["survivors"]
    assert len(r193["records"])==153 and not r193["capped"]
    assert all(x["rank"] == 2*(x["hosts"][1]-x["hosts"][0]+1)+x["retained_QUERY"]
               for x in r193["records"] if x["hosts"]!=[1,17])
    assert len(c["events"])==4783 and c["types"]["A"]["roles"]==N
    original,labels = factors(c["events"])
    assert labels == r194["factor_labels"] == r195["factor_labels"] and len(original)==38
    core = packed(original)
    scope = [s for s in combinations(range(38),4) if s[0]<2 and s[-1]>=36]
    assert len(scope)==2381
    assert pivot_columns([[1,2],[2,4]]) == [0] and pivot_columns([[1,2],[1,3]])==[0,1]
    records,capped = [],False
    try:
        for ids in scope:
            moved = integer_transports(core,ids)
            u,v = [x for x,_ in moved],[y for _,y in moved]
            a,b = pivot_columns(u),pivot_columns(v)
            row = {"factors":ids,"U_pivots":a,"V_pivots":b}
            if len(a)==len(b)==4:
                ud = det([[x[j] for j in a] for x in u])
                vd = det([[x[j] for j in b] for x in v])
                assert ud and vd
                row.update(rank=4,U_minor=ud,V_minor=vd)
            else:
                piv,shifted = exact_deficient(original,ids)
                assert len(piv)<=3
                row.update(rank=len(piv),transported_factors=shifted,product_pivots=piv)
            records.append(row)
    except TimeoutError:
        capped = True
    finally:
        alarm(0)
    assert capped or len(records)==len(scope)
    print(dumps({"head":HEAD,"caller":CALLER,"pins":PINS,"factor_labels":labels,
                 "cap_seconds":SECONDS,"case_cap":len(scope),"capped":capped,
                 "counts":Counter(x["rank"] for x in records),"records":records,
                 "survivors":[x for x in records if x["rank"]<=3],"unvisited":scope[len(records):]},
                 default=str,sort_keys=True,indent=2))
    if capped:
        raise SystemExit(2)


if __name__=="__main__":
    main()
