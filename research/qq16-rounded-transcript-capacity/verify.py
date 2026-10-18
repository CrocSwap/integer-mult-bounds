#!/usr/bin/env python3
"""Source-bound hidden line and finite controls for the capacity proof.

ywz65, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import itertools
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def object_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=object_pairs)


def same(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def pinned_model():
    manifest = read_json(PACKAGE / "SOURCES.json")
    for row in manifest["files"] + manifest["vendored_files"]:
        if row["usage"] == "input":
            raw = (ROOT / row["path"]).read_bytes()
            require(sha256(raw).hexdigest() == row["sha256"], "source hash: " + row["path"])
    vendor = PACKAGE / "vendor/pr2384"
    spec = importlib.util.spec_from_file_location("retained_qq16_2384", vendor / "verify.py")
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    # Preserve all retained source bytes; configure its default checkout root.
    old.sources.__defaults__ = (ROOT,)
    retained = old.build_result()
    old.equal_receipt(retained, read_json(vendor / "RESULT.json"))
    packet, phases, template, previous, pins = old.sources()
    bases, routes = old.derive_routes(packet, phases)
    model = old.Model(packet, routes)
    h = old.zero_bank()
    for port, coefficient in old.COEFFICIENTS.items():
        h[port] = {bases[port][1]: Q(coefficient)}
    initial, query, trace = old.replay(model, template, h)
    return old, h, initial, trace, retained


def capacity(m, radius, overhead, metadata=1):
    require(type(m) is int and m >= 0, "component count")
    require(type(overhead) is int and overhead >= 0, "grid overhead")
    require(type(metadata) is int and metadata >= 1, "metadata count")
    require(radius >= 0, "radius")
    scaled = Q(radius) * (1 << overhead)
    width = 2 * (scaled.numerator // scaled.denominator) + 1
    return metadata * width ** m


def build_result():
    old, h, initial, trace, retained = pinned_model()
    v_h = [old.combination([(2, f)]) for f in h]
    v_a = [old.combination([(2, f)]) for f in initial]
    expected_a = [{145: Q(1), 4: Q(-1)}, {145: Q(1), 25: Q(-1)},
                  {4: Q(1), 25: Q(-1)}, {}, {145: Q(1), 4: Q(-1)},
                  {25: Q(1), 145: Q(-1)}, {25: Q(1), 4: Q(-1)}, {}]
    require(v_a == expected_a, "actual integral selected line")
    require(all(c.denominator == 1 for f in v_h + v_a for c in f.values()), "integer line")
    bound = max(sum(abs(c) for c in f.values()) for f in v_h + v_a)
    require(bound == 2 and old.evaluate(v_a[0]) == 1, "normalization and demanded coordinate")
    require(not any(v_h[p] for p in old.READ), "initial read-port tuple")

    # Enumerate semantic slots, independently of the arithmetic count below.
    slots = []
    for pair, side, port in itertools.product(range(4), range(2), old.READ):
        slots.append(("initial", -1, pair, side, port))
    for index, entry in enumerate(trace):
        for pair, side, port in itertools.product(range(4), range(2), old.A + old.T + old.READ):
            slots.append(("post", index, pair, side, port))
        if index >= 1:
            side = 1 if entry["event"]["kind"] == "terminal" else 0
            for pair, port in itertools.product(range(4), old.U):
                slots.append(("completed", index, pair, side, port))
        event = entry["event"]
        if event["kind"] == "local" and not event["reverse"]:
            for coordinate in range(8):
                slots.append(("history", index, event["pair"], 0, coordinate))
    require(len(slots) == len(set(slots)) == 19944, "complete observed slot count")
    counts = dict(Counter(s[0] for s in slots))
    require(counts == {"initial": 528, "post": 12464, "completed": 6912, "history": 40}, "slot categories")
    require(all(s[3] == 1 for s in slots if s[0] == "completed" and s[1] == 18), "terminal side")

    controls = []
    def reject(name, check):
        try:
            check()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError("control not rejected: " + name)

    reject("unscaled half-integral line is not p-grid integral",
           lambda: require(all(c.denominator == 1 for f in initial for c in f.values()), "fractional"))
    reject("former-Y endpoint is not a zero observation", lambda: require(not any(v_h), "nonzero"))
    reject("omitted imaginary channels are not the declared real tuple",
           lambda: require(len(slots) == 39888, "two channels"))

    packing = []
    for p in range(3, 13):
        values = [Q(k, 1 << p) for k in range(0, (1 << (p - 1)) + 1, 4)]
        require(len(values) == (1 << (p - 3)) + 1, "packed family count")
        require(all(b-a > Q(2, 1 << p) for a, b in zip(values, values[1:])), "disjoint one-ulp balls")
        require(values[0] == 0 and values[-1] == Q(1, 2), "unit-box line range")
        packing.append({"p": p, "exact_inputs": (1 << (p-1))+1, "one_ulp_packing": len(values)})
    reject("two-ulp separation does not give disjoint closed balls",
           lambda: require(Q(2, 64) > 2*Q(1, 64), "closed balls meet"))

    interval_checks = 0
    for numerator, denominator, g in itertools.product(range(9), range(1, 6), range(4)):
        radius = Q(numerator, denominator)
        enumerated = [n for n in range(-100, 101) if abs(Q(n, 1 << g)) <= radius]
        require(len(enumerated) == capacity(1, radius, g), "rational grid-interval count")
        interval_checks += 1
    reject("negative radius", lambda: capacity(1, Q(-1), 0))

    # Toy sharpness/collision at source-line exact p=4 and p=5 cardinalities.
    pairs = list(itertools.product((-1, 0, 1), repeat=2))
    require(len(pairs) == capacity(2, 1, 0) == 9, "nine-state alphabet")
    require(len({pairs[k] for k in range(9)}) == 9, "sharp injective boundary")
    encoded = [pairs[k % 9] for k in range(17)]
    require(encoded[0] == encoded[9] and 0 != 9, "explicit over-capacity collision")
    reject("capacity equality is not an impossibility",
           lambda: require(capacity(2, 1, 0) < 9, "strict comparison"))
    # At p=7 the same collision on the four-ulp packing defeats one-ulp recovery.
    require(Q(4*9, 128) > Q(2, 128), "approximate collision demand separation")

    fine_grid = []
    for p in range(3, 10):
        targets = [Q(k, 1 << p) for k in range((1 << (p-1))+1)]
        fine = [t / (1 << p) for t in targets]
        require(len(set(fine)) == len(targets), "fine-grid injection")
        require(max(fine) <= Q(1, 1 << (p+1)), "small error despite injection")
        require(all((f * (1 << (2*p))).denominator == 1 for f in fine), "2p-grid")
        require(capacity(1, Q(1, 2), p) >= len(targets), "correct fine-grid capacity")
        require(capacity(1, 0, 0, len(targets)) == len(targets), "side metadata escape")
        fine_grid.append({"p": p, "inputs": len(targets)})
    return {"schema_version": 1, "status": "PASS_QQ16_ROUNDED_TRANSCRIPT_CAPACITY",
            "source_head": "b9ef408b1cb0fcd34ab1f1bdbe645573d5de188f",
            "retained_controls": retained["rejected_controls"],
            "integer_selected_line": [old.serialize(f) for f in v_a],
            "coordinate_l1_bound": int(bound), "demand_at_identity": 1,
            "slot_categories": counts, "complex_slots_per_point": len(slots),
            "real_components_per_point": 2*len(slots), "packing": packing,
            "rational_interval_checks": interval_checks,
            "toy_capacity": 9, "toy_over_capacity_inputs": 17,
            "fine_grid_escape": fine_grid, "rejected_controls": controls,
            "scope": "conditional finite transcript capacity; no actual rounded error bound or new kappa"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    result = build_result()
    if args.write:
        with args.write.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        require(same(result, read_json(PACKAGE / "RESULT.json")), "complete typed receipt mismatch")
    print(result["status"])


if __name__ == "__main__":
    main()
