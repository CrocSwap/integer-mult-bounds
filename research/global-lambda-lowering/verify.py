#!/usr/bin/env python3
"""Source-bound ordinary lowering of the global central normalizer.

This is a record-level interpreter and exact accounting check. It does not
simulate the retained fixed-tape movement primitive or the whole multiplier.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json
import random
import shutil
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(root=HERE):
    records = json.loads((root / "RETAINED.json").read_text())["files"]
    for item in records:
        path = root / item["path"]
        need(not path.is_symlink(), "source symlink: " + item["path"])
        data = path.read_bytes()
        need(len(data) == item["bytes"], "source length: " + item["path"])
        need(sha256(data).hexdigest() == item["sha256"], "source SHA256: " + item["path"])
        blob = sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        need(blob == item["git_blob"], "source Git blob: " + item["path"])
    return len(records)


def source_controls():
    """Reject damaged or redirected source evidence in disposable copies."""
    controls = {}
    with tempfile.TemporaryDirectory(prefix="global-lambda-source-") as temporary:
        root = Path(temporary)
        shutil.copytree(HERE / "retained", root / "retained")
        manifest_path = root / "RETAINED.json"
        manifest_bytes = (HERE / "RETAINED.json").read_bytes()
        manifest_path.write_bytes(manifest_bytes)
        source = root / "retained/caller.json"
        original = source.read_bytes()

        def rejected(name, fragment):
            try:
                authenticate(root)
            except (ValueError, FileNotFoundError) as error:
                controls[name] = fragment in str(error)
            else:
                controls[name] = False

        source.write_bytes(bytes([original[0] ^ 1]) + original[1:])
        rejected("source_byte_corruption", "source SHA256:")
        source.write_bytes(original)
        manifest = json.loads(manifest_bytes)
        manifest["files"][0]["git_blob"] = "0" * 40
        manifest_path.write_text(json.dumps(manifest))
        rejected("source_blob_pin", "source Git blob:")
        manifest_path.write_bytes(manifest_bytes)
        source.unlink()
        source.symlink_to(HERE / "retained/caller.json")
        rejected("source_symlink", "source symlink:")
        source.unlink()
        rejected("missing_source", "caller.json")
    need(all(controls.values()), "all source controls reject their mutation")
    return controls


def displacement(q, width, axes):
    need(width >= 1 and 0 < q < 1 << axes, "positive width and nonzero central displacement")
    return sum(q << (axes * j) for j in range(width))


def not_recipe(q, axes):
    """One f-independent NOT record for each set logical coordinate."""
    need(0 < q < 1 << axes, "valid central displacement")
    return [("NOT", i) for i in range(axes) if (q >> i) & 1]


def route_address(address, recipe, axes, width):
    out = address
    for op, axis in recipe:
        need(op == "NOT" and 0 <= axis < axes, "valid movement record")
        for column in range(width):
            out ^= 1 << (axes * column + axis)
    return out


def lowered(data, q, width, axes, sign, residual=None, clear=True):
    """Return Gaussian integer numerators over 2, plus the owned return.

    The interpreter uses the retained NOT record semantics. Array addressing
    here is an oracle for the separately assumed physical movement primitive.
    COPY is ADD into the initialized bank; residual is deliberately retained.
    """
    need(sign in (-1, 1), "normalizer orientation")
    size = 1 << (axes * width)
    need(len(data) == size, "full active rectangle")
    init = [(0, 0)] * size if residual is None else list(residual)
    need(len(init) == size, "complete owned bank")
    scratch = [(a + c, b + d) for (a, b), (c, d) in zip(data, init)]
    recipe = not_recipe(q, axes)
    translated = [scratch[route_address(x, recipe, axes, width)] for x in range(size)]
    output = []
    for (a, b), (c, d) in zip(data, translated):
        output.append((a - sign * b + c + sign * d,
                       b + sign * a + d - sign * c))
    returned = [(0, 0)] * size if clear else translated
    return output, returned


def direct_pair(data, mask, sign):
    """Independent in-place pair formula, not the scratch/NOT interpreter."""
    result = [None] * len(data)
    for x in range(len(data)):
        y = x ^ mask
        if x > y:
            continue
        a, b = data[x]
        c, d = data[y]
        result[x] = (a + c + sign * (d - b), b + d + sign * (a - c))
        result[y] = (a + c + sign * (b - d), b + d + sign * (c - a))
    return result


def scalar_units(event):
    op = event[0]
    if op in ("ADD", "SCALE"):
        value = Fraction(event[-1])
        a, d = abs(value.numerator), value.denominator
        need(a > 0 and d & (d - 1) == 0, "nonzero dyadic caller coefficient")
        return 4 * (a.bit_length() + a.bit_count() + d.bit_length() + 1)
    if op == "SWAP":
        return 8
    if op == "LAMBDA":
        need(event[2] in (-1, 1), "caller normalizer orientation")
        return 16
    need(op in ("HOST2", "IDLE_ONE", "QUERY"), "unknown caller opcode")
    return 0


def accounting(word, caller):
    ports = word["ports"]
    need(len(ports) == len(set(ports)) == 104, "104 literal source ports")
    need(all(0 < q < 512 and q.bit_count() % 2 for q in ports), "odd nine-axis ports")
    events = caller["events"]
    counts = Counter(event[0] for event in events)
    need(caller["roles"] == 40 and caller["stages"] == 18, "frozen caller shape")
    need(counts["LAMBDA"] == 124 and counts["QUERY"] == 6, "literal normalization/query census")
    scalar = sum(scalar_units(event) for event in events)
    translation_passes = counts["LAMBDA"] * len(ports)
    translation_charge = 1000 * translation_passes
    expanded = len(ports) * scalar + translation_charge
    envelope = 32 * caller["roles"] * len(ports) * len(events)
    need(expanded < envelope, "expanded caller fits retained envelope")

    # Reconstruct the source's reviewed upper raw count; do not trust a receipt.
    dims = [len(frame) for frame in word["frames"]]
    main = set(word["live"]) | {r + 112 for r in word["live"]}
    main |= set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    helpers = len(word["initial"]) - len(main)
    paid_calls = sum(event[0] == "MOVE" for event in word["program"])
    lifetimes = sum(event[0] == "INIT" for event in word["program"])
    local_scalar_upper = 0
    live_owned = set()
    peak = 0
    for event in word["program"]:
        op = event[0]
        if op == "INIT":
            need(event[1] not in live_owned, "owned init lifetime")
            live_owned.add(event[1]); peak = max(peak, len(live_owned))
        elif op == "CLEAR":
            need(event[1] in live_owned, "owned clear lifetime")
            live_owned.remove(event[1])
        elif op in ("SCALE", "ADD", "COPY"):
            q = Fraction(event[2] if op == "SCALE" else event[3])
            a, d = abs(q.numerator), q.denominator
            local_scalar_upper += 4 * (a.bit_length() + d.bit_length() + 1)
            if op != "SCALE":
                local_scalar_upper += 4 * a.bit_count()
    need(not live_owned, "native returns all owned fields")
    routes = (paid_calls + 2 * helpers + 416 + 8 * 104 + 4 * lifetimes) * 1000

    def swap_count(selected):
        return len(set(selected) - set(range(len(selected))))

    main_exchanges = main_nine = main_phase = 0
    for qp, zero, *selected in caller["diagonal"]:
        axes = ([0] if qp else []) + [a for st, used in enumerate(selected, 1) if used
                                     for a in range(9 + 8 * (st - 1), 9 + 8 * st)]
        main_exchanges += 2 * swap_count(axes) * 104
        main_nine += 2 * bool(qp) * 104
        main_phase += int(qp == -1) * 104
    idle_exchanges = query_nine = query_phase = 0
    for event in events:
        if event[0] == "IDLE_ONE":
            axes = [a for st in event[2] for a in range(9 + 8 * (st - 1), 9 + 8 * st)]
            idle_exchanges += 2 * swap_count(axes) * 104
        elif event[0] == "QUERY":
            query_nine += 2 * 104
            query_phase += int(event[3] == -1) * 104
    outputs = caller["roles"] * 104 * 26 + (main_exchanges + main_nine + main_phase) * 1000
    remaining = (envelope + counts["QUERY"] * 16 * 104 + outputs
                 + idle_exchanges * 1000 + (query_nine + query_phase) * 1000)
    reviewed = 18 * (local_scalar_upper + routes) + remaining
    need(reviewed == 971071328, "reconstructed reviewed upper raw source count")
    conservative = reviewed + translation_charge
    need(conservative < 10**9, "even a separate translation debit fits the source cap")

    # One global query bank is reserved, separate from all public and native
    # owned slots. Each normalizer macro closes before the next caller event.
    scratch = ("query_scratch", 0)
    lowered_lifetimes = []
    for index, event in enumerate(events):
        if event[0] != "LAMBDA":
            continue
        need(0 <= event[1] < caller["roles"], "normalizer main role exists")
        for port in ports:
            target = ("main", event[1], port)
            need(target != scratch, "scratch cannot alias a productive field")
            lowered_lifetimes.append((index, port))
    need(len(set(lowered_lifetimes)) == translation_passes, "one closed lifetime per normalizer/port")
    return {
        "ports": len(ports), "caller_events": len(events), "lambda_events": counts["LAMBDA"],
        "scalar_units_per_port": scalar, "extra_translation_passes": translation_passes,
        "extra_translation_charge": translation_charge, "expanded_caller_upper": expanded,
        "retained_caller_envelope": envelope, "caller_envelope_slack": envelope - expanded,
        "reviewed_upper_raw": reviewed, "conservative_raw_with_separate_debit": conservative,
        "conservative_raw_headroom": 10**9 - conservative,
        "native_owned_peak": peak, "new_owned_peak": max(peak, 1),
        "new_owned_slots": 0, "query_bank_reuses": translation_passes,
        "paid_gaussian_delta": 0, "productive_target_delta": 0,
        "translation_NOT_records_per_pass_max": max(q.bit_count() for q in ports),
    }


def run():
    count = authenticate()
    word = json.load(gzip.open(HERE / "retained/native-word.json.gz", "rt"))
    caller = json.loads((HERE / "retained/caller.json").read_text())
    rng = random.Random(6706902)
    cases = addresses = 0
    # Every nonzero direction in bounded small rectangles, every basis vector.
    for axes, width in ((1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (3, 1), (3, 2)):
        size = 1 << (axes * width)
        for q in range(1, 1 << axes):
            mask = displacement(q, width, axes)
            for basis in range(size):
                data = [(0, 0)] * size; data[basis] = (1, 0)
                for sign in (-1, 1):
                    actual, scratch = lowered(data, q, width, axes, sign)
                    need(actual == direct_pair(data, mask, sign), "complete finite basis lowering")
                    need(not any(a or b for a, b in scratch), "owned bank returned zero")
                    cases += 1
    # Every actual q at widths 1,2,3; sampled addresses prove no wider finite
    # coverage. The universal statement is the written proof, not this sample.
    for q in word["ports"]:
        for width in (1, 2, 3):
            mask = displacement(q, width, 9)
            recipe = not_recipe(q, 9)
            for _ in range(80):
                spectator = rng.randrange(1 << 17) << (9 * width)
                address = spectator | rng.randrange(1 << (9 * width))
                mapped = route_address(address, recipe, 9, width)
                need(mapped == address ^ mask, "actual repeated-displacement route")
                need(mapped >> (9 * width) == spectator >> (9 * width), "spectators fixed")
                addresses += 1
    # A genuinely dense width-two actual-port lowering; no width-one shortcut.
    q = word["ports"][0]
    data = [(rng.randrange(-4, 5), rng.randrange(-4, 5)) for _ in range(1 << 18)]
    actual, scratch = lowered(data, q, 2, 9, 1)
    need(actual == direct_pair(data, displacement(q, 2, 9), 1), "dense actual width-two lowering")
    need(not any(a or b for a, b in scratch), "dense scratch zero")
    del data, actual, scratch

    # Numerical residue is propagated, never removed by changing COPY to an
    # assignment or by erasing the later scratch output in the analysis.
    data = [(2, -3), (-4, 7), (1, 2), (5, -1)]
    residue = [(1, -1), (0, 1), (-1, 0), (1, 1)]
    clean, _ = lowered(data, 1, 2, 1, 1)
    dirty, _ = lowered(data, 1, 2, 1, 1, residue)
    need(dirty != clean, "dirty-copy residual must affect the result")
    delta = [(Fraction(a-c, 2), Fraction(b-d, 2)) for (a, b), (c, d) in zip(dirty, clean)]
    need(max(abs(x) for pair in delta for x in pair) <= 1, "residual real-coordinate bound")

    controls = source_controls()
    basis = [(1, 0), (0, 0), (0, 0), (0, 0)]
    correct, _ = lowered(basis, 1, 2, 1, 1)
    controls["wrong_translation"] = correct != direct_pair(basis, 1, 1)
    controls["wrong_orientation"] = correct != lowered(basis, 1, 2, 1, -1)[0]
    controls["omitted_clear"] = any(a or b for a, b in lowered(basis, 1, 2, 1, 1, clear=False)[1])
    controls["discarded_dirty_residual"] = dirty != clean
    controls["single_column_route"] = route_address(0, [("NOT", 0)], 1, 2) != 1
    try:
        lowered(basis, 1, 2, 1, 0)
    except ValueError:
        controls["invalid_orientation"] = True
    try:
        scalar_units(["UNKNOWN", 1])
    except ValueError:
        controls["unknown_opcode"] = True
    need(len(controls) == 11 and all(controls.values()), "all actual failure controls")
    result = {"source_files": count, "small_basis_cases": cases,
              "actual_route_addresses": addresses, "dense_width_two_entries": 1 << 18,
              "accounting": accounting(word, caller), "controls": controls}
    expected = HERE / "RESULT.json"
    if expected.exists():
        need(result == json.loads(expected.read_text())["primary"], "frozen exact result")
    print(json.dumps(result, sort_keys=True))
    print("PASS_GLOBAL_LAMBDA_LOWERING")
    return result


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        print("FAIL_GLOBAL_LAMBDA_LOWERING:", exc, file=sys.stderr)
        raise SystemExit(1) from exc
