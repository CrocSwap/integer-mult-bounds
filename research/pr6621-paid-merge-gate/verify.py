#!/usr/bin/env python3
"""Coverage gap for the PR #6621 paid-job merge gate.

The checker uses the vendored receipts and native words. It does not import
the candidate pricing engine or replay the word. Integer comparisons decide
the histogram identities. A mutated receipt and a mutated word are failure
controls.
"""
from collections import Counter
from fractions import Fraction
from gzip import GzipFile
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
STATUS = "PASS_PR6621_MERGE_GATE_DOES_NOT_SEE_THE_MERGE"

MERGE_PAID = {1: -54, 3: -18, 4: 18, 5: -18, 6: 18}
MERGE_TARGETS = {8: 18, 9: -18}
PER_CALL_PAID = {1: -3, 3: -1, 4: 1, 5: -1, 6: 1}
PER_CALL_TARGETS = {8: 1, 9: -1}
RETIREMENT_PAID = {16: -104, 40: 312, 56: -208}
RETIREMENT_TARGETS = {16: -104, 40: 104, 41: 208, 57: -208}
CALLS = 18


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_json(name):
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def load_word(name):
    with GzipFile(EVIDENCE / name) as raw:
        return json.loads(raw.read().decode("utf-8"))


def histogram(cost, key):
    return {int(rank): int(count) for rank, count in cost[key].items()}


def difference(after, before):
    ranks = set(after) | set(before)
    return {rank: after.get(rank, 0) - before.get(rank, 0)
            for rank in ranks if after.get(rank, 0) != before.get(rank, 0)}


def scale(counts, factor):
    return {rank: factor * count for rank, count in counts.items()}


def ordinary_raw(caller_events):
    """Closed form of the ordinary-work expression in PR #6621 pricing.py."""
    return 18 * 10**7 + 17 * 1664 + 32 * 35 * 104 * caller_events + 35 * 104 * (26 + 1000)


def partial_sums(ranks):
    ordered = sorted(ranks, reverse=True)
    total = 0
    sums = []
    for rank in ordered:
        total += rank
        sums.append(total)
    return sums


def assert_merge_shape(paid_delta, target_delta):
    need(paid_delta == MERGE_PAID, "paid merge delta")
    need(target_delta == MERGE_TARGETS, "target merge delta")
    need(scale(PER_CALL_PAID, CALLS) == MERGE_PAID, "eighteen calls times the per-call paid edit")
    need(scale(PER_CALL_TARGETS, CALLS) == MERGE_TARGETS, "eighteen calls times the per-call target edit")
    need(sum(PER_CALL_PAID.values()) == -3, "three fewer paid jobs per call")
    need(sum(rank * count for rank, count in PER_CALL_PAID.items()) == -1, "paid rank mass falls by one")
    need(sum(rank * count for rank, count in PER_CALL_TARGETS.items()) == -1, "target rank mass falls by one")


def assert_majorization():
    """The gaining multiset is strictly majorized by the paying multiset.

    Both have sum 19. For H(r) = r^t with 0 < t < 1, strict concavity and
    Karamata's inequality then give a positive signed gain. The analytic step
    is the written argument in README.md; this function checks every integer
    comparison that argument uses.
    """
    gaining = (1, 1, 1, 3, 5, 8)
    paying = (4, 6, 9)
    need(sum(gaining) == sum(paying) == 19, "equal rank mass")
    left, right = partial_sums(gaining), partial_sums(paying)
    need(len(left) == len(right) + 3, "three extra summands on the gaining side")
    # Compare the largest k parts. The paying side has three parts; pad the
    # remaining prefix with the already-exhausted sum.
    padded = right + [right[-1]] * (len(left) - len(right))
    need(all(a < b for a, b in zip(left[:-1], padded[:-1])), "strict partial sums")
    need(left[-1] == padded[-1] == 19, "the full sums meet")
    # Subadditivity bracket: 1+1+1+3 = 6, and the integral bracket is 5 against 9.
    need(1 + 1 + 1 + 3 == 6, "merge preserves rank mass")
    need(5 - 4 == 1 and 9 - 8 == 1, "edit C compares adjacent unit intervals")


