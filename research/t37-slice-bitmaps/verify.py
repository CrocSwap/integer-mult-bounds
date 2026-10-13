#!/usr/bin/env python3
"""Complete source-bound differential audit and occupied-cell failure checks."""
import argparse
from collections import defaultdict
import hashlib
from pathlib import Path
import random
import runpy
import tempfile

C = runpy.run_path(str(Path(__file__).resolve().with_name("common.py")))
need, same = C["need"], C["same"]
A = runpy.run_path(str(C["HERE"] / "adapter.py"))
K = runpy.run_path(str(C["HERE"] / "kernel.py"))


def outcome(check, context, roles):
    try:
        return {"accepted": True, "receipt": check(context, roles)}
    except Exception as exc:
        return {"accepted": False, "type": type(exc).__name__, "message": str(exc)}


def differential(reference, fast, context, roles):
    cases = []
    for label, value in (("negative offset", -1), ("huge offset", 1 << 256),
                         ("float offset", 0.0), ("null offset", None), ("text offset", "0")):
        cases.append((label, [dict(roles[0], offset=value)] + roles[1:]))
    for label, value in (("zero width", 0), ("negative width", -1), ("boolean width", True),
                         ("integral float width", float(roles[0]["width"])), ("truncated width", roles[0]["width"] - 1)):
        cases.append((label, [dict(roles[0], width=value)] + roles[1:]))
    for index in (0, len(roles) // 2, len(roles) - 1):
        z = roles[index]
        bad = dict(z, offset=context["rank"][z["child"]] - z["width"] + 1)
        cases.append(("capacity at role " + str(index), roles[:index] + [bad] + roles[index+1:]))
    bins = defaultdict(list)
    for i, z in enumerate(roles):
        bins[z["owner_replica"], z["child"], z["port"]].append(i)
    for label, key in (("early overlap", next(k for k, v in bins.items() if len(v) > 1)),
                       ("late overlap", next(k for k, v in reversed(list(bins.items())) if len(v) > 1))):
        indices = bins[key]
        index = indices[-1]
        bad = dict(roles[index], offset=roles[indices[0]]["offset"])
        cases.append((label, roles[:index] + [bad] + roles[index+1:]))
    gap_key = next(k for k, indices in bins.items()
                   if 0 < sum(roles[i]["width"] for i in indices) < context["rank"][k[1]])
    shifted = list(roles)
    for index in bins[gap_key]:
        shifted[index] = dict(roles[index], offset=roles[index]["offset"] + 1)
    cases.append(("same-cardinality pending-prefix gap", shifted))
    reports = []
    for name, changed in cases:
        a, b = outcome(reference, context, changed), outcome(fast, context, changed)
        same(a, b, "differential rejection: " + name)
        need(a["accepted"] is False, "control accepted: " + name)
        reports.append({"name": name, **a})
    expected = reference(context, roles)
    reordered = list(roles)
    random.Random(94).shuffle(reordered)
    accepted = {"original": roles, "reverse role order": list(reversed(roles)), "seed94 role order": reordered}
    first_zero = next(i for i, z in enumerate(roles) if z["offset"] == 0)
    bool_offset = list(roles)
    bool_offset[first_zero] = dict(roles[first_zero], offset=False)
    accepted["reference-accepted boolean zero offset"] = bool_offset
    for name, changed in accepted.items():
        same(reference(context, changed), expected, "reference equivalent input: " + name)
        same(fast(context, changed), expected, "bitmap equivalent input: " + name)
    # A deliberately weakened prefix predicate must accept this invalid word,
    # demonstrating that full frozen valid-input equality alone is insufficient.
    source = K["patch"](__import__("inspect").getsource(reference))
    old = "require(cells == (1 << count) - 1, 'gap in pending prefix')"
    need(source.count(old) == 1, "faulty-kernel control site")
    space = dict(reference.__globals__)
    exec(compile(source.replace(old, "require(count <= c['rank'][child], 'gap in pending prefix')"),
                 "<deliberately-invalid-prefix-check>", "exec"), space)
    false_acceptance = outcome(space["check_roles"], context, shifted)
    need(false_acceptance["accepted"] is True, "weakened prefix control premise")
    return {"rejected": reports, "equivalent_inputs": list(accepted),
            "faulty_optimizer_detected": "cardinality-only prefix test accepts a shifted occupied interval"}


def occupied_trace(context, roles):
    reference, masks = defaultdict(set), defaultdict(int)
    stream = hashlib.sha256()
    cells_added, largest = 0, 0
    for z in roles:
        key = (z["owner_replica"], z["child"], z["port"])
        offset, width = z["offset"], z["width"]
        cells = set(range(offset, offset + width))
        mask = ((1 << width) - 1) << offset
        need(not reference[key] & cells and not masks[key] & mask, "actual trace overlap")
        reference[key].update(cells)
        masks[key] |= mask
        need(masks[key] == sum(1 << x for x in reference[key]), "occupied state after every role")
        cells_added += width
        largest = max(largest, masks[key].bit_length())
        stream.update(C["canonical"]([list(key), str(masks[key])]) + b"\n")
    checks = 0
    for owner, child in context["windows"]:
        for port in range(112):
            key = owner, child, port
            value, mask = reference[key], masks[key]
            need(len(value) == mask.bit_count(), "trace cardinality")
            need((value == set(range(len(value)))) == (mask == (1 << mask.bit_count()) - 1), "trace final prefix")
            checks += 1
    return {"role_prefixes": len(roles), "cell_insertions": cells_added, "slice_prefixes": checks,
            "largest_mask_bits": largest, "changed_bin_stream_sha256": stream.hexdigest()}


def primitive_cases():
    intervals, prefixes = 0, 0
    for capacity in range(9):
        for mask in range(1 << capacity):
            used = {i for i in range(capacity) if mask >> i & 1}
            for offset in range(-1, capacity + 2):
                for width in range(10):
                    cells = set(range(offset, offset + width))
                    old = offset >= 0 and offset + width <= capacity and not used & cells
                    new = False
                    if offset >= 0 and offset + width <= capacity:
                        bits = ((1 << width) - 1) << offset
                        new = not mask & bits
                        if new:
                            need((mask | bits) == sum(1 << i for i in used | cells), "primitive union")
                    need(old == new, "primitive admission")
                    intervals += 1
    for mask in range(1 << 16):
        used = {i for i in range(16) if mask >> i & 1}
        need((used == set(range(len(used)))) == (mask == (1 << mask.bit_count()) - 1), "primitive prefix")
        prefixes += 1
    return {"interval_cases": intervals, "prefix_masks": prefixes}


def run(root, output):
    manifest = C["pins"](root)
    output.mkdir(parents=True, exist_ok=False)
    inputs = C["materialize"](root, output / "inputs", manifest)
    print("unchanged original T37 wrapper and all 14 inherited controls", flush=True)
    before, capture = A["run"](inputs, output / "reference", "reference", root, retain_context=True)
    after, bitmap = A["run"](inputs, output / "bitmap", "bitmap", root)
    same(before, after, "complete reference/bitmap receipt")
    core = capture["core"]
    reference = capture["reference_check"]
    core.check_roles = reference
    implementation = K["install"](core)
    same(implementation, bitmap["implementation"], "same optimized kernel")
    print("every occupied-state prefix and interval/gap rejection controls", flush=True)
    trace = occupied_trace(capture["context"], capture["roles"])
    cases = differential(reference, core.check_roles, capture["context"], capture["roles"])
    primitives = primitive_cases()
    return {"status": "PASS_T37_EXACT_OCCUPANCY_BITMAPS", "sources": manifest,
            "implementation": implementation, "complete_receipt": before, "trace": trace,
            "differential": cases, "primitive_cases": primitives}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=C["ROOT"])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    expected = C["load"](C["HERE"] / "EXPECTED.json")
    with tempfile.TemporaryDirectory(prefix="t37-bitmap-verification-") as tmp:
        result = run(args.source_root.resolve(), args.output or Path(tmp) / "run")
        same(result, expected, "complete verification receipt")
        if args.receipt:
            C["write"](args.receipt, result)
    print("PASS_T37_EXACT_OCCUPANCY_BITMAPS: complete original receipt; 167832 roles; 14 inherited controls; no new kappa")
