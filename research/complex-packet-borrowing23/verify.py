"""Exact geometry, chronology and dirty-input checks for pair-target borrowing.

Apache-2.0. NeoKazuya, with substantial OpenAI Codex assistance.
The symbolic argument is in README.md; the finite replays have narrower scopes.
"""
from __future__ import annotations

import argparse
import contextlib
import gzip
import hashlib
import io
import itertools
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
from collections import Counter
from fractions import Fraction

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONSTRUCTOR = "research/complex-k492-owner-repair/code/construct_k_triangle.py"
INPUTS = "research/direct-delivery504-global/inputs/hamming"
SCHEDULE = "research/complex-k492-owner-repair/data/TRI-SCHEDULE.json"
ASSIGNMENT_SEED = 23
SALT = "23|made, shell, arm, script, fix, tape"


class VerificationError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def span(vectors):
    """Explicit XOR closure, independent of the constructor's row reduction."""
    result = {0}
    for vector in vectors:
        result |= {x ^ vector for x in result}
    return frozenset(result)


def rank(space):
    size = len(space)
    require(size > 0 and size & (size - 1) == 0, "not a binary subspace size")
    return size.bit_length() - 1


def join(left, right):
    return frozenset(a ^ b for a in left for b in right)


def cap(port):
    return frozenset(x for x in range(512) if (x & port).bit_count() % 2 == 0)


def selection_hash(value):
    text = SALT + "|" + json.dumps(value, separators=(",", ":"))
    return hashlib.sha256(text.encode()).hexdigest()


def geometry_worker(destination):
    """Execute the pinned, unchanged constructor with its assertions enabled."""
    require(__debug__, "constructor worker requires assertions")
    output = destination.parent / "raw492"
    old_argv = sys.argv[:]
    try:
        sys.argv = [str(ROOT / CONSTRUCTOR), str(ROOT / INPUTS), str(output), str(ROOT / SCHEDULE)]
        with contextlib.redirect_stdout(io.StringIO()):
            ns = runpy.run_path(str(ROOT / CONSTRUCTOR))
    finally:
        sys.argv = old_argv
    require(ns["NH"] == 492, "unexpected selected raw helper count")
    cases = []
    # Full coordinate pairs are the all-K cells, not the mixed K/M family.
    for pair in ns["TRI"]["full_pairs"]:
        pair = tuple(pair)
        for sign in (-1, 1):
            blocks = sorted(c for c in ns["blocks"] if set(pair) <= set(c))
            require(len(blocks) == 3, "coordinate pair does not have three factories")
            leavers, targets = [], []
            alphas = {}
            for block in blocks:
                module = ns["blocks"][block]
                event_index, alpha = ns["face_info"](block, pair, sign)
                alphas[block] = alpha
                for local in module["events"][event_index][:2]:
                    previous = max(j for j in range(event_index) if local in module["events"][j][:2])
                    register = ns["maps"][block][local]
                    leavers.append({
                        "block": list(block), "local_register": local,
                        "raw120_register": register,
                        "frame": module["event_frames"][previous],
                    })
                for target, coefficient in ns["requests"][(block, pair, sign)]:
                    own, own_coefficient, own_frame = ns["own_rows"][target]
                    targets.append({
                        "root_index": target, "port112_index": target - 8,
                        "port": ns["P"][target], "block": list(block),
                        "own_register": own, "own_frame": list(own_frame),
                        "own_coefficient": str(own_coefficient),
                        "request_coefficient": str(coefficient),
                    })
            require(len(leavers) == len(targets) == 6, "not a six-leaver cell")
            # Normalize target i as the target whose cap excludes source i.
            normalized = []
            for source in leavers:
                outside = [t for t in targets if not span(source["frame"]) <= cap(t["port"])]
                require(len(outside) == 1, "source does not have one forbidden target")
                normalized.append(outside[0])
            require(len({t["root_index"] for t in normalized}) == 6, "forbidden targets are not a bijection")
            coefficients = []
            for target in normalized:
                row = []
                for source in leavers:
                    if source["block"] == target["block"]:
                        q = Fraction(target["own_coefficient"]) if source["raw120_register"] == target["own_register"] else Fraction(0)
                    else:
                        q = Fraction(target["request_coefficient"]) * alphas[tuple(source["block"])]
                    row.append(str(q))
                coefficients.append(row)
            cases.append({"pair": list(pair), "sign": sign, "leavers": leavers,
                          "targets": normalized, "coefficients": coefficients})
    # The within-track draw considered all 52 formed faces, including mixed cells.
    formed = [[list(p), sign] for p in itertools.combinations(range(8), 2)
              for sign in (-1, 1) if (p, sign) not in ns["FULLT"]]
    selected = min(formed, key=selection_hash)
    require(selected == [[6, 7], 1], "seed-selected object changed")
    result = {"selected": selected, "formed_candidate_count": len(formed), "cases": cases,
              "raw492_content_sha256": hashlib.sha256(gzip.decompress((output / "FULL-WORD.json.gz").read_bytes())).hexdigest(),
              "raw492_profile": ns["report"]["local_profile"]}
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


