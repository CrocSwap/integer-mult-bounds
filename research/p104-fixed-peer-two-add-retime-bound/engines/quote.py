"""Price four reversible two-ADD retimes from authenticated receipts only."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path

ROOT=Path(__file__).resolve().parent
PINS={
    "inputs/R100-PRICE.json":"7109125bbf60e3015c8c0ac7b10b24b7de61f358c1508d06604ebccd89ef6343",
    "inputs/R100-GEOMETRY.json":"075301daf545c8021800c36af19d05517e3c4136dac4e2114cb85204d0b31c64",
    "inputs/R92-PRICE.json":"05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
KEYS=[[41321,44605,1305],[43854,44615,1303],[44564,44617,654],[44585,44619,652]]


def unique(pairs):
    obj=dict(pairs)
    if len(obj)!=len(pairs):
        raise ValueError("duplicate JSON key")
    return obj


def main():
    assert __debug__
    docs={}
    for path,pin in PINS.items():
        raw=(ROOT/path).read_bytes()
        if sha256(raw).hexdigest()!=pin:
            raise ValueError("changed dependency "+path)
        if path.endswith(".json"):
            docs[Path(path).stem]=loads(raw,object_pairs_hook=unique)
    price,geom,prior=(docs[k] for k in ("R100-PRICE","R100-GEOMETRY","R92-PRICE"))
    assert price["head"]==geom["head"]==prior["head"]=="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert geom["counts"]=={"binary barrier":37} and geom["timeout"] is None
    assert geom["pins"]["lead/PRICE.json"]==PINS["inputs/R100-PRICE.json"]
    rows=[]
    for row in geom["pairs"]:
        if len(row["contacts"])!=2:
            continue
        f,g,h=row["key"]
        (t1,a),(t2,b)=row["contacts"]
        if a[0]!=b[0] or a[0]!="ADD" or a[1:3]!=b[1:3][::-1]:
            continue
        assert t1==f+1 and t2==f+2 and t2<g and h in a[1:3]
        peer=next(r for r in a[1:3] if r!=h)
        assert peer<1501 and h<1501 and row["ranks"]==[1,1,2]
        assert a[-1]==b[-1]==row["charts"][1]
        if a[1]==h:
            assert (Q(a[3]),Q(b[3]))==(Q(-1),Q(1,2))
            matrix=[["1","-1"],["1/2","1/2"]]
        else:
            assert (Q(a[3]),Q(b[3]))==(Q(1),Q(-1,2))
            matrix=[["1/2","-1/2"],["1","1"]]
        assert Q(matrix[0][0])*Q(matrix[1][1])-Q(matrix[0][1])*Q(matrix[1][0])==1
        rows.append(dict(key=row["key"],charts=row["charts"],ranks=row["ranks"],peer=peer,
            original_pair=row["contacts"],normalized_matrix=matrix,determinant="1",
            late_pre_event_cuts=[f+3,g],per_endpoint_typed_count=g-f-2,
            early_endpoint_exclusion="public peer is at B in the old pair and ascends only"))
    assert [r["key"] for r in rows]==KEYS and len({r["peer"] for r in rows})==4
    assert len({v for r in rows for v in r["key"][:2]})==8
    assert len({v for r in rows for v in (r["key"][2],r["peer"])})==8
    candidates=sum(r["per_endpoint_typed_count"] for r in rows)
    assert candidates==4124
    q=next(r for r in price["profiles"] if r["ranks"]==[1,1,2])
    assert Q(q["full_probe"][0])>0>Q(q["extra_rank_one_upper"])
    old=Counter({int(k):n for k,n in prior["old_targets"].items()})
    old.subtract({int(k):n for k,n in prior["old_paid"].items()})
    delta={1:-34,2:17}
    assert q["paid_delta"]=={str(k):v for k,v in delta.items()}
    changed=old.copy()
    changed.subtract({k:4*v for k,v in delta.items()})
    assert sum(k*v for k,v in old.items())==sum(k*v for k,v in changed.items())==1424
    cost=run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    at,probe,target=[Q(price[k]) for k in ("old_crossing_upper","probe","fixed_target")]
    credit={k:-v for k,v in delta.items()}
    assert cost(credit,at)[1]==Q(q["net"][1]) and cost(changed,probe)[0]>0
    assert 4*cost(credit,at)[1]<1
    print(dumps(dict(head=price["head"],caller=price["caller_head"],kappa=price["kappa"],
        word_sha256=price["word_sha256"],payload_sha256=price["word_payload_sha256"],pins=PINS,
        cases=rows,old_paid=110519,one_new_paid=110502,optimistic_all_four_paid=110451,productive=22461,
        rank_surplus=1424,paid_delta=delta,compatible_paid_delta={k:4*v for k,v in delta.items()},
        one_upper=q["net"][1],whole_upper=str(4*cost(credit,at)[1]),
        complete_four_probe=list(map(str,cost(changed,probe))),fixed_target_complete_upper=str(cost(changed,target)[1]),
        caps=dict(windows=4,typed_cuts=2*candidates,late_cuts=candidates,runner_seconds=20,prototypes=1),
        scope="Receipt-only: original adjacent signed pair, both public paths held fixed except one contracted mover route."),
        indent=2,sort_keys=True))


if __name__=="__main__":
    main()
