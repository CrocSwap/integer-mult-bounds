"""Compare all exact R123 two-edit derivative witnesses."""
from hashlib import sha256
from json import dumps,loads
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PINS={
    "lead/RESULT.json":"4803b929abd8e1d0e9600bb4713e1b5111c61425571492c9e0488f59c2678a6d",
    "independent/RESULT.json":"a44744be08ffd75f02ffbd9c96799f8a995a111b04a136f71f4c4b171a17d5b8",
}


def checked(name):
    raw=(ROOT/name).read_bytes()
    if sha256(raw).hexdigest()!=PINS[name]:
        raise ValueError("changed dependency "+name)
    return loads(raw)


def main():
    assert __debug__
    lead,independent=map(checked,PINS)
    fields=("head","caller","q","body","cap_cases","cap_seconds","counts","unvisited","timeout")
    assert all(lead[k]==independent[k] for k in fields)
    assert lead["events"]==independent["progress"]["caller_events"]==4783
    assert lead["pins"]["plan/PRICE.json"]==independent["pins"]["plan/PRICE.json"]
    assert lead["pins"]["inputs/7113-CALLER.json.gz"]==independent["pins"]["inputs/7113-CALLER.json.gz"]
    assert len(lead["results"])==len(independent["results"])==210
    fields=("fusions","even_mask","witness","nonzero_coordinates","status")
    for a,b in zip(lead["results"],independent["results"],strict=True):
        assert all(a[k]==b[k] for k in fields)
    priority=independent["results"][:2]
    assert all(r["direct_tangent"] and r["witness"]==[36,36,"16"] for r in priority)
    print(dumps(dict(pins=PINS,exact_witness_agreement=210,exact_nonzero_count_agreement=210,
        direct_endpoint_tangent_priority=priority,unequal_mask_excluded=11728,unresolved=0),
        indent=2,sort_keys=True))


if __name__=="__main__":
    main()
