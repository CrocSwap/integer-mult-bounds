"""Check singleton prefix, suffix and unit pairing on exactly 95 frozen virtual cuts."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from math import isqrt
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT=Path(__file__).resolve().parent
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
PRICE="c108a061c6c03306a99a6fbafe919208954a7479ae28fb8a8fbf45d9832e6144"
WORD="4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PAYLOAD="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PRIME=65537
ENGINES={"engines/exact_six.py":"5bffcbbbdc5b0622e29fbc778540cc240b41e7d252e3e5c68d708d48808fcb5a",
         "engines/rolling_exterior.py":"ffc6dfa01554974f2b913b65c39230d3a7f7b6c06da1c940617b7938afe2b9c7"}


def unique(pairs):
    result=dict(pairs)
    if len(result)!=len(pairs):
        raise ValueError("Duplicate JSON key")
    return result


def raw(path,pin):
    value=path.read_bytes()
    if sha256(value).hexdigest()!=pin:
        raise ValueError(f"Changed input {path.name}")
    return value


def read(path,pin,word=False):
    value=raw(path,pin)
    if word:
        value=decompress(value)
        assert sha256(value).hexdigest()==PAYLOAD
    return loads(value,object_pairs_hook=unique)


@cache
def coef(s):
    q=Fraction(s)
    if not q.denominator%PRIME:
        raise ValueError("Nonunit native denominator")
    assert q
    return q.numerator*pow(q.denominator,-1,PRIME)%PRIME,q.denominator


def add(dst,src,k):
    for j,v in src.items():
        w=(dst.get(j,0)+k*v)%PRIME
        if w:
            dst[j]=w
        else:
            dst.pop(j,None)


def scale(v,k):
    return {j:w for j,a in v.items() if (w:=a*k%PRIME)}


def apply(event,state,back,denoms):
    op,d,*args=event
    if op in ("INIT","CLEAR"):
        state[d]={}
    elif op in ("ADD","COPY","SCALE"):
        factor,denominator=coef(args[-2])
        denoms.add(denominator)
        if op=="SCALE":
            if state[d]:
                state[d]=scale(state[d],factor)
        else:
            s=args[0]
            assert s!=d
            if back:
                add(state[s],state[d],factor)
                if op=="COPY":
                    state[d]={}
            else:
                if op=="COPY":
                    assert not state[d]
                add(state[d],state[s],factor)
    else:
        assert op=="MOVE"


def trace(word,requests,deadline):
    n=word["public"]
    program=word["program"]
    size=n+word["owned_fields"]
    denoms=set()
    state=[{} for _ in range(size)]
    for t in range(max(requests),-1,-1):
        if t%128==0 and monotonic()>=deadline:
            raise TimeoutError("backward prefix covectors")
        if t<len(program):
            apply(program[t],state,True,denoms)
        if t in requests:
            r=requests[t]
            add(state[r],{t:1},1)
    assert not any(state[n:])
    prefix={t:{} for t in requests}
    for j,v in enumerate(state[:n]):
        for t,x in v.items():
            prefix[t][j]=x

    state=[{} for _ in range(size)]
    for t,event in enumerate(program):
        if t%128==0 and monotonic()>=deadline:
            raise TimeoutError("forward suffix impulses")
        if t in requests:
            r=requests[t]
            add(state[r],{t:1},1)
        apply(event,state,False,denoms)
    assert not any(state[n:])
    suffix={t:{} for t in requests}
    for j,v in enumerate(state[:n]):
        for t,x in v.items():
            suffix[t][j]=x
    return prefix,suffix,sorted(denoms)


def disposition(p,s,cohort):
    p_bad=next(((j,p[j]) for j in sorted(p) if j not in cohort),None)
    s_bad=next(((j,s[j]) for j in sorted(s) if j not in cohort),None)
    dot=sum(v*s.get(j,0) for j,v in p.items())%PRIME
    status=("exterior_on_both" if p_bad and s_bad else "prefix_exterior" if p_bad else "suffix_exterior"
            if s_bad else "unit_dot_mismatch" if dot!=1 else "needs_exact")
    return dict(status=status,prefix_exterior=p_bad,suffix_exterior=s_bad,dot_mod_prime=dot,
                prefix_nnz_mod_prime=len(p),suffix_nnz_mod_prime=len(s))


def controls():
    assert all(PRIME%d for d in range(2,isqrt(PRIME)+1))
    assert disposition({0:1},{0:1},{0})["status"]=="needs_exact"
    assert disposition({1:1},{0:1},{0})["status"]=="prefix_exterior"
    assert disposition({0:1},{1:1},{0})["status"]=="suffix_exterior"
    assert disposition({0:1},{0:2},{0})["status"]=="unit_dot_mismatch"
    toy={"public":2,"owned_fields":0,"program":[["ADD",0,1,"-3/2",1],["MOVE",0,1,3,False],
           ["SCALE",0,"2/5",3]]}
    a,b,_=trace(toy,{1:0},float("inf"))
    assert a[1]=={0:1,1:coef("-3/2")[0]} and b[1]=={0:coef("2/5")[0]}
    try:
        coef("1/65537")
    except ValueError:
        pass
    else:
        raise AssertionError("Nonunit denominator accepted")
    return ["singleton_unit","prefix_exterior","suffix_exterior","dot_mismatch",
            "signed_prefix_suffix_virtual_MOVE","nonunit_denominator_rejected"]


def check_geometry(word,keys):
    assert (word["public"],word["owned_fields"],len(word["program"]))==(1501,68,76466)
    assert len(keys)==95
    cases={}
    for record in keys:
        t,r,m=record["key"]
        assert t not in cases and len(record["midpoints"])==3
        cases[t]=r
        op,role,a,c,owned=word["program"][t]
        assert op=="MOVE" and role==r and owned is False
        assert len(word["frames"][a])==m-1 and len(word["frames"][c])==m+1 and m in (4,5)
    return cases


def exact_run(word,price,modular,deadline,results):
    for p,pin in ENGINES.items():
        raw(ROOT/p,pin)
    e=run_path(str(ROOT/"engines/exact_six.py"))
    selected=modular["exact_selected"]
    assert len(selected)<=4 and not modular["unvisited"] and modular["price_sha256"]==PRICE
    shape=[dict(key=[t,m],public=[r]) for t,r,m in selected]
    cohort=set(price["endpoint_cohort"])
    if not selected:
        return selected
    for key,(p,s) in zip(selected,e["trace"](word,shape,deadline),strict=True):
        t,r,m=key
        assert len(p)==len(s)==1
        p,s=p[0],s[0]
        outside_p=sorted(p.keys()-cohort)
        outside_s=sorted(s.keys()-cohort)
        dot=e["dot"](p,s)
        live=not outside_p and not outside_s and dot==1
        row=dict(key=key,prefix_exterior=outside_p[:1],suffix_exterior=outside_s[:1],dot=str(dot),
                 status="exact_unit_pair" if live else "exact_excluded")
        if live:
            w={"a":{r:Fraction(1)},"b":{r:Fraction(1)},"c":p,"d":s}
            row["witness"]={k:{j:str(v) for j,v in x.items()} for k,x in w.items()}
            row["coefficient_gate"]=e["physical_screen"](w,[r])
        results.append(row)
    return selected


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument("--price",type=Path)
    p.add_argument("--word",type=Path)
    p.add_argument("--modular",type=Path)
    p.add_argument("--modular-sha")
    p.add_argument("--controls-only",action="store_true")
    a=p.parse_args()
    assert __debug__
    if a.controls_only:
        print(dumps(controls()))
        return
    assert a.price and a.word and bool(a.modular)==bool(a.modular_sha)
    exact=bool(a.modular)
    cap=35 if exact else 20
    limit=4 if exact else 95
    def stop(*_):
        raise TimeoutError(f"hard {cap}-second cap")
    checks,results,keys,denoms=[],[],[],[]
    timeout=None
    signal(SIGALRM,stop)
    alarm(cap)
    deadline=monotonic()+cap-2
    try:
        checks=controls()
        price=read(a.price,PRICE)
        assert price["head"]==HEAD and price["word_sha256"]==WORD and price["case_cap"]==95
        word=read(a.word,WORD,True)
        requests=check_geometry(word,price["keys"])
        keys=[r["key"] for r in price["keys"]]
        assert set(requests.values())<=set(price["endpoint_cohort"])
        if exact:
            modular=read(a.modular,a.modular_sha)
            keys=modular["exact_selected"]
            exact_run(word,price,modular,deadline,results)
        else:
            a_rows,b_rows,denoms=trace(word,requests,deadline)
            for key in keys:
                if monotonic()>=deadline:
                    raise TimeoutError("bounded singleton case sweep")
                t,r,m=key
                results.append(dict(key=key,**disposition(a_rows[t],b_rows[t],set(price["endpoint_cohort"]))))
    except TimeoutError as error:
        timeout=str(error)
    finally:
        alarm(0)
    unresolved=[r["key"] for r in results if r["status"]=="needs_exact"]
    if not exact:
        chosen={tuple(r["key"]):r for r in price["keys"]}
        unresolved.sort(key=lambda key:(not any(x["existing_empty_charts"] for x in chosen[tuple(key)]["midpoints"]),key))
    print(dumps(dict(head=HEAD,price_sha256=PRICE,word_sha256=WORD,prime=PRIME,
        mode="exact" if exact else "modular",case_cap=limit,runner_seconds_cap=cap,
        controls=checks,counts=dict(Counter(r["status"] for r in results)),results=results,
        unvisited=keys[len(results):],exact_selected=unresolved[:4],unresolved=unresolved,
        denominator_units=denoms,timeout=timeout),indent=2,sort_keys=True))
    if timeout:
        raise SystemExit(2)


if __name__=="__main__":
    main()
