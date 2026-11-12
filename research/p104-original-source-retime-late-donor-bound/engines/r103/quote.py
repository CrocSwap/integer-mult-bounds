"""Freeze original-public-source retiming stock before word decode."""
from collections import defaultdict
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN = "ac5ecb17f0e9f3c068423998b350a78c1a4769b6f61b50838be5f3e0d0b1a00c"


def main():
    raw = (ROOT/"inputs/R101-PRICE.json").read_bytes()
    assert sha256(raw).hexdigest()==PIN
    parent = json.loads(raw)
    rows = [r for r in parent["candidates"] if r["add"][1][2]<1501]
    assert len(rows)==5 and len(parent["candidates"])==6
    stock = defaultdict(list)
    for row in rows:
        stock[row["key"][2]].append(row)
    assert len(stock)==4
    for group in stock.values():
        if len(group)>1:
            assert len(group)==2 and set(group[0]["key"][:2])&set(group[1]["key"][:2])
    cuts = sum(2*(r["key"][1]-r["key"][0]-1) for r in rows)
    assert cuts==18864
    one = max(Q(r["quote"]["net"][1]) for r in rows)
    total = sum(max(Q(r["quote"]["net"][1]) for r in group) for group in stock.values())
    assert all(Q(r["quote"]["extra_rank_one_upper"])<0 for r in rows)
    out={"head":parent["head"],"caller_head":parent["caller_head"],"kappa":parent["kappa"],
         "word_sha256":parent["word_sha256"],"payload_sha256":parent["payload_sha256"],
         "parent_price_sha256":PIN,"candidates":rows,"whole_net_upper":str(total),
         "one_net_upper":str(one),"complete_target_upper":parent["whole_target_margin_upper"],
         "full_paid_after_one":parent["one_new_paid"],"productive":parent["targets"],
         "limits":{"events":76466,"pair_windows":5,"typed_cuts":cuts,"runner_seconds":20,
                   "prototype_cases":1,"prototype_seconds":120}}
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    assert __debug__
    main()
