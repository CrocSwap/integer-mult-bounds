"""Authenticate, price and check the first-use owned reconstruction stock."""
from collections import Counter,defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
import sys
from time import monotonic

ROOT=Path(__file__).resolve().parents[1]
PINS={
    "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/R80-OWNED.json":"db293c67c896f54788681b7a8a9fec5f13da0e31fe5b3dd65fbe30e370ff1d2e",
    "inputs/R92-PRICE.json":"05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/aggregate.py":"8bf1b91d7fc0937305466686522f5fb3920c66c71830acfc94adde84ba4f49e1",
    "inputs/donor_span.py":"4d5306e2c0b7e91c79d22c82e8e760aed2c311979298c558e631975d4d1ae5b1",
    "inputs/pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def unique(pairs):
    obj=dict(pairs)
    if len(obj)!=len(pairs):
        raise ValueError("duplicate JSON key")
    return obj


def read(path):
    data=(ROOT/path).read_bytes()
    if sha256(data).hexdigest()!=PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return data


def quote():
    old, owned=(loads(read(p),object_pairs_hook=unique)
                for p in ("inputs/R92-PRICE.json","inputs/R80-OWNED.json"))
    assert old["head"]==owned["head"]=="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert old["caller_head"]=="07a76c5e2738882c0cb322278e56f6cae3c9885d"
    assert old["word_sha256"]==owned["word_sha256"]==PINS["inputs/7334-WORD.json.gz"]
    stock=Counter({int(r):v for r,v in owned["paid_owned_rank"].items()})
    assert sum(stock.values())==47
    paid,target=(Counter({int(k):v for k,v in old[field].items()}) for field in ("old_paid","old_targets"))
    assert (sum(paid.values()),sum(target.values()))==(110519,22461)
    target.subtract(paid)
    assert sum(r*n for r,n in target.items())==1424
    read("inputs/pricing.py")
    cost=run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    at,probe,moon=(Q(old[k]) for k in ("old_crossing_upper","probe","moonshot"))
    one={}
    for r in stock:
        delta={r:17}
        profile=target.copy()
        profile.update(delta)
        margin=cost(profile,probe)
        assert margin[0]>0
        one[r]=dict(paid_delta={r:-17},productive_delta={},gross=list(map(str,cost(delta,at))),
            complete_probe=list(map(str,margin)),paid=110502,productive=22461,surplus=1424+17*r)
    all_delta={r:17*n for r,n in stock.items()}
    all_profile=target.copy()
    all_profile.update(all_delta)
    return dict(head=old["head"],caller=old["caller_head"],pins=PINS,one=one,stock=stock,
        whole_gross_upper=str(cost(all_delta,at)[1]),fixed_target_upper=str(cost(all_profile,moon)[1]),
        case_cap=47,event_cap=76466,runner_seconds=35)


def first_contacts(word,p):
    tape=word["program"]
    n=word["public"]
    seen={}
    records=[]
    ranks=Counter()
    for t,(op,r,*a) in enumerate(tape):
        touch=[r]
        if op in {"ADD","COPY"}:
            touch.append(a[0])
        for j in touch:
            if j in seen:
                old=seen.pop(j)
                records.append(dict(**old,first_clock=t,first_event=tape[t]))
        if op=="MOVE" and a[2]:
            assert r>=n
            rank=abs(len(word["frames"][a[0]])-len(word["frames"][a[1]]))
            assert rank>0
            ranks[rank]+=1
            seen[r]=dict(role=r,move_clock=t,chart_from=a[0],chart_to=a[1],rank=rank)
    assert not seen and ranks==p["stock"] and len(records)==47
    return sorted(records,key=lambda x:(-x["rank"],x["move_clock"]))


def main():
    assert __debug__
    p=quote()
    if sys.argv[1:]==["--price-only"]:
        print(dumps(p,indent=2,sort_keys=True))
        return
    assert not sys.argv[1:]
    deadline=monotonic()+32
    raw=decompress(read("inputs/7334-WORD.json.gz"))
    assert sha256(raw).hexdigest()=="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
    word=loads(raw,object_pairs_hook=unique)
    assert len(word["program"])==p["event_cap"]
    records=first_contacts(word,p)
    ask,refs=defaultdict(set),defaultdict(set)
    for record in records:
        op=record["first_event"][0]
        t,r,c=record["first_clock"],record["role"],record["chart_to"]
        if op in {"ADD","SCALE"}:
            assert record["first_event"][-1]==c
            ask[t].add((c,r))
            refs[t].add(r)
    read("inputs/donor_span.py")
    read("inputs/aggregate.py")
    helper=run_path(str(ROOT/"inputs/donor_span.py"))
    solve=run_path(str(ROOT/"inputs/aggregate.py"))
    tests=solve["controls"](helper)
    banks,values=helper["snapshot"](word,ask,refs,deadline)
    for row in records:
        t,r,c=row["first_clock"],row["role"],row["chart_to"]
        key=t,c,r
        row["delay_events"]=t-row["move_clock"]-1
        if row["first_event"][0] not in {"ADD","SCALE"}:
            row["disposition"]="first contact outside scope"
            continue
        if key not in banks or (t,r) not in values or monotonic()>=deadline:
            row["disposition"]="capped"
            continue
        target=values[t,r]
        bank=banks[key]
        answer=solve["exact_span"](target,bank,deadline,helper)
        if answer is None:
            row["disposition"]="capped"
            continue
        if "rank" in answer:
            answer["span_rank"] = answer.pop("rank")
        row.update(answer)
        row["disposition"]=row.pop("decision")
        row["bank_roles"]=sorted(bank)
        row["row"]={i:str(q) for i,q in target.items()}
    counts=Counter(r["disposition"] for r in records)
    print(dumps(dict(head=p["head"],caller=p["caller"],pins=PINS,controls=tests,counts=counts,
                    records=records,unvisited=[r["move_clock"] for r in records if r["disposition"]=="capped"]),
                indent=2,sort_keys=True))
    if counts["capped"]:
        raise SystemExit(2)


if __name__=="__main__":
    main()
