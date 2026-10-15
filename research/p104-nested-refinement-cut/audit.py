#!/usr/bin/env python3
"""Code-disjoint literal-subspace audit and constructive interval-bypass test.

Tairitsu-Aya, with substantial OpenAI Codex assistance. Apache-2.0.
Does not import verify.py, the old channel producer or its native compiler.
"""
from collections import Counter, defaultdict
from itertools import combinations
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
PIN = "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e"


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def generate(vectors):
    values = {0}
    for v in vectors:
        check(type(v) is int and 0 < v < 512, "binary label")
        values.update({x ^ v for x in tuple(values)})
    return frozenset(values)


def from_basis(vectors):
    result = generate(vectors)
    check(len(result) == 2 ** len(vectors), "independent source basis")
    return result


def reduced_presentation(values):
    # Enumerate each pivot's numerically least representative, without elimination.
    return [min(x for x in values if x.bit_length() == bit)
            for bit in range(9, 0, -1) if any(x.bit_length() == bit for x in values)]


def extend(values, vectors):
    result = set(values)
    for v in vectors:
        result.update({x ^ v for x in tuple(result)})
    return frozenset(result)


def target(values, survivors, hull):
    return len(values) < 512 and (values <= hull or len(values & survivors) >= 2)


def upward_bypass(lo, hi, survivors, hull):
    """Return an actual R->T pair within [lo,hi], or certify none exists.

    This does not use the producer's four sufficient interval categories.
    For an R->T crossing, the target must contain two survivor lines: entry
    into hull is impossible by ascent. A minimum candidate is lo plus those
    two lines and, if lo is in hull, any one vector of hi outside hull.
    Its dimension is independent of the outside vector selected. The README
    proves that this exhausts the possibilities.
    """
    check(lo < hi, "proper nested upward interval")
    if len(lo & survivors) >= 2 or hi <= hull:
        return None
    candidates = sorted(hi & survivors)
    if len(candidates) < 2:
        return None
    other = lo
    if lo <= hull:
        other = extend(lo, [min(hi - hull)])
    check(not target(other, survivors, hull), "candidate R chart")
    for first, second in combinations(candidates, 2):
        goal = extend(other, [first, second])
        if len(goal) == 512:
            continue
        check(lo <= other < goal <= hi and target(goal, survivors, hull), "actual interval bypass")
        return other, goal
    return None


