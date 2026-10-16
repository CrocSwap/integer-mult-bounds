#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact replay of the tagged two-register child-boundary recipe."""
import copy
import gzip
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
WORD_PATH = ROOT / "research/r480-owner-optimum/inputs/local/FULL-WORD.json.gz"
SELECTED_WORD_PIN = ROOT / "research/gauge44-slots/construction/slots/SLOT-PINS-k8.json"
WORD_SHA = "c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8"
EXPECTED_PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def space(vectors):
    """Enumerate the exact F2 span; dimension is log2 of its cardinality."""
    values = {0}
    for vector in vectors:
        values |= {x ^ vector for x in tuple(values)}
    return frozenset(values)


def dimension(vectors):
    size = len(space(vectors))
    require(size > 0 and size & (size - 1) == 0, "span cardinality is not a power of two")
    return size.bit_length() - 1


def as_int_frames(items):
    return [int(x) for x in items]


def regs(operation):
    return [int(operation[1])] + ([int(operation[2])] if operation[0] == "add" else [])


def get_role(r, v):
    return "input" if r < v else "target" if r < 2 * v else "helper"


def member_record(r, before, after, v):
    return {"register": r, "role": get_role(r, v), "from": list(before), "to": list(after)}


def compute_expected(word):
    v, helper_count = int(word["report"]["v"]), int(word["report"]["R"])
    register_count = 2 * v + helper_count
    current = [space([]) for _ in range(register_count)]
    for i, port in enumerate(word["ports"]):
        current[i] = space([int(port)])
    for register, frame in word.get("start_extra", {}).items():
        current[int(register)] = space(as_int_frames(frame))

    profile = Counter()
    pairs = []

    def run_gate(stage, section, index, operation, target, cleanup_index=None):
        target_space = space(target)
        touched = regs(operation)
        prior = [current[r] for r in touched]
        for old in prior:
            require(old <= target_space, f"nonmonotone frame at {section}:{index}")
        deltas = [len(target_space).bit_length() - 1 - (len(old).bit_length() - 1) for old in prior]
        for delta in deltas:
            if delta:
                profile[delta] += 1
        if len(touched) == 2 and deltas == [1, 1]:
            pairs.append({
                "stage": stage, "section": section, "index": index,
                "cleanup_index": cleanup_index, "registers": touched,
                "operation": list(operation[:-1]), "target_space": target_space,
                "prior_spaces": prior,
            })
        for r in touched:
            current[r] = target_space

    for section in ("A", "B"):
        for index, operation in enumerate(word[section]):
            run_gate("gate", section, index, operation, as_int_frames(operation[-1]))

    for schedule_index, (cleanup_index, frame) in enumerate(word.get("early_cleanup", [])):
        operation = word["cleanup"][cleanup_index]
        run_gate("early-cleanup", "cleanup", schedule_index, operation, as_int_frames(frame), cleanup_index)

    full = space([1 << i for i in range(9)])
    finals = {int(r): space(as_int_frames(frame)) for r, frame in word.get("helper_final", {}).items()}
    terminal = []
    for r in range(register_count):
        if v <= r < 2 * v:
            target = space([x for x in range(1, 512) if ((x & int(word["ports"][r - v])).bit_count() % 2) == 0])
        else:
            target = finals.get(r, full)
        old = current[r]
        require(old <= target, f"nonmonotone terminal frame at register {r}")
        delta = len(target).bit_length() - 1 - (len(old).bit_length() - 1)
        if delta:
            profile[delta] += 1
        if delta == 1:
            terminal.append((r, old, target))
        current[r] = target

    profile.update(int(x) for x in word["report"]["centre_ranks"])
    require(dict(sorted(profile.items())) == EXPECTED_PROFILE,
            "source word profile did not replay: " + repr(dict(sorted(profile.items()))))
    require(len(terminal) == 326 and len(terminal) % 2 == 0, "terminal rank-one set changed")
    for i in range(0, len(terminal), 2):
        left, right = terminal[i], terminal[i + 1]
        pairs.append({
            "stage": "terminal", "section": "final", "index": None, "cleanup_index": None,
            "registers": [left[0], right[0]], "operation": None, "target_space": None,
            "prior_spaces": [left[1], right[1]], "final_spaces": [left[2], right[2]],
        })
    return profile, pairs


def key(pair):
    return pair["stage"], pair["section"], pair["index"], tuple(pair["registers"])


