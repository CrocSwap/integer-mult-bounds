#!/usr/bin/env python3
"""Source-pinned L259 temporal gauge construction and complete invoice replay."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys


def need(ok, message):
    if not ok:
        raise ValueError(message)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
_spec = importlib.util.spec_from_file_location("seed32_temporal", HERE / "temporal.py")
need(_spec is not None and _spec.loader is not None, "load exact temporal optimizer")
_temporal = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_temporal)
incident_adds = _temporal.incident_adds
optimize = _temporal.optimize
objective = _temporal.objective
transform = _temporal.transform
small_exhaustive_control = _temporal.small_exhaustive_control
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
SELECTED_KAPPA = "836330098538459/500000000000000000"
PR1263_HEAD = "5fbaca13028846bddbb001e8e07addc2ab8e5816"
PR1259_HEAD = "61367611154266a982fe25e1a6243a8aad77227d"
SEED = 32
HELPER_INDEX = 32
HELPER = 259


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def check_vendor_pins():
    deps = json.loads((HERE / "DEPENDENCIES.json").read_bytes())
    need(deps["schema_version"] == 1 and deps["base_commit"] == BASE, "dependency schema/base")
    need(deps["pr1263_head"] == PR1263_HEAD and deps["pr1259_head"] == PR1259_HEAD,
         "predecessor heads")
    hashes, blobs = deps["vendored_sha256"], deps["source_git_blobs"]
    need(set(hashes) == set(blobs) and hashes, "complete vendor inventory")
    for relative, expected in hashes.items():
        raw = (HERE / relative).read_bytes()
        need(sha(raw) == expected, "vendored SHA-256 " + relative)
        need(re.fullmatch(r"[0-9a-f]{40}", blobs[relative]) and git_blob(raw) == blobs[relative],
             "vendored Git blob " + relative)
    return deps


def check_selected_result():
    selected = json.loads((ROOT / "certificates/selected-result.json").read_bytes())
    need(selected["kappa"] == SELECTED_KAPPA, "selected result at pinned base")
    cert = ROOT / selected["certificate"]
    need(sha(cert.read_bytes()) == selected["certificate_sha256"], "selected certificate hash")
    return selected


def load_parent():
    path = HERE / "vendor/pr1263/verify.py"
    spec = importlib.util.spec_from_file_location("seed32_pinned_pr1263", path)
    need(spec is not None and spec.loader is not None, "load pinned PR1263 verifier")
    parent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    parent.ROOT = ROOT
    return parent


def exact_l259_result():
    deps = check_vendor_pins()
    selected = check_selected_result()
    parent = load_parent()
    parent_result, static_words = parent.compute()
    need(parent_result["status"] == "PASS_MANY_HELPER_DYADIC_CONSTRUCTION",
         "pinned PR1263 construction")
    need(parent_result["base"] == "dadfea6e8a78ff6ba901705f87532a71c6f5bbb8",
         "PR1263 historical construction base")
    eligible = parent_result["eligible_helpers"]
    need(len(eligible) == 237 and eligible == sorted(eligible), "complete sorted helper inventory")
    need(SEED % len(eligible) == HELPER_INDEX and eligible[HELPER_INDEX] == HELPER,
         "OS seed selection of the 33rd eligible helper")
    gauges = json.loads((HERE / "vendor/pr1263/GAUGES.json").read_bytes())
    need(set(gauges) == {"forward", "backward"}, "two orientations in frozen gauge word")
    need(set(gauges["forward"]) == set(gauges["backward"]) and len(gauges["forward"]) == 218,
         "frozen nonzero-static support size")
    need(str(HELPER) in gauges["forward"] and str(HELPER) in gauges["backward"],
         "L259 is in the PR1263 static support")
    need(gauges["forward"][str(HELPER)] != 0 and gauges["backward"][str(HELPER)] != 0,
         "L259 belongs to the nonzero-static class")

    lib = parent.engine()
    _, originals, _, _ = lib.load()
    certificate = {
        "status": "PASS_K8_L259_TEMPORAL_SEED32",
        "base_commit": BASE,
        "selected_kappa": SELECTED_KAPPA,
        "selected_certificate_sha256": selected["certificate_sha256"],
        "assignment": {"seed": SEED, "track": "complex supplier", "eligible_index": HELPER_INDEX,
                       "eligible_count": len(eligible), "helper": HELPER,
                       "static_exponents": {o: gauges[o][str(HELPER)] for o in ("forward", "backward")}},
        "predecessors": {"pr1263_head": PR1263_HEAD, "pr1259_head": PR1259_HEAD,
                         "pr1263_historical_base": parent_result["base"]},
        "directions": {},
    }
    expected = {
        "forward": ([-12, 4], 68001, 67890, 136002, 135780, 52),
        "backward": ([-4, 12], 68009, 67898, 136018, 135796, 68),
    }
    for orientation in ("forward", "backward"):
        events = static_words[orientation]
        terms = incident_adds(events, HELPER)
        need(len(terms) == 144, orientation + " complete 144-ADD coverage")
        optimum = optimize(terms)
        need(optimum["domain"] == expected[orientation][0], orientation + " exact breakpoint interval")
        need(optimum["delta_real"] == -111 and optimum["constant_delta_real"] == 0
             and optimum["constant_exponent"] == 0,
             orientation + " temporal improvement over all constant additional exponents")
        candidate, pulses = transform(events, HELPER, terms, optimum["schedule"])
        before = lib.invoice(events, "copy-init")
        after = lib.invoice(candidate, "copy-init")
        old_real, new_real, old_complex, new_complex, prefix = expected[orientation][1:]
        need(before["real_primitives"] == old_real and after["real_primitives"] == new_real,
             orientation + " complete real lowerer invoices")
        need(before["complex_primitives"] == old_complex and after["complex_primitives"] == new_complex,
             orientation + " complete complex invoices")
        need(after["real_primitives"] - before["real_primitives"] == optimum["delta_real"],
             orientation + " DP agrees with complete lowerer invoice")
        need(before["paid_profile"] == after["paid_profile"], orientation + " paid profile identity")
        need(after["charged_payload_bits"] == 192 and after["prefix_bits"] == prefix,
             orientation + " inherited local precision ceiling")
        need([event for event in events if event[0] != "scalar"]
             == [event for event in candidate if event[0] != "scalar"],
             orientation + " all frame, source, copy and paid events retained")
        baseline_endpoint = lib.replay(originals[orientation], orientation)
        candidate_endpoint = lib.replay(candidate, orientation)
        need(candidate_endpoint == baseline_endpoint, orientation + " all 712 formal columns")
        need(candidate_endpoint.get("formal_input_columns") == 712,
             orientation + " full formal input domain count")
        scale_work = sum(abs(pulse[1]) for pulse in pulses)
        need(len(pulses) == 21 and scale_work == 24, orientation + " all transition and restoration scales")
        schedule_work = 0
        previous = 0
        for exponent in optimum["schedule"]:
            schedule_work += abs(exponent - previous)
            previous = exponent
        schedule_work += abs(previous)
        need(scale_work == schedule_work, orientation + " entry/transition/exit charge")

        identity, identity_pulses = transform(events, HELPER, terms, [0] * len(terms))
        need(identity == events and not identity_pulses, orientation + " zero-schedule control")
        malformed = copy.deepcopy(candidate)
        malformed.pop(pulses[0][3])
        try:
            omitted_scale_detected = lib.replay(malformed, orientation) != baseline_endpoint
        except Exception:
            omitted_scale_detected = True
        need(omitted_scale_detected, orientation + " omitted-transition negative control")

        certificate["directions"][orientation] = {
            "incident_adds": len(terms), "breakpoint_domain": optimum["domain"],
            "domain_size": optimum["domain_size"], "edge_evaluations": optimum["edge_evaluations"],
            "delta_real": optimum["delta_real"], "constant_delta_real": optimum["constant_delta_real"],
            "constant_exponent": optimum["constant_exponent"],
            "schedule": list(optimum["schedule"]), "schedule_l1": optimum["schedule_l1"],
            "transition_scales": len(pulses), "scale_work": scale_work,
            "baseline_real": before["real_primitives"], "candidate_real": after["real_primitives"],
            "baseline_complex": before["complex_primitives"], "candidate_complex": after["complex_primitives"],
            "charged_payload_bits": after["charged_payload_bits"], "prefix_bits": after["prefix_bits"],
            "paid_profile_unchanged": True, "formal_input_columns": 712,
            "candidate_word_sha256": sha(canonical(candidate)),
            "omitted_transition_rejected": True,
        }
    certificate["small_exhaustive_control_delta"] = small_exhaustive_control()
    need(certificate["small_exhaustive_control_delta"] is not None, "small exact DP control")
    return certificate, deps


def main():
    certificate, _ = exact_l259_result()
    path = HERE / "CERTIFICATE.json"
    encoded = canonical(certificate) + b"\n"
    if "--write" in sys.argv:
        need(not path.exists(), "refuse to overwrite frozen certificate")
        path.write_bytes(encoded)
    else:
        need(canonical(json.loads(path.read_bytes())) == canonical(certificate),
             "frozen exact certificate")
    print(certificate["status"])
    for orientation, row in certificate["directions"].items():
        print(orientation, "helper=259", "delta_real", row["delta_real"],
              "complex", row["baseline_complex"], "->", row["candidate_complex"],
              "scales", row["transition_scales"], "work", row["scale_work"],
              "columns", row["formal_input_columns"])


if __name__ == "__main__":
    main()