def assert_gate(candidate_vs_archive, archive_vs_published_predecessor):
    need(candidate_vs_archive == {"paid": RETIREMENT_PAID, "targets": RETIREMENT_TARGETS},
         "top-level gate sees only the retirement delta")
    need(archive_vs_published_predecessor == {"paid": MERGE_PAID, "targets": MERGE_TARGETS},
         "archived predecessor already contains the merge")


def word_census(before, after):
    need(before["schema"] == after["schema"] == "p104-accumulated-block-composition/2", "word schema")
    stable = [key for key in before if key not in ("program", "final")]
    need(all(before[key] == after[key] for key in stable), "public word fields other than program and final")
    changed = [index for index, (left, right) in enumerate(zip(before["final"], after["final"]))
               if left != right]
    need(changed == [435], "only final[435] changes")
    need((before["final"][435], after["final"][435]) == (127, 246), "helper 435 moves from frame 127 to 246")
    before_ops = Counter(event[0] for event in before["program"])
    after_ops = Counter(event[0] for event in after["program"])
    delta = {name: after_ops[name] - before_ops[name]
             for name in set(before_ops) | set(after_ops)
             if after_ops[name] != before_ops[name]}
    need(len(before["program"]) == 18493 and len(after["program"]) == 18561, "program lengths")
    need(delta == {"ADD": 69, "MOVE": -3, "INIT": 1, "CLEAR": 1}, "opcode census")
    need(before["owned_fields"] == after["owned_fields"] == 29, "owned-field count")


def expect_failure(action, label):
    try:
        action()
    except ValueError:
        return
    raise ValueError("failure control accepted a bad " + label)


