"""Reconcile every frozen early and late typed cut from the R116 receipts."""
from collections import Counter
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
import sys

PINS={
    "plan/PRICE.json":"8226a2b9c9240455d6fcdaf3a38929e3336e89f35aed3f15b81564f07ed8387f",
    "lead/RESULT.json":"1d7d7b122757d4345cfea3fa7d1c8525211939b913e900e9974fb93fc5b18e5e",
    "independent/RESULT.json":"f777aaa05cbcb9f6067d9b04220abe9aab01f8eaac5c407b078e0c295ca1f2b7",
}


def unique(items):
    value=dict(items)
    if len(value)!=len(items):
        raise ValueError("duplicate JSON key")
    return value


def main(root):
    docs=[]
    for rel,expected in PINS.items():
        raw=(root/rel).read_bytes()
        if sha256(raw).hexdigest()!=expected:
            raise ValueError(f"changed dependency: {rel}")
        docs.append(loads(raw,object_pairs_hook=unique))
    price,lead,reverse=docs
    assert reverse["head"]==price["head"] and reverse["caller"]==price["caller"]
    assert lead["pins"]["plan/PRICE.json"]==reverse["pins"]["inputs/PRICE.json"]==PINS["plan/PRICE.json"]
    assert lead["pins"]["inputs/7334-WORD.json.gz"]==reverse["pins"]["inputs/7334-WORD.json.gz"]==price["word_sha256"]
    assert lead["completed_literal_events"]==reverse["progress"]["events_replayed"]==76466
    assert lead["timeout"] is None and reverse["timeout"] is None and reverse["complete"]
    assert not lead["unresolved_late_cut_intervals"] and not lead["unresolved_late_count"] and not reverse["unvisited"]
    counts=Counter()
    windows=[]
    for p,a,b in zip(price["cases"],lead["windows"],reverse["rows"],strict=True):
        assert a["key"]==b["key"]==p["key"] and a["peer"]==b["peer"]==p["peer"]
        assert a["charts"]==p["charts"] and b["target_chart"]==p["charts"][2]
        assert b["original_pair"]==p["original_pair"] and b["window"]==p["late_pre_event_cuts"]
        assert a["first_crossed_scalar"]==b["first_scalar_or_lifetime_contact"]
        assert a["first_peer_scalars_in_corridor"][:1]==([] if b["first_scalar_or_lifetime_contact"] is None else [b["first_scalar_or_lifetime_contact"]])
        intervals=[[l,h,chart,clean,clean and at_c] for l,h,chart,at_c,clean in b["intervals"]]
        assert intervals==a["late_intervals"]
        first,last=b["window"]
        assert intervals[0][0]==first and intervals[-1][1]==last
        assert all(x[1]+1==y[0] for x,y in zip(intervals,intervals[1:]))
        assert all(chart!=p["charts"][0] for _,_,chart,_,_ in intervals)
        assert a["early_excluded"]==a["late_tested"]==last-first+1
        assert a["late_peer_at_c"]==b["chart_C_cut_count"]==0
        assert not a["survivors"] and not b["survivors"]
        trajectory=b["peer_chart_path"]
        moves=[[l[1],["MOVE",p["peer"],l[2],r[2],False]]
               for l,r in zip(trajectory,trajectory[1:]) if first<=l[1]<last]
        assert moves==a["peer_moves_through_window"]
        counts.update(b["counts"])
        windows.append(dict(key=a["key"],peer=a["peer"],charts=a["charts"],window=[first,last],
            early_excluded=a["early_excluded"],late_intervals=intervals,peer_moves=moves,
            first_scalar_blocker=a["first_crossed_scalar"]))
    assert len(windows)==4 and counts=={"other clean":2364,"other blocked":1760}
    assert reverse["counts"]==dict(counts)
    assert sum(counts.values())==lead["counts"]["early_excluded"]==lead["counts"]["late_tested"]==4124
    print(dumps(dict(head=price["head"],pins=PINS,matching_windows=4,early_excluded=4124,
        late_tested=4124,total_excluded=8248,late_chart_matches=0,late_counts=counts,
        survivors=0,unresolved=0,windows=windows),indent=2,sort_keys=True))


if __name__=="__main__":
    assert __debug__
    main(Path(sys.argv[1]))
