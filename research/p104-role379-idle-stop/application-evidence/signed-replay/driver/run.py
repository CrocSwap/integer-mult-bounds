#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run the source-pinned #7113 application on a frozen strict role-379 candidate."""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from engines import ASSUMPTIONS, CALLER, PRIOR, SOURCE_PINS, capture_price, prepare, verify_sources
from guard import authenticate_inputs, binding_controls, canonical, digest, launch, read, require, utc, write


def word_profile(word):
    main = set(word["live"]) | {r + 112 for r in word["live"]}
    main |= set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    helper_roles = set(range(word["public"])) - main
    dim = [len(frame) for frame in word["frames"]]
    moves = [(e[2], e[3]) for e in word["program"] if e[0] == "MOVE"]
    helpers = [(word["initial"][r], word["final"][r]) for r in helper_roles]
    paid_counts = Counter(abs(dim[a] - dim[b]) for a, b in moves)
    target_counts = Counter(dim[b] - dim[a] for a, b in helpers)
    require(min(paid_counts) > 0 and min(target_counts) > 0, "Positive native and target ranks")
    return paid_counts, target_counts, set(moves), set(helpers), helper_roles


def signed_invoice(caller, profile):
    paid, targets, _, _, _ = profile
    p, t = Counter(), Counter()
    for e in caller["events"]:
        if e[0] == "J":
            p.update(paid)
            t.update(targets)
        elif e[1] == "QUERY":
            p[1] += len(caller["types"][e[0]]["ports"])
        elif e[1] in ("IDLE_ONE", "IDLE_ODD"):
            p[8 * len(e[3]) + (e[1] == "IDLE_ODD")] += len(caller["types"][e[0]]["ports"])
    for d in caller["types"].values():
        for row in d["diagonal"]:
            t[row[0] % 2 + 8 * sum(row[2:])] += len(d["ports"])
    return {"paid": {str(r): n for r, n in p.items()}, "targets": {str(r): n for r, n in t.items()}}


def verify_native_and_clear(spec, inputs, w, source, life):
    native = json.loads(inputs["native_result"])
    mark = json.loads(inputs["native_receipt"])
    checked = binding_controls(spec, mark, native, digest(inputs["native_result"]))
    require(native["pr"] == spec["source_pr"] and native["head"] == spec["source_head"]
            and native["source"]["canonical_sha256"] == spec["source_canonical_sha256"]
            and native["candidate"]["raw_sha256"] == spec["candidate_raw_sha256"]
            and native["candidate"]["gzip_sha256"] == digest(inputs["word"]),
            "Physical result on the actual source and candidate")
    route = native["route_columns"]
    require(route["all_forward"] == route["all_adjoint"] == 512 and route["wrong_phase"] == "rejected"
            and len(native["finite_replays"]) == 2, "Exact three-route composition and two finite physical oracles")
    clear = json.loads(inputs["clear_result"])
    require(clear["status"] == "PASS_SILENT_PUBLIC_MOVE_SUBSTITUTION"
            and clear["source"]["head"] == spec["source_head"]
            and clear["source"]["gzip_sha256"] == digest(inputs["source_word"])
            and clear["candidate"]["word_sha256"] == spec["candidate_raw_sha256"]
            and clear["candidate"]["gzip_sha256"] == digest(inputs["word"])
            and clear["ordered_clears"] == life and clear["owned_peak"] == 50
            and clear["candidate"]["events"] == len(w["program"])
            and clear["source"]["events"] == len(source["program"]), "Exact CLEAR result on both words")
    return checked


def verify_grid(spec, grid, w, life):
    scale = grid["integer_grid"]["odd_scale_lcm"]
    require(grid["canonical_word_sha256"] == spec["candidate_canonical_sha256"]
            and grid["caller_sha256"] == CALLER, "Fresh candidate and caller grid")
    require(grid["integer_grid"]["dyadic_height"] == grid["rational_grid"]["fractional_bits"]
            and scale == grid["rational_grid"]["odd_scale"]
            and Fraction(grid["integer_grid"]["maximum_scaled_mass"])
            == Fraction(grid["rational_grid"]["scaled_maximum_mass"]),
            "Two independent native grid results agree")
    require(grid["native_envelope"]["census"]["lifetimes"] == life
            and grid["native_envelope"]["census"]["events"] == len(w["program"])
            and grid["context_c"] <= 4096, "Fresh precision inventory and cap")
    require(scale > 0 and scale % 2 == 1 and grid["integer_grid"]["numerator_bits"] <= 24,
            "Supported odd grid and scalar width")


