"""Independently reconstruct the signed role-532 aggregate and separators."""
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/PRICE.json": "d9074aad58d3ffdad995ba68b2ffa541ae2b7df833b757d8e1a9767118140f39",
    "inputs/PLAN.md": "fe812a887136869d9962d37822ac875dc15ce45453261585885199b0bc60b22f",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
MOVER, MOVES = 532, [41176,41178,44611]
ADDS = {41177:["ADD",532,363,"1",744], 41179:["ADD",532,452,"-2",746]}
BANKS = {44611:3,44612:207}
MAX_EVENTS = 76466


def unique(items):
    obj=dict(items)
    if len(obj)!=len(items):
        raise ValueError("duplicate JSON key")
    return obj


def checked(path):
    raw=(ROOT/path).read_bytes()
    if sha256(raw).hexdigest()!=PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return raw


@cache
def scalar(value):
    return Q(value)


def axpy(row, other, q):
    if q:
        for j,v in other.items():
            new=row.get(j,0)+q*v
            if new:
                row[j]=new
            else:
                row.pop(j,None)


def dot(a,b):
    return sum(v*b.get(j,0) for j,v in a.items())


def stop(*_):
    raise TimeoutError("20-second gate")


def time_check(t, deadline):
    if t%128==0 and monotonic()>=deadline:
        stop()


def backward_add(weights,event):
    op,d,*args=event
    if op in ("INIT","CLEAR"):
        weights.pop(d,None)
    elif op=="SCALE" and d in weights:
        weights[d]*=scalar(args[0])
    elif op in ("ADD","COPY") and d in weights:
        src,k,_=args
        axpy(weights,{src:weights[d]},scalar(k))
        if op=="COPY":
            weights.pop(d)


def inventory_and_aggregate(word, deadline):
    program=word["program"]
    n,owned=word["public"],word["owned_fields"]
    state=word["final"][:]+[None]*owned
    banks, mover_events, aggregate={},[],{}
    for t in range(len(program),-1,-1):
        time_check(t,deadline)
        if t in BANKS:
            chart=BANKS[t]
            public=[r for r,c in enumerate(state[:n]) if c==chart and r!=MOVER]
            live_owned=[r for r,c in enumerate(state[n:],n) if c==chart]
            assert state[MOVER]==(746 if t==44611 else 207)
            banks[t]={"chart":chart,"public":public,"owned_excluded":live_owned}
        if t in ADDS:
            _,_,source,coefficient,chart=ADDS[t]
            assert program[t]==ADDS[t] and state[source]==state[MOVER]==chart and source<n
            axpy(aggregate,{source:Q(1)},scalar(coefficient))
        if not t:
            break
        event=program[t-1]
        op,d,*args=event
        touched=(d,args[0]) if op in ("ADD","COPY") else (d,)
        if MOVES[0]<=t-1<=MOVES[-1] and MOVER in touched:
            mover_events.append([t-1,event])
        if op=="MOVE":
            before,after,flag=args
            assert state[d]==after and flag==(d>=n)
            state[d]=before
        elif op=="INIT":
            assert d>=n and state[d]==args[0]
            state[d]=None
        elif op=="CLEAR":
            assert d>=n and state[d] is None
            state[d]=args[0]
        else:
            assert op in ("ADD","COPY","SCALE") and state[d]==args[-1]
            if op in ("ADD","COPY"):
                assert state[args[0]]==state[d] and args[0]!=d
            if op=="COPY":
                assert d>=n
        if aggregate:
            backward_add(aggregate,event)
    assert state==word["initial"]+[None]*owned
    assert all(r<n for r in aggregate)
    old_moves=dict(zip(MOVES,(["MOVE",MOVER,a,b,False]
                             for a,b in zip((3,744,746),(744,746,207),strict=True)),strict=True))
    assert dict(mover_events)==old_moves|ADDS
    return banks,aggregate,mover_events[::-1]


def forward_axes(word,banks,axes,deadline):
    size=word["public"]+word["owned_fields"]
    rows=[{} for _ in range(size)]
    for axis in axes:
        rows[axis][axis]=Q(1)
    absence={}
    for t,event in enumerate(word["program"]):
        time_check(t,deadline)
        if t in banks:
            presence={j for role in banks[t]["public"] for j in rows[role]}
            absence[t]=sorted(set(axes)-presence)
        if t==max(banks):
            break
        op,d,*args=event
        if op in ("INIT","CLEAR"):
            rows[d]={}
        elif op=="ADD":
            src,k,_=args
            axpy(rows[d],rows[src],scalar(k))
        elif op=="COPY":
            src,k,_=args
            rows[d]={j:scalar(k)*v for j,v in rows[src].items()}
        elif op=="SCALE" and rows[d]:
            rows[d]={j:scalar(args[0])*v for j,v in rows[d].items()}
    return absence