def inspect(word):
    entry = {r: from_basis(v) for r, v in word["initial_frames"].items()}
    exit_frames = {r: from_basis(v) for r, v in word["final_frames"].items()}
    live = dict(entry)
    paths = {r: [v] for r, v in entry.items()}
    moves = []
    lives = []
    owned = None
    counts = Counter()
    for n, event in enumerate(word["program"]):
        kind, reg = event[:2]
        counts[kind] += 1
        if kind == "transport":
            before, after = from_basis(event[2]), from_basis(event[3])
            check(live[reg] == before, "frame continuity")
            check(before < after or after < before, "strict nested source move")
            check(abs(len(before).bit_length() - len(after).bit_length()) == event[4], "paid rank")
            moves.append((n, reg, before, after, event[4]))
            live[reg] = after
            if reg != "C":
                paths[reg].append(after)
        elif kind == "zero":
            check(reg == "C" and reg not in live and owned is None, "owned creation")
            live[reg] = from_basis(event[-1])
            owned = []
        elif kind in ("copy", "add"):
            check(live[reg] == live[event[2]] == from_basis(event[-1]), "common chart")
        elif kind == "erase":
            check(reg == "C" and live[reg] == from_basis(event[-1]), "owned discard")
            del live[reg]
        else:
            raise RuntimeError("unrecognized source operation")
        if reg == "C":
            check(owned is not None, "owned lifetime exists")
            owned.append(n)
            if kind == "erase":
                lives.append(owned)
                owned = None
    check(owned is None and live == exit_frames, "complete final frames")
    check(len(lives) == 8 and all(len(life) == 4 for life in lives), "eight four-event lifetimes")
    check(set(entry) == set(exit_frames) and len(entry) == 280, "persistent roles")
    down = [row for row in moves if row[3] < row[2]]
    check(len(down) == 8, "eight descending occurrences")
    labels = [next(iter(row[3] - {0})) for row in down]
    survivors = frozenset(labels)
    hull = generate(labels)
    check(len(hull) == 256 and len(survivors) == 8, "eight-dimensional survivor hull")
    for _, role, old, new, rank in down:
        check(role == "C" and len(old) == 256 and len(new) == 2 and rank == 7, "drop shape")
        check(old & survivors == new - {0}, "exactly its own survivor in drop hyperplane")
        check(not old <= hull and new <= hull, "descending entry into hull")
    groups = defaultdict(list)
    for n, _, old, new, _ in moves:
        if new < old:
            group = "private_downward_interval"
        else:
            check(upward_bypass(old, new, survivors, hull) is None, "a refined upward bypass exists")
            # Compare the full receipt's convenient four-case classification too.
            if len(new & survivors) <= 1:
                group = "upper_at_most_one_survivor"
            elif new <= hull:
                group = "upper_in_survivor_span"
            elif len(old & survivors) >= 2:
                group = "lower_at_least_two_survivors"
            else:
                check(len(old) == 256 and len(new) == 512, "last cover before full chart")
                group = "last_step_to_full"
        groups[group].append(n)
    inside, outside = [], []
    for k in range(104):
        name = f"X{k}"
        check(len(entry[name]) == 2, "singleton source")
        (inside if target(entry[name], survivors, hull) else outside).append(name)
    target_counts = Counter()
    for k in range(104):
        chart = exit_frames[f"Y{k}"]
        check(len(chart) == 256 and target(chart, survivors, hull), "target endpoint color")
        target_counts[str(len(chart & survivors))] += 1

    def all_slots(prefix):
        out = []
        for k in range(104):
            for values in paths[f"{prefix}{k}"]:
                dimension = len(values).bit_length() - 1
                out.append((values, values, dimension, dimension))
        for _, reg, first, last, rank in moves:
            if reg.startswith(prefix) and rank > 1:
                check(first < last, "data moves ascend")
                out.append((first, last, len(first).bit_length(), len(last).bit_length() - 2))
        return out

    left, right = all_slots("X"), all_slots("Y")
    feasible = 0
    for a, b, amin, amax in left:
        for c, d, cmin, cmax in right:
            available = b & d
            if not a <= available or not c <= available:
                continue
            join_size = len(a) * len(c) // len(a & c)
            least = max(join_size.bit_length() - 1, amin, cmin)
            most = min(len(available).bit_length() - 1, amax, cmax)
            feasible += least <= most
    check(feasible == 0, "direct-read gate")
    signature = [[n, reg, sorted(a), sorted(b), rank] for n, reg, a, b, rank in moves]
    computed = {
        "schema_version": 1,
        "status": "PASS_P104_NESTED_REFINEMENT_CUT",
        "source": {"path": INPUT, "sha256": PIN},
        "ambient_binary_dimension": 9,
        "original_events": sum(counts.values()),
        "original_operations": dict(sorted(counts.items())),
        "transport_occurrences": len(moves),
        "transport_signature_sha256": hashlib.sha256(json.dumps(signature, separators=(",", ":")).encode()).hexdigest(),
        "survivor_lines_in_drop_order": labels,
        "survivor_span_reduced_basis": reduced_presentation(hull),
        "drop_hyperplanes": [reduced_presentation(row[2]) for row in down],
        "survivors_per_drop_hyperplane": [len(row[2] & survivors) for row in down],
        "private_lifetimes": lives,
        "interval_classes": dict(sorted(groups.items())),
        "interval_class_counts": {key: len(value) for key, value in sorted(groups.items())},
        "initial_sources_on_target_side": inside,
        "initial_sources_on_other_side": outside,
        "target_survivor_count_histogram": dict(sorted(target_counts.items())),
        "rank_bounds_in_array_units": {
            "other_side_source_count": len(outside),
            "other_side_source_transfer_upper_bound": len(down),
            "all_source_transfer_upper_bound": len(inside) + len(down),
            "identity_required": len(inside) + len(outside),
            "sharpness_claimed": False,
        },
        "direct_read_gate": {
            "source_slots": len(left), "target_slots": len(right),
            "slot_pairs": len(left) * len(right), "common_chart_pairs": feasible,
            "timing_constraints_used": False,
        },
    }
    # Construct excluded routes instead of merely provoking a producer guard.
    outsider = min(set(range(512)) - hull)
    u = from_basis([outsider])
    v = from_basis([outsider, labels[0], labels[1]])
    bypass = upward_bypass(u, v, survivors, hull)
    check(bypass is not None and bypass == (u, v), "new interval really bypasses")
    full = frozenset(range(512))
    check(upward_bypass(frozenset([0]), full, survivors, hull) is not None,
          "new long initial lift really permits a crossing")
    check(not target(full, survivors, hull), "full frame is not target-side")
    check(all(not target(row[2], survivors, hull) for row in down), "old gather hyperplanes are other-side")
    return computed


