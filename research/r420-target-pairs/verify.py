#!/usr/bin/env python3
"""Exact finite R420 target-row compensation construction. Apache-2.0.

Sagar Thakrar, with substantial OpenAI Codex assistance. The target-basis
identity follows Dugongue's PR476; the pinned word/checker are eumemic's PR543.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import random
from collections import Counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/e8-bit-r420"
PINS = {
    "data/bitE8mut-r420.json.gz":
        "e597e3885c0a8daa262afa5985ee2930443329126aece76d33159d81882bdcc2",
    "code/xcheck.py":
        "5737d18a7826fd51e131035f2d7bebba2e2868af91dd7672a5f11208b036d424",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_source():
    for name, expected in PINS.items():
        data = (SOURCE / name).read_bytes()
        if name.endswith(".gz"):
            data = gzip.decompress(data)
        need(hashlib.sha256(data).hexdigest() == expected, "source pin: " + name)
    return json.loads(gzip.decompress((SOURCE / "data/bitE8mut-r420.json.gz").read_bytes()))


def rows(word):
    need(len(word["D"]) == word["v"], "source must have one D row per target")
    result = {d: set(srcs) for _, d, srcs in word["D"]}
    need(len(result) == word["v"], "duplicate source D destination")
    return result


def greedy_baseline(word, seed):
    """One bounded greedy matching; exhaustive pair scoring is not optimal matching."""
    matrix = rows(word)
    candidates = []
    for a in sorted(matrix):
        for b in sorted(matrix):
            if a != b:
                gain = len(matrix[a]) - len(matrix[a] ^ matrix[b]) - 2
                if gain > 0:
                    candidates.append((gain, a, b))
    random.Random(seed).shuffle(candidates)
    candidates.sort(key=lambda item: -item[0])
    used, pairs = set(), []
    for _, a, b in candidates:
        if a not in used and b not in used:
            pairs.append([a, b])
            used.update((a, b))
    return pairs, len(candidates)


def check_matching_dual(word, pairs, dual):
    """Vertex prices upper-bound every disjoint matching; equality proves this class's optimum."""
    matrix = rows(word)
    prices = dual["twice_vertex_prices"]
    need(dual["first_target"] == word["v"] and len(prices) == word["v"], "dual target domain")
    need(all(type(p) is int and p >= 0 for p in prices), "dual prices must be nonnegative integers")
    for a in sorted(matrix):
        for b in sorted(matrix):
            if a < b:
                weight = max(0, max(len(matrix[a]), len(matrix[b])) - len(matrix[a] ^ matrix[b]) - 2)
                need(prices[a - word["v"]] + prices[b - word["v"]] >= 2 * weight,
                     "dual edge inequality failed")
    need(len({v for pair in pairs for v in pair}) == 2 * len(pairs), "dual witness pairs overlap")
    saving = sum(len(matrix[a]) - len(matrix[a] ^ matrix[b]) - 2 for a, b in pairs)
    need(sum(prices) == 2 * saving, "dual objective differs from matching saving")
    return {"unordered_pairs_covered": word["v"] * (word["v"] - 1) // 2,
            "twice_upper_bound": sum(prices), "optimal_saving_in_disjoint_pair_class": saving}


def construct(word, pairs):
    matrix = rows(word)
    zero = word["frames"].index([])
    changed = copy.deepcopy(word)
    gates, used = [], set()
    for a, b in pairs:
        need(a in matrix and b in matrix and a != b, "invalid target pair")
        need(a not in used and b not in used, "target pairs overlap")
        used.update((a, b))
        gates.append([zero, a, [b]])
        gates.append([zero, b, sorted(matrix[b])])
        difference = sorted(matrix[a] ^ matrix[b])
        if difference:
            gates.append([zero, a, difference])
        gates.append([zero, a, [b]])
    gates.extend(copy.deepcopy(g) for g in word["D"] if g[1] not in used)
    changed["D"] = gates
    return changed


def check_prefix(original, changed):
    """Independent set-valued D replay, including all arbitrary target inputs."""
    need(original.keys() == changed.keys(), "word fields changed")
    need(all(original[k] == changed[k] for k in original if k != "D"),
         "field outside D changed")
    v, n = original["v"], 2 * original["v"] + original["R"]
    zero = original["frames"].index([])
    values = [{r} for r in range(n)]
    for frame, dest, sources in changed["D"]:
        need(frame == zero, "D must stay at frame zero")
        need(v <= dest < 2 * v, "D must write only targets")
        need(sources and all(v <= s < n and s != dest for s in sources)
             and len(sources) == len(set(sources)), "invalid D operands")
        for src in sources:
            values[dest].symmetric_difference_update(values[src])
    matrix = rows(original)
    for r in range(n):
        expected = {r} ^ matrix[r] if r in matrix else {r}
        need(values[r] == expected, "D endpoint differs at register " + str(r))
    return n