def validate_geometry(geometry):
    prototype = json.loads((ROOT / INPUTS / "PROTOTYPE.json").read_bytes())
    cases = geometry["cases"]
    require(len(cases) == 8, "expected eight signed all-K cells")
    source_count = support_count = clock_certificates = 0
    for case in cases:
        sources = [span(s["frame"]) for s in case["leavers"]]
        targets = [cap(t["port"]) for t in case["targets"]]
        require(all(rank(s) == 2 for s in sources), "leaver frame is not rank two")
        require(all(rank(h) == 8 for h in targets), "target cap is not rank eight")
        require(rank(frozenset.intersection(*sources)) == 1, "leavers do not share one line")
        for i, target in enumerate(case["targets"]):
            require(target["port"] == prototype["binary_ports"][target["root_index"]], "target port differs from pinned input")
            require(target["port112_index"] == target["root_index"] - 8, "112-port restriction mismatch")
            for j, source in enumerate(sources):
                require((source <= targets[i]) == (i != j), "all-but-one incidence failed")
                require((Fraction(case["coefficients"][i][j]) != 0) == (i != j), "required scalar coefficient is missing")
            source_count += 1
        for mask in range(1, 64):
            space = span(x for i, source in enumerate(case["leavers"]) if mask >> i & 1 for x in source["frame"])
            require(rank(space) == mask.bit_count() + 1, "unexpected leaver join rank")
            allowed = [i for i, target in enumerate(targets) if space <= target]
            require(allowed == [i for i in range(6) if not mask >> i & 1], "coded support/cap incidence failed")
            support_count += 1
        for a, b in itertools.permutations(range(6), 2):
            remaining = [k for k in range(6) if k not in (a, b)]
            for support in range(1, 1 << len(remaining)):
                shared = [remaining[i] for i in range(len(remaining)) if support >> i & 1]
                k = min(shared)
                require(sources[k] <= targets[a] and sources[k] <= targets[b], "shared witness is not admissible at pair contact")
                require(not sources[a] <= targets[a] and not sources[b] <= targets[b]
                        and not sources[k] <= targets[k], "chronology witness has no forbidden cap")
                clock_certificates += 1
    return {"signed_cells": len(cases), "leaver_target_bindings": source_count,
            "exact_join_supports": support_count, "shared_support_clock_certificates": clock_certificates,
            "geometry_sha256": digest(geometry)}


