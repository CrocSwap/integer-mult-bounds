"""Select sixteen previously unresolved rank-seven bank classes."""
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PINS = {
    "ALIASES.json":"ba0120da7b05b948b1e8294c6b3844deade2c40be1f2e0abf4e0beef395f5c85",
    "round102-input/lead/GEOMETRY.json":"2d0dee60998d168d2eff4c16794176c5ec3b4d18ffa8bde247602035f1b68129",
}


def main():
    inputs = {}
    for path,pin in PINS.items():
        raw = (ROOT/path).read_bytes()
        if sha256(raw).hexdigest()!=pin:
            raise ValueError(f"changed dependency {path}")
        inputs[path] = json.loads(raw)
    alias,geo = inputs.values()
    assert alias["timeout"] is None and not alias["unvisited"]
    assert len(alias["classes"])==45 and len(geo["all_representatives"])==65
    bank_by_key = {tuple(r["key"]):r for r in geo["all_representatives"]}
    by_chart = defaultdict(list)
    for cls in alias["classes"]:
        if not cls["reuses"]:
            row=bank_by_key[tuple(cls["keys"][0])]
            assert not row["owned"]
            by_chart[row["key"][1]].append(row|{"aliases":cls["keys"][1:]})
    assert len(by_chart)==5 and sum(map(len,by_chart.values()))==29
    for group in by_chart.values():
        group.sort(key=lambda r:(-len(r["public"]),r["key"]))
    order = [group[i] for i in range(max(map(len,by_chart.values())))
             for _,group in sorted(by_chart.items()) if i<len(group)]
    chosen=order[:16]
    assert len({row["key"][0] for row in chosen})==len(chosen)==16
    print(json.dumps(dict(head=geo["head"],pins=PINS,scope="Five charts round-robin, widest unresolved bank first, earliest cut on ties",
        selected=chosen,unselected=order[16:],counts=Counter(row["key"][1] for row in chosen),
        caps={"modular_cases":16,"modular_seconds":25,"exact_cases":4,"exact_seconds":35}),
        indent=2,sort_keys=True))


if __name__=="__main__":
    assert __debug__
    main()
