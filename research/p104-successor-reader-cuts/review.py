#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay three scoped exclusions from the unchanged P104 native words."""

from collections import Counter
import gzip
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import binary
import rational
from common import HERE, Q, authenticate, canonical, digest, enclose, histogram, load, margin
from common import matches_interval, scaled

TARGET = "0.003889928046155"
COMPARATOR = "0.00387992802506"
RAW = "0.003879928046155"
RAT_HEAD = "14c74c6a67108f675ac1196a5f2415ead0920e71"
BIT_TAIL_HEAD = "2d1fb9c878ae1e292cb918de40fa8e4f7fa7f75e"
RAT_WORD = "7660985e0b618cdbee13e4190a4c6d5f91fbdf01a8f7a5186fdde8b980c19b48"
BIT_WORD = "d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d"
RAT_LAYOUT = "f7de788c4a559282d35a9fce42f841a0e8de5a4015db871e718f9245569b0aa7"
BIT_LAYOUT = "a0ffffd99fb9b91f0013695877480766319ac51b926ed00dd5f7ec32f2d1e1a6"
RAT_CALLER = "156fdf3a4a129b39225fd6ca51011de27974d7f104e8b04907c17ed5344bc858"
BIT_CALLER = "757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b"


def raw_hash(relative):
    return digest((HERE / relative).read_bytes())


def unpacked_hash(relative):
    return digest(gzip.decompress((HERE / relative).read_bytes()))


def add(hist, delta):
    result = hist.copy()
    result.update(delta)
    assert all(n > 0 for n in result.values()), result
    return result


def difference(left, right):
    grades = left.keys() | right.keys()
    return {i: left[i] - right[i] for i in sorted(grades) if left[i] != right[i]}


def price_family(calls, paid, targets, paid_delta, repair_grade, crossing):
    after_paid = add(paid, paid_delta)
    baseline = margin(paid, targets, TARGET)
    nominal_credit = margin(after_paid, paid, TARGET)
    assert nominal_credit[0] > -baseline[0]
    extra = add(after_paid, {1: calls})
    extra_margin = margin(extra, targets, TARGET)
    debited = margin(after_paid, add(targets, {1: -calls}), TARGET)
    assert extra_margin[1] < 0 and extra_margin == debited
    restored = add(after_paid, {repair_grade: calls})
    restored_credit = margin(restored, paid, TARGET)
    r_lo = margin(paid, targets, crossing[0])
    r_hi = margin(paid, targets, crossing[1])
    assert r_lo[0] > 0 > r_hi[1], (r_lo, r_hi)
    assert margin(paid, targets, RAW if calls == 36 else crossing[1])[1] < 0
    assert margin(paid, targets, COMPARATOR)[0] > 0
    return {
        "calls": calls, "paid": paid, "targets": targets, "target": TARGET,
        "baseline_target_margin": enclose(baseline),
        "fixed_invoice_raw_bracket": crossing,
        "directed_margins_on_raw_bracket": [enclose(r_lo), enclose(r_hi)],
        "margin_at_7831_qualified_lower": enclose(margin(paid, targets, COMPARATOR)),
        "margin_at_unchanged_7831_binary_raw_upper": enclose(margin(paid, targets, RAW)),
        "counterfactual_paid_delta": paid_delta, "counterfactual_productive_delta": {},
        "counterfactual_signed_credit": enclose(nominal_credit),
        "counterfactual_margin_at_enrolled_target": enclose(margin(after_paid, targets, TARGET)),
        "counterfactual_margin_with_extra_grade_one_per_call": enclose(extra_margin),
        "counterfactual_margin_with_one_grade_one_target_lost_per_call": enclose(debited),
        "control_extra_grade": repair_grade, "signed_credit_with_control_extra": enclose(restored_credit),
        "earned_credit": 0,
    }


