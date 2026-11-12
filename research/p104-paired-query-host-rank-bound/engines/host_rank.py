"""Unit-body exact modular relative phase defect for an existing Type A J host."""
from fractions import Fraction
from functools import cache
from hashlib import sha256
from itertools import combinations
import json
from math import isqrt
from pathlib import Path
import sys
from time import monotonic

PRIME=65521
DIMENSION=36
PRICE="15b2f25a9fccde7800f7638d3625e5d44e601052f124e09810583fbbd3eaac5a"
CALLER="255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"


def checked(path,pin):
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=pin:
        raise ValueError(f"changed dependency: {path.name}")
    return json.loads(raw)


@cache
def residue(value):
    x=Fraction(value)
    assert x.denominator%PRIME
    return x.numerator*pow(x.denominator,-1,PRIME)%PRIME


def compile_type_a(caller):
    steps, hosts, queries = {}, {}, {}
    a=residue(caller["types"]["A"]["alpha2"])
    assert a==PRIME-1
    for clock, (kind,op,*args) in enumerate(caller["events"]):
        if kind=="J":
            x,y,u,v=args[0]
            assert len({x,y,u,v})==4
            hosts[op]=clock
            steps[clock]=[("ADD",y,x,-1),("ADD",u,v,-a)]
        elif kind=="A":
            d,*p=args
            if op=="QUERY":
                assert (d,*p)==(0,1,-1)
                queries[clock]=True
                steps[clock]=[("ADD",d,p[0],-1)]
            elif op=="ADD":
                steps[clock]=[(op,d,p[0],residue(p[1]))]
            elif op=="SCALE":
                k=residue(p[0])
                assert k
                steps[clock]=[(op,d,d,k)]
            elif op=="SWAP":
                steps[clock]=[(op,d,p[0],0)]
            elif op=="IDLE_ODD":
                steps[clock]=[("SCALE",d,d,-1 if p[1]%2 else 1)]
            else:
                assert op in ("LAMBDA","IDLE_ONE")
        else:
            assert kind=="B"
    return steps,hosts,queries


def basis(j,dimension=DIMENSION):
    return [int(i==j) for i in range(dimension)]


def invert(factors):
    return [(op,d,s,-k if op=="ADD" else pow(k,-1,PRIME) if op=="SCALE" else k)
            for op,d,s,k in reversed(factors)]


def act(factors, v):
    for op,d,s,k in factors:
        if op=="ADD":
            v[d]=(v[d]+k*v[s])%PRIME
        elif op=="SCALE":
            v[d]=v[d]*k%PRIME
        else:
            assert op=="SWAP"
            v[d],v[s]=v[s],v[d]
    return v


def determinant3(rows):
    (a,b,c),(d,e,f),(g,h,i)=rows
    return (a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g))%PRIME


def rank_gate(columns):
    reduced={}
    original={}
    for j, column in enumerate(columns):
        v=column.copy()
        for i, earlier in reduced.items():
            if v[i]:
                v=[(a-v[i]*b)%PRIME for a,b in zip(v,earlier)]
        p=next((i for i,x in enumerate(v) if x),None)
        if p is None:
            continue
        inv=pow(v[p],-1,PRIME)
        reduced[p]=[a*inv%PRIME for a in v]
        original[j]=column
        if len(original)==3:
            rows=list(reduced)
            cols=list(original)
            minor=[[original[c][r] for c in cols] for r in rows]
            witness=determinant3(minor)
            assert witness
            return {"row_keys":rows,"column_keys":cols,"minor":minor,"determinant_mod_prime":witness}
    return None


def solve(steps, q1, q2, host):
    lo,hi=min(q1,q2,host),max(q1,q2,host)
    clocks=range(lo,hi+1)
    original=[f for t in clocks for f in steps.get(t,[])]
    def changed(t):
        return [("ADD",0,1,1)] if t in (q1,q2) else steps.get(t,[])
    in_inverse=invert([f for t in range(lo,host) for f in changed(t)])
    out_inverse=invert([f for t in range(host+1,hi+1) for f in changed(t)])
    plus=[(op,d,s,-k) for op,d,s,k in steps[host]]
    for j in range(DIMENSION):
        v=basis(j)
        required=act(out_inverse,act(original,act(in_inverse,v.copy())))
        baseline=act(plus,v)
        yield [(a-b)%PRIME for a,b in zip(required,baseline)]


def controls():
    old=[("ADD",0,1,-2),("ADD",2,3,2)]
    third=old+[("ADD",4,5,2)]
    def defect(factors):
        return [[(a-b)%PRIME for a,b in zip(act(factors,basis(j,6)),basis(j,6))] for j in range(6)]
    assert rank_gate(defect(old)) is None
    assert rank_gate(defect(third))["determinant_mod_prime"]==PRIME-8
    return ["unmodified two-axis phase defect", "planted third independent signed axis"]


def main():
    root=Path(sys.argv[1])
    price=checked(root/"price/PRICE.json",PRICE)
    caller=checked(root/"price/inputs/7113-CALLER.json",CALLER)
    assert price["head"]==HEAD and all(PRIME%d for d in range(2,isqrt(PRIME)+1))
    assert (caller["stages"],caller["types"]["A"]["roles"],len(caller["types"]["A"]["ports"]))==(17,36,96)
    start=monotonic()
    steps,hosts,queries=compile_type_a(caller)
    keys=[[*a,b] for a in combinations(queries,2) for b in sorted(hosts)]
    assert keys==price["keys"] and len(keys)==102
    checks=controls()
    tested=[]
    for a,b,j in keys:
        if monotonic()-start>=18:
            break
        host=hosts[j]
        witness=rank_gate(solve(steps,a,b,host))
        tested.append(dict(key=[a,b,j],host_clock=host,decision="rank at least three" if witness else "provisional",witness=witness))
    print(json.dumps(dict(head=HEAD, price_sha256=PRICE, caller_sha256=CALLER, field_prime=PRIME,
        phase_values=[1,-1], body="all one", case_cap=102, runner_cap_seconds=18, controls=checks,
        tested=tested, unvisited=keys[len(tested):], survivors=[x["key"] for x in tested if x["witness"] is None]),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