def validate(recipe, raw, word):
    require(hashlib.sha256(raw).hexdigest() == WORD_SHA, "pinned word content hash")
    selected_pin = json.loads(SELECTED_WORD_PIN.read_text())
    require(selected_pin["word_sha256"] == WORD_SHA, "selected slot output does not pin the same word")
    require(recipe["source"]["decompressed_sha256"] == WORD_SHA, "recipe word pin")
    require(recipe["model"] == {"m": 73, "stages": 9, "families": 896, "centre": 64, "idle_rank_cap": 51},
            "model pin")
    profile, wanted = compute_expected(word)
    wanted_keys = [key(p) for p in wanted]
    got = recipe["pairs"]
    require([key(p) for p in got] == wanted_keys, "pair list is not the deterministic complete pairing")

    for pair, expected in zip(got, wanted):
        require(pair["rank"] == 2 and len(pair["quotient_vectors"]) == 2, "joint rank must be two")
        require(pair["registers"] == expected["registers"], "member register order")
        for vector, register, before, after in zip(
                pair["quotient_vectors"], expected["registers"], expected["prior_spaces"],
                expected.get("final_spaces", [expected.get("target_space")] * 2)):
            require(dimension(after) - dimension(before) == 1, "each member must be codimension one")
            vector = int(vector)
            require(vector in after and vector not in before, "quotient vector must add the one missing direction")

        if pair["stage"] == "terminal":
            matrix = [[1, 0], [0, 1]]
            require(pair["coefficient"] is None and pair["cleanup_index"] is None, "terminal metadata")
        else:
            target = expected["target_space"]
            require(pair["cleanup_index"] == expected["cleanup_index"], "cleanup index")
            coeff = Q(int(expected["operation"][3]), int(expected["operation"][4]))
            require(pair["coefficient"] == str(coeff), "gate coefficient")
            matrix = [[1, coeff], [0, 1]]
            require(all(before <= target for before in expected["prior_spaces"]),
                    "gate shear input lanes must fit the common target")
        inverse = [[matrix[0][0], -matrix[0][1]], [0, 1]]
        product = [
            [sum(matrix[i][k] * inverse[k][j] for k in range(2)) for j in range(2)]
            for i in range(2)
        ]
        require(product == [[1, 0], [0, 1]], "joint map inverse")

    counts = recipe["counts"]
    require(counts == {
        "gate_pairs": 574,
        "early_cleanup_pairs": 16,
        "terminal_pairs": 163,
        "total_rank_two_children": 753,
        "a_gate_count": len(word["A"]),
        "b_gate_count": len(word["B"]),
        "source_gate_count": len(word["A"]) + len(word["B"]),
        "scheduled_early_cleanup_entries": len(word.get("early_cleanup", [])),
        "terminal_rank_one_transitions": 326,
    }, "pair-count receipt")
    before = {int(r): int(n) for r, n in recipe["profile_before"].items()}
    after = {int(r): int(n) for r, n in recipe["profile_after_ideal_joint_interfaces"].items()}
    require(before == EXPECTED_PROFILE == dict(profile), "before profile")
    expected_after = Counter(before)
    expected_after[1] -= 2 * counts["total_rank_two_children"]
    expected_after[2] += counts["total_rank_two_children"]
    require(dict(sorted(after.items())) == dict(sorted(expected_after.items())), "virtual profile change")
    require(sum(r * n for r, n in before.items()) == sum(r * n for r, n in after.items()) == 5586,
            "rank mass changed")
    require(recipe["rank_mass_before_and_after"] == 5586, "rank-mass receipt")
    return after


