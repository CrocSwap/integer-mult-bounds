"""Exact reverse chronology and signed covectors for the one immediate loan."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal
from time import monotonic

ROOT=Path(__file__).resolve().parent
PINS={
    "inputs/R145-PLAN.md":"12a040d21c719ac7573a423b27876a720b55a65dee074ebfab3539c1b29ea7f5",
    "inputs/R137-PRICE.json":"1e8270d9a48728327f7eab9610a272fbb8ef09518dc4ddc5ceb573be00ae2beb",
    "inputs/R137-RESULT.json":"a109deda97d3b4f5ceb52814a50186035ea44ac1bdaf47281f564dcc2da239db",
    "inputs/R141-REVERSE.json":"508b66c75a45f43b7d231071787d5737feda0505f9d8e633306b19c3423ebad9",
    "inputs/reverse_covectors.py":"b398327e066ec30935bac400666be00d0d661331cad15a6247d695de24a4045f",
    "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER="07a76c5e2738882c0cb322278e56f6cae3c9885d"
RAW="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
KEY={"owner":1540,"anchor":45647,"carrier":988,"carrier_move":36647,"charts":[260,1091]}
EVENTS,SECONDS=76466,20
ZERO,ONE=Q(0),Q(1)


def unique(pairs):
    x=dict(pairs)
    if len(x)!=len(pairs):
        raise ValueError("duplicate JSON key")
    return x


def check(root,name,digest):
    data=(root/name).read_bytes()
    if sha256(data).hexdigest()!=digest:
        raise ValueError("changed dependency "+name)
    return data


def axpy(dst,src,multiplier):
    for key,v in src.items():
        x=dst.get(key,ZERO)+multiplier*v
        if x:
            dst[key]=x
        else:
            dst.pop(key,None)


def evaluate(vector,covector):
    return sum((v*vector.get(k,ZERO) for k,v in covector.items()),ZERO)


def solve(target,donors):
    for x,v in sorted(target.items()):
        if not any(x in row for row in donors.values()):
            return dict(decision="outside donor span",dual={x:"1"},value=str(v))
    pivots=[]
    for role,row in donors.items():
        r=row.copy()
        coeff={role:ONE}
        for pivot,old,expansion in pivots:
            c=r.get(pivot,ZERO)
            if c:
                axpy(r,old,-c)
                axpy(coeff,expansion,-c)
        if not r:
            continue
        p=min(r)
        v=r[p]
        pivots.append((p,{k:x/v for k,x in r.items()},{k:x/v for k,x in coeff.items()}))
    remaining=target.copy()
    coeff={}
    for pivot,row,expansion in pivots:
        c=remaining.get(pivot,ZERO)
        if c:
            axpy(remaining,row,-c)
            axpy(coeff,expansion,c)
    if not remaining:
        actual={}
        for role,v in coeff.items():
            axpy(actual,donors[role],v)
        assert actual==target
        return dict(decision="supported",coefficients={r:str(v) for r,v in coeff.items()})
    q=min(remaining)
    dual={q:ONE}
    for pivot,row,_ in reversed(pivots):
        axpy(dual,{pivot:ONE},-evaluate(row,dual))
    assert all(evaluate(r,dual)==0 for r in donors.values())
    assert evaluate(target,dual)==remaining[q]
    return dict(decision="outside donor span",dual={i:str(v) for i,v in dual.items()},value=str(remaining[q]))


def occurrences(event):
    return event[1:3] if event[0] in ("ADD","COPY") else event[1:2]


def reverse_bank(word,deadline):
    tape=word["program"]
    h,m,f,u=(KEY[k] for k in ("owner","anchor","carrier","carrier_move"))
    a,b=KEY["charts"]
    n=word["public"]
    assert tape[u]==["MOVE",f,a,b,False] and tape[m]==["MOVE",h,a,b,True]
    assert f<n<=h
    assert h in occurrences(tape[m+1]) and f in occurrences(tape[u+1])
    assert all(h not in occurrences(tape[t]) for t in range(u,m))
    last=next(t for t in range(u-1,-1,-1) if h in occurrences(tape[t]))
    assert tape[m+1]==["ADD",756,h,"1",b]
    assert tape[u+1]==["ADD",862,f,"1",b]
    spans=[]
    for chart in (a,b):
        space={0}
        for vector in word["frames"][chart]:
            assert vector not in space
            space|={x^vector for x in space}
        spans.append(space)
    assert spans[0]<spans[1] and len(spans[1])==2*len(spans[0])

    state=word["final"]+[None]*word["owned_fields"]
    for t in range(len(tape)-1,u-1,-1):
        if t%128==0 and monotonic()>=deadline:
            raise TimeoutError("reverse chart cap")
        op,role,*args=tape[t]
        if op=="MOVE":
            before,after,owned=args
            assert state[role]==after and owned==(role>=n)
            state[role]=before
        elif op=="INIT":
            assert state[role]==args[0] and role>=n
            state[role]=None
        elif op=="CLEAR":
            assert state[role] is None and role>=n
            state[role]=args[0]
        else:
            assert op in ("ADD","COPY","SCALE") and all(state[r]==args[-1] for r in occurrences(tape[t]))
    assert state[h]==state[f]==a
    donors=[r for r,chart in enumerate(state) if chart==b and r not in (h,f)]
    return donors,[[t,tape[t]] for t in (last,u+1,m+1)]


def controls():
    assert solve({0:Q(3),1:Q(-2)},{5:{0:ONE},7:{1:ONE}})=={
        "decision":"supported","coefficients":{5:"3",7:"-2"}}
    assert solve({0:ONE,1:ONE,2:Q(3)},{5:{0:ONE,2:ONE},7:{1:ONE,2:ONE}})=={
        "decision":"outside donor span","dual":{2:"1",1:"-1",0:"-1"},"value":"1"}
    return ["exact signed recovery","exact separating dual with no absent coordinate"]


def main():
    assert __debug__
    cli=ArgumentParser(description=__doc__)
    cli.add_argument("--root",type=Path,default=ROOT)
    cli.add_argument("--price-sha")
    cli.add_argument("--controls-only",action="store_true")
    args=cli.parse_args()
    tests=controls()
    if args.controls_only:
        print(dumps(tests))
        return
    if not args.price_sha:
        cli.error("requires frozen R145 price SHA-256")
    pins={"inputs/R145-PRICE.json":args.price_sha}|PINS
    raw={name:check(args.root,name,digest) for name,digest in pins.items()}
    old=loads(raw["inputs/R137-PRICE.json"],object_pairs_hook=unique)
    price=loads(raw["inputs/R145-PRICE.json"],object_pairs_hook=unique)
    frozen=loads(raw["inputs/R141-REVERSE.json"],object_pairs_hook=unique)
    prior=loads(raw["inputs/R137-RESULT.json"],object_pairs_hook=unique)
    assert all((p["head"],p["caller"])==(HEAD,CALLER) for p in (old,price,prior))
    assert not frozen["eligible"] and [45647,1,1] in frozen["counts"]
    assert old["one"]["1"]["paid_delta"]=={"1":-17} and old["one"]["1"]["gross"]==["17","17"]
    assert Q(old["one"]["1"]["complete_probe"][0])>0
    engine=run_path(str(args.root/"inputs/reverse_covectors.py"))

    def stop(*_):
        raise TimeoutError("20-second hard cap")
    signal(SIGALRM,stop)
    alarm(SECONDS)
    deadline=monotonic()+SECONDS-1
    try:
        blob=decompress(raw["inputs/7334-WORD.json.gz"])
        assert sha256(blob).hexdigest()==RAW
        word=loads(blob,object_pairs_hook=unique)
        tape=word["program"]
        assert len(tape)==EVENTS and word["public"]==1501 and word["owned_fields"]==68
        donors,contacts=reverse_bank(word,deadline)
        carrier=KEY["carrier"]
        rows=engine["prefix_rows"](tape,KEY["carrier_move"],[carrier,*donors],deadline)
        assert all(k<word["public"] for row in rows.values() for k in row)
        ans=solve(rows[carrier],{r:rows[r] for r in donors})
        ans|=dict(head=HEAD,caller=CALLER,key=KEY,controls=tests,contacts=contacts,
                  caps={"events":EVENTS,"keys":1,"seconds":SECONDS},pins=pins,
                  donor_public=[r for r in donors if r<word["public"]],
                  donor_owned=[r for r in donors if r>=word["public"]],
                  rows={r:{k:str(v) for k,v in row.items()} for r,row in rows.items()},unresolved=[])
    finally:
        alarm(0)
    print(dumps(ans,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
