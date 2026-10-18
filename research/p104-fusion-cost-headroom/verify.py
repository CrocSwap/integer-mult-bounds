#!/usr/bin/env python3
"""Source-bound local P104 fusion budgets. Standard library, Apache-2.0."""

import argparse
import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
GRID = 1 << 160
LOG_TERMS = 128
EXP_TERMS = 24
EXPECTED_PROFILES = {
    2586: [1632, 74, 86, 104, 48, 42, 76, 8],
    2662: [1504, 58, 74, 93, 57, 57, 91, 8],
    2712: [1498, 60, 74, 92, 58, 56, 92, 8],
}
UNIT_MERGES = {
    2662: {2: 16, 3: 28, 4: 39, 5: 30, 6: 15},
    2712: {1: 2, 2: 16, 3: 28, 4: 40, 5: 30, 6: 16},
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def enclose_grid(lower, upper, grid=GRID):
    require(lower <= upper and grid > 0, "interval order/grid")
    return Q((lower * grid).__floor__(), grid), Q((upper * grid).__ceil__(), grid)


def log_bounds(rank):
    """ln(r) = 2 sum z^(2k+1)/(2k+1), z=(r-1)/(r+1)."""
    require(type(rank) is int and 1 <= rank <= 8, "log rank domain")
    z = Q(rank - 1, rank + 1)
    square = z * z
    power, total = z, Q(0)
    for k in range(LOG_TERMS):
        total += 2 * power / (2 * k + 1)
        power *= square
    tail = 2 * power / ((2 * LOG_TERMS + 1) * (1 - square))
    return enclose_grid(total, total + tail)


def exp_negative_bounds(x):
    """Alternating Taylor enclosure for exp(-x), with 0 <= x <= 1."""
    require(0 <= x <= 1, "exponential domain")
    term, total = Q(1), Q(1)
    for k in range(1, EXP_TERMS + 1):
        term *= -x / k
        total += term
    lower = total - abs(term * x / (EXP_TERMS + 1))
    return lower, total


def power_bounds(rank, saving, logs):
    require(0 <= saving <= Q(1, 50), "saving domain")
    lo, hi = logs[rank]
    lower = rank * exp_negative_bounds(saving * hi)[0]
    upper = rank * exp_negative_bounds(saving * lo)[1]
    return enclose_grid(lower, upper)


def gain_bounds(before, after, saving, logs):
    lower, upper = Q(0), Q(0)
    for rank in range(1, 9):
        count = before[rank - 1] - after[rank - 1]
        if count:
            lo, hi = power_bounds(rank, saving, logs)
            lower += count * (lo if count > 0 else hi)
            upper += count * (hi if count > 0 else lo)
    return lower, upper


def binary_rank(vectors):
    require(len(vectors) <= 18, "binary row count")
    pivots = [0] * 9
    for original in vectors:
        require(type(original) is int and 0 < original < 512, "binary vector")
        value = original
        for bit in range(8, -1, -1):
            if value & (1 << bit):
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return sum(value != 0 for value in pivots)


def profile_from_word(word):
    require(word.get("schema_version") == 1, "word schema")
    events = word["program"]
    require(type(events) is list and 1 <= len(events) <= 6000, "event bound")
    profile, counts = Counter(), Counter()
    for event in events:
        require(type(event) is list and event, "event shape")
        op = event[0]
        require(op in ("transport", "add", "sign", "zero", "erase"), "opcode")
        counts[op] += 1
        if op == "transport":
            require(len(event) == 5, "transport shape")
            old, new, rank = event[2:]
            require(type(old) is list and type(new) is list, "frame shape")
            require(max(len(old), len(new)) <= 9, "frame dimension bound")
            d0, d1 = binary_rank(old), binary_rank(new)
            require(d0 == len(old) and d1 == len(new), "independent frame rows")
            require(binary_rank(old + new) == max(d0, d1), "nested transport")
            require(type(rank) is int and 1 <= rank <= 8, "child rank domain")
            require(rank == abs(d1 - d0), "declared/intrinsic transport rank")
            profile[rank] += 1
    return [profile[r] for r in range(1, 9)], dict(sorted(counts.items()))


def read_bounded(path, compressed=False):
    require(path.stat().st_size <= 2_000_000, "input container bound")
    if compressed:
        with gzip.open(path, "rb") as stream:
            data = stream.read(2_000_001)
    else:
        data = path.read_bytes()
    require(len(data) <= 2_000_000, "input payload bound")
    return data


def checked_payload(path, digest, compressed=False):
    data = read_bounded(path, compressed)
    require(hashlib.sha256(data).hexdigest() == digest, "source SHA256: " + str(path))
    return data


def load_sources(package=PACKAGE, root=ROOT):
    sources = json.loads(read_bounded(package / "SOURCES.json"))
    files = sources["files"]
    require(len(files) == 3, "selected input inventory")
    selected = {}
    for entry in files:
        if entry["path"] == "certificates/selected-result.json":
            # Preserve the historical calculation when the live selection changes.
            path = package / "inputs/SELECTED-AT-BASE.json"
            selected[entry["path"]] = json.loads(checked_payload(path, entry["sha256"]))
        elif entry["usage"] == "input":
            path = root / entry["path"]
            selected[entry["path"]] = json.loads(checked_payload(path, entry["sha256"]))
    record = selected["certificates/selected-result.json"]
    assembly_path = "research/community-frontier1094-audit/ASSEMBLY.json"
    require(record["certificate"] == assembly_path, "selected certificate binding")
    assembly = selected[assembly_path]
    data = read_bounded(root / assembly_path)
    require(hashlib.sha256(data).hexdigest() == record["certificate_sha256"],
            "selected certificate digest")
    require(assembly["kappa"] == record["kappa"], "selected kappa binding")
    predecessors = json.loads(read_bounded(package / "PREDECESSORS.json"))["files"]
    require(len(predecessors) == 6, "predecessor inventory")
    words = {}
    for entry in predecessors:
        path = package / entry["path"]
        data = checked_payload(path, entry["sha256"], entry["compressed"])
        header = b"blob " + str(len(data)).encode("ascii") + b"\0"
        require(hashlib.sha1(header + data).hexdigest() == entry["git_blob"],
                "source Git blob")
        if entry["compressed"]:
            words[entry["pr"]] = json.loads(data)
    require(set(words) == {2586, 2662, 2712}, "word inventory")
    return words, Q(assembly["complex_lower"]), record["kappa"]


def validate_profiles(words):
    profiles, receipts = {}, {}
    for pr in (2586, 2662, 2712):
        profile, counts = profile_from_word(words[pr])
        require(profile == EXPECTED_PROFILES[pr], "complete profile " + str(pr))
        mass = sum(rank * count for rank, count in enumerate(profile, 1))
        require(mass == 3542, "rank mass")
        require({k: v for k, v in counts.items() if k != "transport"} ==
                {"add": 3104, "erase": 8, "sign": 208, "zero": 8}, "retained event counts")
        profiles[pr] = profile
        receipts[str(pr)] = dict(profile=profile, rank_mass=mass, counts=counts)
    for pr in (2662, 2712):
        delta = [0] * 8
        for rank, count in UNIT_MERGES[pr].items():
            delta[0] += count
            delta[rank - 1] += count
            delta[rank] -= count
        require(delta == [n - m for n, m in zip(profiles[2586], profiles[pr], strict=True)],
                "unit-merge decomposition for monotonicity")
    return profiles, receipts


def display_interval(bounds):
    lo, hi = enclose_grid(*bounds, grid=10**18)
    return [str(lo), str(hi)]


def break_even(before, after, logs):
    """Locate the unique gain=1 point on a decimal grid, by certified signs."""
    # Uniqueness uses the checked unit-merge decomposition and README derivative proof.
    grid = 10**12
    left, right = 0, grid // 50
    require(gain_bounds(before, after, Q(left, grid), logs)[1] < 1, "root left")
    require(gain_bounds(before, after, Q(right, grid), logs)[0] > 1, "root right")
    for _ in range(35):
        if right - left == 1:
            break
        mid = (left + right) // 2
        lo, hi = gain_bounds(before, after, Q(mid, grid), logs)
        require(hi < 1 or lo > 1, "root sign unresolved")
        if hi < 1:
            left = mid
        else:
            right = mid
    require(right - left == 1, "root iteration bound exhausted")
    return dict(saving_bracket=[str(Q(left, grid)), str(Q(right, grid))],
                left_gain=display_interval(gain_bounds(before, after, Q(left, grid), logs)),
                right_gain=display_interval(gain_bounds(before, after, Q(right, grid), logs)))


def rejected(name, action, fragment):
    try:
        action()
    except ValueError as exc:
        require(fragment in str(exc), "wrong rejection: " + name)
        return name
    raise ValueError("control accepted: " + name)


def controls(words, profiles, saving, logs):
    bad = json.loads(json.dumps(words[2662]))
    event = next(e for e in bad["program"] if e[0] == "transport")
    event[4] += 1
    names = [rejected("wrong intrinsic rank", lambda: profile_from_word(bad), "transport rank")]
    altered = {k: list(v) for k, v in profiles.items()}
    altered[2662][0] -= 1
    altered[2662][1] += 2
    altered[2662][2] -= 1
    require(sum((r + 1) * n for r, n in enumerate(altered[2662])) == 3542,
            "mass-preserving control")
    wrong = gain_bounds(profiles[2586], altered[2662], saving, logs)
    right = gain_bounds(profiles[2586], profiles[2662], saving, logs)
    require(wrong[1] < right[0], "equal mass must not imply equal moment")
    names.append("equal-mass different profile")
    require(gain_bounds(profiles[2662], profiles[2586], saving, logs)[1] < 0,
            "reversed improvement")
    names.append("reversed comparison")
    for pr in (2662, 2712):
        upper = gain_bounds(profiles[2586], profiles[pr], saving, logs)[1]
        require(upper - 1 < 0, "one extra H1 cannot improve")
    names.append("one uncompensated H1")
    names.append(rejected("negative saving", lambda: power_bounds(2, Q(-1, 100), logs),
                          "saving domain"))
    require(gain_bounds(profiles[2586], profiles[2712], Q(0), logs) == (0, 0),
            "zero-saving equal-mass control")
    names.append("zero-saving no strict improvement")
    return names


def audit(package=PACKAGE, root=ROOT):
    words, saving, kappa = load_sources(package, root)
    profiles, receipts = validate_profiles(words)
    logs = {r: log_bounds(r) for r in range(1, 9)}
    comparisons = {}
    for pr in (2662, 2712):
        before, after = profiles[2586], profiles[pr]
        selected = gain_bounds(before, after, saving, logs)
        target = gain_bounds(before, after, Q(1, 99), logs)
        require(0 < selected[0] < selected[1] < 1, "selected one-H1 budget")
        require(3 < target[0] < target[1] < 4, "target H1 budget")
        comparisons[str(pr)] = dict(selected_gain=display_interval(selected),
                                    planning_target_gain=display_interval(target),
                                    unit_merges={str(r): n for r, n in UNIT_MERGES[pr].items()},
                                    one_H1_break_even=break_even(before, after, logs))
    incremental = gain_bounds(profiles[2662], profiles[2712], saving, logs)
    require(0 < incremental[0] < incremental[1] < Q(1, 50), "retiming incremental budget")
    return dict(schema_version=1, status="PASS_P104_FUSION_COST_HEADROOM",
                selected_primitive_saving=str(saving), selected_kappa=kappa,
                planning_target_saving="1/99", profiles=receipts, comparisons=comparisons,
                retiming_incremental_gain=display_interval(incremental),
                controls=controls(words, profiles, saving, logs),
                scope="Fixed caller normalization; added H1 has no offsetting credits; no supplier or kappa claim")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write an additional receipt exclusively")
    args = parser.parse_args()
    result = audit()
    require(result == json.loads(read_bounded(PACKAGE / "RESULT.json")), "stored result mismatch")
    if args.out:
        with args.out.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    print("PASS_P104_FUSION_COST_HEADROOM profiles=3 comparisons=2 controls=6 no_new_kappa")


if __name__ == "__main__":
    main()
