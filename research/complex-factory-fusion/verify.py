#!/usr/bin/env python3
"""Verify the exact factory, every raw-word column and the fixed banked bill.

Prepared for Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0. This finite check does not prove the multiplication theorem.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from circuit import compile_factory, local_check, need, reference, variants
from comparator import cache_word, gauge_census
from full import ROOT, build, canonical, digest, load_module, locate, lower_program, read, replay, scalar_pattern, write
import host


def check_pins():
    pins = read(HERE / "SOURCES.json")
    for name, expected in pins["files"].items():
        path = ROOT / name
        data = path.read_bytes()
        if path.suffix == ".gz":
            import gzip
            data = gzip.decompress(data)
        need(hashlib.sha256(data).hexdigest() == expected, "source pin: " + name)
    return pins


def check_local(word, candidate):
    result = {}
    accumulated = load_module("local_factory999", HERE / "sources/pr999-lower.py")
    originals = variants(read(ROOT / "research/complex-factory5-resynthesis/CIRCUIT.json")["original"])
    for name, scalar in variants(word).items():
        baseline = local_check(scalar, reference(scalar))
        current = []
        for op in scalar_pattern(scalar, list(range(8))):
            for primitive in accumulated.lower(op)[1]:
                current.append([primitive[0], *[8 if r[0] == "W" else r[1] for r in primitive[1:]]])
        need(current == [list(op) for op in reference(scalar)], "PR999 changed factory comparison")
        cached = local_check(scalar, reference(scalar, reuse=True))
        strong = local_check(scalar, cache_word(scalar))
        census = gauge_census(scalar)
        implementation = variants(candidate, True)[name] + [["clear", 8]]
        fresh = local_check(scalar, implementation)
        local_check(originals[name], implementation)
        fresh["original_87_macro_boundary"] = True
        need(fresh["primitives"] == 38 < strong["primitives"] == 44
             and strong["primitives"] < cached["primitives"] < baseline["primitives"],
             "factory cost did not improve the strong comparator")
        from fractions import Fraction as Q
        need(Q(fresh["peak_row_l1"]) <= Q(baseline["peak_row_l1"])
             and fresh["fractional_depth"] <= baseline["fractional_depth"],
             "factory precision guard")
        result[name] = {"pr696": baseline, "cached_work": cached, "strong": strong,
                        "extended_gauge_census": census, "candidate": fresh}
    return result


def rejection(action, reason):
    try:
        action()
    except ValueError as error:
        need(reason in str(error), "control failed for another reason: " + str(error))
        return
    raise ValueError("accepted negative control: " + reason)


def local_controls(word, candidate, certificate):
    controls = []
    for name, scalar in variants(word).items():
        primitives = variants(candidate, True)[name] + [["clear", 8]]
        for index in range(len(primitives)):
            mutant = primitives[:index] + primitives[index + 1:]
            rejection(lambda: local_check(scalar, mutant), "exact factory boundary")
        controls.append({"variant": name, "single_primitive_deletions_rejected": len(primitives)})
    altered = copy.deepcopy(certificate)
    altered["levels"][0] = True
    rejection(lambda: compile_factory(word, altered), "noninteger certificate")
    altered = copy.deepcopy(certificate)
    altered["dual_flow"][0] = 2
    rejection(lambda: compile_factory(word, altered), "dual capacity")
    altered = copy.deepcopy(certificate)
    altered["dual_flow"][0] = 0
    rejection(lambda: compile_factory(word, altered), "dual conservation")
    altered = copy.deepcopy(certificate)
    altered["primitives"][3][1] = True
    rejection(lambda: compile_factory(word, altered), "primitive certificate types")
    return {"deletion_families": controls, "certificate_controls": 4}


def host_controls(good, native):
    mutants = {}
    bad = copy.deepcopy(good)
    bad["calls"].pop()
    mutants["missing_call"] = (bad, "missing hosted work")
    bad = copy.deepcopy(good)
    bad["calls"][1]["owners"][224] = bad["calls"][1]["owners"][225]
    mutants["aliased_owner"] = (bad, "aliased complete-invocation owner")
    bad = copy.deepcopy(good)
    bad["banks"][0]["complement_axes"] = [71]
    mutants["wrong_complement"] = (bad, "wrong bank complement")
    bad = copy.deepcopy(good)
    bad["calls"][0]["local_program_sha256"] = "0" * 64
    mutants["unbound_program"] = (bad, "unbound local program")
    bad = copy.deepcopy(good)
    index = next(i for i, e in enumerate(bad["execution_schedule"]) if e["kind"] == "bridge")
    bad["execution_schedule"].pop(index)
    mutants["missing_bridge"] = (bad, "bridge repetition")
    bad = copy.deepcopy(good)
    next(e for e in bad["execution_schedule"] if e["kind"] == "bank_padding_cover_sweep")["families"][1] += 1
    mutants["stale_bank_range"] = (bad, "stale bank sweep")
    bad = copy.deepcopy(good)
    next(e for e in bad["execution_schedule"] if e["kind"] == "translate_every_live_family")["charged_calls_per_cover"] -= 1
    mutants["unpaid_translation"] = (bad, "unpaid final translation")
    bad = copy.deepcopy(good)
    next(e for e in bad["execution_schedule"] if e["kind"] == "bridge")["coefficient"] *= -1
    mutants["wrong_bridge_sign"] = (bad, "changed schedule operation")
    bad = copy.deepcopy(good)
    bad["private_namespace"]["coefficient"][0] -= 1
    mutants["private_alias"] = (bad, "private namespace overlap")
    for bad, reason in mutants.values():
        rejection(lambda: host.audit(bad, native), reason)
    bad = copy.deepcopy(native)
    bad["ports"][0], bad["ports"][1] = bad["ports"][1], bad["ports"][0]
    rejection(lambda: host.audit(good, bad), "changed hosted data ports")
    return list(mutants) + ["changed_data_port_order"]


def phase_replay(out):
    prior = load_module("factory681_phases", ROOT / "research/complex-factory5-resynthesis/verify.py")
    prior.run(ROOT / "research/direct-delivery504-global/code/phases_delta.py",
              ["--local", out / "local", "--baseline",
               ROOT / "research/direct-delivery504-global/inputs/phase-baseline",
               "--compiler", ROOT / "research/direct-delivery504-global/vendor/clifford"],
              out / "phases.log")
    receipt = read(out / "local/CLIFFORD-REVIEW.json")
    receipt.pop("seconds")
    receipt.pop("canonical_word_sha256")
    need(receipt["all_child_equalities_include_global_phase"]
         and receipt["directed_edges"] == 3110 and receipt["endpoint_adapters"] == 224,
         "incomplete phase replay")
    return receipt


def verify(out):
    pins = check_pins()
    word = read(ROOT / pins["factory_source"])["replacement"]
    certificate = read(HERE / "CIRCUIT.json")
    candidate = compile_factory(word, certificate)
    local = check_local(word, candidate)
    controls = {"local": local_controls(word, candidate, certificate)}
    native, programs, bindings, inherited = build(out, word)
    print("PASS factory and native bindings", flush=True)
    phases = phase_replay(out)
    print("PASS exact phase recipes", flush=True)
    results, emitted = {}, {}
    for orientation, events in programs.items():
        windows = locate(events, word, bindings, orientation)
        write(out / (orientation + "-FACTORY-WINDOWS.json"), windows)
        # A climb on a wire already read in the interval cannot be moved left.
        if orientation == "forward":
            mutant = copy.deepcopy(events)
            window = next(w for w in windows if any(e[0] == "climb"
                          for e in events[w["begin"] + 3:w["end"]]))
            first = next(i for i in range(window["begin"], window["end"])
                         if mutant[i][0] == "scalar")
            later = next((i for i in range(first + 1, window["end"])
                          if mutant[i][0] == "climb"), None)
            need(later is not None, "missing climb control site")
            mutant[later][2] = mutant[first][1][1][1]
            rejection(lambda: locate(mutant, word, bindings, orientation), "climb cannot move")
            controls["factory_placement"] = ["climb_crosses_live_register_use"]
        results[orientation], emitted[orientation] = {}, {}
        for mode in ("pr696", "accumulated", "cache", "strong", "candidate"):
            stream = lower_program(events, windows, word, candidate, mode)
            results[orientation][mode] = replay(stream, native, orientation)
            emitted[orientation][mode] = stream
            write(out / (orientation + "-" + mode + "-PRIMITIVES.json.gz"), stream)
        from fractions import Fraction as Q
        need(Q(results[orientation]["candidate"]["positive_peak"]) <=
             Q(inherited["local"]["local"][orientation]["prefix_l1_upper"]),
             "whole-word precision reserve exceeded")
        for mode in ("cache", "strong", "candidate"):
            need(results[orientation][mode]["real_primitives"] <
                 results[orientation]["accumulated"]["real_primitives"], "no whole-word saving")
    need(results["forward"]["pr696"]["real_primitives"] == 123320
         and results["backward"]["pr696"]["real_primitives"] == 123336,
         "pinned PR924 complete primitive bill")
    # A wrong physical frame must fail at the actual emitted primitive.
    mutant = copy.deepcopy(emitted["forward"]["candidate"])
    first = next(e for e in mutant if e[0] == "primitive" and e[2] != 0 and e[1][1][0] == "L")
    first[2] = 0
    rejection(lambda: replay(mutant, native, "forward"), "live common frame")
    controls["whole_word"] = ["wrong_primitive_frame"]
    print("PASS all ten complete primitive projections", flush=True)
    checks = read(out / "local/LOCAL-CHECKS.json")
    physical = {"native_word_sha256": digest(native),
                "clifford_recipes_sha256": digest(read(out / "local/CLIFFORD-RECIPES.json")),
                "phase_check_sha256": digest(phases)}
    hosting = {}
    for mode in ("pr696", "accumulated", "cache", "strong", "candidate"):
        descriptions = {o: results[o][mode] for o in programs}
        controller = host.construct(native, descriptions, physical)
        admission = host.audit(controller, native)
        hosting[mode] = {"admission": admission, "invoice": host.invoice(controller, admission, checks),
                         "controller_sha256": digest(controller)}
        write(out / (mode + "-HOST.json.gz"), controller)
        if mode == "candidate":
            controls["hosting"] = host_controls(controller, native)
    strong, fresh = (hosting[x]["invoice"] for x in ("strong", "candidate"))
    saving = strong["per_cover_vertex_bound"] - fresh["per_cover_vertex_bound"]
    need(saving == strong["hosted_scalar_primitives"] - fresh["hosted_scalar_primitives"]
         and saving == 24192, "hosted saving or retained outside bill")
    result = {"status": "PASS_EXACT_COMPLEX_FACTORY_FUSION", "base_commit": pins["base_commit"],
              "local": local, "native": inherited, "phase": phases, "programs": results,
              "hosted": hosting, "controls": controls,
              "saved_vs_pr696_per_call": {o: results[o]["pr696"]["real_primitives"]
                                         - results[o]["candidate"]["real_primitives"] for o in programs},
              "pr999_saved_outside_factories": {o: results[o]["pr696"]["real_primitives"]
                                               - results[o]["accumulated"]["real_primitives"] for o in programs},
              "extra_saved_vs_strong_per_call": {o: results[o]["strong"]["real_primitives"]
                                                 - results[o]["candidate"]["real_primitives"] for o in programs},
              "small_integer_saved_outside_factories": {
                  o: results[o]["cache"]["real_primitives"] - results[o]["strong"]["real_primitives"]
                  - sum(28 * (local[name]["cached_work"]["primitives"] - 44)
                        for name in (("main", "cleanup") if o == "forward" else
                                     ("dual_main", "dual_cleanup"))) for o in programs},
              "extra_saved_hosted": saving, "new_kappa": False}
    return json.loads(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="retain artifacts in a new directory")
    parser.add_argument("--write", type=Path, help="write a new development receipt")
    args = parser.parse_args()
    need(args.write is None or not args.write.exists(), "receipt output already exists")
    if args.out:
        need(not args.out.exists(), "artifact output already exists")
        args.out.mkdir(parents=True)
        result = verify(args.out.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix="complex-factory-fusion-") as directory:
            result = verify(Path(directory))
    if args.write:
        with args.write.open("x") as output:
            json.dump(result, output, indent=2, sort_keys=True)
            output.write("\n")
    else:
        need(canonical(result) == canonical(read(HERE / "EXPECTED.json")), "complete expected receipt")
    print("PASS_EXACT_COMPLEX_FACTORY_FUSION primitives=44->38 columns=725 "
          "calls=72 extra_vs_strong=" + str(result["extra_saved_hosted"]) + " no_new_kappa")


if __name__ == "__main__":
    main()
