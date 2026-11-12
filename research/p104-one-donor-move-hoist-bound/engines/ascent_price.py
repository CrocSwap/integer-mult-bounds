"""One-owned-ascent deletion price including restored chart lifetime."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "inputs/NATIVE-RESULT.json": "c6d1b00a83185ab0062397b363258b1f3f6685d755e9c1d4f7d3e7e511240812",
}


def read(p):
    raw = (ROOT/p).read_bytes()
    assert sha256(raw).hexdigest()==PINS[p]
    return raw


def main():
    assert __debug__
    b=loads(read("inputs/R92-PRICE.json"))
    source=loads(read("inputs/NATIVE-RESULT.json"))["native"]
    read("inputs/pricing.py")
    cost=run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    ranks={int(r):n for r,n in source["rises"].items()}
    assert (sum(ranks.values()),sum(r*n for r,n in ranks.items()))==(23,56)
    stock=Counter({int(r):n for r,n in b["old_targets"].items()})
    stock.subtract({int(r):n for r,n in b["old_paid"].items()})
    assert sum(r*n for r,n in stock.items())==1424
    upper=Q(b["old_crossing_upper"])
    probe=Q(b["probe"])
    cases={}
    for d in ranks:
        trial=stock.copy()
        trial[d]+=17
        cases[d]={"gross":cost({d:17},upper),"complete_probe":cost(trial,probe),
                  "rank_surplus":1424+17*d,"delta_paid":{d:-17}}
        assert cases[d]["complete_probe"][0]>0
    ordinary_baseline=782715464
    # Four lifetime routing slots, two additionally reserved chart moves as
    # ordinary maps, COPY +/-1 (16), INIT/CLEAR (4). No credit for removed routes.
    ordinary_upper=ordinary_baseline+17*(6*1000+16+4)
    assert ordinary_upper<10**9
    print(dumps({"pins":PINS,"head":b["head"],"caller":b["caller_head"],"all_owned_rise_stock":ranks,
        "total_relaxed_gross":cost({d:17*n for d,n in ranks.items()},upper),
        "max_one_gross":cases[max(ranks)]["gross"],"cases":cases,
        "ordinary_source_units_upper":ordinary_upper,"extra_lifetimes_per_native":1,
        "extra_macros_per_native":3,"extra_scalar_services":17*3*32,"extra_map_slots_reserved":6*17,
        "productive_positions":22461,"added_paid_children":0},default=str,sort_keys=True,indent=2))


if __name__=="__main__":
    main()
