"""Recompute the seed-25 exact temporal census and full L359 candidate invoice."""

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
PR1263 = "5fbaca13028846bddbb001e8e07addc2ab8e5816"
PR1259 = "61367611154266a982fe25e1a6243a8aad77227d"
SEED = 25
EXPECTED_ZERO = [272, 288, 348, 359, 381, 440, 444, 446, 447, 469,
                 478, 479, 491, 503, 507, 514, 515, 519, 542]
SELECTED_KAPPA = "836330098538459/500000000000000000"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "load " + name)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


independent = module("seed25_independent", HERE / "independent.py")
incident_adds = independent.incident_adds
optimize = independent.optimize
transform = independent.transform


def check_dependencies():
    deps = json.loads((HERE / "DEPENDENCIES.json").read_bytes())
    need(deps["schema_version"] == 1 and deps["base_commit"] == BASE,
         "pinned base and dependency schema")
    need(deps["pr1263_head"] == PR1263 and deps["pr1259_head"] == PR1259,
         "pinned predecessor heads")
    need(set(deps["vendored_sha256"]) == set(deps["source_git_blobs"]),
         "complete source blob inventory")
    for rel, expected in deps["vendored_sha256"].items():
        raw = (HERE / rel).read_bytes()
        need(sha(raw) == expected, "vendored SHA-256 " + rel)
        blob_id = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(re.fullmatch(r"[0-9a-f]{40}", deps["source_git_blobs"][rel])
             and blob_id == deps["source_git_blobs"][rel], "source Git blob pin " + rel)
    return deps


