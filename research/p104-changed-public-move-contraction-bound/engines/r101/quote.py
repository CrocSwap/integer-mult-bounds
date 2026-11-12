"""Preprice a same-clock public donor-bank contraction."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/R100-PRICE.json": "7109125bbf60e3015c8c0ac7b10b24b7de61f358c1508d06604ebccd89ef6343",
    "inputs/R100-GEOMETRY.json": "075301daf545c8021800c36af19d05517e3c4136dac4e2114cb85204d0b31c64",
}


def unique(pairs):
    result = dict(pairs)
    if len(result)!=len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def main():
    docs = {}
    for path,pin in PINS.items():
        data = (ROOT/path).read_bytes()
        if sha256(data).hexdigest()!=pin:
            raise ValueError(f"changed dependency {path}")
        docs[path] = json.loads(data,object_pairs_hook=unique)
    price,geo = docs.values()
    assert price["head"]==geo["head"] and len(geo["pairs"])==37 and not geo["timeout"]
    assert geo["pins"]["lead/PRICE.json"]==PINS["inputs/R100-PRICE.json"]
    profiles = {tuple(q["ranks"]):q for q in price["profiles"]}
    candidates, by_role = [],{}
    for row in geo["pairs"]:
        if len(row["contacts"])!=1 or row["charts"][1]==207:
            continue
        t,event = row["contacts"][0]
        f,g,role = row["key"]
        if event[0]!="ADD" or event[1]!=role:
            continue
        p,q,s = row["ranks"]
        quote = profiles[(*sorted((p,q)),s)]
        assert row["net"]==quote["net"] and Q(quote["full_probe"][0])>0
        candidates.append({"key":row["key"],"charts":row["charts"],"add":[t,event],
                           "ranks":row["ranks"],"quote":quote})
        if role not in by_role or Q(quote["net"][1])>Q(by_role[role]["net"][1]):
            by_role[role]=quote
    assert len(candidates)==6 and len(by_role)==4
    assert all(Q(q["extra_rank_one_upper"])<0 for q in by_role.values())
    target_full_upper = Q(price["whole_target_margin_upper"])
    largest_unrestricted = max(Q(r["net_target"][1]) for r in profiles.values())
    base_target_upper = target_full_upper-price["distinct_compatible_cap"]*largest_unrestricted
    whole_target_upper = base_target_upper + sum(max(Q(r["quote"]["net_target"][1]) for r in candidates if r["key"][2]==role)
                                                 for role in by_role)
    candidates.sort(key=lambda r:(-Q(r["quote"]["net"][0]),r["key"]))
    print(json.dumps({
        "head":price["head"],"pins":PINS,"kappa":price["kappa"],"caller_head":price["caller_head"],
        "word_sha256":price["word_sha256"],"payload_sha256":price["word_payload_sha256"],
        "probe":price["probe"],"candidates":candidates,"old_paid":110519,"one_new_paid":110502,
        "targets":22461,"rank_surplus":1424,"distinct_roles":len(by_role),
        "one_net_upper":str(max(Q(q["net"][1]) for q in by_role.values())),
        "whole_net_upper":str(sum(Q(q["net"][1]) for q in by_role.values())),
        "whole_target_margin_upper":str(whole_target_upper),
        "limits":{"cases":12,"runner_seconds":20,"prototype_cases":1,"prototype_seconds":120},
        "scope":"Only moved destination has a sole ADD at its original clock. Use arbitrary rational same-clock public donor rows at A or C, excluding mover. No extra paid call. Complete price treats auxiliary ordinary cost as free, checks actual scalar/grid/compiler/ownership costs for any candidate.",
    },indent=2,sort_keys=True))


if __name__=="__main__":
    assert __debug__
    main()
