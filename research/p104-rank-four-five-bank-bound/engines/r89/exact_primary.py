"""Rational two-sided pairing for the frozen six-bank continuation."""
from collections import Counter
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import sys
from time import monotonic

PINS = {
    "lead/SELECTION.json": "27a14af96296f0f2d162c77aa38e4051f3aaf8a8156dd654b414dd1196a6d597",
    "inputs/PRICE.json": "b4bf8e00a8289f03b1da731fb3ab563a771d88d875e0da73acf70954df2f2c56",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/paired_rank.py": "d1b7c34e6f8c8a7b810414762015e6e300a8292422af66ff671ae09741141f09",
    "inputs/paired_support.py": "38c796cbe1a73f386177faf88cd53294d4b911f6cde7fd47cd9fcef3b558373f",
}


def main():
    deadline = monotonic() + 32
    root = Path(sys.argv[1])
    raw = {}
    for path, pin in PINS.items():
        value = (root/path).read_bytes()
        if sha256(value).hexdigest() != pin:
            raise ValueError(f"changed dependency: {path}")
        raw[path] = value
    select = json.loads(raw["lead/SELECTION.json"])
    price = json.loads(raw["inputs/PRICE.json"])
    word = json.loads(decompress(raw["inputs/7334-WORD.json.gz"]))
    rank, solve = [run_path(str(root/"inputs"/x)) for x in ("paired_rank.py", "paired_support.py")]
    cohort, _ = solve["initial_groups"](word)
    assert set(price["endpoint_cohort"]) == cohort
    controls = solve["controls"]()
    banks = {r["key"][0]: r["public"] for r in select["selected"]}
    assert len(banks) == 6 and all(not r["owned"] for r in select["selected"])
    prefix = rank["side"](word, banks, cohort, deadline, False)
    open_banks = {t: banks[t] for t, rows in prefix.items() if any(c for _, c in rows)}
    suffix = rank["side"](word, open_banks, cohort, deadline, True) if open_banks else {}
    results, pending = [], []
    for row in select["selected"]:
        t = row["key"][0]
        if t not in prefix or (t in open_banks and t not in suffix):
            pending.append(row["key"])
            continue
        f = prefix[t]
        record = {**row, "pure_prefix_dimension": len(f),
                  "nonzero_prefix_images": sum(bool(c) for _, c in f)}
        if t not in open_banks:
            results.append(record | dict(status="no nonzero pure prefix"))
            continue
        s = suffix[t]
        record.update(pure_suffix_dimension=len(s), nonzero_suffix_images=sum(bool(d) for _, d in s))
        if not any(d for _, d in s):
            results.append(record | dict(status="no nonzero pure suffix"))
            continue
        try:
            pair = solve["paired"](f, s, deadline)
        except solve["Capped"]:
            pending.append(row["key"])
            continue
        if pair is None:
            results.append(record | dict(status="no unit pairing"))
            continue
        assert solve["dot"](pair["a"],pair["b"]) == solve["dot"](pair["c"],pair["d"]) == 1
        results.append(record | dict(status="exact paired support",
            witness={k: {j: str(x) for j,x in v.items()} for k,v in pair.items()}))
    print(json.dumps(dict(head=price["head"],pins=PINS,controls=controls,exact_cap=6,seconds_cap=32,
        results=results,counts=Counter(r["status"] for r in results),selected_unresolved=pending,
        unselected=select["unselected"]), indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