def compute():
    deps = check_dependencies()
    selected = json.loads((ROOT / "certificates/selected-result.json").read_bytes())
    need(selected["kappa"] == SELECTED_KAPPA, "selected result at the pinned base")
    selected_cert = ROOT / selected["certificate"]
    need(sha(selected_cert.read_bytes()) == selected["certificate_sha256"],
         "selected certificate hash")
    source_pins = json.loads((HERE / "SOURCES.json").read_bytes())
    selected_pins = source_pins["selected_result"]
    need(source_pins["base_commit"] == BASE
         and sha((ROOT / selected_pins["path"]).read_bytes()) == selected_pins["sha256"],
         "selected-result source pin")
    need(selected_pins["certificate_path"] == selected["certificate"]
         and selected_pins["certificate_sha256"] == selected["certificate_sha256"],
         "selected-certificate source pin")
    need(sha((ROOT / selected_pins["source_manifest_path"]).read_bytes())
         == selected_pins["source_manifest_sha256"], "selected source manifest pin")
    inherited_pin = HERE / source_pins["pr1263"]["inherited_source_pin_file"]
    need(sha(inherited_pin.read_bytes()) == source_pins["pr1263"]["inherited_source_pin_sha256"],
         "inherited PR1263 source-pin manifest")

    parent = module("seed25_pinned_pr1263", HERE / "vendor/pr1263/verify.py")
    parent.ROOT = ROOT
    parent_result, static_words = parent.compute()
    need(parent_result["status"] == "PASS_MANY_HELPER_DYADIC_CONSTRUCTION",
         "PR1263 frozen source replay")
    need(parent_result["base"] == "dadfea6e8a78ff6ba901705f87532a71c6f5bbb8",
         "PR1263 historical source base")
    need(all(v["support"] == 218 and v["saving_complex"] == 13000
             for v in parent_result["orientations"].values()), "PR1263 218-helper word")

    gauges = json.loads((HERE / "vendor/pr1263/GAUGES.json").read_bytes())
    forward_support = set(map(int, gauges["forward"]))
    backward_support = set(map(int, gauges["backward"]))
    eligible = set(parent_result["eligible_helpers"])
    zero_helpers = sorted(eligible - forward_support)
    need(zero_helpers == EXPECTED_ZERO and forward_support == backward_support,
         "exact PR1263 zero-static eligible helper domain")
    need(SEED % len(zero_helpers) == 6 and zero_helpers[6] == 444,
         "seed-indexed first helper")
    scan_order = zero_helpers[SEED % len(zero_helpers):] + zero_helpers[:SEED % len(zero_helpers)]

    lib = parent.engine()
    word, originals, _, _ = lib.load()
    result = {
        "status": "PASS_ZERO_STATIC_TEMPORAL_CENSUS",
        "assignment_seed": SEED,
        "track": "complex supplier",
        "base_commit": BASE,
        "selected_kappa": SELECTED_KAPPA,
        "selected_certificate_sha256": selected["certificate_sha256"],
        "predecessors": {"pr1263_head": PR1263, "pr1259_head": PR1259},
        "domain": {
            "eligible_helpers": len(eligible),
            "static_gauged_helpers": len(forward_support),
            "zero_static_helpers": zero_helpers,
            "scan_order": scan_order,
            "orientation": ["forward", "backward"],
            "schedule_values": "all integers, reduced to the exact breakpoint interval",
        },
        "orientations": {},
    }
    winner_candidates = {}
    all_rows = {}
    for orientation in ("forward", "backward"):
        rows = []
        optimized = {}
        for helper in scan_order:
            need(word["start"][helper] == 0 and word["final"][helper] == 1,
                 orientation + " cold/FULL helper boundary")
            need(not any(event[0] == "residual_adapter" and event[2] == helper
                         for event in originals[orientation]), orientation + " no residual adapter")
            need(not any(event[0] == "scalar" and event[1][0] in ("copy", "clear")
                         and ["L", helper] in event[1][1:]
                         for event in originals[orientation]), orientation + " no incident COPY/clear")
            terms = incident_adds(static_words[orientation], helper)
            opt = optimize(terms)
            optimized[helper] = (terms, opt)
            rows.append({
                "helper": helper,
                "incident_adds": opt["incident_adds"],
                "domain": opt["domain"],
                "edge_evaluations": opt["edge_evaluations"],
                "best_delta_real": opt["delta_real"],
                "best_constant_delta_real": opt["constant_delta_real"],
                "best_constant_exponent": opt["constant_exponent"],
                "transition_scale_macros": opt["transition_scale_macros"],
            })

        best_helper = min(scan_order, key=lambda helper: (optimized[helper][1]["delta_real"], helper))
        need(best_helper == 359, orientation + " exact best zero-static temporal helper")
        terms, optimum = optimized[best_helper]
        schedule = [[index, exponent] for (index, _, _), exponent
                    in zip(terms, optimum["schedule"])]
        candidate, pulses = transform(static_words[orientation], best_helper, schedule)
        before = lib.invoice(static_words[orientation], "copy-init")
        after = lib.invoice(candidate, "copy-init")
        base_invoice = parent_result["orientations"][orientation]["baseline"]
        need(after["real_primitives"] - before["real_primitives"] == optimum["delta_real"],
             orientation + " DP agrees with full lowerer invoice")
        need(optimum["delta_real"] == -242 and optimum["constant_delta_real"] == 0,
             orientation + " exact temporal improvement over every constant exponent")
        need(after["complex_primitives"] == base_invoice["complex_primitives"] - 13484,
             orientation + " full-word invoice vs original PR1094 word")
        need(after["complex_primitives"] == before["complex_primitives"] - 484,
             orientation + " complete 484-primitive improvement over PR1263")
        need(after["charged_payload_bits"] == 192 and after["prefix_bits"] <= 192,
             orientation + " inherited local precision ceiling")
        need(before["paid_profile"] == after["paid_profile"],
             orientation + " paid recursive profile unchanged")
        need(lib.replay(candidate, orientation) == lib.replay(originals[orientation], orientation),
             orientation + " all formal source columns")
        need([event for event in candidate if event[0] != "scalar"]
             == [event for event in static_words[orientation] if event[0] != "scalar"],
             orientation + " frame, source, and paid event sequence unchanged")
        need(len(pulses) == optimum["transition_scale_macros"] == 33,
             orientation + " transition scale macro count")
        scale_work = sum(abs(pulse[1]) for pulse in pulses)
        previous = 0
        schedule_work = 0
        for exponent in optimum["schedule"]:
            schedule_work += abs(exponent - previous)
            previous = exponent
        schedule_work += abs(previous)
        need(scale_work == schedule_work, orientation + " full entry/transition/exit scale work")

        # A zero schedule is an exact identity control; the best constant schedule
        # has zero delta, so the reported gain requires time variation.
        identity, identity_pulses = transform(static_words[orientation], best_helper,
                                               [[index, 0] for index, _, _ in terms])
        need(identity == static_words[orientation] and not identity_pulses,
             orientation + " zero schedule identity control")
        malformed = [list(event) for event in candidate]
        malformed.pop(pulses[0][3])
        try:
            omitted_pulse_matches = (lib.replay(malformed, orientation)
                                     == lib.replay(originals[orientation], orientation))
        except Exception:
            omitted_pulse_matches = False
        need(not omitted_pulse_matches, orientation + " omitted-transition-scale control rejected")
        rows_by_helper = {row["helper"]: row for row in rows}
        need(all(row["best_constant_delta_real"] == 0 for row in rows),
             orientation + " all 19 static zero-coordinate controls")

        result["orientations"][orientation] = {
            "helpers_checked": len(rows),
            "helpers": rows,
            "winner": best_helper,
            "winner_incident_adds": len(terms),
            "winner_domain": optimum["domain"],
            "winner_edge_evaluations": optimum["edge_evaluations"],
            "winner_delta_real": optimum["delta_real"],
            "winner_transition_scale_macros": len(pulses),
            "winner_transition_scale_work": scale_work,
            "winner_schedule": schedule,
            "baseline_static_invoice": before,
            "candidate_invoice": after,
            "omitted_transition_scale_rejected": True,
            "saving_complex_vs_pr1263": before["complex_primitives"] - after["complex_primitives"],
            "saving_complex_vs_original": base_invoice["complex_primitives"] - after["complex_primitives"],
            "formal_endpoint": lib.replay(candidate, orientation),
            "candidate_sha256": sha(canonical(candidate)),
        }
        winner_candidates[orientation] = candidate
        all_rows[orientation] = rows_by_helper

    # The selected winner is a single-coordinate result; do not sum independent
    # savings across shared ADDs or infer a composed multi-coordinate optimum.
    need(result["orientations"]["forward"]["winner"] == result["orientations"]["backward"]["winner"],
         "same winning helper in both orientations")
    return result


def main():
    result = compute()
    cert_path = HERE / "CERTIFICATE.json"
    if "--write" in sys.argv:
        need(not cert_path.exists(), "refuse to overwrite frozen certificate")
        cert_path.write_bytes(canonical(result) + b"\n")
    else:
        frozen = json.loads(cert_path.read_bytes())
        need(canonical(result) == canonical(frozen), "frozen exact certificate")
    print(result["status"])
    for orientation, row in result["orientations"].items():
        print(orientation, "helpers", row["helpers_checked"], "winner", row["winner"],
              "delta_real", row["winner_delta_real"],
              "complex", row["candidate_invoice"]["complex_primitives"],
              "saved_vs_PR1263", row["saving_complex_vs_pr1263"],
              "columns", row["formal_endpoint"].get("formal_input_columns"))


if __name__ == "__main__":
    main()
