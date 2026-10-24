#!/usr/bin/env python3
"""Check bounded residues against source division and a subset-sum oracle."""
from hashlib import sha256
from itertools import product
import gzip
import importlib.util
import json
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from membership import member, obstruction


def need(ok, message):
    if not ok: raise ValueError(message)


def load_source():
    for item in json.loads((HERE / "SOURCES.json").read_text())["files"]:
        if item["usage"] == "input":
            need(sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"], "source hash mismatch")
    spec = importlib.util.spec_from_file_location("old", ROOT / "research/p104-clifford-exactness/model.py")
    old = importlib.util.module_from_spec(spec); spec.loader.exec_module(old)
    return old


def coefficient(values, mask):
    a = b = 0
    sub = mask
    while True:
        sign = -1 if (mask.bit_count() - sub.bit_count()) & 1 else 1
        a += sign * values[sub][0]; b += sign * values[sub][1]
        if not sub: return a, b
        sub = (sub - 1) & mask


def divisible(z, power):
    a, b = z
    # Separate repeated Gaussian division oracle, without the bit criterion.
    for _ in range(power):
        if (a + b) % 2: return False
        a, b = (a + b) // 2, (b - a) // 2
    return True


def check(values, old, full=False):
    before = list(values)
    answer = obstruction(values)
    need((answer is None) == old.member(values), "source membership mismatch")
    if full:
        need((answer is None) == all(divisible(coefficient(values, s), s.bit_count())
                                     for s in range(len(values))), "subset oracle mismatch")
    if answer is not None:
        mask, a, b, bits = answer
        exact = coefficient(values, mask)
        need((a, b) == tuple(x % (1 << bits) for x in exact), "rejection certificate residue")
        need(not divisible(exact, mask.bit_count()), "rejection certificate divides")
    need(values == before, "input mutated")
    return answer is None


def actual_prefixes(old):
    source = ROOT / "research/p104-rounded-collector/inputs"
    word = json.loads((source / "WORD.json").read_text())["program"]
    native = json.loads(gzip.decompress((source / "NATIVE.json.gz").read_bytes()))["transports"]
    events = word[2025:2040]
    need(len(word) == 5398 and events[0][0] == "zero" and events[-1][0] == "erase", "source interval")
    names = [e[2] for e in events[1:6]]
    need(names == ["D31", "D30", "D29", "D28", "D27"], "source roles")
    checks = 0; digest = sha256()
    for seed in range(3):
        arrays = {name: old.encode([((x * (j + 3) + seed) % 23 - 11,
                                     (x * x + j + seed) % 29 - 14) for x in range(512)])
                  for j, name in enumerate(names + ["Q7"])}
        original = {k: list(v) for k, v in arrays.items()}
        for index, event in enumerate(events, 2025):
            op, dst = event[:2]
            if op == "zero": arrays[dst] = [(0, 0)] * 512
            elif op == "add":
                scale = int(event[3])
                arrays[dst] = [(a + scale * c, b + scale * d)
                               for (a,b),(c,d) in zip(arrays[dst], arrays[event[2]])]
            elif op == "transport":
                records = [x for x in native if index in x["events"]]
                need(len(records) == 1 and records[0]["events"] == [index], "native occurrence")
                recipe = records[0]["recipe"]
                need(recipe["rank"] == event[4] == 7 and records[0]["old"] == event[2]
                     and records[0]["new"] == event[3], "native frame binding")
                arrays[dst] = old.wrapper(arrays[dst], recipe["right"])
                need(check(arrays[dst], old), "right wrapper"); checks += 1
                for bit in range(7):
                    ideal = old.ideal_stage(arrays[dst], bit)
                    arrays[dst] = old.lift_stage(arrays[dst], bit)
                    need(arrays[dst] == ideal and check(arrays[dst], old), "literal native prefix")
                    checks += 1
                arrays[dst] = old.wrapper(arrays[dst], recipe["left"])
                need(check(arrays[dst], old), "left wrapper"); checks += 1
            elif op == "erase":
                need(arrays[dst] == [(0, 0)] * 512, "private cleanup")
                del arrays[dst]; continue
            else: raise ValueError("unexpected collector operation")
            need(check(arrays[dst], old), "whole-event prefix"); checks += 1
            digest.update(json.dumps(arrays[dst]).encode())
        need(all(arrays[k] == original[k] for k in names), "borrowed sources")
        need("C" not in arrays, "owned row retained")
        total = [tuple(sum(original[k][i][j] for k in names) for j in range(2)) for i in range(512)]
        recipe = next(x["recipe"] for x in native if x["events"] == [2031])
        total = old.wrapper(total, recipe["right"])
        for bit in range(7): total = old.ideal_stage(total, bit)
        total = old.wrapper(total, recipe["left"])
        expected = [old.add(x, y) for x, y in zip(original["Q7"], total)]
        need(arrays["Q7"] == expected, "complete collector query endpoint")
    return checks, digest.hexdigest()


def replay():
    old = load_source(); small = 0
    for r in (0, 1, 2):
        for raw in product(range(2), repeat=2 * (1 << r)):
            values = list(zip(raw[::2], raw[1::2]))
            check(values, old, True); small += 1
    real = 0
    for raw in product(range(4), repeat=8):
        check([(v, 0) for v in raw], old, False); real += 1
    broad = controls = 0
    for r in range(1, 10):
        for width in (4, 127, 1024, 8064):
            coeff = [((-1 if i & 1 else 1) * ((1 << width) + i * 17),
                      (-1 if i & 2 else 1) * ((1 << width) + i * 13)) for i in range(1 << r)]
            values = old.encode(coeff)
            need(check(values, old, r <= 4), "encoded positive")
            high = 1 << ((r + 1) // 2)
            changed = [(a + (i + 1) * high, b - (i * 3 + 1) * high) for i, (a,b) in enumerate(values)]
            need(check(changed, old, r <= 4), "discarded high-bit invariance")
            values[-1] = old.add(values[-1], (1, 0))
            need(not check(values, old, r <= 4), "top coefficient violation")
            broad += 3
        zero = [(0, 0)] * (1 << r)
        impulse = list(zero); impulse[-1] = (1 << (((r + 1) // 2) - 1), 0)
        need(not check(impulse, old) and member(zero), "sharp modulus")
        controls += 1
    # Even Gaussian coordinate divisibility alone loses an odd pi constraint.
    need(not member([(0,0), (1,0)]), "odd pi condition"); controls += 1
    for bad in ([], [(1,0)] * 3, [(True,0)], [[1,0]], [(1.0,0)]):
        try: member(bad)
        except ValueError: controls += 1
        else: raise ValueError("malformed input accepted")
    count, digest = actual_prefixes(old)
    return {"status": "PASS_NEWTON_BOUNDED_RESIDUE_VALIDATOR_NO_NEW_KAPPA",
            "complete_small_binary_gaussian_arrays": small, "complete_rank3_real_residue_arrays": real,
            "large_signed_cases": broad, "actual_collector_prefixes": count,
            "collector_prefix_sha256": digest, "controls": controls,
            "rank9_residue_bits_per_component": 5, "rank9_residue_data_bits": 5120,
            "rank9_modular_subtractions": 4608, "largest_source_coefficient_bits": 8065}


if __name__ == "__main__":
    result = replay()
    if "--record" in sys.argv: (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    else: need(json.dumps(result, sort_keys=True) == json.dumps(json.loads((HERE / "RESULT.json").read_text()), sort_keys=True), "typed receipt mismatch")
    print(json.dumps(result, sort_keys=True))
