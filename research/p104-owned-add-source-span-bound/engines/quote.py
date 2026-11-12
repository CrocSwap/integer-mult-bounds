"""Full predecode price for replacing the source of one owned destination ADD."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT=Path(__file__).resolve().parent
PINS={"inputs/R82-PRICE.json":"82baf8740dfc695d304602d92bd3888961c965f76a5bcb4784cbd4f9726e7ee6",
      "inputs/R82-CONTACTS.json":"664c3824078877c6b9e6ace20d8b03202a250e67e0f09b66a7304ce1ab8a5d00",
      "inputs/READBACK.json":"337668788fb39ec9575887f9c5faf438a880471f78d936357dabf7deeac5de82",
      "inputs/pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182"}


def integer_histogram(values):
    return Counter({int(r):c for r,c in values.items()})


def main():
    inputs={}
    for key,want in PINS.items():
        payload=(ROOT/key).read_bytes()
        if sha256(payload).hexdigest()!=want:
            raise ValueError(f"changed dependency: {key}")
        if key.endswith(".json"):
            inputs[key]=loads(payload)
    prev=inputs["inputs/R82-PRICE.json"]
    contacts=inputs["inputs/R82-CONTACTS.json"]
    old=inputs["inputs/READBACK.json"]
    assert old["head"]==prev["head"]==contacts["head"]
    assert contacts["status"]=="EXHAUSTED" and not contacts["survivors"]
    group=[p for p in prev["candidates"] if p["owner_access"]=="destination"]
    assert {p["owner"] for p in group}=={1501,1531,1532}
    assert all(a["move_clocks"][1]<b["move_clocks"][0] for a,b in zip(group,group[1:]))
    keys=[[p["owner"],*p["move_clocks"],end,c] for p in group
          for end,(lo,hi) in sorted(p["cut_windows_pre_event"].items()) for c in range(lo,hi+1)]
    assert len(keys)==33 and {tuple(x) for x in keys}<={tuple(row["key"]) for row in contacts["decisions"]}
    paid,targets=(integer_histogram(old[key]) for key in ("paid","targets"))
    delta=Counter()
    for p in group:
        delta.update(integer_histogram(p["paid_delta"]))
        assert not p["target_delta"] and p["quote"]["paid_positions"]==110502
    modified=paid.copy()
    modified.update(delta)
    signed=targets.copy()
    signed.subtract(modified)
    assert sum(modified.values())==110468 and sum(r*c for r,c in signed.items())==1424
    f=run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    upper=Fraction(old["new_raw_interval"][1])
    probe=upper+Fraction(1,10**9)
    gross=f({r:-c for r,c in delta.items()},upper)
    assert 0<gross[0]<=gross[1]<1
    changed=f(signed,probe)
    assert changed[0]>0
    with_extra=signed.copy()
    with_extra[1]-=1
    assert f(with_extra,upper)[1]<0
    interval=lambda x:[str(i) for i in x]
    print(dumps(dict(head=old["head"],word_sha256=prev["word_sha256"],input_sha256=PINS,
        case_cap=33,time_cap_seconds=20,build_cap=1,candidates=group,keys=keys,
        gross_upper_all_three=interval(gross),complete_probe_margin=interval(changed),
        extra_rank_one_upper=interval(f(with_extra,upper)),paid_all_three=dict(modified),
        scope="Keep all fixed paid itineraries except fuse one destination-owned pair. Match its literal source value by exact existing same-chart donor rows. Optimistically free added ordinary work, no new paid operation. No word decoded."),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