def chronology_check():
    """Independent finite check of the five-event order contradiction.

    T is the last pair contact, A = Xa->Yb, B = Xb->Ya,
    C = Xa->Yk and D = Xb->Yk. README derives these requirements.
    """
    prefix_admissible = surviving = 0
    branches = Counter()
    for order in itertools.permutations("TABCD"):
        at = {name: order.index(name) for name in order}
        if not (at["T"] < at["A"] and at["T"] < at["B"]
                and at["C"] < at["A"] and at["D"] < at["B"]):
            continue
        prefix_admissible += 1
        if at["C"] < at["D"]:
            branches["C_before_D_forbids_B"] += 1
            surviving += at["B"] < at["D"]
        else:
            branches["D_before_C_forbids_A"] += 1
            surviving += at["A"] < at["C"]
    require(surviving == 0 and prefix_admissible > 0 and len(branches) == 2,
            "chronology obstruction failed or is vacuous")
    return {"orders_examined": 120, "orders_meeting_four_required_precedences": prefix_admissible,
            "surviving_orders": surviving, "contradiction_branches": dict(sorted(branches.items()))}


def scalar_matrix(registers, operations, backward=False):
    size = len(registers)
    index = {name: i for i, name in enumerate(registers)}
    rows = [[Fraction(i == j) for j in range(size)] for i in range(size)]
    for target, source, coefficient in operations:
        t, s, q = index[target], index[source], Fraction(coefficient)
        if backward:
            t, s, q = s, t, -q
        rows[t] = [a + q * b for a, b in zip(rows[t], rows[s])]
    return rows


def expected_matrix(registers, missing=None, backward=False, n=3):
    rows = scalar_matrix(registers, [])
    index = {name: i for i, name in enumerate(registers)}
    for i in range(n):
        for j in range(n):
            if i != j and (i, j) != missing:
                t, s = index[f"y{i}"], index[f"x{j}"]
                if backward:
                    t, s = s, t
                rows[t][s] = Fraction(-1 if backward else 1)
    return rows


def framed_replay(registers, core, source_spaces, target_caps, *, ignore_source_pollution=False):
    """Replay actual ambient F_2^9 frames, then charge every final climb."""
    zero = frozenset({0})
    full = frozenset(range(512))
    current = {r: source_spaces[int(r[1:])] if r.startswith("x") else zero for r in registers}
    final = {r: target_caps[int(r[1:])] if r.startswith("y") else full for r in registers}
    profile = Counter()
    for step, (target, source, _) in enumerate(core):
        frame = join(current[target], current[source])
        for r in (target, source):
            if not frame <= final[r]:
                return {"ok": False, "step": step, "register": r}
        for r in (target, source):
            if ignore_source_pollution and r.startswith("x"):
                continue
            delta = rank(frame) - rank(current[r])
            if delta:
                profile[delta] += 1
            current[r] = frame
    for r in registers:
        require(current[r] <= final[r], "final frame is not reachable")
        delta = rank(final[r]) - rank(current[r])
        if delta:
            profile[delta] += 1
    return {"ok": True, "profile": {str(k): v for k, v in sorted(profile.items())},
            "rank_mass": sum(k*v for k, v in profile.items())}