def frame_paths(word):
    paths = [[frame] for frame in word["start"]]
    for section in ("D", "A", "B", "C"):
        for frame, dest, sources in word[section]:
            for reg in [dest] + sources:
                if paths[reg][-1] != frame:
                    paths[reg].append(frame)
    for reg, frame in enumerate(word["final"]):
        if paths[reg][-1] != frame:
            paths[reg].append(frame)
    return paths


def additions(word):
    return sum(len(g[2]) for sec in ("D", "A", "B", "C") for g in word[sec]) + sum(
        len(row) for row in word["scatter"])


def positive_prefix(word):
    """Lower to scalar ADD/COPY events; price the signed lift without cancellation."""
    n, v = 2 * word["v"] + word["R"], word["v"]
    events = []
    for section in ("D", "A", "scatter", "B", "C"):
        if section == "scatter":
            for k, register in enumerate(word["ret"]):
                events.append((2, register, 0))
                events.extend((1, v + t, n) for t, row in enumerate(word["scatter"]) if k in row)
                events.append((3, register, 0))
        else:
            events.extend((1, dest, src) for _, dest, sources in word[section] for src in sources)
    peaks = []
    for reverse in (False, True):
        values, peak = [1] * (n + 1), 1
        for op, dest, src in reversed(events) if reverse else events:
            if reverse and op in (2, 3):
                op = 5 - op
            if op == 1:
                values[dest] += values[src]
                peak = max(peak, values[dest])
            elif op == 2:
                values[n] = values[dest]
            else:
                values[n] = 0
        peaks.append(peak)
    forward, backward = peaks
    payload = 64 * forward ** 3 * backward ** 2
    need(payload < 2 ** 104, "local native payload exceeds inherited cap")
    return {"forward": forward, "reverse": backward,
            "local_payload_upper": payload, "local_payload_bits": payload.bit_length()}


def controls(original, changed, pairs):
    cases = []
    mutant = copy.deepcopy(changed)
    del mutant["D"][0]
    cases.append(("missing initial target mix", mutant, "D endpoint differs"))
    mutant = copy.deepcopy(changed)
    del mutant["D"][3]
    cases.append(("missing final target unmix", mutant, "D endpoint differs"))
    mutant = copy.deepcopy(changed)
    mutant["D"][2][2].pop()
    cases.append(("missing helper contribution", mutant, "D endpoint differs"))
    mutant = copy.deepcopy(changed)
    mutant["D"][0][0] = original["final"][0]
    cases.append(("illegal nonzero D frame", mutant, "D must stay"))
    mutant = copy.deepcopy(changed)
    mutant["D"][0][1] = 2 * original["v"]
    cases.append(("target feeds helper", mutant, "D must write only targets"))
    mutant = copy.deepcopy(changed)
    forbidden = [original["frames"].index([]), 2 * original["v"], [pairs[0][0]]]
    mutant["D"] += [forbidden, copy.deepcopy(forbidden)]
    cases.append(("neutral target feedback into helper", mutant, "D must write only targets"))
    mutant = copy.deepcopy(changed)
    mutant["D"][0][2] = [0]
    cases.append(("source access at frame zero", mutant, "invalid D operands"))
    mutant = copy.deepcopy(changed)
    mutant["A"][0][2].pop()
    cases.append(("mutation outside claimed scope", mutant, "field outside D"))
    for name, mutant, reason in cases:
        need(mutant != changed, "negative control did not mutate: " + name)
        try:
            check_prefix(original, mutant)
        except ValueError as error:
            need(reason in str(error), name + " failed for the wrong reason")
        else:
            raise ValueError("accepted negative control: " + name)
    try:
        construct(original, pairs + pairs[:1])
    except ValueError as error:
        need("overlap" in str(error), "wrong overlapping-pair rejection")
    else:
        raise ValueError("accepted overlapping pairs")
    # An F2-neutral pair is legal but must still pay for both additions.
    neutral = copy.deepcopy(changed)
    gate = [original["frames"].index([]), pairs[0][0], [pairs[0][1]]]
    neutral["D"] += [gate, copy.deepcopy(gate)]
    check_prefix(original, neutral)
    need(additions(neutral) == additions(changed) + 2, "neutral pair underpriced")
    return {"negative": len(cases) + 1, "positive_paid_neutral_pair": 1}


