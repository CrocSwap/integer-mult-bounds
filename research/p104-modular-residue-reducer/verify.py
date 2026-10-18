"""Source-bound exact finite witness, with explicit optimized-mode checks.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""

import hashlib
import json
from pathlib import Path
import random
import types

ROOT = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_source(path):
    # Compile authenticated source bytes, never preexisting bytecode.
    module = types.ModuleType(path.stem)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def sources():
    pins = json.loads((ROOT / "PREDECESSOR.json").read_text())
    need(sorted(entry["local"] for entry in pins["files"]) ==
         ["HNF7.json", "vendor/lattice.py"], "exact predecessor inventory")
    for entry in pins["files"]:
        data = (ROOT / entry["local"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == entry["sha256"], "predecessor bytes")
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        need(hashlib.sha1(blob).hexdigest() == entry["git_blob"], "predecessor Git blob")
        need(entry["source_commit"] == "0cc430349a3f3dc200666bc22e997076e0a557ed",
             "predecessor commit")
    raw = json.loads((ROOT / "HNF7.json").read_text())
    need(type(raw["rank"]) is int and raw["rank"] == 7, "rank-seven witness")
    rows = [[0]*256 for _ in range(256)]
    need(len(raw["rows"]) == 256, "sparse rows")
    for i, sparse in enumerate(raw["rows"]):
        last = -1
        for j, value in sparse:
            need(type(j) is int and last < j < 256 and type(value) is int,
                 "canonical sparse entries")
            rows[i][j] = value
            last = j
    return rows, load_source(ROOT / "vendor" / "lattice.py")


def main():
    reducer = load_source(ROOT / "reducer.py")
    rows, old = sources()
    old.validate_basis(rows)
    program = reducer.Reducer(rows, 16)
    rng = random.Random(3035)
    inputs = [[0]*256, [15]*256]
    inputs += [[int(i == j) for i in range(256)] for j in range(256)]
    inputs += [[rng.randrange(16) for _ in range(256)] for _ in range(32)]
    for value in inputs:
        state = list(value)
        program.apply(state)
        need(program.residues(state) == old.canonical(value, rows), "coset representative")
        program.apply(state, inverse=True)
        need(state == value, "inverse modular program")
    signed = []
    for width in (1, 4, 32, 512, 4090, 4096):
        signed += [[rng.getrandbits(width)*rng.choice((-1, 1)) for _ in range(256)]
                   for _ in range(2)]
    for value in signed:
        original = list(value)
        low = [x % 16 for x in value]
        state = program.apply(list(low))
        small = program.residues(state)
        need(small == old.canonical(value, rows), "signed coset")
        target = rng.getrandbits(program.bits)
        work = [0]*256
        result = program.oracle(value, target, work)
        need(result == target ^ program.packed(state), "dirty target update")
        need(program.oracle(value, result, work) == target and not any(work), "oracle inverse")
        need(value == original, "retained signed source")
        wide = old.ideal([x-t for x, t in zip(value, low, strict=True)], 7)
        correction = old.ideal([t-s for t, s in zip(low, small, strict=True)], 7)
        lifted = old.lift(small, 7)
        coupled = [a+b+c for a, b, c in zip(wide, correction, lifted, strict=True)]
        need(coupled == old.lift(value, 7), "identical signed lifting map")
    receipt = program.invoice()
    receipt.update({"low_bit_fixtures": len(inputs), "signed_lifting_fixtures": len(signed),
                    "lift_pairs_per_128_complex_block": 448,
                    "added_ideal_pairs_per_128_complex_block": 448,
                    "no_new_kappa": True})
    expected = json.loads((ROOT / "RESULT.json").read_text())
    need(json.dumps(receipt, sort_keys=True) == json.dumps(expected, sort_keys=True),
         "typed exact receipt")
    print("PASS_P104_MODULAR_RESIDUE_REDUCER " + json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
