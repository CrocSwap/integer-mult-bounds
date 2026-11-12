"""Price every sole-ADD public source window before decoding."""
from collections import defaultdict
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PINS={
    "inputs/PRICE.json":"7109125bbf60e3015c8c0ac7b10b24b7de61f358c1508d06604ebccd89ef6343",
    "inputs/GEOMETRY.json":"075301daf545c8021800c36af19d05517e3c4136dac4e2114cb85204d0b31c64",
}


def checked():
    result={}
    for path,pin in PINS.items():
        raw=(ROOT/path).read_bytes()
        if sha256(raw).hexdigest()!=pin:
            raise ValueError(f"changed dependency {path}")
        result[path]=json.loads(raw)
    return result


def main():
    assert __debug__
    price,geo=checked().values()
    assert price["head"]==geo["head"] and geo["counts"]=={"binary barrier":37}
    profiles={tuple(r["ranks"]):r for r in price["profiles"]}
    rows=[]
    for r in geo["pairs"]:
        if len(r["contacts"])!=1:
            continue
        t,e=r["contacts"][0]
        f,g,s=r["key"]
        if e[0]!="ADD" or e[2]!=s:
            continue
        p,q,z=r["ranks"]
        quote=profiles[(*sorted((p,q)),z)]
        assert Q(quote["full_probe"][0])>0>Q(quote["extra_rank_one_upper"])
        rows.append(dict(key=r["key"],charts=r["charts"],ranks=r["ranks"],add=[t,e],quote=quote))
    roles=defaultdict(list)
    for r in rows:
        roles[r["key"][2]].append(r)
    assert len(rows)==8 and len(roles)==7
    for group in roles.values():
        if len(group)>1:
            assert len(group)==2 and set(group[0]["key"][:2])&set(group[1]["key"][:2])
    limits={"events":76466,"windows":8,"typed_cuts":33560,"seconds":20,"prototypes":1,"prototype_seconds":120}
    assert sum(2*(r["key"][1]-r["key"][0]-1) for r in rows)==limits["typed_cuts"]
    bound=lambda field:sum(max(Q(r["quote"][field][1]) for r in group) for group in roles.values())
    old_moon=Q(price["whole_target_margin_upper"])-price["distinct_compatible_cap"]*max(Q(r["net_target"][1]) for r in profiles.values())
    print(json.dumps(dict(head=price["head"],caller=price["caller_head"],kappa=price["kappa"],pins=PINS,
        word_sha256=price["word_sha256"],payload_sha256=price["word_payload_sha256"],probe=price["probe"],
        old_paid=price["full_paid_before"],new_paid=price["full_paid_after"],productive=price["productive_positions"],
        candidate_rows=rows,one_upper=str(max(Q(r["quote"]["net"][1]) for r in rows)),
        whole_upper=str(bound("net")),whole_target_complete_upper=str(old_moon+bound("net_target")),limits=limits),
        indent=2,sort_keys=True))


if __name__=="__main__":
    main()
