"""Price fallback stock from sealed metadata only."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from itertools import product
from json import dumps, loads
from pathlib import Path
from runpy import run_path

PINS = {
    "lead/GEOMETRY.json": "075301daf545c8021800c36af19d05517e3c4136dac4e2114cb85204d0b31c64",
    "lead/PRICE.json": "7109125bbf60e3015c8c0ac7b10b24b7de61f358c1508d06604ebccd89ef6343",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
HELPERS = "bf353b3e05d0bf5fe3e49c15673c4cb9203251329bd594009303541cf7fecc09"


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Duplicate JSON key")
    return result


def read(path, expected):
    data = path.read_bytes()
    if sha256(data).hexdigest() != expected:
        raise ValueError("Changed input " + path.name)
    return data


def rank_tilt(anchor, old, cost, at, probe, target):
    p,q,_ = anchor["ranks"]
    alternatives = {}
    # Relax the unknown midpoint dimension and the other role's two paid ranks.
    for mid in range(p,10-q):
        for left,right in product(range(1,mid+1),range(1,10-mid)):
            for offset in range(1-min(p,left),min(q,right)):
                if not offset:
                    continue
                new = Counter((p+offset,q-offset,left+offset,right-offset))
                new.subtract((p,q,left,right))
                credit = {rank:-17*n for rank,n in new.items() if n}
                if not credit:
                    continue
                interval = cost(credit,at)
                changed = old.copy()
                changed.update(credit)
                if interval[1] > 0 and cost(changed,probe)[1] > 0:
                    alternatives[left,right,offset] = (interval[1],cost(credit,target)[1])
    maxima = [max((v[i] for v in alternatives.values()),default=Q(0)) for i in (0,1)]
    return len(alternatives),maxima


def packing(rows,axis):
    conflicts = []
    for row in rows:
        conflicts.append(sum(1<<j for j,r in enumerate(rows) if
            row["contact"][0] == r["contact"][0] or set(row["key"][:2]).intersection(r["key"][:2])))

    @cache
    def best(mask):
        if not mask:
            return Q(0)
        index = (mask & -mask).bit_length()-1
        return max(best(mask & ~(1<<index)), rows[index]["uppers"][axis]+best(mask & ~conflicts[index]))

    return best((1<<len(rows))-1)


def main():
    assert __debug__
    p = ArgumentParser(description=__doc__)
    p.add_argument("--r100",type=Path,required=True)
    p.add_argument("--helpers",type=Path,required=True)
    args = p.parse_args()
    raw = {name:read(args.r100/name,pin) for name,pin in PINS.items()}
    data = lambda name: loads(raw[name],object_pairs_hook=unique)
    geom,price,prior = (data(k) for k in ("lead/GEOMETRY.json","lead/PRICE.json","inputs/R92-PRICE.json"))
    helper_data = loads(read(args.helpers,HELPERS),object_pairs_hook=unique)
    assert len(helper_data["rows"]) == 1101 and helper_data["complete"]
    helpers = {r["role"] for r in helper_data["rows"]}
    assert geom["head"] == price["head"] == prior["head"] == "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert price["caller_head"] == prior["caller_head"] == "07a76c5e2738882c0cb322278e56f6cae3c9885d"
    assert len(geom["pairs"]) == 37 and not geom["timeout"]
    old = Counter({int(r):n for r,n in prior["old_targets"].items()})
    old.subtract({int(r):n for r,n in prior["old_paid"].items()})
    at,probe,target = (Q(price[k]) for k in ("old_crossing_upper","probe","fixed_target"))
    cost = run_path(str(args.r100/"inputs/pricing.py"))["cost"]
    profile = {tuple(r["ranks"]):r for r in price["profiles"]}
    typed,tilt,skip = [],[],[]
    single = [r for r in geom["pairs"] if len(r["contacts"]) == 1]
    changed = set(price["roles"])
    protected = {863,1355,1531,1567,1568}
    for r in single:
        f,g,mover = r["key"]
        clock,add = r["contacts"][0]
        assert add[0] == "ADD" and mover in add[1:3] and f<clock<g
        p,q,s = r["ranks"]
        quote = profile[(*sorted((p,q)),s)]
        assert Q(quote["full_probe"][0]) > 0
        if add[2] == mover and add[1] < 1501:
            typed.append(dict(key=r["key"],charts=r["charts"],ranks=r["ranks"], contact=[clock,add],
                recipient=add[1],quote=quote,uppers=[Q(quote[k][1]) for k in ("net","net_target")]))
        peer = add[2] if add[1] == mover else add[1]
        if peer >= 1501 or peer in protected or peer not in helpers:
            skip.append([clock,"peer outside eligible public helper class"])
            continue
        if peer in changed and not any(v["key"][2] == peer and v["contacts"] == [[clock,add]] for v in single):
            skip.append([clock,"changed peer has no corresponding sole-ADD pair"])
            continue
        variants, uppers = rank_tilt(r,old,cost,at,probe,target)
        tilt.append(dict(key=r["key"],ranks=r["ranks"],charts=r["charts"],contact=[clock,add],
                         peer=peer,positive_relaxed_profiles=variants,uppers=uppers))
    assert len(typed) == 8 and len({r["key"][2] for r in typed}) == 7
    assert sum(2*(r["key"][1]-r["key"][0]-1) for r in typed) == 33560
    assert len(single) == 17 and len(tilt)+len(skip) == len(single)
    assert all(len({tuple(r["key"]) for r in rows}) == len(rows) for rows in (typed,tilt))

    def summary(rows):
        return dict(one_upper=str(max(row["uppers"][0] for row in rows)),
            whole_upper=str(packing(rows,0)),fixed_target_complete_upper=str(cost(old,target)[1]+packing(rows,1)),
            anchors=rows)

    result = dict(head=price["head"],caller=price["caller_head"],pins=PINS|{"helpers":HELPERS},
        classification="receipt-only price arithmetic, no literal word or support",
        source_side=summary(typed),midpoint_rank_tilt=summary(tilt),midpoint_guard_exclusions=skip)
    print(dumps(result,indent=2,sort_keys=True,default=str))


if __name__ == "__main__":
    main()
