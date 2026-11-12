"""Compare the R121 signed contact, rail, geometry and price receipts."""
from hashlib import sha256
from json import dumps,loads
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PINS={
    "lead/RESULT.json":"ea1ef4e57573f6bc3ae64e7fe2f4b210c60ec5d2b153ced9b6b165c844f45f45",
    "independent/RESULT.json":"93d35f1d581a8648c5d17e79ff2cd5c11372c04a43dd2682b9d7865a54a56cfc",
}


def read(name):
    raw=(ROOT/name).read_bytes()
    if sha256(raw).hexdigest()!=PINS[name]:
        raise ValueError("changed dependency "+name)
    return loads(raw)


def main():
    assert __debug__
    primary,independent=map(read,PINS)
    assert primary["head"]==independent["head"] and primary["caller"]==independent["caller"]
    assert primary["pins"]==independent["pins"]
    assert primary["literal_events"]==independent["progress"]["events"]==76466
    assert primary["counts"]==independent["counts"]=={"nesting exclusion":4}
    assert not independent["unvisited"] and independent["timeout"] is None
    rows=[]
    for w in primary["results"]:
        assert w["exact_middle_contacts"]
        for case in w["cases"]:
            i,= [x for x in independent["rows"] if x["key"]==w["key"] and x["chart"]==case["chart"]]
            assert (i["key"][2],i["peer"])==tuple(w["roles"])
            assert i["matrix"]==[[int(v) for v in a] for a in w["matrix"]]
            assert i["peer_old_ranks"]==w["old_peer_ranks"]==[0,1]
            for rail in w["rails"]:
                b,inside,a=i["rails"][str(rail["role"])]
                assert b[:2]==rail["before"] and a[:2]==rail["after"]
                assert [e[:2] for e in inside]==rail["inside"]
                assert [b[-2],a[-1]]==rail["outer"]
            assert i["price"]==case["price"] and i["failed_legs"]==case["failed_legs"]
            u=i["unique_common_span"]
            assert u["lower_join_basis"]==u["upper_meet_basis"]==[50]
            assert u["upper_union_rank"]==3 and u["intersection_rank"]==1
            rows.append({"key":w["key"],"chart":case["chart"],"failure":i["failed_legs"][0],
                "outside_witness":[l["witness"] for l in i["legs"] if not l["valid"]][0]})
    assert len(rows)==4
    print(dumps(dict(pins=PINS,agreement=rows,unique_span_basis=[50],preserved_ranks=[1,1,0,1],unresolved=0),
        indent=2,sort_keys=True))


if __name__=="__main__":
    main()