def catalogue_check(work, folder, maps, deadline, word_sha):
    slices = []
    catalogue = sorted(maps)
    size = len(catalogue)
    cat_sha = digest(json.dumps(catalogue, separators=(",", ":")).encode())
    for start in range(0, size, 1000):
        stop = min(start + 1000, size)
        label = f"SHORT-CATALOGUE-{start}-{stop}"
        launch(work, label, folder / "short_native_catalogue.py", deadline,
               ("--start", start, "--stop", stop), log_dir=folder)
        blob = (folder / (label + ".log")).read_bytes()
        record = json.loads(blob[blob.index(b"\n{") + 1:])
        require((record["word_sha256"], record["catalogue_digest"], record["catalogue_size"],
                 record["slice_start"], record["slice_stop"], record["checked_maps"]) ==
                (word_sha, cat_sha, size, start, stop, stop - start)
                and record["phase_control_rejected"], "Exact fresh catalogue slice and wrong-phase control")
        slices.append(record)
    require(sum(r["main_boundary_pairs"] for r in slices) == 104, "Complete physical boundary catalogue")
    return slices


def run(spec, inputs, work, deadline, pins):
    tick = time.monotonic()
    pr = spec["source_pr"]
    head, raw_sha, zip_sha, life, entrance = SOURCE_PINS[pr]
    require(spec["source_head"] == head and digest(inputs["source_word"]) == zip_sha,
            "Exact source head and gzip")
    w_raw, b_raw = (gzip.decompress(inputs[k]) for k in ("word", "source_word"))
    w, source = map(json.loads, (w_raw, b_raw))
    candidate = digest(canonical(w))
    word_sha = digest(inputs["word"])
    require(digest(w_raw) == spec["candidate_raw_sha256"] and candidate == spec["candidate_canonical_sha256"],
            "Exact candidate raw and canonical bytes")
    require(digest(b_raw) == raw_sha and digest(canonical(source)) == spec["source_canonical_sha256"],
            "Exact source raw and canonical bytes")
    require(w.keys() == source.keys() and all(w[k] == source[k] for k in w if k != "program"),
            "Matched literal native headers")
    require((w["public"], w["owned_fields"], len(w["live"])) == (1501, 68, 104)
            and (w["initial"][457], w["initial"][461]) == entrance, "Declared native interface")
    profile, old_profile = word_profile(w), word_profile(source)
    expected_paid, expected_helpers, paid_maps, helper_maps, helper_roles = profile
    maps = paid_maps | helper_maps
    require(len(maps) == spec["catalogue_size"] and len(helper_roles) == 1101 and {457, 461} <= helper_roles,
            "Frozen map denominator and helper entrances")
    checked = verify_native_and_clear(spec, inputs, w, source, life)
    grid, ordinary = map(json.loads, (inputs["grid"], inputs["ordinary"]))
    verify_grid(spec, grid, w, life)
    require(ordinary["source_word_raw_sha256"] == digest(w_raw) and ordinary["caller_sha256"] == CALLER,
            "Actual ordinary-model source identity")
    caller_bytes = read(PRIOR / "caller/expected/ODD-TYPE-AB-CALLER.json", CALLER)
    caller = json.loads(caller_bytes)
    require(caller["stages"] == 17 and caller["ambient_rank"] == 145
            and [e[1] for e in caller["events"] if e[0] == "J"] == list(range(1, 18)), "All signed invocations")
    old, new = signed_invoice(caller, old_profile), signed_invoice(caller, profile)
    source_invoice = json.loads(inputs["source_invoice"])
    require({k: source_invoice[k] for k in old} == old, "Matched complete source invoice")
    require(sum(new["paid"].values()) == spec["paid_positions"] and sum(new["targets"].values()) == 22461,
            "Frozen complete signed paid and target census")
    independent = json.loads(inputs["independent_pair"])
    require(independent["result"] == "PASS_PAIRED_EXACT_REPLAY_AND_CONDITIONAL_PRICE"
            and independent["source"]["head"] == head
            and independent["source"]["literal_sha256"] == raw_sha
            and independent["source"]["gzip_sha256"] == zip_sha
            and independent["candidate"]["literal_sha256"] == spec["candidate_raw_sha256"]
            and independent["candidate"]["gzip_sha256"] == word_sha
            and independent["source"]["full_signed_invoice"] == source_invoice
            and independent["candidate"]["full_signed_invoice"] == source_invoice | new
            and independent["source"]["price"]["kappa"] == spec["source_bracket"]
            and independent["candidate"]["price"]["kappa"] == spec["bracket"],
            "Independent exact pair and both directed crossing brackets")
    cost = capture_price(spec, source_invoice, source_invoice | new)
    write(work / "PRICE-OUTER.json", cost)
    folder, copies = prepare(spec, inputs, grid, work, pins)
    ingredient = folder / "native_ingredient.py"
    ingredient.write_bytes(read(HERE / ingredient.name))
    induction = folder / "INGREDIENT-INPUT.json"
    write(induction, {"candidate_canonical_sha256": candidate, "clear_lifetimes": life, "bit_pin": spec["bit_pin"],
                      "retained_18_caller_sha256": digest((folder / "admission-source/data/caller.json").read_bytes()),
                      "physical_evidence_sha256": digest(inputs["native_result"]),
                      "clear_evidence_sha256": digest(inputs["clear_result"])})
    launch(work, "native_ingredient", ingredient, deadline)
    native_bridge = folder.parent / "RESULT.json"
    n = json.loads(native_bridge.read_bytes())["native"]
    require(n["paid"] == {str(r): q for r, q in expected_paid.items()}
            and n["helpers"] == {str(r): q for r, q in expected_helpers.items()},
            "Independent fresh transposed native histograms")
    cohort = folder / "COHORT-PRICE.json"
    write(cohort, {"paid": new["paid"], "target": new["targets"], "bracket": spec["bracket"]})
    copies.update({str(path.relative_to(work)): digest(path.read_bytes())
                   for path in (ingredient, induction, native_bridge, cohort)})
    checks = ("emit_odd_type_b", "emit_odd_type_ab", "check_odd_caller_exact_grid",
              "check_odd_physical_binding", "check_odd_precision", "check_odd_partial_admission",
              "check_odd_fixed_tape_counts")
    for script in checks:
        launch(work, script, folder / (script + ".py"), deadline)
    require((folder / "ODD-TYPE-AB-CALLER.json").read_bytes() == caller_bytes, "Exact regenerated caller bytes")

    def report(name):
        return json.loads((folder / name).read_bytes())

    binding = report("ODD-PHYSICAL-BINDING.json")
    geometry = binding["occurrence_and_geometry"]
    precision = report("ODD-PRECISION.json")
    partial = report("ODD-ADMISSION-PARTIAL.json")
    tape = report("ODD-FIXED-TAPE-COUNTS.json")
    for evidence in (binding, precision, partial, tape):
        require(evidence["native_sha256"] == candidate and evidence["caller_sha256"] == CALLER,
                "Signed intermediate result custody")
    require(geometry["native_calls"] == 17 and geometry["native_contact_boundaries"] == 13600
            and geometry["reserved_native_banks"] == 1156 and geometry["fresh_helpers"] == len(helper_roles) * 17
            and geometry["paid"] == new["paid"] and geometry["targets"] == new["targets"]
            and geometry["rank_surplus"] == partial["invoice"]["S"] == 1424
            and partial["invoice"]["empty_root_credits"] == 0 and binding["aliased_main_rejected"],
            "Complete occurrence and physical ownership binding")
    require(partial["invoice"]["P"] == new["paid"] and partial["invoice"]["T"] == new["targets"]
            and partial["crossing_probe_rejected"] and partial["compiler_outer"] == cost["gate"],
            "Outer corroboration and lower-bracket control")
    require(precision["rounded_caller"] == grid["caller_envelope"] and precision["context_c"] == grid["context_c"]
            and tape["context_bound_bits"] < tape["H"] and tape["max_scalar_numerator_bits"] <= 24,
            "Candidate fixed precision and tape")
    charged = partial["ordinary"]["conservative_total"]
    require(charged == ordinary["retained_signed_model_total"], "Independent ordinary source-unit agreement")
    scale = grid["integer_grid"]["odd_scale_lcm"]
    sites = 2 * geometry["native_calls"] * w["public"]
    extra = sites * 4 * (scale.bit_length() + 1 + scale.bit_count())
    require(charged + extra < 10**9, "Ordinary cap including all native-scale conversions")
    slices = catalogue_check(work, folder, maps, deadline, word_sha)
    launch(work, "assemble_odd_application", folder / "assemble_odd_application.py", deadline)
    launch(work, "fixed_controls", work / "controls.py", deadline)
    assembly = report("ODD-8X9-APPLICATION-CHECKS.json")
    falsifiers = json.loads((work / "CONTROLS.json").read_bytes())
    require(assembly["status"] == "PASS_8X9_EXACT_COMPONENT_APPLICATION_CHECKS"
            and assembly["assumptions"] == ASSUMPTIONS and assembly["native_canonical_sha256"] == candidate
            and assembly["caller_sha256"] == CALLER and falsifiers["positive"] == 1 and falsifiers["rejecting"] == 7,
            "Final joined component and fixed-tape controls")
    for rel, pin in copies.items():
        read(work / rel, pin)
    authenticate_inputs(spec)
    verify_sources()
    old_maps = old_profile[2] | old_profile[3]
    return {"status": "PASS_FRESH_SIGNED_CALLER_CONDITIONAL_COMPONENTS", "source_pr": pr, "source_head": head,
            "source_canonical_sha256": digest(canonical(source)), "candidate_canonical_sha256": candidate,
            "candidate_gzip_sha256": word_sha, "caller_sha256": CALLER, **new, "price_outer": cost["gate"],
            "clear_lifetimes": life, "reserved_native_banks": geometry["reserved_native_banks"],
            "catalogue_size": len(maps), "catalogue_common_with_source": len(maps & old_maps),
            "catalogue_new_to_source": sorted(maps - old_maps), "catalogue_boundary_pairs": 104,
            "birth_roles": {r: {"frame": w["initial"][r], "distinct_owners_bound": 17} for r in (457, 461)},
            "fixed_tape": tape, "ordinary": {"retained": charged, "native_scale": scale, "extra_sites": sites,
                "extra_charge_with_possible_overlap": extra, "model_total": charged + extra,
                "model_margin": 10**9 - charged - extra},
            "controls": {"native_receipt_mutations": checked, "fixed_tape": falsifiers,
                         "absolute_phase_rejections": len(slices), "aliased_main_rejected": True,
                         "lower_crossing_probe_rejected": True},
            "assumptions": ASSUMPTIONS, "seconds": time.monotonic() - tick, "source_copy_pins": copies,
            "assembly_sha256": digest((folder / "ODD-8X9-APPLICATION-CHECKS.json").read_bytes())}


