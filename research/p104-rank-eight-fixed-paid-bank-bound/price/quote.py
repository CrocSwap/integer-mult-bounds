"""Preprice fixed-paid rank-eight splits for the 3-to-245 helper cohort."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/ADMITTED.json": "c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13",
    "inputs/READBACK.json": "337668788fb39ec9575887f9c5faf438a880471f78d936357dabf7deeac5de82",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "inputs/7314-HELPERS.json": "bf353b3e05d0bf5fe3e49c15673c4cb9203251329bd594009303541cf7fecc09",
    "inputs/7334-CHANGED.json": "f4d3f6ca2d87f8cd68c01ac9f77b69bd5a796f92bd567cea8afe3ac7c72e8e4b",
}


def unique(pairs):
    out = dict(pairs)
    if len(out) != len(pairs):
        raise ValueError("duplicate input key")
    return out


def main():
    assert __debug__
    data = {}
    for name, pin in PINS.items():
        raw = (ROOT / name).read_bytes()
        if sha256(raw).hexdigest() != pin:
            raise ValueError(f"changed dependency {name}")
        if name.endswith(".json"):
            data[Path(name).stem] = json.loads(raw, object_pairs_hook=unique)
    a, b, h, x = (data[k] for k in ("ADMITTED", "READBACK", "7314-HELPERS", "7334-CHANGED"))
    assert a["head"] == b["head"] == "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert a["exit"] == 0 and a["caller"] == b["caller_head"] and b["copies"] == 17
    assert len(h["rows"]) == 1101 and h["complete"] and len(x["roles"]) == 14
    protected = set(x["roles"]) | {863, 1355, 1531, 1567, 1568}
    cohort = sorted(r["role"] for r in h["rows"] if r["role"] not in protected
                    and (r["initial"], r["final"], r["old_productive_rank"]) == (3, 245, 8))
    assert len(cohort) == len(set(cohort)) == 15
    paid, target = [Counter({int(k): v for k, v in b[name].items()}) for name in ("paid", "targets")]
    old = target.copy()
    old.subtract(paid)
    assert (sum(paid.values()),sum(target.values()),sum(k*v for k,v in old.items())) == (110519,22461,1424)
    assert target[8] >= 17*len(cohort) and not b["empty_root_credits"]
    change = {4:34,8:-17}
    new = old.copy()
    new.update(change)
    cost = run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    crossing = Q(a["crossing"][1])
    probe = crossing + Q(1,10**9)
    moonshot = Q("0.0040075385047236")
    assert cost(old,probe)[1] < 0 < cost(new,probe)[0]
    def price(k):
        delta = cost(change,k)
        incumbent = cost(old,k)
        return {"old_margin":list(map(str,incumbent)), "gross_one":list(map(str,delta)),
                "whole_15_upper":str(15*delta[1]),"complete_15_upper":str(incumbent[1]+15*delta[1])}
    print(json.dumps({"head":a["head"],"caller":a["caller"],"pins":PINS,"cohort":cohort,
        "word_sha256":a["inputs"]["WORD.json.gz"],"productive_delta":change,"paid_delta":{},
        "incumbent":str(crossing),"probe":str(probe),"moonshot":str(moonshot),
        "at_incumbent":price(crossing),"at_target":price(moonshot),
        "event_cap":76466,"geometry_runner_seconds":20,"support_cap":16,"support_runner_seconds":25,
        "exact_cap":4,"exact_runner_seconds":35,"build_cap":1},indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