def main():
    public_old = load_json("pr6551-result.json")
    public_new = load_json("pr6621-result.json")
    archive_old = load_json("archive6551-retirement-result.json")
    archive_new = load_json("archive6621-retirement-result.json")
    need(public_old["status"] == "PASS_REBALANCED_RETIREMENT_KAPPA_00329492", "PR #6551 status")
    need(public_new["status"] == "PASS_PAID_JOB_MERGES_KAPPA_00329700", "PR #6621 status")
    need(archive_old["status"] == archive_new["status"] == "PASS_GAUSSIAN_ROOT_RETIREMENT_KAPPA_00329394",
         "both archived predecessor receipts keep the old status")
    old_cost = public_old["candidate"]["complete_cost"]
    new_cost = public_new["candidate"]["complete_cost"]
    old_archive = archive_old["candidate"]["complete_cost"]
    new_archive = archive_new["candidate"]["complete_cost"]

    paid_delta = difference(histogram(new_cost, "paid"), histogram(old_cost, "paid"))
    target_delta = difference(histogram(new_cost, "targets"), histogram(old_cost, "targets"))
    assert_merge_shape(paid_delta, target_delta)
    need(old_cost["paid_calls"] == 67096 and new_cost["paid_calls"] == 67042, "paid-call totals")
    need(old_cost["productive_fields"] == new_cost["productive_fields"] == 13756, "productive fields")
    need(old_cost["rank_mass_surplus"] == new_cost["rank_mass_surplus"] == 760, "rank-mass surplus")
    need(old_cost["kappa"] == "82373/25000000" and new_cost["kappa"] == "3297/1000000", "published kappa strings")
    need(public_old["candidate"]["changes"] == public_new["candidate"]["changes"],
         "machine-readable changes blocks are identical")
    need(public_new["candidate"]["changes"]["gain_formula"] == "208*(H41-H40-H57+H56)",
         "changes block still names the retirement formula")
    need(public_new["candidate"]["changes"]["paid"] == {str(k): v for k, v in RETIREMENT_PAID.items()},
         "changes paid map is the retirement delta")
    retirement_mass = sum(rank * count for rank, count in RETIREMENT_TARGETS.items())
    need(retirement_mass == -832 == public_new["candidate"]["changes"]["rank_mass_change"],
         "retirement target rank-mass change")

    need(old_cost["nonrecursive"]["raw_scalar_upper"] == new_cost["nonrecursive"]["raw_scalar_upper"]
         == ordinary_raw(611) == 254932208, "public ordinary-work bound uses 611 caller events")
    need(old_archive["nonrecursive"]["raw_scalar_upper"] == new_archive["nonrecursive"]["raw_scalar_upper"]
         == ordinary_raw(609) == 254699248, "archived ordinary-work bound uses 609 caller events")
    need(new_cost["nonrecursive"]["local_scalar"] - old_cost["nonrecursive"]["local_scalar"] == 648, "local scalar")
    need(new_cost["nonrecursive"]["local_routes"] - old_cost["nonrecursive"]["local_routes"] == 1000, "local routes")
    need(1000 == 1000 * (sum(PER_CALL_PAID.values()) + 4),
         "route delta matches one extra lifetime and three fewer per-call paid jobs")

    archive_paid = difference(histogram(new_archive, "paid"), histogram(old_archive, "paid"))
    archive_targets = difference(histogram(new_archive, "targets"), histogram(old_archive, "targets"))
    gate_paid = difference(histogram(new_cost, "paid"), histogram(new_archive, "paid"))
    gate_targets = difference(histogram(new_cost, "targets"), histogram(new_archive, "targets"))
    published_gate_paid = difference(histogram(old_cost, "paid"), histogram(old_archive, "paid"))
    published_gate_targets = difference(histogram(old_cost, "targets"), histogram(old_archive, "targets"))
    assert_gate({"paid": gate_paid, "targets": gate_targets},
                {"paid": archive_paid, "targets": archive_targets})
    need(published_gate_paid == RETIREMENT_PAID and published_gate_targets == RETIREMENT_TARGETS,
         "PR #6551 really does differ from its own archived predecessor by the retirement delta")
    need(old_archive["kappa"] == new_archive["kappa"] == "164697/50000000",
         "archived kappa string is unchanged")
    old_root = [Fraction(item) for item in old_archive["raw_root_interval"]]
    new_root = [Fraction(item) for item in new_archive["raw_root_interval"]]
    need(old_root[0] <= old_root[1] < new_root[0] <= new_root[1],
         "rewritten predecessor crossing moved strictly upward")
    need(new_root[0] > Fraction(old_archive["kappa"]),
         "rewritten predecessor crossing is above its own stated kappa")

    word_census(load_word("word-pr6529.json.gz"), load_word("word-pr6621.json.gz"))
    assert_majorization()

    expect_failure(lambda: assert_merge_shape({**MERGE_PAID, 1: -53}, MERGE_TARGETS), "paid delta")
    expect_failure(lambda: assert_majorization_mutated(), "majorization")
    expect_failure(
        lambda: assert_gate({"paid": MERGE_PAID, "targets": MERGE_TARGETS},
                            {"paid": MERGE_PAID, "targets": MERGE_TARGETS}),
        "compare gate")
    bad_word = load_word("word-pr6621.json.gz")
    bad_word["final"][435] = 127
    expect_failure(lambda: word_census(load_word("word-pr6529.json.gz"), bad_word), "final frame")
    print(STATUS)


def assert_majorization_mutated():
    """Equal multisets have equal partial sums, so the strict inequality fails."""
    gaining = (4, 6, 9)
    paying = (9, 6, 4)
    left, right = partial_sums(gaining), partial_sums(paying)
    width = max(len(left), len(right))
    left += [left[-1]] * (width - len(left))
    right += [right[-1]] * (width - len(right))
    need(sum(gaining) == sum(paying), "mutated sums")
    need(all(a < b for a, b in zip(left[:-1], right[:-1])), "mutated partial sums")


if __name__ == "__main__":
    main()
