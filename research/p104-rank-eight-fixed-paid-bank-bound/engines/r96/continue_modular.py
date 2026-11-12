"""Check only the 310 banks outside the first R96 modular cap."""
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
    "lead/REMAINING.json": "3597499663a57702856945e91214a65e1d0f94db8643b93c0234c2bbf9291b1a",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/exterior_minor.py": "b25fef5432d8ea9cff9eecc422cf07ccf7473568084de3e8d3d1b5224793504d",
    "inputs/reverse_engine.py": "751d5d0c4c665c8768ff69bcf939700d3be2f989c59f09af3a4aa14d3c1ebbc4",
}


def main():
    assert __debug__ and sys.version_info[:2] == (3,12)
    deadline = monotonic() + 22
    root = Path(sys.argv[1])
    inputs = {}
    for name, expected in PINS.items():
        data = (root/name).read_bytes()
        if sha256(data).hexdigest() != expected:
            raise ValueError(f"changed dependency: {name}")
        inputs[name] = data
    engine = run_path(str(root/"inputs/exterior_minor.py"))
    reverse = run_path(str(root/"inputs/reverse_engine.py"))
    unique = engine["unique"]
    price = json.loads(inputs["price/PRICE.json"],object_pairs_hook=unique)
    previous = json.loads(inputs["lead/REMAINING.json"],object_pairs_hook=unique)
    assert price["head"] == previous["head"] == engine["HEAD"]
    keys = [tuple(k) for k in previous["unvisited_prefix"]]
    assert len(keys) == len(set(keys)) == previous["next_modular_cases"] == 310
    assert not set(keys) & set(map(tuple,previous["dual_drops_requiring_rational"]))
    word = json.loads(decompress(inputs["inputs/7334-WORD.json.gz"]),object_pairs_hook=unique)
    cohort = set(price["cohort"])
    controls = reverse["controls"](engine)
    prefix, visited_prefix = engine["sweep"](word,keys,cohort,deadline)
    remaining = [prefix[key] for key in keys if key in prefix and prefix[key]["disposition"] == "rank drop"]
    suffix, visited_suffix = reverse["sweep"](word,remaining,cohort,engine,deadline)
    rows = []
    for key in keys:
        p, s = prefix.get(key), suffix.get(key)
        if p and p["disposition"] == "excluded":
            status = "prefix_exclusion"
        elif s:
            status = "suffix_exclusion" if s["disposition"] == "excluded" else "dual_drop"
        else:
            status = "capped"
        rows.append({"key":list(key),"prefix":p,"suffix":s,"status":status})
    print(json.dumps({"head":price["head"],"pins":PINS,"controls":controls,"case_cap":310,
        "runner_seconds":25,"visited_prefix_events":visited_prefix,"visited_suffix_events":visited_suffix,
        "counts":Counter(r["status"] for r in rows),"rows":rows,
        "existing_exact_pending":previous["dual_drops_requiring_rational"]},indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
