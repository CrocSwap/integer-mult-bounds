"""Check the seven frozen prefix drops in the rank-eight cohort."""
from collections import Counter
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import sys
from time import monotonic

PINS = {
    "lead/RESULT.json": "45b6c8992dcff04b7252dfec809fc64812b86f094531ed3964ff967408057ed2",
    "price/PRICE.json": "a78be64c3e3ae8a0e532237c4dd3541aa9ad3fcbbc3c25d79c8a03fb7e07c525",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/exterior_minor.py": "b25fef5432d8ea9cff9eecc422cf07ccf7473568084de3e8d3d1b5224793504d",
    "inputs/reverse_engine.py": "751d5d0c4c665c8768ff69bcf939700d3be2f989c59f09af3a4aa14d3c1ebbc4",
}


def main():
    assert __debug__
    deadline = monotonic() + 20
    root = Path(sys.argv[1])
    raw = {}
    for name, digest in PINS.items():
        raw[name] = (root/name).read_bytes()
        if sha256(raw[name]).hexdigest() != digest:
            raise ValueError(f"changed dependency: {name}")
    engine = run_path(str(root/"inputs/exterior_minor.py"))
    reverse = run_path(str(root/"inputs/reverse_engine.py"))
    unique, scalar, plus, prime, minor = (engine[k] for k in ("unique","scalar","plus","P","exterior_minor"))
    price = json.loads(raw["price/PRICE.json"],object_pairs_hook=unique)
    prefix = json.loads(raw["lead/RESULT.json"],object_pairs_hook=unique)
    word = json.loads(decompress(raw["inputs/7334-WORD.json.gz"]),object_pairs_hook=unique)
    assert prefix["head"] == price["head"] == engine["HEAD"]
    assert prefix["counts"] == {"excluded":9,"rank drop":7} and not prefix["unvisited"]
    requests = {row["key"][0]: row for row in prefix["rows"] if row["disposition"] == "rank drop"}
    assert len(requests)==7
    controls = reverse["controls"](engine)
    public = word["public"]
    active = word["final"] + [None] * word["owned_fields"]
    columns = [{i:1} for i in range(public)] + [None]*word["owned_fields"]
    cohort = set(price["cohort"])
    results = {}
    tape = word["program"]
    for cut in range(len(tape),-1,-1):
        if (cut % 128 == 0 or cut in requests) and monotonic() >= deadline:
            break
        if cut in requests:
            row = requests[cut]
            c = row["key"][1]
            bank = [i for i in range(public) if active[i] == c]
            owners = [i for i in range(public,len(active)) if active[i] == c]
            assert bank == row["public"] and owners == row["owned"]
            result = minor(bank,columns,cohort)
            results[cut] = {k: row[k] for k in ("key","public","owned","pivots")} | result
        if cut:
            reverse["reverse_event"](tape[cut-1],active,columns,public,scalar,plus,prime)
    if cut == 0:
        assert active == word["initial"]+[None]*word["owned_fields"]
    rows = [results[t] for t in requests if t in results]
    print(json.dumps({"head":price["head"],"pins":PINS,"controls":controls,"rows":rows,
        "counts":Counter(r["disposition"] for r in rows),"unvisited":[requests[t]["key"] for t in requests if t not in results],
        "unselected":prefix["unselected"]},indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