def main():
    require(sys.flags.isolated and sys.dont_write_bytecode and __debug__, "Use Python -I -B with assertions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--go", required=True, type=Path)
    parser.add_argument("--work", required=True, type=Path)
    args = parser.parse_args()
    spec_bytes = args.spec.read_bytes()
    spec, go = map(json.loads, (spec_bytes, args.go.read_bytes()))
    require(go["status"] == "GO" and go["spec_sha256"] == digest(spec_bytes)
            and go["source_head"] == spec["source_head"]
            and go["candidate_canonical_sha256"] == spec["candidate_canonical_sha256"]
            and go["scope"] == "fresh-signed-caller-outer"
            and go["event_id"] and go["receipt_id"], "Exact registered run authorization")
    names = ("run.py", "guard.py", "engines.py", "native_ingredient.py")
    require(set(go["driver_files"]) == set(names), "Frozen driver closure")
    for name in names:
        read(HERE / name, go["driver_files"][name])
    wall = go["wall_seconds"]
    require(type(wall) is int and 150 <= wall <= 900, "Signed wall budget")
    work = args.work.resolve()
    require(work.is_relative_to(HERE) and work != HERE, "Dedicated signed output directory")
    cpu = go["cpu"]
    require(type(cpu) is int and cpu in os.sched_getaffinity(0), "Registered CPU affinity")
    os.sched_setaffinity(0, {cpu})
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (wall, wall))

    def interrupted(signum, _frame):
        raise InterruptedError(f"Signal {signum}")

    for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGALRM):
        signal.signal(signum, interrupted)
    deadline = time.monotonic() + wall
    signal.alarm(wall)
    inputs = authenticate_inputs(spec)
    pins = verify_sources()
    work.mkdir()
    write(work / "START.json", {"started": utc(), "spec": spec, "authorization": go,
                                "interpreter": sys.executable, "affinity": sorted(os.sched_getaffinity(0)),
                                "address_space": resource.getrlimit(resource.RLIMIT_AS),
                                "cpu_per_process": resource.getrlimit(resource.RLIMIT_CPU)})
    try:
        result = run(spec, inputs, work, deadline, pins)
        for name in names:
            read(HERE / name, go["driver_files"][name])
        signal.alarm(0)
        write(work / "RESULT.json", result)
    except BaseException as failure:
        signal.alarm(0)
        write(work / "EXIT.json", {"ended": utc(), "status": "INCOMPLETE", "error": repr(failure)})
        raise
    write(work / "EXIT.json", {"ended": utc(), "status": "COMPLETE", "result_sha256": digest((work / "RESULT.json").read_bytes())})
    print(result["status"], result["candidate_canonical_sha256"], flush=True)


if __name__ == "__main__":
    main()
