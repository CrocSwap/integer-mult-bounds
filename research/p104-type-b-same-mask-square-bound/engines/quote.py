"""Price repeated Type B even singleton calls from authenticated metadata."""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from runpy import run_path
import sys

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
TARGET = Fraction("0.0040075385047236")
PINS = {
    "PRICE.json": "33aad506112912ddf0721a2b007d9194eaa02e5792aceda2f9774f8838511262",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "inputs/7334-READBACK.json": "337668788fb39ec9575887f9c5faf438a880471f78d936357dabf7deeac5de82",
    "inputs/7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/7334-ADMITTED.json": "c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13",
}


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def main(root):
    data = {}
    for path, pin in PINS.items():
        raw = (root / path).read_bytes()
        if sha256(raw).hexdigest() != pin:
            raise ValueError("changed dependency: " + path)
        if path.endswith(".json") and path != "inputs/7113-CALLER.json":
            data[path] = json.loads(raw, object_pairs_hook=unique)
    stock, readback, admission = (data[path] for path in
        ("PRICE.json", "inputs/7334-READBACK.json", "inputs/7334-ADMITTED.json"))
    assert stock["head"] == readback["head"] == admission["head"] == HEAD and admission["exit"] == 0
    assert stock["caller_head"] == readback["caller_head"] == admission["caller"] == CALLER
    assert stock["caller_sha256"] == admission["caller_sha256"] == PINS["inputs/7113-CALLER.json"]
    lo, hi = map(Fraction, admission["crossing"])
    assert (lo, hi) == tuple(map(Fraction, stock["crossing"]))
    assert (lo, hi) == tuple(map(Fraction, readback["new_raw_interval"]))
    assert stock["ports"] == 8 and stock["copies"] == readback["copies"] == 17
    paid, targets = (Counter({int(r): n for r, n in readback[k].items()}) for k in ("paid", "targets"))
    signed = targets.copy()
    signed.subtract(paid)
    assert sum(paid.values()) == 110519 and sum(targets.values()) == 22461
    assert sum(r*n for r,n in signed.items()) == readback["rank_surplus"] == 1424
    assert not readback["empty_root_credits"]

    groups = defaultdict(list)
    for c, (role, mask) in stock["even_jobs"].items():
        if len(mask) == 1:
            groups[role, mask[0]].append(int(c))
    repeated = {key: sorted(clocks) for key, clocks in groups.items() if len(clocks)>1}
    cases = [dict(earlier=a,later=b,role=role,stage=stage) for (role,stage),clocks in sorted(repeated.items())
             for a,b in combinations(clocks,2)]
    assert len(cases) == len(repeated) == 9 and all(len(v)==2 for v in repeated.values())
    assert all(case["role"] == 0 for case in cases)
    assert len({case[key] for case in cases for key in ("earlier","later")}) == 18
    assert all(a["later"]<b["earlier"] for a,b in zip(cases,cases[1:]))
    cases.sort(key=lambda r:(r["later"]-r["earlier"],r["earlier"]))
    count = len(cases)
    assert (cases[0]["earlier"],cases[0]["later"],cases[0]["stage"]) == (4646,4660,17)

    cost = run_path(str(root / "inputs/pricing.py"))["cost"]
    probe = hi + Fraction(1,10**9)
    assert cost(signed,probe)[1]<0

    def quote(deletions, k):
        changed = signed.copy()
        changed[8] += deletions
        assert paid[8] >= deletions
        gross = cost({8:deletions}, k)
        margin = cost(changed, k)
        return dict(paid_delta={8:-deletions}, productive_delta={}, gross=list(map(str,gross)),
                    complete_margin=list(map(str,margin)), signed_surplus=1424+8*deletions)

    price = {label:{
        "one_edit_at_incumbent":quote(m,hi), "one_edit_at_probe":quote(m,probe),
        "whole_at_incumbent":quote(m*count,hi), "whole_at_moonshot":quote(m*count,TARGET),
        "complex_moonshot_minimum_edits_necessary":int((-cost(signed,TARGET)[1])//cost({8:m},TARGET)[1])+1,
    } for label,m in (("one_retained_rank8_square",8),("all_ordinary_square",16))}
    assert Fraction(price["one_retained_rank8_square"]["one_edit_at_probe"]["complete_margin"][0])>0
    print(json.dumps(dict(head=HEAD,caller_head=CALLER,source_sha256=PINS,
        source_scope="R85 exact Type B even singleton metadata only; caller hashed without decoding",
        cases=cases,whole_disjoint_cases=count,price=price,old_crossing=list(map(str,(lo,hi))),price_probe=str(probe),
        old_paid=paid,old_targets=targets,moonshot=str(TARGET),bit_premise=readback["bit_premise"],
        old_moonshot_margin=list(map(str,cost(signed,TARGET))),
        limits=dict(projector_keys=9,projector_seconds=20,formal_keys=1,formal_seconds=60,physical_keys=1,physical_seconds=90)),
        indent=2,sort_keys=True))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
