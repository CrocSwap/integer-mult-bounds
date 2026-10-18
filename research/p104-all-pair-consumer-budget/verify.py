#!/usr/bin/env python3
"""Exact conditional P104 consumer screen for every positive pair count."""

import argparse
import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
KAPPA = Q(836330098538459, 500000000000000000)
FORWARD = {1: 1216, 2: 74, 3: 86, 4: 104, 5: 48, 6: 42, 7: 68, 8: 8}
DUAL = {1: 1498, 2: 60, 3: 74, 4: 92, 5: 58, 6: 56, 7: 92, 8: 8}
PROGRESS = 104 * 8 + 104 * 8 + 150 * 9
MAX_JSON_BYTES = 2_000_000


def require(condition, message):
    """Keep proof checks enabled under Python -O."""
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    """Reject duplicate JSON keys rather than silently accepting a last value."""
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate key: {key}")
        result[key] = value
    return result


def load_json(path, compressed=False):
    """Read bounded JSON, including bounded decompression of retained words."""
    require(path.stat().st_size <= MAX_JSON_BYTES, f"oversized input: {path}")
    opener = gzip.open if compressed else open
    with opener(path, "rb") as stream:
        raw = stream.read(MAX_JSON_BYTES + 1)
    require(len(raw) <= MAX_JSON_BYTES, f"oversized payload: {path}")
    return json.loads(raw, object_pairs_hook=unique_object), raw


def authenticate():
    """Authenticate live sources and original retained Git blobs without Git."""
    sources, _ = load_json(PACKAGE / "SOURCES.json")
    require(len(sources["files"]) <= 8, "live source inventory bound")
    for row in sources["files"]:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            require(path.stat().st_size <= MAX_JSON_BYTES, "live input size")
            raw = path.read_bytes()
            require(hashlib.sha256(raw).hexdigest() == row["sha256"], row["path"])
    predecessors, _ = load_json(PACKAGE / "PREDECESSORS.json")
    require(len(predecessors["files"]) == 4, "predecessor inventory")
    for row in predecessors["files"]:
        path = PACKAGE / row["path"]
        require(path.stat().st_size <= MAX_JSON_BYTES, "predecessor container size")
        opener = gzip.open if path.suffix == ".gz" else open
        with opener(path, "rb") as stream:
            raw = stream.read(MAX_JSON_BYTES + 1)
        require(len(raw) <= MAX_JSON_BYTES, "predecessor payload size")
        require(hashlib.sha256(raw).hexdigest() == row["raw_sha256"], row["path"])
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(
            hashlib.sha1(blob, usedforsecurity=False).hexdigest() == row["git_blob"],
            "original Git blob",
        )


def binary_rank(vectors):
    """Eliminate at most eighteen vectors in the fixed nine-bit label space."""
    require(len(vectors) <= 18, "frame vector bound")
    pivots = [0] * 9
    for value in vectors:
        require(type(value) is int and 0 < value < 512, "binary frame vector")
        for bit in range(8, -1, -1):
            if value & (1 << bit):
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return sum(value != 0 for value in pivots)


def transport_profile(events):
    """Recount nested-frame ranks, not just the declared rank field."""
    require(len(events) <= 6000, "event bound")
    profile = Counter()
    for event in events:
        if event[0] != "transport":
            continue
        require(len(event) == 5, "transport shape")
        before, after, declared = event[2:]
        left, right = binary_rank(before), binary_rank(after)
        require(binary_rank(before + after) == max(left, right), "nonnested transport")
        rank = abs(right - left)
        require(
            type(declared) is int and rank == declared and 1 <= rank <= 8,
            "transport rank",
        )
        profile[rank] += 1
    return dict(sorted(profile.items()))


def endpoint_progress(document):
    """Recount net persistent frame progress, without admitting owner hosting."""
    initial, final = document["initial_frames"], document["final_frames"]
    require(initial.keys() == final.keys(), "persistent endpoint inventory")
    require(len(initial) <= 358, "persistent role bound")
    return sum(binary_rank(frame) for frame in final.values()) - sum(
        binary_rank(frame) for frame in initial.values()
    )


def source_profiles():
    """Retain predecessor native correctness; independently recount its invoice."""
    core, raw = load_json(
        ROOT / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
    )
    correction, _ = load_json(
        PACKAGE / "inputs/PR2458-CIRCUIT.json.gz", compressed=True
    )
    dual, _ = load_json(PACKAGE / "inputs/PR2712-WORD.json.gz", compressed=True)
    require(
        hashlib.sha256(raw).hexdigest() == correction["source_witness_sha256"],
        "core binding",
    )
    added = correction["insertions"]
    require(len(added) == 2, "two forward insertion cuts")
    forward = Counter(transport_profile(core["program"]))
    for insertion in added:
        forward.update(transport_profile(insertion["events"]))
    require(dict(forward) == FORWARD, "forward profile")
    require(transport_profile(dual["program"]) == DUAL, "dual profile")
    require(
        not core["initial_frames"].keys() & correction["initial_frames"].keys(),
        "disjoint added forward roles",
    )
    require(
        endpoint_progress(core) + endpoint_progress(correction) == PROGRESS,
        "forward endpoint progress",
    )
    require(endpoint_progress(dual) == PROGRESS, "dual endpoint progress")
    return dict(sorted(forward.items())), dict(DUAL)


