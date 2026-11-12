"""Price a nested carrier split before reading the literal word."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "../lead/PRICE.json": "88ff264d2744dee9bc0bc9ecfe25fc4e53f30958c8c947d16e4df87c908e5c65",
}

def read(name):
    raw = (ROOT / name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError(f"changed {name}")
    return raw

def main():
    assert __debug__
    p = json.loads(read("inputs/R92-PRICE.json"))
    prior = json.loads(read("../lead/PRICE.json"))
    read("inputs/pricing.py")
    cost = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    assert p["head"] == prior["head"] and p["caller_head"] == prior["caller"]
    incumbent, probe, target = (Q(p[k]) for k in ("old_crossing_upper", "probe", "moonshot"))
    net = Counter({int(r): n for r, n in p["old_targets"].items()})
    net.subtract({int(r): n for r, n in p["old_paid"].items()})
    cells = []
    for r in range(1, 7):
        for s in range(1, 10-r):
            gain = {r+s: 17, s: -17}
            edited = net.copy()
            edited.update(gain)
            gross = cost(gain, incumbent)
            at_probe = cost(edited, probe)
            assert gross[0] > 0 and at_probe[0] > 0
            cells.append(dict(r=r,s=s,paid_delta={r+s:-17,s:17},rank_surplus=1424+17*r,
                              gross=list(map(str,gross)),complete_probe=list(map(str,at_probe)),
                              fixed_target_complete_upper=str(cost(edited,target)[1])))
    print(json.dumps(dict(pins=PINS, head=p["head"], caller=p["caller_head"], paid=110519,
                          productive=22461, whole_gross_upper=prior["whole_gross_upper"],
                          fixed_target_upper=prior["fixed_target_upper"],
                          maximum_one_edit=max(cells,key=lambda c:Q(c["gross"][1])), cells=cells),
                     sort_keys=True, indent=2))

if __name__ == "__main__":
    main()
