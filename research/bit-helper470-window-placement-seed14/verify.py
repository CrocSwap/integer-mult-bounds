#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fixed-slot timing and cost of PR1256's helper470 endpoint, not admission.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance.
PR1256 owns the local patch; PR589/555 and PR510/463/442 own its inputs.
"""
import argparse
import copy
import gzip
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "research/e8-bit-p111-tuned/"
WORD = PREFIX + "tune/bitE8mut-p111-tuned.json.gz"
RECORD = PREFIX + "tune/EXPECTED.json"
SELECTION = PREFIX + "data/selection9-p111.json"
CHAIN = PREFIX + "vendor/pr510/e8-r480-nine-stage/vendor/"
GLOBAL = CHAIN + "e8-r715-eleven-stage-whole/code/global_k.py"
HOSTING = CHAIN + "idle-axis-hosting/hosting_core.py"
SEED, V, R, T, M, W = 14, 111, 439, 32, 64, 28416
HELPER = 470 - 2 * V
SAVING = Q(1733427039589844234749, 10**24)
LOCAL_DELTA = Counter({1: 1, 5: 1, 7: -1})


class Reject(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise Reject(message)


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def counts(hist):
    return {str(r): n for r, n in sorted(hist.items()) if n}


def difference(left, right):
    out = Counter(left)
    out.subtract(right)
    return Counter({r: n for r, n in out.items() if n})


def add_hist(*parts):
    out = Counter()
    for part in parts:
        out.update(part)
    return Counter({r: n for r, n in out.items() if r and n})


def read_inputs(root=ROOT):
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    data = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        raw = (root / row["path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA256: " + row["path"])
        header = b"blob " + str(len(raw)).encode() + b"\0"
        require(hashlib.sha1(header + raw).hexdigest() == row["git_blob"], "source Git blob")
        data[row["path"]] = raw
    return data


def rational_basis(vectors):
    pivots = {}
    for vector in vectors:
        row = list(map(Q, vector))
        for pivot, basis in sorted(pivots.items()):
            coefficient = row[pivot]
            if coefficient:
                row = [x - coefficient * y for x, y in zip(row, basis)]
        pivot = next((i for i, x in enumerate(row) if x), None)
        if pivot is not None:
            scale = row[pivot]
            pivots[pivot] = tuple(x / scale for x in row)
    return pivots


class Geometry:
    def __init__(self, word):
        self.bases = [rational_basis(word["lines"][i] for i in f) for f in word["frames"]]

    def rank(self, frame):
        return len(self.bases[frame])

    @lru_cache(None)
    def nested(self, first, second):
        for vector in self.bases[first].values():
            row = list(vector)
            for pivot, basis in sorted(self.bases[second].items()):
                scale = row[pivot]
                row = [x - scale * y for x, y in zip(row, basis)]
            if any(row):
                return False
        return True


def local_replay(word, geometry, retired=False, omit_early=None, stale_cleanup=False):
    """Reprice the credited patch. Scatter inherits the abstract COPY contract.

    This is not a native COPY compiler or reverse physical frame routing.
    """
    n = 2 * V + R
    require((word["v"], word["R"], word["h"]) == (V, R, 8), "word dimensions")
    frames = list(word["start"])
    values = [1 << i for i in range(n)]
    histogram, operations = Counter(), Counter()
    paths = [[f] for f in frames]
    scalar = []

    def move(register, frame):
        old = frames[register]
        require(geometry.nested(old, frame), "local frame descent")
        if old != frame:
            rank = geometry.rank(frame) - geometry.rank(old)
            require(rank > 0, "equal-space frame alias")
            histogram[rank] += 1
            operations["MOVE"] += 1
            frames[register] = frame
            paths[register].append(frame)

    def add(target, source):
        require(target != source, "self ADD")
        values[target] ^= values[source]
        scalar.append((target, source))
        operations["ADD"] += 1

    def gates(section):
        for frame, target, sources in section:
            require(len(set([target, *sources])) == 1 + len(sources), "gate operands")
            for register in [target, *sources]:
                move(register, frame)
            for source in sources:
                add(target, source)

    gates(word["D"])
    gates(word["A"])
    require(all(frames[i] == 0 for i in range(V, 2 * V)), "scatter target frame")
    copy_ranks = [geometry.rank(frames[h]) for h in word["ret"]]
    require(copy_ranks == [7] * 9, "retained COPY charges")
    histogram.update(copy_ranks)
    operations.update(COPY=9, ERASE=9)
    for target, sources in enumerate(word["scatter"], V):
        for source in sources:
            add(target, word["ret"][source])
    if retired:
        early = [[186, 470, [77]], [513, 444, [470]], [513, 475, [470]]]
        gates([g for i, g in enumerate(early) if i != omit_early])
        require(values[470] == 1 << 470, "helper restoration")
        require(all(not (x >> 470 & 1) for i, x in enumerate(values) if i != 470), "helper isolation")
    gates(word["B"])
    cleanup = copy.deepcopy(word["C"])
    if retired and not stale_cleanup:
        require(cleanup[580] == [1, 444, [470]] and cleanup[2343] == [1, 470, [77]], "PR1256 patch operands")
        cleanup[580] = [1, 444, [77]]
        del cleanup[2343]
    gates(cleanup)
    final = list(word["final"])
    if retired:
        final[470] = 513
    for register, frame in enumerate(final):
        move(register, frame)
    target = [(1 << i) ^ ((1 << (i - V)) if V <= i < 2 * V else 0) for i in range(n)]
    require(values == target, "all dirty forward columns")
    inverse = [1 << i for i in range(n)]
    for dst, src in reversed(scalar):
        inverse[dst] ^= inverse[src]
    require(inverse == target, "all dirty inverse scalar columns")
    result = {
        "operations": dict(sorted(operations.items())), "profile": counts(histogram),
        "rank_mass": sum(r * k for r, k in histogram.items()), "children": sum(histogram.values()),
        "helper470_frames": paths[470], "helper470_dimensions": [geometry.rank(f) for f in paths[470]],
        "columns_each_direction": n, "copy_ranks": copy_ranks,
    }
    return result, paths


def schedule():
    """Independent transcription of the pinned K=4 recipe and idle-level rule."""
    events = [{"kind": "local", "stage": 0, "pair": 0, "reverse": False}]
    for pair in range(4):
        events.append({"kind": "local", "stage": 2 * pair + 1, "pair": pair, "reverse": True})
        if pair < 3:
            events.append({"kind": "bridge", "dst": pair, "src": pair + 1, "coefficient": 1})
        events.append({"kind": "local", "stage": 2 * pair + 2, "pair": pair, "reverse": False})
        if pair < 3:
            events.append({"kind": "bridge", "dst": pair, "src": pair + 1, "coefficient": -1})
    events += [{"kind": "bridge", "dst": j + 1, "src": j, "coefficient": 1} for j in (2, 1, 0)]
    events.append({"kind": "exchange"})
    result, levels, index = [], [-1] * 4, 0
    for event in events:
        result.append(event)
        if event["kind"] != "local":
            continue
        stage, pair = event["stage"], event["pair"]
        require(levels[pair] == stage - 1, "recipe levels")
        levels[pair] = stage
        if stage in (1, 3, 5):
            destinations = [(stage + 1) // 2]
        elif stage in (2, 4, 6):
            destinations = [stage // 2]
        elif stage == 8:
            destinations = list(range(4))
        else:
            destinations = []
        for destination in destinations:
            old = levels[destination]
            result.append({"kind": "idle", "idx": index, "pair": destination,
                           "rank": 7 * (stage - old), "source_level": old, "target_level": stage})
            levels[destination] = stage
            index += 1
    require(levels == [8] * 4 and index == 10, "complete idle schedule")
    return result


def windows(events):
    """Backward scan each child; no imported producer window implementation."""
    result = {}
    for at, event in enumerate(events):
        if event["kind"] != "idle":
            continue
        pair = event["pair"]
        allowed = []
        for earlier in reversed(events[:at]):
            kind = earlier["kind"]
            if kind == "bridge" and pair in (earlier["dst"], earlier["src"]):
                break
            if kind == "local":
                if pair == earlier["pair"]:
                    break
                allowed.append(earlier["stage"])
        result[event["idx"]] = (pair, event["rank"], tuple(sorted(allowed)))
    return result


def allocate(selection):
    """Recreate the published deterministic slot ordering without imports."""
    allocation, next_helper = [], Counter()
    demand = defaultdict(list)
    for child, width, stage, count in sorted(selection["stages"]):
        demand[child, width].extend([stage] * count)
    pattern_by_child = defaultdict(list)
    for child, widths, count in selection["patterns"]:
        pattern_by_child[child].append((tuple(widths), count))
    for child in sorted(pattern_by_child):
        family_copy, consumed = 0, Counter()
        for pattern, count in sorted(pattern_by_child[child], key=lambda p: (-sum(p[0]), p[0])):
            for _ in range(count):
                offset = 0
                for width in sorted(pattern, reverse=True):
                    stage = demand[child, width][consumed[width]]
                    consumed[width] += 1
                    helper = next_helper[stage, width]
                    next_helper[stage, width] += 1
                    allocation.append((child, family_copy, offset, width, stage, helper))
                    offset += width
                family_copy += 1
        require(family_copy == 2 * V, "family copies per child")
        require(all(consumed[w] == len(seq) for (i, w), seq in demand.items() if i == child), "selection demand")
    require(next_helper == Counter({(stage, 8): R for stage in range(9)}), "complete selected helpers")
    return allocation


def placement_audit(allocation, win, converted):
    used, seen = defaultdict(set), set()
    for child, cp, offset, width, stage, helper in allocation:
        require(child in win and stage in win[child][2], "outside untouched window")
        require(0 <= cp < 2 * V and 0 <= stage < 9 and 0 <= helper < R, "owner domain")
        expected_width = 7 if helper == HELPER and stage in converted else 8
        require(width == expected_width, "helper residual width")
        require(offset >= 0 and offset + width <= win[child][1], "slot extent")
        cells = set(range(offset, offset + width))
        require(not used[child, cp].intersection(cells), "coordinate collision")
        used[child, cp].update(cells)
        require((stage, helper) not in seen, "duplicate helper")
        seen.add((stage, helper))
        active_pair = 0 if stage == 0 else (stage - 1) // 2
        require(win[child][0] != active_pair, "host is active data")
    require(seen == set(itertools.product(range(9), range(R))), "missing helper")
    remainder = {(child, cp): rank - len(used[child, cp])
                 for child, (_, rank, _) in win.items() if rank
                 for cp in range(2 * V)}
    require(all(r >= 0 for r in remainder.values()), "negative idle rank")
    return remainder, used


def owners_for_replicas(allocation, win):
    owners = []
    for replica in range(T):
        for child, cp, offset, width, stage, helper in allocation:
            side, port = divmod(cp, V)
            family = replica * (8 * V) + (2 * win[child][0] + side) * V + port
            require(0 <= family < W, "physical owner index")
            owners.append((stage, replica, helper, family, child, offset, width))
    require(len(owners) == 9 * T * R, "replicated owner count")
    return owners


def full_profile(local, allocation, win, converted):
    remainder, _ = placement_audit(allocation, win, converted)
    result = Counter({rank: 9 * T * count for rank, count in local.items()})
    result.update({rank: len(converted) * T * count for rank, count in LOCAL_DELTA.items()})
    result.update(Counter({r: n * T for r, n in Counter(remainder.values()).items() if r}))
    require(all(n > 0 for n in result.values()), "nonpositive full-profile entry")
    return result


def single_delta(old_remainder, destination=None):
    # destination=None shrinks in place; destination=7 or 42 relocates.
    delta = Counter(LOCAL_DELTA)
    if destination is None:
        delta.update({old_remainder + 1: 1})
        delta.subtract({old_remainder: 1})
    else:
        delta.update({old_remainder + 8: 1})
        delta.subtract({old_remainder: 1, destination: 1})
        if destination > 7:
            delta[destination - 7] += 1
    require(sum(r * n for r, n in delta.items()) == 0, "all returned and consumed idle rank")
    return add_hist(delta)


def outward(lower, upper, bits=160):
    scale = 1 << bits
    return Q((lower * scale).__floor__(), scale), Q((upper * scale).__ceil__(), scale)


@lru_cache(None)
def weight(rank):
    """Exact positive atanh logarithm and exponential tails; no float decisions."""
    require(0 <= rank <= M, "rank domain")
    if rank == 0:
        return Q(0), Q(0)
    x, shifts = Q(M, rank), 0
    while x > 2:
        x /= 2
        shifts += 1

    def log_reduced(value):
        z = (value - 1) / (value + 1)
        z2, power, total = z * z, z, Q(0)
        for j in range(64):
            total += power / (2 * j + 1)
            power *= z2
        return 2 * total, 2 * total + 2 * power / (129 * (1 - z2))

    l, u = log_reduced(x)
    l2, u2 = log_reduced(Q(2))
    l, u = outward(l + shifts * l2, u + shifts * u2)
    l, u = SAVING * l, SAVING * u
    require(0 <= l <= u < Q(1, 100), "exponential domain")

    def polynomial(value):
        total = term = Q(1)
        for j in range(1, 25):
            term *= value / j
            total += term
        return total, term

    lower, _ = polynomial(l)
    upper, last = polynomial(u)
    upper += last * u / 25 / (1 - u / 26)
    return outward(rank * lower, rank * upper)


def raw_cost(histogram):
    lower = upper = Q(0)
    for rank, count in histogram.items():
        lo, hi = weight(rank)
        lower += count * (lo if count >= 0 else hi)
        upper += count * (hi if count >= 0 else lo)
    return outward(lower, upper)


def bill(histogram):
    lo, hi = raw_cost(histogram)
    # Inherited PR589 bad-residue surcharge. Other allowances stay fixed.
    unit_lo, unit_hi = weight(1)
    surcharge = Q(32 * M * sum(histogram.values()), 10**16 * W)
    return outward(lo / (M * W) + surcharge * unit_lo,
                    hi / (M * W) + surcharge * unit_hi)


def interval(pair):
    return [str(x) for x in outward(*pair, bits=100)]


def expect_rejection(name, fn):
    try:
        fn()
    except Reject:
        return name
    raise Reject("negative control accepted: " + name)


def generate(root=ROOT):
    inputs = read_inputs(root)
    word = json.loads(gzip.decompress(inputs[WORD]))
    record = json.loads(inputs[RECORD])
    selection = json.loads(inputs[SELECTION])["bit"]
    geometry = Geometry(word)
    original, paths = local_replay(word, geometry)
    retired, new_paths = local_replay(word, geometry, True)
    require([i for i, pair in enumerate(zip(paths, new_paths)) if pair[0] != pair[1]] == [470], "changed frame paths")
    local = Counter({int(k): v for k, v in original["profile"].items()})
    require(original["profile"] == record["word"]["local_histogram"], "baseline local profile")
    require(difference(Counter({int(k): v for k, v in retired["profile"].items()}), local) == LOCAL_DELTA, "retirement profile delta")
    events = schedule()
    win = windows(events)
    allocation = allocate(selection)
    remainder, occupied = placement_audit(allocation, win, set())
    baseline = full_profile(local, allocation, win, set())
    require(counts(baseline) == record["nine"]["profile"], "selected global profile")
    old = {stage: next(row for row in allocation if row[4:] == (stage, HELPER)) for stage in range(9)}
    old_remainders = {s: remainder[old[s][:2]] for s in old}
    require(len({old[s][:2] for s in old}) == 9, "distinct old children for additive return costs")

    stages, destinations, fallback_optional, fallback_mandatory = [], {}, {}, {}
    for stage in range(9):
        candidates = []
        for (child, cp), free_rank in sorted(remainder.items()):
            if stage not in win[child][2] or (child, cp) == old[stage][:2]:
                continue
            for offset in range(win[child][1] - 7 + 1):
                if not occupied[child, cp].intersection(range(offset, offset + 7)):
                    require(free_rank in (7, 42), "new destination class")
                    candidates.append((child, cp, offset, free_rank))
        destinations[stage] = candidates
        q_counts = Counter(row[3] for row in candidates)
        same = single_delta(old_remainders[stage])
        require(raw_cost(same)[0] > 0, "same-slot strict loss")
        optional, mandatory = Counter(), same
        if q_counts[7]:
            optional = mandatory = single_delta(old_remainders[stage], 7)
            require(raw_cost(optional)[1] < 0, "seven-slot strict gain")
        fallback_optional[stage], fallback_mandatory[stage] = optional, mandatory
        stages.append({"stage": stage, "old_slot": list(old[stage]), "old_remainder": old_remainders[stage],
                       "relocations_by_initial_idle_rank": counts(q_counts), "same_slot_raw_delta": interval(raw_cost(same)),
                       "rank7_raw_delta": interval(raw_cost(optional)) if q_counts[7] else None,
                       "rank42_raw_delta": interval(raw_cost(single_delta(old_remainders[stage], 42))) if q_counts[42] else None})
    require([s for s in range(9) if any(row[3] == 7 for row in destinations[s])] == [2, 4, 6], "rank-seven timing support")

    # Every joint assignment to originally empty 42-children partitions into
    # these subsets. This covers shared remainder costs, not only single moves.
    eligible = [s for s in range(9) if any(row[3] == 42 for row in destinations[s])]
    require(eligible == list(range(3, 9)), "rank-42 timing support")
    groups = []
    for size in range(1, len(eligible) + 1):
        for subset in itertools.combinations(eligible, size):
            delta = Counter({42: -1})
            if size < 6:
                delta[42 - 7 * size] += 1
            for stage in subset:
                delta.update(LOCAL_DELTA)
                delta[old_remainders[stage] + 8] += 1
                delta[old_remainders[stage]] -= 1
            optional_gap = difference(delta, add_hist(*(fallback_optional[s] for s in subset)))
            mandatory_gap = difference(delta, add_hist(*(fallback_mandatory[s] for s in subset)))
            require(raw_cost(optional_gap)[0] > 0, "joint rank42 group improves optional fallback")
            require(raw_cost(mandatory_gap)[0] > 0, "joint rank42 group improves mandatory fallback")
            require(sum(delta.values()) >= sum(sum(fallback_mandatory[s].values()) for s in subset), "surcharge group monotonicity")
            groups.append({"stages": list(subset), "profile_delta": counts(delta),
                           "optional_fallback_gap": interval(raw_cost(optional_gap)),
                           "mandatory_fallback_gap": interval(raw_cost(mandatory_gap))})
    require(len(groups) == 63, "joint subset coverage")

    converted = {2, 4, 6}
    replacements = {}
    for stage in sorted(converted):
        nominees = [row for row in destinations[stage] if row[3] == 7]
        child, cp, offset, _ = nominees[SEED % len(nominees)]
        replacements[stage] = (child, cp, offset, 7, stage, HELPER)
    candidate = [replacements.get(row[4], row) if row[5] == HELPER else row for row in allocation]
    optional_profile = full_profile(local, candidate, win, converted)
    expected_delta = Counter({r: T * n for r, n in add_hist(*fallback_optional.values()).items()})
    require(difference(optional_profile, baseline) == expected_delta, "literal selective recount")
    require(sum(optional_profile.values()) == sum(baseline.values()), "selective child-count surcharge unchanged")
    require(sum(r * n for r, n in optional_profile.items()) == sum(r * n for r, n in baseline.items()), "selective rank mass")
    require(bill(baseline)[1] < 1, "selected baseline bill")
    require(bill(optional_profile)[1] < bill(baseline)[0], "complete inherited selective bill")
    mandatory = [replacements.get(row[4], (*row[:3], 7, *row[4:])) if row[5] == HELPER else row for row in allocation]
    mandatory_profile = full_profile(local, mandatory, win, set(range(9)))
    require(difference(mandatory_profile, baseline) == Counter({r: T * n for r, n in add_hist(*fallback_mandatory.values()).items()}), "mandatory recount")
    require(bill(mandatory_profile)[0] > bill(baseline)[1], "uniform conversion is more expensive in this class")
    owners = owners_for_replicas(candidate, win)

    controls = []
    for i in range(3):
        controls.append(expect_rejection("omit retirement gate " + str(i), lambda i=i: local_replay(word, geometry, True, omit_early=i)))
    controls.append(expect_rejection("stale cleanup", lambda: local_replay(word, geometry, True, stale_cleanup=True)))
    def mutate_slot(fn):
        changed = [list(row) for row in candidate]
        fn(changed)
        placement_audit(changed, win, converted)
    at = next(i for i, row in enumerate(candidate) if row[4:] == (2, HELPER))
    controls.append(expect_rejection("premature rank7 host", lambda: mutate_slot(lambda rows: rows[at].__setitem__(4, 0))))
    controls.append(expect_rejection("width undercharge", lambda: mutate_slot(lambda rows: rows[at].__setitem__(3, 6))))
    controls.append(expect_rejection("slot overflow", lambda: mutate_slot(lambda rows: rows[at].__setitem__(2, 1))))
    controls.append(expect_rejection("duplicate helper", lambda: mutate_slot(lambda rows: rows.append(rows[at]))))
    controls.append(expect_rejection("missing helper", lambda: mutate_slot(lambda rows: rows.pop(at))))
    controls.append(expect_rejection("wrong family copy", lambda: mutate_slot(lambda rows: rows[at].__setitem__(1, 2 * V))))
    false_free = add_hist(expected_delta, Counter({7: 3 * T}))
    controls.append(expect_rejection("omit consumed idle rank", lambda: require(sum(r*n for r,n in false_free.items()) == 0, "missing consumption")))
    missing_return = add_hist(expected_delta, Counter({10: -2*T, 2: 2*T, 12: -T, 4: T}))
    controls.append(expect_rejection("omit returned old-host rank", lambda: require(sum(r*n for r,n in missing_return.items()) == 0, "missing return")))
    return {
        "status": "PASS_FIXED_SLOT_TIMING_AND_CONDITIONAL_COST", "assignment_seed": SEED,
        "base_commit": json.loads((HERE / "SOURCES.json").read_text())["base_commit"],
        "scope": "Fixed baseline other-helper placements; contiguous width-seven residuals in originally idle cells, or shrinking in place. New freed holes are not destinations. Conditional rank model, not physical/H4 admission.",
        "saving_tested": str(SAVING), "local_baseline": original, "credited_pr1256_local": retired,
        "schedule": events, "windows": {str(i): [p, rank, list(st)] for i, (p, rank, st) in win.items()},
        "stages": stages, "single_relocations": sum(len(x) for x in destinations.values()),
        "joint_rank42_subsets": groups, "selective_stages": sorted(converted),
        "replacement_slots": [list(replacements[s]) for s in sorted(replacements)],
        "owner_occurrences": len(owners), "owners_sha256": hashlib.sha256(canonical(owners).encode()).hexdigest(),
        "profiles": {"baseline": counts(baseline), "selective": counts(optional_profile), "mandatory": counts(mandatory_profile)},
        "selective_delta": counts(expected_delta), "mandatory_delta": counts(difference(mandatory_profile, baseline)),
        "raw_delta_per_replica": {"selective": interval(raw_cost(add_hist(*fallback_optional.values()))),
                                  "mandatory": interval(raw_cost(add_hist(*fallback_mandatory.values())))},
        "complete_bills": {"baseline": interval(bill(baseline)), "selective": interval(bill(optional_profile)), "mandatory": interval(bill(mandatory_profile))},
        "child_counts": {"baseline": sum(baseline.values()), "selective": sum(optional_profile.values()), "mandatory": sum(mandatory_profile.values())},
        "rank_mass": sum(r*n for r,n in baseline.items()), "rejection_controls": controls,
        "no_new_kappa": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path, help="create a new receipt; never overwrite")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = generate(args.root)
    if args.emit:
        with args.emit.open("x") as file:
            file.write(canonical(result))
    else:
        expected = json.loads((HERE / "CERTIFICATE.json").read_text())
        require(result == expected, "committed certificate mismatch")
    print("PASS_HELPER470_WINDOW_PLACEMENT stages=2,4,6 relocations=" + str(result["single_relocations"]) +
          " joint_groups=63 controls=" + str(len(result["rejection_controls"])) + " no_new_kappa")


if __name__ == "__main__":
    main()
