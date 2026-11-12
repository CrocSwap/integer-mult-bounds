"""Compare independent reverse and primary forward R92 geometry receipts."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

PINS={
    "lead_geometry":"e9f93f3271855012b2de705c70f186f78c31a369d28110e92c5f2ffadae209b3",
    "lead_guards":"c23e9c74b3479e4af6c452eeb73e000878148ec385560a0642433a1c5bac4a07",
    "reverse":"f8e56b109352e07dfb8203bdbe42a10cb94374246b4cd419421e4f52e2730c4a",
}


def unique(pairs):
    result=dict(pairs)
    if len(result)!=len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def main():
    documents={}
    for name,arg in zip(PINS,sys.argv[1:],strict=True):
        raw=Path(arg).read_bytes()
        if sha256(raw).hexdigest()!=PINS[name]:
            raise ValueError("changed dependency: "+name)
        documents[name]=json.loads(raw,object_pairs_hook=unique)
    lead,guards,reverse=(documents[k] for k in PINS)
    assert lead["head"]==guards["head"]==reverse["head"]
    assert guards["geometry_sha256"]==PINS["lead_geometry"]
    assert lead["events_replayed"]==reverse["events_replayed"]==76466
    assert lead["native_public_paid_histogram"]==reverse["all_public_paid_rank_histogram"]
    assert lead["first_unvisited_event"] is None and reverse["first_unvisited_event"] is None
    assert lead["counts"]["cohort_rank_two_crossings"]==reverse["qualifying_move_count"]==95
    lead_map={(r["move_clock"],r["mover"],r["rank"],r["quotient_representative"]):
              [(x["chart"],x["eligible"]) for x in r["labels"]] for r in lead["raw_placements"]}
    reverse_map={(r["cut"],r["mover"],r["midpoint_rank"],r["quotient_direction"]):
                 [(c,c==r["selected_label"] or c in {x["chart"] for x in r["other_eligible_labels"]})
                  for c in r["existing_labels"]] for r in reverse["attempted"]}
    assert lead_map==reverse_map and len(lead_map)==len(lead["raw_placements"])==len(reverse["attempted"])==285
    reverse_labels={(r["cut"],l["chart"],r["mover"]):(r,l)
                    for r in reverse["attempted"] for l in r["blocked_labels"]}
    assert len(reverse_labels)==len(guards["cases"])==31
    for row in guards["cases"]:
        r,l=reverse_labels[tuple(row["key"])]
        assert row["rank"]==r["midpoint_rank"] and row["old_move"]==["MOVE",r["mover"],r["low_chart"],r["high_chart"],False]
        assert row["status"]=="empty_chart" and not row["public"] and not row["owned"]
        assert row["other_eligible"]==l["other_pivots"]==[] and row["public"]==l["public"] and row["owned"]==l["owned"]
    assert not lead["eligible"] and not reverse["eligible"] and not guards["eligible"]
    assert not lead["selected"] and not reverse["selected"]
    assert not lead["unvisited_support_keys"] and not reverse["unselected"]
    counts=Counter((r["midpoint_rank"],bool(r["existing_labels"])) for r in reverse["attempted"])
    print(json.dumps(dict(head=lead["head"],pins=PINS,matched_quotient_placements=285,
        matched_existing_label_banks=31,rank4_absent=counts[4,False],rank5_absent=counts[5,False],
        rank4_empty=counts[4,True],rank5_empty=counts[5,True],eligible=0,unresolved=0,
        selected_support_keys=[]),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
