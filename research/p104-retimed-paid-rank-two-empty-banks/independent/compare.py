"""Authenticate both R98 engines and compare their full frozen window coverage."""
from collections import Counter
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
import sys

PINS = {
    "independent/RESULT.json": "5f3ae7635ed0fcf4b558b6a67a1d340363f7f34cceb3f3d6ecc2c51a3785d060",
    "lead/GEOMETRY.json": "48487c55c2aa8d60a0f4aebc577f78e08abc4fda24e4ed0bba3dc2115b8de3e7",
}


def unique(items):
    value = dict(items)
    if len(value) != len(items):
        raise ValueError("duplicate JSON key")
    return value


def main(root):
    values = []
    for rel, digest in PINS.items():
        raw = (root / rel).read_bytes()
        if sha256(raw).hexdigest() != digest:
            raise ValueError(f"changed receipt: {rel}")
        values.append(loads(raw, object_pairs_hook=unique))
    a, b = values
    assert a["head"] == b["head"] and a["r98_price_sha256"] == b["pins"]["lead/PRICE.json"]
    assert a["complete"] and b["timeout"] is None and b["first_unvisited_event"] is None
    assert a["forward_events"] == a["reverse_events"] == a["cap_events_per_pass"] == 76466
    assert not a["selected"] and not b["representatives"] and b["eligible_raw_cuts"] == 0
    assert a["raw_candidate_cuts"] == a["raw_scheduled_cuts"] == b["raw_cut_count"] == b["visited_labelled_cuts"] == 29641
    groups = {}
    for row in a["results"]:
        key = tuple(row[k] for k in ("anchor","mover","chart"))
        groups.setdefault(key, []).append(row)
    assert len(groups) == len(a["labelled_anchors"]) == len(b["windows"]) == 31
    out = []
    for x, y in zip(a["labelled_anchors"], b["windows"], strict=True):
        key = tuple(x[k] for k in ("anchor","mover","chart"))
        assert list(key) == y["anchor"]
        assert x["window"] == [y["first"],y["last"]]
        assert x["rank"] == y["cut_rank"] and x["quotient_representative"] == y["quotient_rep"]
        assert [x["source"],x["destination"]] == y["outer_charts"]
        pre, post = groups[key]
        assert all(not r["public"] and not r["owned"] for r in (pre,post))
        clock = x["anchor"]
        assert [pre["first"],pre["last"]] == [y["first"],clock]
        assert [post["first"],post["last"]] == [clock+1,y["last"]]
        out.append(dict(anchor=key, window=x["window"], outer_charts=y["outer_charts"],
            previous_contact=x["previous_contact"], next_contact=x["next_contact"],
            pre=[pre["first"],pre["last"]],post=[post["first"],post["last"]],
            chart_rank=x["rank"], raw_empty_cuts=y["last"]-y["first"]+1))
    assert sum(r["raw_empty_cuts"] for r in out) == 29641
    print(dumps(dict(head=a["head"], pins=PINS, agree=31, raw_empty_cuts=29641,
        complete=True, eligible=0, remaining=0, grouping=Counter({"pre_anchor":31,"post_anchor":31}),
        windows=out), indent=2, sort_keys=True))


if __name__ == "__main__":
    assert __debug__
    main(Path(sys.argv[1]))