def reverse_rows(word, cut, roles, deadline):
    size=word["public"]+word["owned_fields"]
    values=[{} for _ in range(size)]
    for role in roles:
        values[role][role]=Q(1)
    for t in range(cut-1,-1,-1):
        time_check(t,deadline)
        op,d,*args=word["program"][t]
        if op in ("INIT","CLEAR"):
            values[d]={}
        elif op=="SCALE" and values[d]:
            values[d]={j:scalar(args[0])*v for j,v in values[d].items()}
        elif op in ("ADD","COPY"):
            src,k,_=args
            axpy(values[src],values[d],scalar(k))
            if op=="COPY":
                values[d]={}
    out={r:{} for r in roles}
    for axis,row in enumerate(values):
        if axis>=word["public"]:
            assert not row
        for role,value in row.items():
            out[role][axis]=value
    return out


def eliminate(rows,target,deadline):
    basis={}
    for role,vector in rows.items():
        if monotonic()>=deadline:
            stop()
        work,weights=vector.copy(),{role:Q(1)}
        for pivot,(row,w) in sorted(basis.items()):
            scale=-work.get(pivot,0)
            axpy(work,row,scale)
            axpy(weights,w,scale)
        if work:
            pivot=min(work)
            q=work[pivot]
            basis[pivot]=({j:v/q for j,v in work.items()},{j:v/q for j,v in weights.items()})
    residual,weights=target.copy(),{}
    for pivot,(row,w) in sorted(basis.items()):
        scale=residual.get(pivot,0)
        axpy(residual,row,-scale)
        axpy(weights,w,scale)
    if not residual:
        rebuilt={}
        for role,q in weights.items():
            axpy(rebuilt,rows[role],q)
        assert rebuilt==target
        return len(basis),weights,None
    dual={min(residual):Q(1)}
    for pivot,(row,_) in reversed(sorted(basis.items())):
        axpy(dual,{pivot:Q(1)},-dot(dual,row))
    assert all(dot(dual,row)==0 for row in rows.values()) and dot(dual,target)!=0
    return len(basis),None,dual


def controls():
    src={4:{1:Q(1),2:Q(1)},5:{2:Q(1)}}
    budget=monotonic()+1
    assert eliminate(src,{1:Q(1)},budget)==(2,{4:Q(1),5:Q(-1)},None)
    assert eliminate(src,{1:Q(1),7:Q(1)},budget)==(2,None,{7:Q(1)})
    weights={2:Q(-2),1:Q(1)}
    backward_add(weights,["ADD",2,3,"1/2",6])
    assert weights=={1:Q(1),2:Q(-2),3:Q(-1)}
    return ["positive exact signed aggregate", "perturbed exterior coordinate", "backward source sign"]


def formatted(vector):
    return {j:str(v) for j,v in sorted(vector.items())} if vector is not None else None


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(20)
    deadline=monotonic()+18
    tests=controls()
    price=loads(checked("inputs/PRICE.json"),object_pairs_hook=unique)
    checked("inputs/PLAN.md")
    assert (price["head"],price["caller"],price["word_sha256"])==(HEAD,CALLER,PINS["inputs/7334-WORD.json.gz"])
    row,=[r for r in price["candidates"] if r["role"]==MOVER and r["clocks"]==MOVES]
    assert row["charts"]==[3,744,746,207] and dict(row["contacts"])==ADDS
    raw=decompress(checked("inputs/7334-WORD.json.gz"))
    assert sha256(raw).hexdigest()==PAYLOAD
    word=loads(raw,object_pairs_hook=unique)
    assert len(word["program"])==MAX_EVENTS and word["public"]==1501
    assert [len(word["frames"][c]) for c in row["charts"]]==[0,3,6,8]
    banks,aggregate,events=inventory_and_aggregate(word,deadline)
    assert aggregate and len(banks)==2
    tested_axes=sorted(aggregate)[:16]
    absence=forward_axes(word,banks,tested_axes,deadline)
    results=[]
    for cut,bank in sorted(banks.items()):
        if absence[cut]:
            rank,coefficients,dual=None,None,{absence[cut][0]:Q(1)}
            method="exact unit-impulse exterior coordinate"
        else:
            rows=reverse_rows(word,cut,bank["public"],deadline)
            rank,coefficients,dual=eliminate(rows,aggregate,deadline)
            method="exact backward sparse row elimination"
        results.append(dict(bank,cut=cut,method=method,bank_rank=rank,
            coefficients=formatted(coefficients),dual=formatted(dual),
            dual_on_aggregate=str(dot(dual,aggregate)) if dual is not None else None,
            status="excluded" if dual is not None else "exact support"))
    alarm(0)
    print(dumps(dict(head=HEAD,caller=CALLER,pins=PINS,controls=tests,mover=MOVER,
        mover_events=events,aggregate=formatted(aggregate),tested_axes=tested_axes,
        results=results,unresolved=[],cap_events=MAX_EVENTS,cap_seconds=20,
        scope="One exact mover window and two fixed public endpoint banks."),
        indent=2,sort_keys=True))


if __name__=="__main__":
    main()
