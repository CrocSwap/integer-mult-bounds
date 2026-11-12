"""Test the frozen sixteen rank-seven-cohort banks by exact exterior minors."""
from collections import Counter
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import sys
from time import monotonic

PINS = {
    "lead/PRICE.json": "4e0d6436eb4fc6a9dfa34c05ba98aacc63e3a8bf7214145dd9f9254763c5a13e",
    "lead/GEOMETRY.json": "2d0dee60998d168d2eff4c16794176c5ec3b4d18ffa8bde247602035f1b68129",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/exterior_rank56.py": "9fceafc627fe3781bcb8d5229eaefebc557de613f0d4723aa1d36ce4ab9954ac",
}


def main():
    assert __debug__
    deadline = monotonic() + 22
    root = Path(sys.argv[1])
    raw = {}
    for name, digest in PINS.items():
        raw[name] = (root/name).read_bytes()
        if sha256(raw[name]).hexdigest() != digest:
            raise ValueError(f"changed dependency: {name}")
    engine = run_path(str(root/"inputs/exterior_rank56.py"))
    unique = engine["unique"]
    price = json.loads(raw["lead/PRICE.json"], object_pairs_hook=unique)
    geometry = json.loads(raw["lead/GEOMETRY.json"], object_pairs_hook=unique)
    word = json.loads(decompress(raw["inputs/7334-WORD.json.gz"]), object_pairs_hook=unique)
    assert geometry["head"] == price["head"] == engine["HEAD"]
    assert geometry["status"] == "EXHAUSTED" and geometry["eligible_bank_count"] == 65
    assert len(geometry["selected"]) == 16 and len(price["cohort"]) == 5
    selected = {tuple(row["key"]): row for row in geometry["selected"]}
    controls = engine["controls"]()
    result, events = engine["sweep"](word, list(selected), set(price["cohort"]), deadline)
    assert all(all(row[k] == selected[key][k] for k in ("key","public","owned","pivots"))
               for key,row in result.items())
    rows = [result[k] for k in selected if k in result]
    print(json.dumps({"head":price["head"],"pins":PINS,"event_count":events,"case_cap":16,"runner_seconds":25,
        "controls":controls,"rows":rows,"counts":Counter(row["disposition"] for row in rows),
        "unvisited":[list(k) for k in selected if k not in result],
        "unselected":geometry["unvisited_keys"]},indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
