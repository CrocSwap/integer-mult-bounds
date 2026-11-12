"""Match the ten R108 forward and reverse exact neighboring contacts."""
from collections import Counter
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
import sys

PINS = {
    "independent/RESULT.json": "2fa3e2ac13b486416976ddf9c228ed80147eab7a1efacf8be26b5860102156c7",
    "lead/ROUTES.json": "7787cbedb364a51ae1c3712086bbc3f70da35ba018037429ad7794d52c8edb93",
}


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON key")
    return result


def main(root):
    values = []
    for rel,digest in PINS.items():
        data = (root/rel).read_bytes()
        if sha256(data).hexdigest() != digest:
            raise ValueError(f"changed receipt: {rel}")
        values.append(loads(data,object_pairs_hook=unique))
    reverse,forward=values
    assert reverse["head"]==forward["head"] and reverse["caller"]==forward["caller"]
    assert all(reverse["pins"][k]==forward["pins"][k] for k in reverse["pins"])
    assert reverse["complete"] and not reverse["unvisited"] and reverse["timeout"] is None
    assert reverse["progress"]["events_replayed"]==forward["events"]==76466
    assert reverse["counts"]=={"adjacent contact is not MOVE":10}
    assert forward["topology_counts"]=={"no four-MOVE topology":10} and not forward["price_counts"]
    results, sides=[],Counter()
    for a,b in zip(reverse["rows"],forward["results"],strict=True):
        assert a["key"]==b["key"] and a["contact"]==[b["clock"],b["add"]]
        assert a["midpoint_chart"]==b["old_chart"] and a["peer"]==b["peer"]
        assert a["moving"]["role"]==b["mover"] and a["moving"]["clocks"]==b["anchor_move_clocks"]
        neighbours=[a["other"][k] for k in ("previous","next")]
        assert neighbours==[list(p) for p in zip(b["peer_neighbour_clocks"],b["peer_neighbour_events"],strict=True)]
        assert b["status"]=="no four-MOVE topology" and not b["variants"]
        blockers=[side for side,(_,event) in zip(("before","after"),neighbours,strict=True) if event[0]!="MOVE"]
        assert blockers and all(event[0] in ("ADD","MOVE") for _,event in neighbours)
        sides["both" if len(blockers)==2 else blockers[0]]+=1
        results.append(dict(key=a["key"],anchor_clock=b["clock"],mover_moves=[a["moving"]["previous"],a["moving"]["next"]],
            peer=a["peer"],peer_neighbours=neighbours,blocking_sides=blockers))
    assert len(results)==10
    print(dumps(dict(head=forward["head"],input_sha256=PINS,matched=10,no_route=10,
        actual_offset_count=0,geometry="skipped",remaining=0,blocking_sides=sides,results=results),
        indent=2,sort_keys=True))


if __name__=="__main__":
    assert __debug__
    main(Path(sys.argv[1]))
