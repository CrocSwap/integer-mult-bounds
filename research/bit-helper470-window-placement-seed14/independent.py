#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate fixed-slot state enumeration and pinned Mercator cost cross-check.

Does not import verify.py or use its 63-subset dominance reduction. The source
window/expansion routines are comparison oracles, not new independent code.
Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance.
"""
import ast
import hashlib
import importlib.util
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "research/e8-bit-p111-tuned/"
CHAIN = PREFIX + "vendor/pr510/e8-r480-nine-stage/vendor/"


def check(ok, message):
    if not ok:
        raise ValueError(message)


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def shifted(profile, terms):
    values = list(profile)
    for rank, count in terms:
        if rank:
            values[rank] += count
    return tuple(values)


def enumerate_profiles(old_remainder, seven_stages, large_stages, mandatory=False):
    """Enumerate canonical histogram/bin-load states for all joint choices.

    Only load multisets matter for the nine identical empty 42-children. All
    eligible stages have the same access to all nine, so this quotient loses
    neither a cost profile nor a feasibility distinction. Six relevant calls
    fit into one bin and at most six bins are needed.
    """
    states = {(tuple([0] * 43), ())}
    state_counts = []
    for stage in range(9):
        r = old_remainder[stage]
        result = set()
        common = [(1, 1), (5, 1), (7, -1), (r, -1)]
        for profile, loads in states:
            if not mandatory:
                result.add((profile, loads))
            result.add((shifted(profile, common + [(r + 1, 1)]), loads))
            if stage in seven_stages:
                result.add((shifted(profile, common + [(r + 8, 1), (7, -1)]), loads))
            if stage in large_stages:
                hosted = shifted(profile, common + [(r + 8, 1)])
                result.add((hosted, tuple(sorted((*loads, 1)))))
                for i, load in enumerate(loads):
                    if load < 6:
                        changed = list(loads)
                        changed[i] += 1
                        result.add((hosted, tuple(sorted(changed))))
        states = result
        state_counts.append(len(states))
    profiles = set()
    for profile, loads in states:
        check(len(loads) <= 9, "large-window inventory")
        final = shifted(profile, [(rank, amount) for load in loads
                                  for rank, amount in ((42, -1), (42 - 7 * load, 1))])
        check(sum(i * n for i, n in enumerate(final)) == 0, "complete rank mass")
        profiles.add(final)
    return profiles, state_counts


def main():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for row in pins["files"]:
        if row["usage"] == "input":
            raw = (ROOT / row["path"]).read_bytes()
            check(hashlib.sha256(raw).hexdigest() == row["sha256"], "source drift")
            check(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == row["git_blob"], "source blob")
    receipt = json.loads((HERE / "CERTIFICATE.json").read_text())
    host = module(ROOT / CHAIN / "idle-axis-hosting/hosting_core.py", "original_hosting")
    tree = ast.parse((ROOT / CHAIN / "e8-r715-eleven-stage-whole/code/global_k.py").read_text())
    recipe = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == "recipe")
    namespace = {}
    exec(compile(ast.Module(body=[recipe], type_ignores=[]), "pinned recipe", "exec"), namespace)
    non_idle = [e for e in receipt["schedule"] if e["kind"] != "idle"]
    check(non_idle == namespace["recipe"](4), "pinned recipe identity")
    # Independently audit every level transition and complete terminal level.
    levels, children = [-1] * 4, 0
    for event in receipt["schedule"]:
        if event["kind"] == "local":
            p, s = event["pair"], event["stage"]
            check(levels[p] == s - 1, "local entrance level")
            levels[p] = s
        elif event["kind"] == "bridge":
            check(levels[event["dst"]] == levels[event["src"]], "bridge levels")
        elif event["kind"] == "idle":
            p = event["pair"]
            check(event["idx"] == children and event["source_level"] == levels[p], "idle source")
            check(event["rank"] == 7 * (event["target_level"] - levels[p]), "idle paid rank")
            levels[p] = event["target_level"]
            children += 1
    check(levels == [8] * 4 and children == 10, "full schedule completion")
    win = host.windows(receipt["schedule"])
    actual_windows = {str(i): [p, rank, sorted(st)] for i, (p, rank, st) in win.items()}
    check(actual_windows == receipt["windows"], "forward/backward window algorithms")
    ys, zs, _ = host.load_selection(ROOT / PREFIX / "data/selection9-p111.json", "bit")
    slots, remainder = host.expand({i: x for i, x in win.items() if x[1] and x[2]}, ys, zs,
                                  {s: [(h, 8) for h in range(439)] for s in range(9)}, 222)
    old = {s: next(row for row in slots if row[4:] == (s, 248)) for s in range(9)}
    r = {s: remainder[old[s][:2]] for s in old}
    for row in receipt["stages"]:
        check(list(old[row["stage"]]) == row["old_slot"] and r[row["stage"]] == row["old_remainder"], "source expansion")
    # Existing occupied cells are contiguous prefixes in the frozen expansion.
    # Count legal start offsets from free lengths, independently of the primary
    # cell-intersection scan. Only whole free 7- and 42-children survive.
    seven, large, census = set(), set(), []
    for stage in range(9):
        counts = Counter()
        for (child, cp), free in remainder.items():
            if stage in win[child][2] and free >= 7 and (child, cp) != old[stage][:2]:
                counts[free] += free - 6
        if counts[7]:
            seven.add(stage)
        if counts[42]:
            large.add(stage)
        check({str(k): v for k, v in counts.items()} == receipt["stages"][stage]["relocations_by_initial_idle_rank"], "full destination census")
        census.append(sum(counts.values()))
    check(sum(census) == receipt["single_relocations"], "single placement coverage")
    check(seven == {2, 4, 6} and large == set(range(3, 9)), "temporal support")

    # Apply the actual three declared replacements to the original expander's
    # output. Recount cells and all replicated owner indices with integer masks.
    replace = {row[4]: tuple(row) for row in receipt["replacement_slots"]}
    check(set(replace) == {2, 4, 6} and len(receipt["replacement_slots"]) == 3, "replacement inventory")
    check(all(row[3:] == (7, s, 248) for s, row in replace.items()), "replacement identity")
    candidate = [replace.get(row[4], row) if row[5] == 248 else row for row in slots]
    masks, seen = {}, set()
    for child, cp, offset, width, stage, helper in candidate:
        check(stage in win[child][2] and 0 <= cp < 222, "witness owner/window")
        check(width == (7 if stage in replace and helper == 248 else 8), "witness width")
        check(0 <= offset and offset + width <= win[child][1], "witness extent")
        mask = ((1 << width) - 1) << offset
        check(not (masks.get((child, cp), 0) & mask), "witness overlap")
        masks[child, cp] = masks.get((child, cp), 0) | mask
        check((stage, helper) not in seen, "witness duplicate")
        seen.add((stage, helper))
    check(len(seen) == 3951, "witness completeness")
    original_record = json.loads((ROOT / PREFIX / "tune/EXPECTED.json").read_text())
    recount = Counter({int(k): 288 * v for k, v in original_record["word"]["local_histogram"].items()})
    recount.update({1: 96, 5: 96, 7: -96})
    for child, (_, rank, _) in win.items():
        for cp in range(222):
            remainder_rank = rank - masks.get((child, cp), 0).bit_count()
            if remainder_rank:
                recount[remainder_rank] += 32
    check({str(k): v for k, v in recount.items()} == receipt["profiles"]["selective"], "witness complete histogram")
    owners = [(s, replica, h, replica * 888 + (2 * win[i][0] + cp // 111) * 111 + cp % 111, i, off, width)
              for replica in range(32) for i, cp, off, width, s, h in candidate]
    owner_digest = hashlib.sha256((json.dumps(owners, indent=2, sort_keys=True) + "\n").encode()).hexdigest()
    check(len(owners) == receipt["owner_occurrences"] and owner_digest == receipt["owners_sha256"], "replicated witness binding")

    engine = module(ROOT / "research/native-complex-moment552/engines/moment.py", "pinned_mercator")
    alternate = module(ROOT / "research/native-complex-moment552/engines/base_two_moment.py", "pinned_base_two")
    saving = F(receipt["saving_tested"])
    check(saving == F(1733427039589844234749, 10**24), "tested exponent")
    scale = 1 << 224
    weights = [(0, 0)]
    for rank in range(1, 43):
        lo, hi = engine.logarithm(F(64, rank))
        low, high = engine.exponential(saving * lo, saving * hi)
        lower, upper = rank * low * scale, rank * high * scale
        check(lower.denominator == upper.denominator == 1, "dyadic oracle")
        weights.append((int(lower), int(upper)))

    report = {}
    for required, key in [(False, "selective"), (True, "mandatory")]:
        profiles, state_counts = enumerate_profiles(r, seven, large, mandatory=required)
        certificate_delta = receipt["selective_delta" if not required else "mandatory_delta"]
        target = tuple(int(certificate_delta.get(str(i), 0)) // 32 for i in range(43))
        check(all(int(n) % 32 == 0 for n in certificate_delta.values()), "replica scaling")
        check(target in profiles, "declared minimizer absent")
        min_gap = None
        for profile in profiles:
            if profile == target:
                continue
            delta = [a - b for a, b in zip(profile, target)]
            lower_raw = sum(n * weights[i][0 if n >= 0 else 1] for i, n in enumerate(delta))
            # Multiply the complete per-replica bill difference by the positive
            # factor m W 10^16. The child-count surcharge remains included.
            children = sum(delta)
            bad_lower = children * weights[1][0 if children >= 0 else 1]
            lower_complete = 10**16 * lower_raw + 32 * 64 * 64 * bad_lower
            check(lower_complete > 0, "enumerated alternative defeats declared minimum")
            min_gap = lower_complete if min_gap is None else min(min_gap, lower_complete)
        report[key] = {"states_after_each_stage": state_counts, "distinct_complete_profiles": len(profiles),
                       "strict_alternatives": len(profiles) - 1, "minimum_scaled_gap_numerator": str(min_gap)}

    # Check absolute full bills by both retained engines. The second engine
    # handles the raw bill; append the same declared bad-residue surcharge.
    for name, histogram in receipt["profiles"].items():
        h = {int(k): v for k, v in histogram.items()}
        low, high = engine.moment(h, 64, 28416, saving, bad=True)
        cl, ch = map(F, receipt["complete_bills"][name])
        check(cl <= low <= high <= ch, "Mercator complete bill containment")
        low2, high2 = alternate.moment(64, 28416, sorted(h.items()), saving)
        loglow, loghigh = alternate.log_bounds(F(64))
        elo = alternate.exp_bounds(saving * loglow)[0]
        ehi = alternate.exp_bounds(saving * loghigh)[1]
        surcharge = F(32 * 64 * sum(h.values()), 10**16 * 28416)
        low2, high2 = low2 + surcharge * elo, high2 + surcharge * ehi
        check(max(cl, low2) <= min(ch, high2), "second-engine bill overlap")
        if name == "selective":
            check(high2 < 1, "second-engine favorable selective bill")
        elif name == "mandatory":
            check(low2 > 1, "second-engine unfavorable mandatory bill")
    print(json.dumps(report, sort_keys=True))
    print("PASS_INDEPENDENT_HELPER470_PLACEMENT complete_joint_profiles_checked no_new_kappa")


if __name__ == "__main__":
    main()
