"""Reconcile both primes and both exact six-bank receipts."""
from argparse import ArgumentParser
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

PINS = {
    "lead_modular": "a3505dd0cfd3ee9e242f804e12e3c4705ea6548080d537f597cec355f358e92c",
    "independent_modular": "fa35b69613ad4af03eada14f251827464dba0d002f67da085817422ec3351649",
    "lead_exact": "6c89dc61732e9f3dd0bd6bf7b3653c0aae555543959919b6955c3d49e8caf3c6",
    "independent_exact": "f68c7033ed1840704c5b66edb9dc6ad223628c80879b1862796de6735a41b961",
}


def main():
    p=ArgumentParser(description=__doc__)
    for name in PINS:
        p.add_argument(name,type=Path)
    args=p.parse_args()
    assert __debug__
    docs=[]
    for name, pin in PINS.items():
        raw=getattr(args,name).read_bytes()
        assert sha256(raw).hexdigest()==pin, f"Changed receipt {name}"
        docs.append(loads(raw))
    lead,independent,lead_exact,independent_exact=docs
    assert len({r["head"] for r in docs})==1 and lead["prime"]!=independent["prime"]
    for old,new,expected in (
        (lead["results"],independent["tested"],4183),
        (lead["prior_controls"],independent["prior_24"],24),
    ):
        by_key={tuple(r["key"]):r for r in new}
        assert len(old)==len(by_key)==expected
        for row in old:
            other=by_key[tuple(row["key"])]
            assert all(row[k]==other[k] for k in ("key","public","owned","pivots"))
            assert row["exterior_rank"]==other["modular_rank"]
            assert (row["disposition"]=="excluded") == (other["status"]=="no_nonzero_pure_prefix")
    assert lead["rank_drops"]==independent["rank_drops"] and len(lead["rank_drops"])==2134
    assert not lead["unvisited"] and not independent["unvisited"]
    exact={}
    for row,other in zip(lead_exact["results"],independent_exact["results"],strict=True):
        assert row["key"]==other["key"] and row["public"]==other["bank"]
        assert row["pure_prefix_dimension"]==other["prefix_nullity"]
        assert row["pure_suffix_dimension"]==other["suffix_nullity"]
        assert row["status"] == ("no nonzero pure suffix" if not other["suffix_nullity"] else "no unit pairing")
        assert other["status"]=="no_exact_unit_pair"
        exact[tuple(row["key"])]=[other["prefix_nullity"],other["suffix_nullity"]]
    assert len(exact)==6 and not lead_exact["selected_unresolved"] and not independent_exact["unresolved"]
    print(dumps(dict(head=lead["head"],input_sha256=PINS,modular_exact_bank_agreements=4207,
        new_full_rank_exclusions=2049,modular_rank_drops=2134,exact_scope_exclusions=6,
        remaining_unresolved=2128,exact_nullities=[[list(k),d] for k,d in exact.items()]),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