def scalar_and_escape_checks(selected):
    source_spaces = [span(s["frame"]) for s in selected["leavers"][:3]]
    target_caps = [cap(t["port"]) for t in selected["targets"][:3]]
    basic_registers = ["x0", "x1", "x2", "y0", "y1", "y2"]
    # A source-free zero-frame precondition is allowed; it removes target dirt
    # introduced by the useful later y0->y1 broadcast.
    precondition = [("y1", "y0", -1)]
    events = [("y0", "x2", 1), ("y1", "y0", 1), ("y0", "x1", 1),
              ("y1", "x0", 1), ("y2", "x0", 1), ("y2", "x1", 1)]
    scalar_ok = strict_ok = relaxed_ok = 0
    for order in itertools.permutations(range(6)):
        ops = [events[i] for i in order]
        if scalar_matrix(basic_registers, precondition + ops) != expected_matrix(basic_registers):
            continue
        scalar_ok += 1
        strict_ok += framed_replay(basic_registers, precondition + ops, source_spaces, target_caps)["ok"]
        relaxed_ok += framed_replay(basic_registers, precondition + ops, source_spaces, target_caps,
                                    ignore_source_pollution=True)["ok"]
    require(scalar_ok > 0 and strict_ok == 0 and relaxed_ok > 0,
            "six-event enumeration or source-pollution negative control failed")

    # Dropping one required off-diagonal entry removes the contradiction.
    missing_core = [events[i] for i in (0, 1, 4, 2, 3)]
    require(scalar_matrix(basic_registers, precondition + missing_core)
            == expected_matrix(basic_registers, missing=(2, 1)), "missing-entry scalar control")
    missing_replay = framed_replay(basic_registers, precondition + missing_core, source_spaces, target_caps)
    require(missing_replay["ok"], "missing-entry frame control")

    registers = ["x0", "x1", "x2", "h0", "h1", "y0", "y1", "y2"]
    compensation = [("y1", "y0", -1), ("y0", "h1", -1),
                    ("y1", "h1", 1), ("y1", "h0", -1)]
    escape_core = [("h0", "x0", 1), ("h1", "x1", 1), ("y0", "x2", 1),
                   ("y1", "y0", 1), ("y0", "h1", 1), ("y1", "h0", 1),
                   ("y2", "x0", 1), ("y2", "x1", 1)]
    cleanup = [("h1", "x1", -1), ("h0", "x0", -1)]
    whole = compensation + escape_core + cleanup
    for backward in (False, True):
        require(scalar_matrix(registers, whole, backward) == expected_matrix(registers, backward=backward),
                "two-carrier arbitrary-dirt scalar replay failed")
    escape = framed_replay(registers, compensation + escape_core, source_spaces, target_caps)
    require(escape["ok"], "two-carrier frame replay failed")
    # Cleanup runs after the charged final climbs and touches only full-frame
    # sources/helpers. It therefore incurs no unrecorded frame transitions.
    require(all(not r.startswith("y") for e in cleanup for r in e[:2]), "cleanup touches a target")

    direct = [("y0", "x1", 1), ("y1", "x2", 1), ("y2", "x0", 1),
              ("y0", "x2", 1), ("y1", "x0", 1), ("y2", "x1", 1)]
    require(scalar_matrix(registers, direct) == expected_matrix(registers), "direct dirty-input scalar control")
    baseline = framed_replay(registers, direct, source_spaces, target_caps)
    require(baseline["ok"], "direct frame control")
    delta = Counter({int(k): v for k, v in escape["profile"].items()})
    delta.subtract({int(k): v for k, v in baseline["profile"].items()})
    delta = {str(k): v for k, v in sorted(delta.items()) if v}
    require(delta == {"2": 2, "7": 2, "9": -2}, "paid escape difference changed")
    # 2^s+7^s>9^s follows for every 0<s<1 from strict subadditivity.
    # This integer identity binds the comparison to the verified profiles.
    require(2 + 7 == 9 and baseline["rank_mass"] == escape["rank_mass"], "unmatched rank budget")

    rejected = {}
    for name, bad in (
        ("omit_h0_cleanup", compensation + escape_core + cleanup[:1]),
        ("omit_h1_compensation", compensation[:1] + compensation[2:] + escape_core + cleanup),
        ("double_shared_target_read", compensation + [e if i != 3 else (e[0], e[1], 2)
                                                        for i, e in enumerate(escape_core)] + cleanup),
    ):
        rejected[name] = scalar_matrix(registers, bad) != expected_matrix(registers)
    require(all(rejected.values()), "dirty-input mutation escaped")
    return {"permutations_examined": 720, "arbitrary_input_scalar_passes": scalar_ok,
            "scalar_and_strict_frame_passes": strict_ok,
            "false_passes_when_source_pollution_is_omitted": relaxed_ok,
            "missing_required_entry_control": missing_replay,
            "two_carrier_escape": {**escape, "columns_each_orientation": 8,
                                   "scalar_additions_including_precondition_compensation_cleanup": len(whole),
                                   "all_dirty_helpers_restored": True},
            "matched_stock_direct_control": baseline,
            "escape_minus_direct_profile": delta, "dirty_input_mutations_rejected": rejected}


