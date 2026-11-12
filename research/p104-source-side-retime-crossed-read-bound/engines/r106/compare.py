"""Compare all R106 pre-event cut classifications across both exact engines."""
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PINS = {"inputs/RETIMING.json":"75569c300403795c4859263f823dee3c165979afaf32b8943201e31b1a050120",
        "RESULT.json":"955a87e4ff6c2f29d2d5d4dd55c57ff2774cffa2b086cf9a00ce15de90651662"}


def read(name):
    raw = (ROOT/name).read_bytes()
    assert sha256(raw).hexdigest() == PINS[name], name
    return loads(raw)


def cells(rows):
    return {t:tuple(values) for lo,hi,*values in rows for t in range(lo,hi+1)}


def main():
    assert __debug__
    primary,reverse = map(read,PINS)
    assert primary["head"] == reverse["head"]
    assert not primary["candidates"] and not reverse["survivors"]
    assert primary["timeout"] is reverse["timeout"] is None
    count = 0
    blocked = []
    for a,b in zip(primary["rows"],reverse["rows"],strict=True):
        assert a["key"] == b["pair"] and a["recipient"] == b["recipient"] and a["old_add"] == b["old_add"]
        for i,j in zip(a["sides"],b["cuts"],strict=True):
            assert i["target_chart"] == j["required_chart"]
            x,y = cells(i["intervals"]),cells(j["intervals"])
            assert set(x) == set(y)
            for t,(actual,reason,barrier) in y.items():
                lead,chart = x[t]
                assert chart == actual
                assert lead == ("wrong chart" if reason == "different chart" else "recipient contact barrier")
                if reason != "different chart":
                    assert barrier in a["nearest_barriers"]
                    blocked.append((t,barrier))
            count += len(y)
    assert count == 33560 and len(blocked) == 43
    print(dumps(dict(pins=PINS,agreement=True,typed_cut_count=count,chart_match_barriers=blocked),indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
