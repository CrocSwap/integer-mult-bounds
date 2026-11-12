"""Quote a distinct odd/odd union using the authenticated signed comparator."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/R85-PRICE.json": "33aad506112912ddf0721a2b007d9194eaa02e5792aceda2f9774f8838511262",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}

def read(name):
    raw = (ROOT / name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError(f"changed {name}")
    return raw

def main():
    assert __debug__
    p = json.loads(read("inputs/R85-PRICE.json"))
    read("inputs/pricing.py")
    cost = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    assert p["copies"] == 17 and p["ports"] == 8
    jobs = p["odd_jobs"]
    left = sorted(int(t) for t, (_, stages) in jobs.items() if stages == [8])
    right = sorted(int(t) for t, (_, stages) in jobs.items() if stages == [9])
    assert (left,right) == ([1339,1340],[2970,2971]) and len(jobs) == 4
    paid = Counter({int(r): n for r,n in p["complete_paid"].items()})
    baseline = Counter({int(r): n for r,n in p["complete_targets"].items()})
    baseline.subtract(paid)
    values = dict(incumbent=Q(p["crossing"][1]),probe=Q(p["price_probe"]),target=Q(p["moonshot"]))
    cases = {}
    for retained in (16,18):
        cases[retained] = {}
        for count in (1,2):
            gain = {9:16*count,retained:-8*count}
            edited = baseline.copy()
            edited.update(gain)
            cases[retained][count] = {
                "paid_delta": {r:-n for r,n in gain.items()},
                "paid":sum(paid.values())-8*count,
                "new_rank_surplus":sum(r*n for r,n in edited.items()),
                "gross": {k:list(map(str,cost(gain,x))) for k,x in values.items()},
                "complete": {k:list(map(str,cost(edited,x))) for k,x in values.items()},
            }
    print(json.dumps(dict(head=p["head"],caller=p["caller_head"],ports=p["ports"],copies=p["copies"],
                          input_sha256=PINS,caller_sha256=p["caller_sha256"],odd_jobs=jobs,
                          pairs=list(product(left,right)),max_compatible_pair_relaxation=2,
                          cases=cases,points={k:str(v) for k,v in values.items()}),indent=2,sort_keys=True))

if __name__ == "__main__":
    main()