def run_rational(audit, summary):
    relative = "inputs/DOUBLE-CANDIDATE.json.gz"
    word, layout, app = load(relative), load("inputs/LAYOUT.json.gz"), load("inputs/DOUBLE-APPLICATION.json")
    assert unpacked_hash(relative) == RAT_WORD == digest(canonical(word))
    assert digest(canonical(layout)) == RAT_LAYOUT == app["layout_sha256"] == audit["layout"]
    assert RAT_WORD == app["word_sha256"] == audit["word"] == summary["rational_word"]
    assert app["caller"] == audit["signed"]["caller_sha256"] == RAT_CALLER
    assert app["binary_word"] == BIT_WORD
    for prior, later in [
        ("ordinary_elementary_record_upper", "ordinary_elementary_record_upper"),
        ("scalar_services", "ordinary_scalar_services"),
        ("scalar_step_rate", "ordinary_scalar_step_rate"),
        ("ordinary_map_slots", "ordinary_map_slots"),
        ("native_numeric_homes", "native_numeric_homes"),
    ]:
        assert app["application"]["ordinary"][prior] == audit["ordinary"][later], (prior, later)
    source = load("receipts/chart282.json")
    neighbor = load("receipts/rational-neighbor.json")
    assert source["source"]["head"] == neighbor["source"]["commit"] == RAT_HEAD
    tape = rational.Tape(word)
    chart282 = rational.check_chart282(tape, source["cut"])
    exterior = rational.neighbor_review(tape, neighbor["cut"])
    c = app["caller_census"]
    calls = c["calls"]
    assert calls == audit["signed"]["native_calls"] == 48
    native_paid, native_targets = rational.census(tape, layout)
    assert native_paid == histogram(app["native"]["paid_native_ranks"])
    assert native_targets == histogram(app["native"]["positive_helper_ranks"])
    paid = scaled(native_paid, calls) + histogram(c["fixed_caller_paid"])
    targets = scaled(native_targets, calls) + histogram(c["fixed_root_targets"])
    assert paid == histogram(app["application"]["invoice"]["paid"]) == histogram(audit["signed"]["paid"])
    assert targets == histogram(app["application"]["invoice"]["targets"]) == histogram(audit["signed"]["productive"])
    assert paid == histogram(source["signed_price"]["complete_published_baseline_paid"])
    assert targets == histogram(source["signed_price"]["complete_published_baseline_targets"])
    existing = Counter(tape.grade(*tape.moves[i]) for i in rational.REDIRECT)
    reroute = Counter(tape.grade(a, b) for a, b in ((3, 278), (3, 304), (278, 127)))
    paid_delta = difference(scaled(reroute, calls), scaled(existing, calls))
    assert paid_delta == {3: -48, 5: -48, 7: 48}
    assert paid_delta == histogram(source["signed_price"]["nominal_paid_delta"])
    crossing = summary["rational_raw_bracket"]
    assert crossing == audit["signed"]["candidate_raw_bracket"]
    fifth_grade = exterior["fifth_channel"]["grade"]
    assert fifth_grade == 3
    result = price_family(calls, paid, targets, paid_delta, fifth_grade, crossing)
    for predecessor in [source["signed_price"], neighbor["signed_price"]]:
        assert predecessor["native_calls"] == 48
        assert matches_interval(predecessor["nominal_credit"], list(map(Q, result["counterfactual_signed_credit"])))
        deficit = [-Q(x) for x in reversed(result["baseline_target_margin"])]
        assert matches_interval(predecessor["baseline_deficit"], deficit)
    assert matches_interval(neighbor["signed_price"]["signed_saving_of_restored_five_channel_control"],
                            list(map(Q, result["signed_credit_with_control_extra"])))
    return {"chart282": chart282, "exterior": exterior, "invoice": result, "native_paid": native_paid,
            "native_targets": native_targets, "archived_ordinary": app["application"]["ordinary"]}