def log_lower(value):
    """128-term positive atanh sum, rounded down to six decimal places."""
    require(type(value) is Q and Q(1) <= value <= Q(137), "log domain")
    require(value.denominator <= 8, "log denominator bound")
    t = (value - 1) / (value + 1)
    term, total = t, Q(0)
    for index in range(128):
        total += 2 * term / (2 * index + 1)
        term *= t * t
    return Q((total * 1_000_000).__floor__(), 1_000_000)


def mass(profile):
    return sum(rank * count for rank, count in profile.items())


def discounted(dual, units=416):
    """Removing H1 grants at least any integer-rank deletion of the same mass."""
    require(type(units) is int and 0 <= units <= dual[1], "discount bound")
    result = dict(dual)
    result[1] -= units
    return result


def coefficients(forward, dual, width):
    """L(p) >= A*p+B once the caller width is at least this fixed width."""
    logs = {rank: log_lower(Q(width, rank)) for rank in range(1, 9)}
    slope = sum((forward[r] + dual[r]) * r * logs[r] for r in logs)
    intercept = sum(forward[r] * r * logs[r] for r in logs)
    return slope, intercept


def prove(forward, dual, rate=KAPPA):
    """Finite base cases and an affine infinite tail, never a large-p census."""
    require(type(rate) is Q and Q(0) < rate < Q(1), "saving domain")
    relaxed = discounted(dual)
    require(mass(forward) == 3070 and mass(relaxed) == 3126, "source masses")
    # All p have mass excess 56-40p before clamping negative idle to zero.
    require(mass(forward) - PROGRESS == 56, "mass intercept")
    require(mass(forward) + mass(relaxed) - 2 * PROGRESS - 208 == -40, "mass slope")
    p1_excess = 2 * mass(forward) + mass(relaxed) - 25 * 208
    require(p1_excess == 4066, "p=1 without banks mass test")
    # I_B >= (m-1)W+mB-(2p+1)C gives excess 56-40p even when clamped.
    p1_bank_excess = 2 * mass(forward) + mass(relaxed) - 3 * PROGRESS - 208
    require(p1_bank_excess == 16, "p=1 arbitrary fully paid banks mass test")
    finite = []
    for pairs in range(2, 8):
        width, roles = 16 * pairs + 9, 208 * pairs
        idle = (width - 1) * roles - (2 * pairs + 1) * PROGRESS
        require(idle >= 0, "nonnegative idle base case")
        slope, intercept = coefficients(forward, relaxed, width)
        numerator = 56 - 40 * pairs + rate * (slope * pairs + intercept)
        require(
            numerator > 46, f"finite p={pairs} does not reject by the stated margin"
        )
        finite.append(
            {
                "pairs": pairs,
                "width": width,
                "idle_mass": idle,
                "excess_numerator_lower": str(numerator),
            }
        )
    slope, intercept = coefficients(forward, relaxed, 137)
    tail_slope, tail_intercept = rate * slope - 40, 56 + rate * intercept
    require(tail_slope > Q(2, 3) and tail_intercept > 76, "infinite-tail positivity")
    return {
        "p1_mass_excess": p1_excess,
        "p1_any_paid_banks_mass_excess_lower": p1_bank_excess,
        "finite": finite,
        "tail_from_pairs": 8,
        "tail_slope_lower": str(tail_slope),
        "tail_intercept_lower": str(tail_intercept),
        "tail_log_lower": {str(r): str(log_lower(Q(137, r))) for r in range(1, 9)},
    }


def run():
    authenticate()
    forward, dual = source_profiles()
    assembly, _ = load_json(
        ROOT / "research/community-frontier1094-audit/ASSEMBLY.json"
    )
    require(Q(assembly["kappa"]) == KAPPA, "selected benchmark binding")
    result = prove(forward, dual)
    return {
        "schema_version": 1,
        "status": "PASS_P104_ALL_PAIR_CONSUMER_BUDGET",
        "benchmark_kappa": str(KAPPA),
        "forward_profile": forward,
        "dual_profile": dual,
        "forgiven_dual_rank_units": 416,
        "granted_progress_per_call": PROGRESS,
        "proof": result,
        "scope": (
            "Conditional paired-chain coverage; all integer p>=1 and finite fully "
            "paid banks. No supplier or new kappa."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write", action="store_true", help="replace this package's RESULT.json"
    )
    args = parser.parse_args()
    result = run()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        written = (PACKAGE / "RESULT.json").write_text(encoded)
        require(written == len(encoded), "incomplete receipt write")
    else:
        expected, _ = load_json(PACKAGE / "RESULT.json")
        expected_encoding = json.dumps(expected, indent=2, sort_keys=True) + "\n"
        require(encoded == expected_encoding, "receipt mismatch")
    print(result["status"] + " all_p>=1 finite=6 tail_from=8 no_new_kappa")


if __name__ == "__main__":
    main()
