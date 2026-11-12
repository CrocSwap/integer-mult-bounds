"""Frozen fixed-host J reuse price, without decoding the literal caller."""
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

PINS = {
    "inputs/PREVIOUS-PRICE.json": "bbc486a3eb0e2aed03dd09f400fa94de1a59312058a9826880999155b10453bf",
    "inputs/7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CLOCKS = (1516, 1580, 1659, 1721)


def main():
    root=Path(__file__).resolve().parent
    values={}
    for name, pin in PINS.items():
        raw=(root/name).read_bytes()
        if sha256(raw).hexdigest()!=pin:
            raise ValueError(f"changed dependency {name}")
        values[name]=raw
    old=json.loads(values["inputs/PREVIOUS-PRICE.json"])
    assert old["head"]==HEAD and old["type_a_ports"]==96
    assert old["caller_sha256"]==PINS["inputs/7113-CALLER.json"]
    old_bill={r:int(n) for r,n in old["old_paid"].items()}
    old_bill["1"]-=192
    two=old["by_number_of_reused_queries"]["2"]
    assert two["paid"]==old_bill and two["paid_delta"]=={"1":-192}
    assert two["target_delta"]=={} and sum(old_bill.values())==110327
    assert all(Fraction(x)>0 for x in two["complete_margin_at_old_crossing"])
    keys=[list(a)+[b] for a,b in product(combinations(CLOCKS,2),range(1,18))]
    print(json.dumps(dict(head=HEAD, input_sha256=PINS, scope="two QUERYs converted to even ADDs with one existing J recompiled, fixed signed rank-two invoice and ordinary adapters; all other events fixed",
        one_pair_price=two, proposed_pair_clocks=CLOCKS, keys=keys, key_cap=102, runner_cap_seconds=20,
        one_pair_optimistic_gross=192, disjoint_two_pair_optimistic_gross=384), indent=2, sort_keys=True))


if __name__=="__main__":
    main()