def exhaustive_small_interval_controls(labels):
    """Compare the bypass decision with literal all-pairs subspace lattices.

    One lattice has dimension four; another is a four-dimensional quotient
    ending at the full nine-dimensional chart. The latter exercises the
    exceptional color of the full chart, not just small proper charts.
    """
    survivors = frozenset(labels)
    hull = generate(labels)
    outside = min(set(range(512)) - hull)

    def lattice(base, extra):
        quotient = generate(extra)
        found = {frozenset([0])}
        pending = [frozenset([0])]
        while pending:
            current = pending.pop()
            for vector in quotient - current:
                successor = extend(current, [vector])
                if successor not in found:
                    found.add(successor)
                    pending.append(successor)
        return [extend(base, part - {0}) for part in found]

    low = generate([labels[k] ^ labels[7] for k in range(5)])
    growing = low
    extra = []
    for unit in (1 << k for k in range(9)):
        if unit not in growing:
            extra.append(unit)
            growing = extend(growing, [unit])
    check(len(extra) == 4 and len(growing) == 512, "four-dimensional full-chart quotient")
    lattices = [lattice(frozenset([0]), [outside, *labels[:3]]), lattice(low, extra)]
    tested = 0
    for charts in lattices:
        check(len(charts) == 67, "all 67 binary subspaces of dimension-four quotient")
        crossings = [(a, b) for a in charts for b in charts
                     if a < b and not target(a, survivors, hull) and target(b, survivors, hull)]
        for a in charts:
            for b in charts:
                if not a < b:
                    continue
                literal = any(a <= x and y <= b for x, y in crossings)
                constructed = upward_bypass(a, b, survivors, hull) is not None
                check(literal == constructed, "exhaustive interval-bypass comparison")
                tested += 1
    # This safe rank-two interval is outside the four sufficient source cases:
    # its lower chart is the seven-dimensional even survivor subspace.
    even = generate([labels[k] ^ labels[7] for k in range(7)])
    check(len(even) == 128 and not even & survivors, "even survivor hyperplane")
    check(upward_bypass(even, frozenset(range(512)), survivors, hull) is None,
          "four-case classification is sufficient, not necessary")
    return tested


def main():
    data = (ROOT / INPUT).read_bytes()
    check(hashlib.sha256(data).hexdigest() == PIN, "input digest")
    result = inspect(json.loads(data))
    expected = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    check(result == expected, "independent complete receipt comparison")
    tested = exhaustive_small_interval_controls(result["survivor_lines_in_drop_order"])
    print("PASS_INDEPENDENT_P104_REFINEMENT_AUDIT: literal spans, exact upward-bypass test, full receipt")
    print(f"Exhaustive controls: {tested} strict intervals in two complete 67-chart lattices")


if __name__ == "__main__":
    main()
