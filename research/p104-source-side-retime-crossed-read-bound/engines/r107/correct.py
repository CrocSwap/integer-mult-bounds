"""Exact missing source functional and late chart correction at one paid pair."""
from bisect import bisect_left
from collections import defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT=Path(__file__).resolve().parents[1]
PINS={
    "lead/PRICE.json":"526dcf4131c5cfd184047413ccd4a19d9602c42e4e1df034061c5bce453ec476",
    "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/donor_span.py":"4d5306e2c0b7e91c79d22c82e8e760aed2c311979298c558e631975d4d1ae5b1",
}


def checked():
    result={}
    for path,pin in PINS.items():
        raw=(ROOT/path).read_bytes()
        if sha256(raw).hexdigest()!=pin:
            raise ValueError(f"changed dependency {path}")
        result[path]=raw
    return result


def touched(event):
    op,d,*args=event
    return (d,args[0]) if op in ("ADD","COPY") else (d,)


def barrier(event,role):
    op,d,*_=event
    return op!="MOVE" and not (op=="ADD" and d==role)


def chart_at(move_clocks,move_targets,initial,cut):
    i=bisect_left(move_clocks,cut)
    return move_targets[i-1] if i else initial


def hard_cap(*_):
    raise TimeoutError("20 second R107 cap")


def main():
    assert __debug__
    signal(SIGALRM,hard_cap)
    alarm(20)
    deadline=monotonic()+18
    doc=checked()
    price=json.loads(doc["lead/PRICE.json"])
    tape_raw=decompress(doc["inputs/7334-WORD.json.gz"])
    assert sha256(tape_raw).hexdigest()==price["payload_sha256"]
    word=json.loads(tape_raw)
    tape=word["program"]
    f,g,s=price["key"]
    a,b,c=price["charts"]
    old,first=price["old_add"]
    t,second=price["crossed"]
    d,p=first[1],second[1]
    assert (word["public"],len(tape),f,old,t,g,s,d,p)==(1501,76466,44611,44612,44613,46018,532,205,198)
    assert tape[f]==["MOVE",s,a,b,False] and tape[old]==first and tape[t]==second and tape[g]==["MOVE",s,b,c,False]
    assert first[2]==s and second[2]==d and Q(first[3])*Q(second[3])==Q(price["correction"])
    roles={s,d,p}
    log=defaultdict(list)
    for k,e in enumerate(tape):
        if k%128==0 and monotonic()>=deadline:
            raise TimeoutError("literal contact cap")
        for role in touched(e):
            if role in roles:
                log[role].append((k,e))
    assert [(k,e) for k,e in log[s] if f<=k<=g]==[(f,tape[f]),(old,first),(g,tape[g])]
    moves=[(k,e[3]) for k,e in log[p] if e[0]=="MOVE"]
    move_clocks=[k for k,_ in moves]
    move_targets=[c for _,c in moves]
    blocks=[(k,e) for k,e in log[p] if k>t and barrier(e,p)]
    first_barrier=blocks[0] if blocks else None
    late=[]
    for cut in range(price["cuts"][0],price["cuts"][1]+1):
        actual=chart_at(move_clocks,move_targets,word["initial"][p],cut)
        barriers=[(k,e) for k,e in log[d] if old<k<cut and barrier(e,d)]
        assert barriers==[(t,second)]
        state="wrong recipient chart" if actual!=c else "recipient observed or scaled" if first_barrier and first_barrier[0]<cut else "late exact restoration feasible"
        late.append({"cut":cut,"recipient_chart":actual,"status":state})
    assert len(late)==43
    e=run_path(str(ROOT/"inputs/donor_span.py"))
    controls=e["controls"]()
    banks,targets=e["snapshot"](word,{t:{(b,s)}},{old:{s}},deadline)
    all_rows=banks[t,b,s]
    bank={r:row for r,row in all_rows.items() if r<word["public"]}
    target=targets[old,s]
    assert d in bank and p in bank and s not in bank
    adjusted=bank[d].copy()
    e["axpy"](adjusted,target,-Q(first[3]))
    bank[d]=adjusted
    full=e["solve"](target,bank,deadline)
    if full is None:
        raise TimeoutError("exact donor solve capped")
    covered=set().union(*(set(row) for row in bank.values()))
    missing=next(((j,str(target[j])) for j in sorted(target) if j not in covered),None)
    if missing:
        assert full["matching_coefficients"] is None
    result=dict(head=price["head"],pins=PINS,controls=controls,paid_edit=price["key"],limits=price["limits"],
        exact_crossed_response=price["correction"],late_cuts=late,late_eligible=[r["cut"] for r in late if r["status"]=="late exact restoration feasible"],
        recipient_moves=moves,next_recipient_barrier=first_barrier,
        old_read_bank=dict(cut=t,chart=b,public=sorted(bank),owned_excluded=sorted(set(all_rows)-set(bank)),
            target_role=s,target_nnz=len(target),coordinate_separator=missing,**full))
    alarm(0)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