def verify_sources():
    pins = json.loads((HERE / "SOURCE-PINS.json").read_bytes())
    for relative, expected in pins["sha256"].items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        require(actual == expected, "pinned source changed: " + relative)
    return pins


def coded_cell_checks(selected):
    """Replay the discovered six-source circuit without trusting solver output."""
    witness = json.loads((HERE / "CODED-CELL.json").read_bytes())
    require(witness["selected"] == [selected["pair"], selected["sign"]], "coded cell binding changed")
    require([[Fraction(x) for x in row] for row in selected["coefficients"]]
            == [[Fraction(i != j) for j in range(6)] for i in range(6)],
            "coded witness needs the selected unit-coefficient cell")
    registers = [f"x{i}" for i in range(6)] + ["h0"] + [f"y{i}" for i in range(6)]
    core, direct = witness["core"], witness["direct"]
    require(len(core) == 28 and len(direct) == 30, "unexpected core lengths")
    require(all(q == 1 and t != s and t in registers and s in registers
                and not t.startswith("x") for t, s, q in core), "invalid positive core")
    require(all(t.startswith("y") and s.startswith("x") and q == 1 for t, s, q in direct),
            "direct control is not direct delivery")
    require(all(s.startswith("x") for t, s, _ in core if t == "h0"),
            "compensation derivation requires helper writes from immutable sources")
    precondition = [(t, s, -q) for t, s, q in reversed(core) if not s.startswith("x")]
    cleanup = [(t, s, -q) for t, s, q in reversed(core) if t == "h0"]
    whole = precondition + core + cleanup
    for backward in (False, True):
        expected = expected_matrix(registers, backward=backward, n=6)
        require(scalar_matrix(registers, whole, backward) == expected, "one-helper arbitrary-dirt replay")
        require(scalar_matrix(registers, direct, backward) == expected, "six-source direct replay")
    spaces = [span(s["frame"]) for s in selected["leavers"]]
    caps = [cap(t["port"]) for t in selected["targets"]]
    paid = framed_replay(registers, precondition + core, spaces, caps)
    baseline = framed_replay(registers, direct, spaces, caps)
    require(paid["ok"] and baseline["ok"], "six-source native frame replay")
    require(paid["rank_mass"] == baseline["rank_mass"] == 99, "unmatched six-source stock")
    require(all(t == "h0" and s.startswith("x") for t, s, _ in cleanup),
            "cleanup must run on full-frame sources and helper after final climbs")
    delta = Counter({int(k): v for k, v in paid["profile"].items()})
    delta.subtract({int(k): v for k, v in baseline["profile"].items()})
    delta = {str(k): v for k, v in sorted(delta.items()) if v}
    require(delta == {"1": -16, "2": 5, "3": 5, "9": -1}, "coded cost comparison changed")
    # README proves positivity of direct-minus-coded for every 0<s<1:
    # with x=3^s, it is >= (3-x)(11/3-x)>0. The exact profile above is
    # the finite premise of that analytic argument, not a numerical sampling.
    mutations = {
        "omit_compensation": core + cleanup,
        "omit_helper_cleanup": precondition + core,
        "omit_coded_helper_read": precondition + [e for e in core if e[1] != "h0"] + cleanup,
        "double_shared_target_read": precondition + [
            [t, s, 2 if s.startswith("y") else q] for t, s, q in core] + cleanup,
    }
    rejected = {name: scalar_matrix(registers, bad) != expected_matrix(registers, n=6)
                for name, bad in mutations.items()}
    require(all(rejected.values()), "one-helper mutation escaped")
    return {"witness_sha256": digest(witness), "columns_each_orientation": 13,
            "core_additions": len(core), "zero_frame_precondition_additions": len(precondition),
            "full_frame_cleanup_additions": len(cleanup), "total_scalar_additions": len(whole),
            "coded": paid, "same_stock_direct": baseline,
            "coded_minus_direct_profile": delta, "mutations_rejected": rejected}


