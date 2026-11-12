"""Exact complete price of a public monotone paid MOVE contraction."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/BENCHMARK.json": "004331cff6ca8644489d7b7084e5c67439d74a2d283e4d64a9fdb9f88679253d",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/7334-CHANGED.json": "f4d3f6ca2d87f8cd68c01ac9f77b69bd5a796f92bd567cea8afe3ac7c72e8e4b",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def unique(pairs):
    result = dict(pairs)
    if len(result)!=len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def hist(x):
    return Counter({int(k):v for k,v in x.items()})


def interval(x):
    return list(map(str,x))


def main():
    docs = {}
    for path,pin in PINS.items():
        data = (ROOT/path).read_bytes()
        if sha256(data).hexdigest()!=pin:
            raise ValueError(f"changed dependency {path}")
        if path.endswith(".json"):
            docs[path] = json.loads(data,object_pairs_hook=unique)
    bench,prior,changed = docs.values()
    assert bench["head"] == prior["head"] and len(changed["roles"])==14
    assert changed["word_sha256"][-1]=="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
    assert bench["status"]=="exact-complete-receipt-reused"
    targets,paid = hist(prior["old_targets"]),hist(prior["old_paid"])
    assert sum(targets.values())==22461 and sum(paid.values())==110519
    old = targets.copy()
    old.subtract(paid)
    assert sum(r*n for r,n in old.items())==1424
    cost = run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    at = Q(prior["old_crossing_upper"])
    probe = Q(prior["probe"])
    bit = Q(prior["retained_bit_premise"])
    target = Q(prior["moonshot"])
    assert at == Q(bench["crossing"][1]) and at < probe < bit < target
    profiles=[]
    for p in range(1,9):
        for q in range(p,10-p):
            change=Counter((p,q))
            change.subtract((p+q,))
            change=Counter({r:17*n for r,n in change.items()})
            new=old.copy()
            new.update(change)
            assert sum(r*n for r,n in new.items())==1424
            full_probe=cost(new,probe)
            assert full_probe[0]>0
            profiles.append({"ranks":[p,q,p+q],"paid_delta":{r:-n for r,n in change.items()},
                             "net":interval(cost(change,at)),"full_probe":interval(full_probe),
                             "net_target":interval(cost(change,target)),
                             "extra_rank_one_upper":str(cost(new,at)[1]-1)})
    assert len(profiles)==20
    # Every public MOVE is strict ascending within rank 0..9. Each of the 14
    # roles can have at most 9 MOVEs and thus at most four disjoint pairs.
    stock=len(changed["roles"])*(9//2)
    max_net=max(Q(x["net"][1]) for x in profiles)
    max_target=max(Q(x["net_target"][1]) for x in profiles)
    out={"head":bench["head"],"kappa":bench["kappa"],"caller_head":prior["caller_head"],
         "pins":PINS,"word_sha256":prior["word_sha256"],"word_payload_sha256":changed["word_sha256"][-1],
         "roles":changed["roles"],"old_crossing_upper":str(at),"probe":str(probe),
         "fixed_target":str(target),"bit_premise":str(bit),"full_paid_before":110519,"full_paid_after":110502,
         "productive_positions":22461,"rank_surplus":1424,"profiles":profiles,
         "distinct_compatible_cap":stock,"one_net_upper":str(max_net),
         "whole_net_upper":str(stock*max_net),"whole_target_margin_upper":str(cost(old,target)[1]+stock*max_target),
         "limits":{"event_cap":76466,"runner_seconds":20,"paid_pairs":112,"builds":1,"prototype_seconds":120}}
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    assert __debug__
    main()
