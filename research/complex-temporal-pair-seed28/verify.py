#!/usr/bin/env python3
"""Compose a seed-selected pair of exact temporal gauges on one shared ADD."""
import copy
import gzip
import hashlib
import importlib.util
import itertools
import json
from fractions import Fraction as Q
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
LEGACY = PACKAGE / "vendor/pr1369"
REPORT = PACKAGE / "RESULT.json"
SOURCES = PACKAGE / "SOURCES.json"
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
PR1369 = "f28e1c460cd910886f9b06835abd6b1c96d2992f"
SEED = 28
ZERO_HELPERS = [272, 288, 348, 359, 381, 440, 444, 446, 447, 469,
                478, 479, 491, 503, 507, 514, 515, 519, 542]
EXPECTED_PAIR_POOL = [[348, 359], [479, 515]]
EXPECTED_PAIR = (348, 359)
EXPECTED_SHARED_ADD = 24336
SELECTED_KAPPA = "836330098538459/500000000000000000"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                       allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def import_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "load " + name)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def check_source_pins(sources):
    need(sources["schema_version"] == 1 and sources["base_commit"] == BASE,
         "base source manifest")
    for row in sources["base_files"]:
        raw = (ROOT / row["path"]).read_bytes()
        need(sha(raw) == row["sha256"], "base input SHA-256: " + row["path"])
        need(blob(raw) == row["git_blob"], "base input Git blob: " + row["path"])
    need(len(sources["vendored_files"]) == 16, "complete PR1369 source snapshot")
    for row in sources["vendored_files"]:
        raw = (PACKAGE / row["path"]).read_bytes()
        need(sha(raw) == row["sha256"], "vendored SHA-256: " + row["path"])
        need(blob(raw) == row["git_blob"], "vendored source Git blob: " + row["path"])
    pred = sources["predecessors"]
    need(pred["pr1369"]["head"] == PR1369, "PR1369 exact head")
    need(pred["pr1263"]["head"] ==
         "5fbaca13028846bddbb001e8e07addc2ab8e5816", "PR1263 exact head")
    need(pred["pr1259"]["head"] ==
         "61367611154266a982fe25e1a6243a8aad77227d", "PR1259 exact head")
    need(pred["pr1310"]["head"] ==
         "b9ca10f02fca37c8214d880c244ac14ead6bae7a", "PR1310 scope pin")
    need(pred["pr1376"]["head"] ==
         "49f112ac76e95415fcea8969de28f74c8928b2b1", "PR1376 overlap pin")
    need(pred["pr1380"]["head"] ==
         "c2bc6848cffb2e2203095d4c4bbc45b0848c22e7", "PR1380 overlap pin")


def load_predecessor(sources):
    legacy = import_file("seed28_pinned_pr1369", LEGACY / "verify.py")
    legacy.ROOT = ROOT
    captured = {}
    original_loader = legacy.module

    def capture_parent(name, path):
        module = original_loader(name, path)
        if name == "seed25_pinned_pr1263":
            original_compute = module.compute

            def compute_and_capture():
                result, static_words = original_compute()
                captured["parent_result"] = result
                captured["static_words"] = static_words
                captured["parent_module"] = module
                return result, static_words

            module.compute = compute_and_capture
        return module

    legacy.module = capture_parent
    result = legacy.compute()
    certificate_path = LEGACY / "CERTIFICATE.json"
    certificate = json.loads(certificate_path.read_bytes())
    need(canonical(result) == canonical(certificate),
         "recomputed PR1369 certificate equality")
    need(result["status"] == "PASS_ZERO_STATIC_TEMPORAL_CENSUS",
         "PR1369 single-coordinate census")
    need(result["base_commit"] == BASE and
         result["selected_kappa"] == SELECTED_KAPPA, "PR1369 selected source")
    need(captured.get("static_words") is not None, "recover pinned PR1263 word")
    return legacy, result, captured["parent_result"], captured["static_words"], captured["parent_module"]