def verify_assignment(pins):
    claim = json.loads((HERE / "CLAIM.json").read_bytes())
    require(claim["assignment_seed"] == ASSIGNMENT_SEED and claim["salt"] == SALT,
            "assignment seed or salt changed")
    require(claim["base_commit"] == pins["base_commit"], "assignment base differs from source pins")
    require(claim["salt_sha256"] == hashlib.sha256(SALT.encode()).hexdigest(), "salt digest mismatch")
    candidates = claim["candidates"]
    require(len(candidates) == 3 and len({c["id"] for c in candidates}) == 3, "candidate count changed")
    for candidate in candidates:
        actual = hashlib.sha256((SALT + "|" + candidate["id"]).encode()).hexdigest()
        require(actual == candidate["selection_hash"], "candidate selection digest mismatch")
    require(min(candidates, key=lambda c: c["selection_hash"])["id"]
            == claim["selected"] == "cross-factory-packet-sharing", "selected mechanism changed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--geometry-worker", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--native-worker", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--native-output", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--record", type=Path, help="write a development evidence file instead of comparing EXPECTED.json")
    args = parser.parse_args()
    if args.geometry_worker is not None:
        geometry_worker(args.geometry_worker)
        return
    if args.native_worker is not None:
        require(__debug__, "native worker requires assertions")
        verify_sources()
        native = runpy.run_path(str(HERE / "native.py"))
        result = native["rebuild_and_audit"](json.loads(args.native_worker.read_bytes()), args.native_worker.parent)
        args.native_output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return
    pins = verify_sources()
    verify_assignment(pins)
    with tempfile.TemporaryDirectory(prefix="packet-borrowing23-") as temporary:
        output = Path(temporary) / "geometry.json"
        environment = dict(os.environ)
        environment.pop("PYTHONOPTIMIZE", None)
        result = subprocess.run([sys.executable, "-I", "-B", str(Path(__file__).resolve()),
                                 "--geometry-worker", str(output)], env=environment,
                                capture_output=True, text=True, check=False)
        require(result.returncode == 0, "assertion-enabled constructor worker failed: " + result.stderr[-3000:])
        geometry = json.loads(output.read_bytes())
        native_output = Path(temporary) / "native.json"
        result = subprocess.run([sys.executable, "-I", "-B", str(Path(__file__).resolve()),
                                 "--native-worker", str(output), "--native-output", str(native_output)],
                                env=environment, capture_output=True, text=True, check=False)
        require(result.returncode == 0, "assertion-enabled native audit failed: " + result.stderr[-3000:])
        native = json.loads(native_output.read_bytes())
    selected = next(case for case in geometry["cases"] if [case["pair"], case["sign"]] == geometry["selected"])
    evidence = {"schema": "complex-packet-borrowing23/2", "base_commit": pins["base_commit"],
                "assignment_seed": ASSIGNMENT_SEED, "salt_sha256": hashlib.sha256(SALT.encode()).hexdigest(),
                "selected": geometry["selected"], "formed_candidate_count": geometry["formed_candidate_count"],
                "raw492_content_sha256": geometry["raw492_content_sha256"],
                "geometry": validate_geometry(geometry), "chronology": chronology_check(),
                "scalar_and_paid_controls": scalar_and_escape_checks(selected),
                "one_helper_cell": coded_cell_checks(selected), "native_comparison": native}
    if args.record:
        args.record.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(evidence, indent=2))
        return
    require(evidence == json.loads((HERE / "EXPECTED.json").read_bytes()), "evidence differs from EXPECTED.json")
    print("PASS_COMPLEX_CODED_CELL_AND_PAIR_BORROWING_OBSTRUCTION")
    print("One-helper cell; matched-stock native words, 714 columns each orientation; 8 signed cells; 720 order controls")


if __name__ == "__main__":
    main()
