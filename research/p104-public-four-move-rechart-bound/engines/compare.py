"""Reconcile the exact frozen R88 contact and rank decisions."""
from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

PINS={
    "lead":"7ef82a94baec5e5ede8af38bc9172739f0cff24be94f8d4c3c5bc4e877768805",
    "independent":"97e6272c27714065c382360eb2a7a26209a13bf13a568ca4a643d46ec4b7889d",
}


def main():
    p=ArgumentParser(description=__doc__)
    for name in PINS:
        p.add_argument(name,type=Path)
    args=p.parse_args()
    docs=[]
    for name,pin in PINS.items():
        raw=getattr(args,name).read_bytes()
        assert sha256(raw).hexdigest()==pin, f"Changed receipt {name}"
        docs.append(loads(raw))
    lead,ind=docs
    assert lead["head"]==ind["head"] and lead["ancestor_head"]==ind["predecessor_head"]
    assert not any((lead["unresolved"],ind["unresolved"],lead["unvisited"],ind["unvisited"],
                    lead["survivors"],ind["survivors"]))
    ranks=[]
    for a,b in zip(lead["outcomes"],ind["decisions"],strict=True):
        assert a["key"]==b["key"] and a["ancestor_ADD_clock"]==b["legacy_add_clock"]
        assert a["current_ADD_clock"]==b["current_add_clock"]
        assert a["ancestor_relative_order"]==a["current_relative_order"]==b["legacy_order"]
        assert [a["ancestor_MOVE_clocks"][str(r)] for r in b["roles"]]==b["legacy_move_clocks"]
        assert [a["current_MOVE_clocks"][str(r)] for r in b["roles"]]==b["current_move_clocks"]
        assert a["literal_ADD"]==["ADD",*b["literal_add"]]
        cert=a["geometry_certificate"]
        assert cert["wanted_rank"]==b["required_rank"]==5
        assert cert["low_union_rank"]==b["low_union_rank"]==4
        assert cert["high_intersection_rank"]==b["high_intersection_rank"]==4
        assert a["status"]==b["status"]=="high_intersection_too_small"
        assert Fraction(a["gross_at_incumbent"][1])==Fraction(b["directed_gross_upper"])
        ranks.append([a["key"],b["current_add_clock"],4,5])
    assert len(ranks)==9
    print(dumps(dict(head=lead["head"],pins=PINS,exact_key_agreements=9,
                    exact_rank_intervals_collapsed_to_old_span=9,geometry_survivors=0,unresolved=0,rows=ranks),
                indent=2,sort_keys=True))


if __name__=="__main__":
    main()