def screen(after):
    sys.path.insert(0, str(ROOT / "research/complex-local-word-ceiling"))
    import ceiling
    base = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
    grid = Q(1, 10**12)
    base_lo, base_hi = ceiling.ceiling(base, 73, 896, 9, 64, grid=grid)
    cand_lo, cand_hi = ceiling.ceiling(after, 73, 896, 9, 64, grid=grid)
    gain_floor = cand_lo / base_hi - 1
    target_moment = ceiling.relax(after, 73, 896, 9, 64, Q(1, 99))
    kappa_cap = cand_hi / (1 + cand_hi)
    five_percent_point = base_hi * Q(105, 100)
    moment_at_five_percent = ceiling.relax(after, 73, 896, 9, 64, five_percent_point)
    W = Q(896, 9)
    rank_one = ceiling.child_cost(1, 73, five_percent_point)
    idle_unit = ceiling.child_cost(51, 73, five_percent_point)
    extra_rank_one_lo = (rank_one[0] - idle_unit[1] / 51) / W
    extra_rank_one_hi = (rank_one[1] - idle_unit[0] / 51) / W
    headroom_lo = 1 - moment_at_five_percent[1]
    headroom_hi = 1 - moment_at_five_percent[0]
    safe_extra_rank_ones = int(headroom_lo // extra_rank_one_hi)
    possible_extra_rank_ones = int(headroom_hi // extra_rank_one_lo)
    require(gain_floor > Q(5, 100), "ideal ceiling improvement did not clear 5 percent")
    require(target_moment[0] > 1, "target 1/99 unexpectedly passes the relaxation")
    require(safe_extra_rank_ones == possible_extra_rank_ones == 11,
            "overhead headroom at the 5 percent threshold changed")
    return {
        "grid": str(grid),
        "baseline_a_ceiling": [str(base_lo), str(base_hi)],
        "joint_profile_a_ceiling": [str(cand_lo), str(cand_hi)],
        "guaranteed_relative_ceiling_gain": str(gain_floor),
        "guaranteed_relative_ceiling_gain_decimal": f"{float(gain_floor) * 100:.9f}%",
        "joint_profile_kappa_cap_from_complex_side_only": str(kappa_cap),
        "relaxation_at_a_equals_1_over_99": [str(x) for x in target_moment],
        "a_at_guaranteed_5_percent_gain": str(five_percent_point),
        "relaxation_at_5_percent_threshold": [str(x) for x in moment_at_five_percent],
        "extra_rank_one_cost_per_call_vs_rank_51_idle_mass": [str(extra_rank_one_lo), str(extra_rank_one_hi)],
        "headroom_per_call_at_5_percent_threshold": [str(headroom_lo), str(headroom_hi)],
        "maximum_extra_rank_one_children_per_call_while_retaining_5_percent": safe_extra_rank_ones,
    }


def main():
    raw = gzip.decompress(WORD_PATH.read_bytes())
    word = json.loads(raw)
    recipe = json.loads((PKG / "PAIR-RECIPE.json").read_text())
    after = validate(recipe, raw, word)
    costs = screen(after)

    # Semantic negative controls: missing, duplicated, and corrupted interface evidence must fail.
    controls = []
    for name, mutate in (
        ("missing_pair", lambda r: r["pairs"].pop()),
        ("duplicate_pair", lambda r: r["pairs"].__setitem__(-1, copy.deepcopy(r["pairs"][0]))),
        ("changed_gate_map", lambda r: r["pairs"][0].__setitem__("coefficient", 999)),
        ("bad_quotient_vector", lambda r: r["pairs"][0]["quotient_vectors"].__setitem__(0, 0)),
    ):
        bad = copy.deepcopy(recipe)
        mutate(bad)
        try:
            validate(bad, raw, word)
        except (AssertionError, ValueError, KeyError, IndexError):
            controls.append(name)
        else:
            raise AssertionError("negative control accepted: " + name)

    from collections import defaultdict
    role_pairs = defaultdict(Counter)
    for pair in recipe["pairs"]:
        role_pairs[pair["stage"]]["/".join(get_role(r, word["report"]["v"]) for r in pair["registers"])] += 1
    report = {
        "status": "PASS_JOINT_CHILD_INTERFACE_CANDIDATE",
        "scope": "Exact tagged direct-sum frame transitions on one selected local word; supplier admission, physical hosting, and global assembly are unproved.",
        "source_word_sha256": WORD_SHA,
        "pair_counts": recipe["counts"],
        "pair_role_counts": {stage: dict(sorted(counts.items())) for stage, counts in sorted(role_pairs.items())},
        "profile_before": recipe["profile_before"],
        "profile_after_ideal_joint_interfaces": recipe["profile_after_ideal_joint_interfaces"],
        "rank_mass": 5586,
        "cost_screen": costs,
        "positive_evidence": [
            "all 753 tagged rank-two quotient interfaces have exact dimension two",
            "each gate-pair map is an invertible integer shear and both frame lanes remain in the shared target",
            "terminal pairs are exact direct sums of two independent codimension-one boundaries",
            "the native word and frames are unchanged; only the recursive-call grouping changes",
        ],
        "negative_controls_rejected": controls,
        "unpriced_obligations": recipe["charge_ledger"]["unpriced_obligation"],
        "no_new_kappa_claimed": True,
    }
    encoded = json.dumps(report, sort_keys=True, indent=2) + "\n"
    result_path = PKG / "RESULT.json"
    if "--write" in sys.argv[1:]:
        result_path.write_text(encoded)
    else:
        require(result_path.exists(), "RESULT.json missing; run verify.py --write after reviewing this report")
        require(json.loads(result_path.read_text()) == report, "RESULT.json differs from exact replay")
    print("PASS_JOINT_CHILD_INTERFACE_CANDIDATE pairs=753 gain=" + costs["guaranteed_relative_ceiling_gain_decimal"])
    print("PASS_NEGATIVE_CONTROLS " + ",".join(controls))
    print("LIMIT no supplier admission, physical cost, global assembly, or new kappa")


if __name__ == "__main__":
    main()