def verify():
    original = load_source()
    recipe = json.loads((HERE / "recipe.json").read_text())
    greedy, positive = greedy_baseline(original, recipe["seed"])
    pairs = recipe["pairs"]
    dual = json.loads((HERE / "matching-dual.json").read_text())
    matching_proof = check_matching_dual(original, pairs, dual)
    corrupted_dual = copy.deepcopy(dual)
    corrupted_dual["twice_vertex_prices"][0] -= 1
    try:
        check_matching_dual(original, pairs, corrupted_dual)
    except ValueError as error:
        need("dual edge inequality" in str(error), "wrong underpriced-dual rejection")
    else:
        raise ValueError("accepted underpriced dual")
    changed = construct(original, pairs)
    columns = check_prefix(original, changed)
    spec = importlib.util.spec_from_file_location("r420_source_xcheck", SOURCE / "code/xcheck.py")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    audited, labels, _, hypotheses, conclusion, _ = checker.check(original)
    need(all(hypotheses.values()) and all(conclusion.values()), "source interface failed")
    # Geometry is unchanged. Reuse only the exact frame catalogue and its audit.
    audited.w = changed
    audited.full()
    new_hypotheses, new_conclusion, _ = audited.interface()
    failed = [key for key, value in {**new_hypotheses, **new_conclusion}.items() if not value]
    need(failed == ["H2_D_frame0_targets_from_helpers", "K_equals_D"],
         "unexpected inherited interface result: " + str(failed))
    before_paths, after_paths = frame_paths(original), frame_paths(changed)
    need(before_paths == after_paths, "physical frame paths changed")
    histogram = Counter()
    for path in after_paths:
        for a, b in zip(path, path[1:]):
            histogram[audited.fdim[b] - audited.fdim[a]] += 1
    copy_frames = list(changed["start"])
    for section in ("D", "A"):
        for frame, dest, sources in changed[section]:
            for reg in [dest] + sources:
                copy_frames[reg] = frame
    for reg in changed["ret"]:
        need(audited.fdim[copy_frames[reg]] == original["h"], "copy is not at full frame")
        histogram[audited.fdim[copy_frames[reg]]] += 1
    rank_mass = sum(rank * count for rank, count in histogram.items())
    controls_result = controls(original, changed, pairs)
    result = {
        "status": "finite circuit improvement; semantic D interface required; no new kappa",
        "seed": recipe["seed"], "oriented_pairs_scored": original["v"] * (original["v"] - 1),
        "positive_orientations": positive, "selected_disjoint_pairs": len(pairs),
        "greedy_saved_additions": additions(original) - additions(construct(original, greedy)),
        "matching_optimality": matching_proof, "underpriced_dual_rejected": True,
        "D_additions_before": sum(len(g[2]) for g in original["D"]),
        "D_additions_after": sum(len(g[2]) for g in changed["D"]),
        "total_additions_before": additions(original), "total_additions_after": additions(changed),
        "saved_additions": additions(original) - additions(changed),
        "symbolic_columns": columns, "helpers": original["R"], "copies": len(original["ret"]),
        "frame_catalogue": labels, "paid_histogram": dict(sorted(histogram.items())),
        "rank_mass": rank_mass, "unchanged_frame_paths": len(after_paths),
        "inherited_checks_rejected": failed, "controls": controls_result,
        "positive_prefix_before": positive_prefix(original),
        "positive_prefix_after": positive_prefix(changed),
        "changed_word_canonical_sha256": hashlib.sha256(json.dumps(
            changed, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "source_pins": PINS,
    }
    return original, changed, result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="store_true", help="print the exact replay receipt")
    parser.add_argument("--native", action="store_true", help="also run original C++ cohort checkers")
    args = parser.parse_args()
    original, changed, receipt = verify()
    expected = HERE / "certificate.json"
    need(expected.is_file(), "missing frozen certificate")
    need(json.loads(json.dumps(receipt)) == json.loads(expected.read_text()), "certificate mismatch")
    if args.native:
        spec = importlib.util.spec_from_file_location("r420_target_pairs_native", HERE / "native.py")
        native = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(native)
        native_receipt = native.verify_native(original, changed)
        print(json.dumps(native_receipt, indent=2, sort_keys=True))
    if args.report:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    print("PASS_R420_TARGET_PAIRS D=%d->%d ADDs=%d->%d saved=%d columns=%d rank_mass=%d" % (
        receipt["D_additions_before"], receipt["D_additions_after"],
        receipt["total_additions_before"], receipt["total_additions_after"],
        receipt["saved_additions"], receipt["symbolic_columns"], receipt["rank_mass"]))
