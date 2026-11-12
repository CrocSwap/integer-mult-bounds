"""Test the frozen sixteen rank-eight-cohort banks by exact exterior minors."""
from collections import Counter
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import sys
from time import monotonic

PINS = {
    "price/PRICE.json": "a78be64c3e3ae8a0e532237c4dd3541aa9ad3fcbbc3c25d79c8a03fb7e07c525",
    "lead/GEOMETRY.json": "c6f9f018df8b58fcdf4f44356bd59bcac6d411b7845104ff4ad372ed4a95cfbd",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/exterior_minor.py": "b25fef5432d8ea9cff9eecc422cf07ccf7473568084de3e8d3d1b5224793504d",
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
    engine = run_path(str(root/"inputs/exterior_minor.py"))
    unique = engine["unique"]
    price = json.loads(raw["price/PRICE.json"], object_pairs_hook=unique)
    geometry = json.loads(raw["lead/GEOMETRY.json"], object_pairs_hook=unique)
    word = json.loads(decompress(raw["inputs/7334-WORD.json.gz"]), object_pairs_hook=unique)
    assert geometry["head"] == price["head"] == engine["HEAD"]
    assert geometry["status"] == "EXHAUSTED" and geometry["eligible_bank_count"] == 326
    assert len(geometry["selected"]) == 16 and len(price["cohort"]) == 15
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