def run_binary(receipt, summary):
    word, caller = load("inputs/WORD.json.gz"), load("inputs/EFREE-CALLER.json.gz")
    assert digest(canonical(word)) == summary["binary_word"] == receipt["word_sha256"] == BIT_WORD
    assert raw_hash("inputs/EFREE-CALLER.json.gz") == receipt["native"]["caller_sha256"] == BIT_CALLER
    assert digest(canonical({k: word[k] for k in ("frames", "start", "final")})) == BIT_LAYOUT
    assert raw_hash("inputs/WORD.json.gz") == receipt["native"]["candidate_gzip_sha256"]
    assert unpacked_hash("inputs/WORD.json.gz") == receipt["native"]["candidate_file_sha256"]
    charts = binary.Charts(word["frames"])
    forward = binary.tape(word, charts)
    adjoint = binary.tape(word, charts, adjoint=True)
    assert len(forward[1]) == len(adjoint[1]) == 2874 and forward[4] == adjoint[4]
    assert forward[4] == receipt["native"]["instruction_counts"]
    s11 = load("receipts/two-banks.json")
    s8 = load("inputs/CAUSAL-forward.json.gz")
    assert unpacked_hash("inputs/CAUSAL-forward.json.gz") == s11["source"]["predecessor_causal"]
    assert s11["source"]["word"] == BIT_WORD
    result = binary.cut(word, charts, forward, s11["cut"], s8)
    calls, paid, targets, fixed_paid, fixed_targets, counts = binary.census(word, forward[1], charts, caller)
    native = receipt["native"]
    assert calls == native["native_calls"] == 36
    assert paid == histogram(native["native_paid"]) and targets == histogram(native["native_targets"])
    paid, targets = scaled(paid, calls) + fixed_paid, scaled(targets, calls) + fixed_targets
    assert paid == histogram(native["paid"]) and targets == histogram(native["targets"])
    assert paid == histogram(s11["invoice"]["baseline"]["paid"])
    assert targets == histogram(s11["invoice"]["baseline"]["targets"])
    ordinary = binary.literal_ordinary(word, caller, counts, calls, paid, targets)
    assert ordinary == native["ordinary"] == load("inputs/PHYSICAL.json")["native"]["ordinary"]
    before = Counter(item["grade"] for item in result["held"])
    after = Counter({charts.grade(binary.FIRST, binary.BANK): 1, result["cases"][0]["route"][2]: 1})
    paid_delta = difference(scaled(after, calls), scaled(before, calls))
    assert paid_delta == {2: 36, 3: -36}
    assert paid_delta == histogram(s11["invoice"]["hypothetical_fixed_grade_recode"]["paid_delta"])
    assert summary["binary_raw_bracket"] == receipt["raw_crossing"]
    prices = price_family(calls, paid, targets, paid_delta, 1, receipt["raw_crossing"])
    for prior, fresh in [
        (s11["invoice"]["baseline"]["signed_margin"], prices["baseline_target_margin"]),
        (s11["invoice"]["directed_credit"], prices["counterfactual_signed_credit"]),
        (s11["invoice"]["hypothetical_one_extra_grade_one_per_call"]["signed_margin"],
         prices["counterfactual_margin_with_extra_grade_one_per_call"]),
    ]:
        assert prior == fresh, (prior, fresh)
    return {"cut": result, "invoice": prices, "retained_ordinary": ordinary,
            "native_coefficients_checked_each_orientation": word["public"] ** 2}


def main():
    assert sys.flags.optimize == 0, "Replay requires Python assertions"
    anchors = authenticate()
    source_lock = {item["file"]: item for item in load("SOURCE-LOCK.json")}
    upstream_binary = load("inputs/7786-SOURCE-LOCK.json")["sources"]["source"]
    local_caller = source_lock["inputs/EFREE-CALLER.json.gz"]
    public_caller = upstream_binary["files"][local_caller["source"]["path"]]
    assert local_caller["source"]["commit"] == upstream_binary["commit"]
    assert (local_caller["sha256"], local_caller["git_blob"]) == (public_caller["sha256"], public_caller["blob"])
    for public in load("inputs/7831-SOURCES.json"):
        name = public["path"].rsplit("/", 1)[-1]
        local = source_lock.get(f"inputs/{name}")
        if local:
            assert local["sha256"] == public["sha256"]
            assert (local["source"]["commit"], local["source"]["path"]) == (public["head"], public["path"])
    receipt = load("inputs/BIT.json")
    audit = load("inputs/AUDIT.json")
    summary = load("inputs/7831-RESULT.json")
    comparator = load("receipts/7831-independent.json")
    assert comparator["head"] == BIT_TAIL_HEAD
    assert summary["claim"] == comparator["qualified_conditional_lower"] == COMPARATOR
    assert (summary["power"], summary["paid_cutoff"], summary["productive_floor"], summary["log_power"]) == (
        416, 10, 16, 44)
    assert summary["binary_ordinary"] == receipt["ordinary_admitted"] == "0.003879928025145"
    assert summary["binary_raw_bracket"][1] == comparator["joint_raw_upper"] == RAW
    assert Q(TARGET) - Q(RAW) == Q("0.00001")
    assert summary["rational_word"] == RAT_WORD and summary["binary_word"] == BIT_WORD
    output = {
        "status": "PASS_SCOPED_EXCLUSIONS",
        "goal": "goal-c9b923e487624c27b9078b5182fc7dee",
        "step": "s13-independent-cuts",
        "binding": "progress.goal-c9b923e487624c27b9078b5182fc7dee.00000209",
        "authenticated_blobs": anchors,
        "comparison": {"pinned_head": BIT_TAIL_HEAD, "qualified_lower": COMPARATOR,
                       "enrolled_target": TARGET, "raw_upper": RAW,
                       "tensor_factors": 416, "paid_cutoff_base": 10, "productive_floor_base": 16,
                       "log_power": 44, "scope": "Retain the archived cutoff and verify its fixed input bills."},
        "rational": run_rational(audit, summary),
        "binary": run_binary(receipt, summary),
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