def scale_word(events, helper_a, optimum_a, helper_b, optimum_b, independent):
    terms_a = independent.incident_adds(events, helper_a)
    terms_b = independent.incident_adds(events, helper_b)
    need(len(terms_a) == len(optimum_a["schedule"]), "L348 complete schedule")
    need(len(terms_b) == len(optimum_b["schedule"]), "L359 complete schedule")
    schedule_a = {term[0]: exponent for term, exponent
                  in zip(terms_a, optimum_a["schedule"])}
    schedule_b = {term[0]: exponent for term, exponent
                  in zip(terms_b, optimum_b["schedule"])}
    current = {helper_a: 0, helper_b: 0}
    inserted = []
    result = []
    for index, source_event in enumerate(events):
        event = copy.deepcopy(source_event)
        for helper, schedule in ((helper_a, schedule_a), (helper_b, schedule_b)):
            if index in schedule:
                exponent = schedule[index]
                change = exponent - current[helper]
                if change:
                    scale = independent.two_power(change)
                    output_index = len(result)
                    result.append(["scalar", ["scale", ["L", helper],
                                               scale.numerator, scale.denominator], event[2]])
                    inserted.append([helper, index, change, event[2], output_index])
                current[helper] = exponent
        if index == len(events) - 1:
            need(source_event == ["phase", "done"], "terminal restoration boundary")
            for helper in (helper_a, helper_b):
                if current[helper]:
                    scale = independent.two_power(-current[helper])
                    output_index = len(result)
                    result.append(["scalar", ["scale", ["L", helper],
                                               scale.numerator, scale.denominator], 1])
                    inserted.append([helper, index, -current[helper], 1, output_index])
        if event[0] == "scalar" and event[1][0] == "add":
            gate = event[1]
            sign_a = int(gate[1] == ["L", helper_a]) - int(gate[2] == ["L", helper_a])
            sign_b = int(gate[1] == ["L", helper_b]) - int(gate[2] == ["L", helper_b])
            coefficient = Q(gate[3], gate[4]) * independent.two_power(
                sign_a * current[helper_a] + sign_b * current[helper_b])
            gate[3], gate[4] = coefficient.numerator, coefficient.denominator
        result.append(event)
    need(len(result) == len(events) + len(inserted), "inserted scale census")
    return result, inserted, schedule_a, schedule_b, terms_a, terms_b


def replay_equal(lib, candidate, original, orientation):
    try:
        return lib.replay(candidate, orientation) == lib.replay(original, orientation)
    except Exception:
        return False


def invoice_view(row):
    fields = ("real_primitives", "complex_primitives", "charged_payload_bits", "prefix_bits")
    return {key: row[key] for key in fields if key in row}


