"""Exact rational exterior support of the frozen virtual singleton banks."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal
from time import monotonic

HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CAP,SECONDS=95,20
PINS={
    "inputs/PLAN.md":"27e368fbe3d9b6c1fcb73ccd0955e842e80f14a16bd1a5f14d78a03ddbbf4319",
    "inputs/PRICE.json":"c108a061c6c03306a99a6fbafe919208954a7479ae28fb8a8fbf45d9832e6144",
    "inputs/R92-REVERSE.json":"f8e56b109352e07dfb8203bdbe42a10cb94374246b4cd419421e4f52e2730c4a",
    "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "reused/exact_six.py":"5bffcbbbdc5b0622e29fbc778540cc240b41e7d252e3e5c68d708d48808fcb5a",
    "reused/rolling_exterior.py":"ffc6dfa01554974f2b913b65c39230d3a7f7b6c06da1c940617b7938afe2b9c7",
}


def unique(pairs):
    result=dict(pairs)
    if len(result)!=len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def read(root):
    raw={}
    for path, pin in PINS.items():
        raw[path]=(root/path).read_bytes()
        if sha256(raw[path]).hexdigest()!=pin:
            raise ValueError("changed dependency: "+path)
    return raw


def decode(raw):
    return json.loads(raw,object_pairs_hook=unique)


def evidence(vector, allowed):
    other=sorted(set(vector)-allowed)
    return [[i,str(vector[i])] for i in other]


def first_gate(p,s,allowed):
    prefix,suffix=evidence(p,allowed),evidence(s,allowed)
    if not p or prefix:
        status="no_nonzero_pure_prefix"
    elif not s or suffix:
        status="no_nonzero_pure_suffix"
    else:
        status="provisional_both_sides_pure"
    return dict(status=status,prefix_exterior=prefix,suffix_exterior=suffix,
        prefix_nonzero=bool(p),suffix_nonzero=bool(s),prefix_support=len(p),suffix_support=len(s))


def controls(trace):
    # At cut 1, a role-0 impulse/covector straddles the harmless MOVE.
    selected=[dict(key=[1,0],public=[0])]
    base=dict(public=2,owned_fields=0,initial=[0,0],final=[1,0],program=[
        ["ADD",1,0,"1",0],["MOVE",0,0,1,False],
    ])
    (p,),(s,)=trace(base,selected,monotonic()+2)[0]
    assert first_gate(p,s,{0})["status"]=="provisional_both_sides_pure" and p==s=={0:Q(1)}
    blocker=base|dict(program=[["ADD",0,1,"-3/2",0],base["program"][1]])
    (p,),(s,)=trace(blocker,selected,monotonic()+2)[0]
    assert first_gate(p,s,{0})["prefix_exterior"]==[[1,"-3/2"]]
    blocker=base|dict(initial=[0,1],final=[1,1],program=[
        ["SCALE",0,"2",0],base["program"][1],["ADD",1,0,"-5/3",1]])
    (p,),(s,)=trace(blocker,selected,monotonic()+2)[0]
    assert first_gate(p,s,{0})["suffix_exterior"]==[[1,"-5/3"]]
    assert first_gate(p,s,{0})["status"]=="no_nonzero_pure_suffix"
    return ["planted mover with both pure unit images","signed prefix exterior","signed suffix exterior"]


def inventory(price, reverse):
    assert price["head"]==reverse["head"]==HEAD and not reverse["eligible"]
    assert price["word_sha256"]==PINS["inputs/7334-WORD.json.gz"]
    assert reverse["events_replayed"]==76466 and reverse["status"]=="EXHAUSTED"
    assert (price["case_cap"],price["runner_seconds_cap"],price["existing_empty_labels"])==(CAP,SECONDS,31)
    attempted=defaultdict(list)
    for r in reverse["attempted"]:
        assert r["selected_label"] is None and not r["other_eligible_labels"]
        assert all(not label["public"] and not label["owned"] for label in r["blocked_labels"])
        attempted[r["cut"],r["mover"],r["midpoint_rank"]].append(r)
    selected=[]
    for r in price["keys"]:
        t,mover,rank=r["key"]
        mids=attempted[t,mover,rank]
        assert r["midpoints"]==[{"existing_empty_charts":m["existing_labels"],
                                 "quotient_representative":m["quotient_direction"]} for m in mids]
        assert len(mids)==3 and len({(m["low_chart"],m["high_chart"]) for m in mids})==1
        selected.append(dict(key=[t,mover],public=[mover],old_move=["MOVE",mover,mids[0]["low_chart"],mids[0]["high_chart"],False]))
    assert len({tuple(x["key"]) for x in price["keys"]})==len(attempted)==len(selected)==CAP
    return selected


def audit(root):
    start=monotonic()
    raw=read(root)
    price, reverse = (decode(raw[path]) for path in ("inputs/PRICE.json","inputs/R92-REVERSE.json"))
    selected=inventory(price,reverse)
    helper=run_path(str(root/"reused/exact_six.py"))
    checks=controls(helper["trace"])
    word=decode(decompress(raw["inputs/7334-WORD.json.gz"]))
    cohort=set(price["endpoint_cohort"])
    assert len(cohort)==615
    for r in selected:
        t,mover=r["key"]
        assert word["program"][t]==r["old_move"] and mover in cohort
    stop=None
    results=[]
    try:
        maps=helper["trace"](word,selected,start+SECONDS-2)
        for planned, ((p,),(s,)), key in zip(selected,maps,price["keys"],strict=True):
            if monotonic()>=start+SECONDS-2:
                raise TimeoutError("cooperative result cap")
            result=first_gate(p,s,cohort)
            if result["status"]=="provisional_both_sides_pure":
                result.update(pure_prefix={i:str(x) for i,x in p.items()},pure_suffix={i:str(x) for i,x in s.items()})
            results.append(result|dict(key=key["key"],old_move=planned["old_move"],midpoints=len(key["midpoints"])))
    except TimeoutError as exc:
        stop=str(exc)
    unvisited=[r["key"] for r in price["keys"][len(results):]]
    return dict(head=HEAD,pins=PINS,controls=checks,runner_seconds_cap=SECONDS,case_cap=CAP,
        scope="exact rational one-column and one-row purity; no unit pairing or physical build",
        status="CAPPED" if unvisited else "EXHAUSTED",results=results,unvisited=unvisited,stop=stop,
        counts=dict(Counter(r["status"] for r in results)),
        survivors=[r["key"] for r in results if r["status"]=="provisional_both_sides_pure"])


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("root",type=Path)
    parser.add_argument("--controls-only",action="store_true")
    args=parser.parse_args()
    assert __debug__
    if args.controls_only:
        result=controls(run_path(str(args.root/"reused/exact_six.py"))["trace"])
    else:
        def hard_stop(*_):
            raise TimeoutError("hard exact 20-second cap")
        signal(SIGALRM,hard_stop)
        alarm(SECONDS)
        try:
            result=audit(args.root)
        finally:
            alarm(0)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