def verify():
    sources = json.loads(SOURCES.read_bytes())
    check_source_pins(sources)
    selected = json.loads((ROOT / "certificates/selected-result.json").read_bytes())
    need(selected["kappa"] == SELECTED_KAPPA and 1094 in selected["source_prs"],
         "selected conditional result")
    assembly = json.loads((ROOT / "research/community-frontier1094-audit/ASSEMBLY.json").read_bytes())
    need(assembly.get("selected_kappa") == SELECTED_KAPPA or
         assembly.get("kappa") == SELECTED_KAPPA, "selected assembly kappa")

    legacy, legacy_result, parent_result, static_words, parent = load_predecessor(sources)
    gauges = json.loads((LEGACY / "vendor/pr1263/GAUGES.json").read_bytes())
    forward_static = set(map(int, gauges["forward"]))
    backward_static = set(map(int, gauges["backward"]))
    eligible = set(map(int, parent_result["eligible_helpers"]))
    zero = sorted(eligible - forward_static)
    need(zero == ZERO_HELPERS and forward_static == backward_static,
         "complete zero-static helper inventory")
    need(len(eligible) == 237 and len(forward_static) == 218,
         "PR1263 237/218 helper inventory")

    lib = parent.engine()
    word, original_words, _, _ = lib.load()
    orientation_results = {}
    pair_lists = []
    candidate_words = {}
    for orientation in ("forward", "backward"):
        events = static_words[orientation]
        helper_terms = {helper: legacy.independent.incident_adds(events, helper)
                        for helper in zero}
        helper_opts = {helper: legacy.independent.optimize(helper_terms[helper])
                       for helper in zero}
        predecessor_rows = {row["helper"]: row for row in
                            legacy_result["orientations"][orientation]["helpers"]}
        need(set(predecessor_rows) == set(zero), orientation + " all 19 predecessor rows")
        for helper in zero:
            opt = helper_opts[helper]
            row = predecessor_rows[helper]
            need(opt["incident_adds"] == row["incident_adds"] and
                 opt["domain"] == row["domain"] and
                 opt["edge_evaluations"] == row["edge_evaluations"] and
                 opt["delta_real"] == row["best_delta_real"] and
                 opt["constant_delta_real"] == row["best_constant_delta_real"],
                 orientation + " PR1369 exact DP row " + str(helper))

        schedules = {helper: {term[0]: exponent for term, exponent in
                              zip(helper_terms[helper], helper_opts[helper]["schedule"])}
                     for helper in zero}
        pair_pool = []
        for helper_a, helper_b in itertools.combinations(zero, 2):
            shared_active = sorted(index for index in
                                   set(schedules[helper_a]) & set(schedules[helper_b])
                                   if schedules[helper_a][index] != 0 and
                                   schedules[helper_b][index] != 0)
            if (shared_active and helper_opts[helper_a]["delta_real"] < 0 and
                    helper_opts[helper_b]["delta_real"] < 0):
                pair_pool.append((helper_a, helper_b, shared_active))
        pair_lists.append([[a, b, shared] for a, b, shared in pair_pool])
        need([[a, b] for a, b, _ in pair_pool] == EXPECTED_PAIR_POOL,
             orientation + " seed-selected interacting pair domain")
        pair_index = SEED % len(pair_pool)
        helper_a, helper_b, shared = pair_pool[pair_index]
        need((helper_a, helper_b) == EXPECTED_PAIR and shared == [EXPECTED_SHARED_ADD],
             orientation + " seed-selected pair and shared ADD")

        opt_a, opt_b = helper_opts[helper_a], helper_opts[helper_b]
        before = lib.invoice(events, "copy-init")
        need(before["paid_profile"] == parent_result["orientations"][orientation]["baseline"]["paid_profile"],
             orientation + " PR1263 paid profile")
        individual = {}
        for helper, opt, terms in ((helper_a, opt_a, helper_terms[helper_a]),
                                   (helper_b, opt_b, helper_terms[helper_b])):
            single, pulses = legacy.independent.transform(
                events, helper, [[term[0], exponent]
                                 for term, exponent in zip(terms, opt["schedule"])])
            single_invoice = lib.invoice(single, "copy-init")
            need(single_invoice["real_primitives"] - before["real_primitives"] == opt["delta_real"],
                 orientation + " single coordinate full invoice")
            need(single_invoice["paid_profile"] == before["paid_profile"],
                 orientation + " single coordinate profile")
            need(lib.replay(single, orientation) == lib.replay(events, orientation),
                 orientation + " single coordinate complete map")
            individual[str(helper)] = invoice_view(single_invoice)

        candidate, inserted, schedule_a, schedule_b, terms_a, terms_b = scale_word(
            events, helper_a, opt_a, helper_b, opt_b, legacy.independent)
        after = lib.invoice(candidate, "copy-init")
        need(len(inserted) == opt_a["transition_scale_macros"] +
             opt_b["transition_scale_macros"] == 54,
             orientation + " full entry/transition/exit scale census")
        need(len(candidate) == len(events) + 54,
             orientation + " complete scalar event count")
        need(after["paid_profile"] == before["paid_profile"],
             orientation + " complete paid-profile equality")
        need(after["charged_payload_bits"] == 192 and after["prefix_bits"] <= 192,
             orientation + " inherited precision charge")
        need(after["prefix_bits"] == (52 if orientation == "forward" else 68),
             orientation + " local prefix ceiling")
        need([e for e in candidate if e[0] != "scalar"] ==
             [e for e in events if e[0] != "scalar"],
             orientation + " all frame and paid events unchanged")
        endpoint = lib.replay(candidate, orientation)
        need(endpoint == lib.replay(events, orientation),
             orientation + " all 712 formal columns")

        term_a = next(term for term in terms_a if term[0] == shared[0])
        term_b = next(term for term in terms_b if term[0] == shared[0])
        need(term_a[1] == term_b[1], orientation + " shared original ADD coefficient")
        exponent_a, exponent_b = schedule_a[shared[0]], schedule_b[shared[0]]
        delta_a = legacy.independent.add_price(
            term_a[1] * legacy.independent.two_power(term_a[2] * exponent_a)) - legacy.independent.add_price(term_a[1])
        delta_b = legacy.independent.add_price(
            term_b[1] * legacy.independent.two_power(term_b[2] * exponent_b)) - legacy.independent.add_price(term_b[1])
        delta_joint = legacy.independent.add_price(
            term_a[1] * legacy.independent.two_power(term_a[2] * exponent_a +
                                                     term_b[2] * exponent_b)) - legacy.independent.add_price(term_a[1])
        cross = delta_joint - delta_a - delta_b
        joint_delta = after["real_primitives"] - before["real_primitives"]
        need((delta_a, delta_b, delta_joint, cross) == (-1, -4, -2, 3),
             orientation + " exact shared-ADD correction")
        need(joint_delta == opt_a["delta_real"] + opt_b["delta_real"] + cross == -400,
             orientation + " exact complete composition price")
        need(before["complex_primitives"] - after["complex_primitives"] == 800,
             orientation + " complete complex invoice saving")

        original_invoice = parent_result["orientations"][orientation]["baseline"]
        need(original_invoice["complex_primitives"] - after["complex_primitives"] == 13800,
             orientation + " total saving over PR1094 original")

        # Positive identity control: both all-zero schedules leave the word byte-identical.
        zero_a = {term[0]: 0 for term in terms_a}
        zero_b = {term[0]: 0 for term in terms_b}
        zero_candidate, zero_pulses, _, _, _, _ = scale_word(
            events, helper_a, {"schedule": tuple(zero_a[i] for i, _, _ in terms_a)},
            helper_b, {"schedule": tuple(zero_b[i] for i, _, _ in terms_b)},
            legacy.independent)
        need(zero_candidate == events and not zero_pulses,
             orientation + " all-zero schedule identity")

        # Negative control: remove a charged L348 entry/transition/restore scale.
        helper_a_scales = [row for row in inserted if row[0] == helper_a]
        need(bool(helper_a_scales), orientation + " L348 scale exists")
        missing_scale = copy.deepcopy(candidate)
        missing_scale.pop(helper_a_scales[0][4])
        need(not replay_equal(lib, missing_scale, events, orientation),
             orientation + " omitted L348 scale rejected")

        # Negative control: omit L359's contribution at the one shared ADD.
        wrong_shared = copy.deepcopy(candidate)
        found_shared = []
        for row in wrong_shared:
            if row[0] == "scalar" and row[1][0] == "add" and \
                    ["L", helper_a] in row[1][1:3] and ["L", helper_b] in row[1][1:3]:
                found_shared.append(row)
        need(len(found_shared) == 1, orientation + " unique shared ADD")
        shared_gate = found_shared[0][1]
        coefficient_without_b = term_a[1] * legacy.independent.two_power(term_a[2] * exponent_a)
        shared_gate[3], shared_gate[4] = coefficient_without_b.numerator, coefficient_without_b.denominator
        need(not replay_equal(lib, wrong_shared, events, orientation),
             orientation + " omitted shared coordinate rejected")

        orientation_results[orientation] = {
            "helpers": [helper_a, helper_b],
            "helper_schedules": {
                str(helper_a): {"domain": opt_a["domain"], "schedule": list(opt_a["schedule"]),
                                   "delta_real": opt_a["delta_real"],
                                   "transition_scale_macros": opt_a["transition_scale_macros"]},
                str(helper_b): {"domain": opt_b["domain"], "schedule": list(opt_b["schedule"]),
                                   "delta_real": opt_b["delta_real"],
                                   "transition_scale_macros": opt_b["transition_scale_macros"]}},
            "single_candidate_invoices": individual,
            "shared_add": {"index": shared[0], "coefficient":
                           [term_a[1].numerator, term_a[1].denominator],
                           "signs": [term_a[2], term_b[2]],
                           "exponents": [exponent_a, exponent_b],
                           "separate_real_add_deltas": [delta_a, delta_b],
                           "combined_real_add_delta": delta_joint,
                           "cross_correction_real": cross},
            "static_invoice": invoice_view(before),
            "candidate_invoice": invoice_view(after),
            "joint_real_delta": joint_delta,
            "complex_saving_vs_PR1263": before["complex_primitives"] - after["complex_primitives"],
            "complex_saving_vs_PR1094": original_invoice["complex_primitives"] - after["complex_primitives"],
            "scale_macros": len(inserted),
            "input_event_count": len(events),
            "candidate_event_count": len(candidate),
            "non_scalar_events_unchanged": True,
            "all_712_columns_equal": True,
            "candidate_sha256": sha(canonical(candidate)),
            "endpoint_sha256": sha(canonical(endpoint)),
            "controls": {"zero_schedule_identity": "passed",
                         "missing_L348_transition_scale": "rejected",
                         "missing_L359_shared_coefficient": "rejected"}}
        candidate_words[orientation] = candidate

    need(pair_lists[0] == pair_lists[1], "same seed-selected pair pool both ways")
    selected_certificate = json.loads((ROOT / "certificates/selected-result.json").read_bytes())
    return {
        "status": "PASS_COMPLEX_TEMPORAL_PAIR",
        "assignment_seed": SEED,
        "base_commit": BASE,
        "selected_kappa_unchanged": selected_certificate["kappa"],
        "predecessor_pr1369_head": PR1369,
        "zero_static_helper_count": len(zero),
        "pair_search_domain": "all 171 unordered pairs of the 19 zero-static helpers; retain improving solo DPs active together on a shared ADD",
        "qualifying_pairs_both_orientations": pair_lists[0],
        "seed_index": SEED % len(pair_lists[0]),
        "selected_pair": list(EXPECTED_PAIR),
        "orientations": orientation_results,
        "no_joint_optimality_claim": True,
        "no_new_kappa": True,
        "scope": "Feasible composition of two exact single-coordinate minima on a pinned shared-ADD pair; no two-coordinate optimum, supplier admission, or paid-profile change."
    }


def main():
    write = len(sys.argv) == 2 and sys.argv[1] == "--write"
    need(len(sys.argv) == 1 or write, "usage: verify.py [--write]")
    result = verify()
    if write:
        need(not REPORT.exists(), "refusing to overwrite RESULT.json")
        REPORT.write_text(json.dumps(result, indent=2) + "\n")
        print("WROTE_RESULT " + str(REPORT.relative_to(ROOT)))
        return
    expected = json.loads(REPORT.read_text())
    need(canonical(result) == canonical(expected), "stored RESULT.json differs from exact replay")
    print("PASS_COMPLEX_TEMPORAL_PAIR seed=28 helpers=348,359 shared_add=24336 cross=+3real saving=800complex/orientation controls=3 no_new_kappa")


if __name__ == "__main__":
    main()
