"""Verify a temporal L253 gauge over PR1263's frozen 218-helper word.

Seed 27 and substantial OpenAI Codex assistance; Apache-2.0.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = "vendor/pr1263/verify.py"
PARENT_COMMIT = "5fbaca13028846bddbb001e8e07addc2ab8e5816"
VARYING_COMMIT = "61367611154266a982fe25e1a6243a8aad77227d"
BASE_COMMIT = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
SEED = 27


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, "module spec " + name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def modules():
    deps = json.loads((HERE / "DEPENDENCIES.json").read_bytes())
    require(deps["base_commit"] == BASE_COMMIT, "exact current base")
    require(deps["pr1263_head"] == PARENT_COMMIT, "PR1263 source head")
    require(deps["pr1259_head"] == VARYING_COMMIT, "PR1259 source head")
    blobs = deps["source_git_blobs"]
    require(set(blobs) == set(deps["vendored_sha256"])
            and all(re.fullmatch(r"[0-9a-f]{40}", value) for value in blobs.values()),
            "vendored source Git blob inventory")
    for rel, digest in deps["vendored_sha256"].items():
        require(sha((HERE / rel).read_bytes()) == digest, "vendored dependency " + rel)
    parent = load_module("pinned_pr1263_verify", HERE / PARENT)
    # The attributed verifier is byte-identical to the pinned PR1263 head, but
    # runs its source loader against this package's exact checked-out base.
    parent.ROOT = ROOT
    varying = load_module("pinned_pr1259_search", HERE / "vendor/pr1259/search.py")
    return parent, varying


def compute():
    parent, varying = modules()
    selected = json.loads((ROOT / "certificates/selected-result.json").read_bytes())
    require(selected["kappa"] == "836330098538459/500000000000000000"
            and selected["decimal"] == "0.001672660197076918",
            "current selected conditional frontier")
    selected_certificate = ROOT / selected["certificate"]
    require(sha(selected_certificate.read_bytes()) == selected["certificate_sha256"],
            "selected assembly certificate hash")
    parent_result, static_candidates = parent.compute()
    require(parent_result["status"] == "PASS_MANY_HELPER_DYADIC_CONSTRUCTION", "PR1263 replay")
    require(all(row["support"] == 218 and row["saving_complex"] == 13000
                for row in parent_result["orientations"].values()), "PR1263 frozen candidate")
    lib = parent.engine()
    word, originals, _, _ = lib.load()

    gauge_maps = json.loads((HERE / "vendor/pr1263/GAUGES.json").read_bytes())
    gauge_map = gauge_maps["forward"]
    backward_map = gauge_maps["backward"]
    support = sorted(map(int, gauge_map))
    helper_index = SEED % len(support)
    helper = support[helper_index]
    require(len(support) == 218 and helper == 253 and set(gauge_map) == set(backward_map),
            "seed-indexed helper L253")
    require(int(backward_map[str(helper)]) == -int(gauge_map[str(helper)]),
            "orientation inverse static gauge")
    require(helper in parent_result["eligible_helpers"], "seed helper is eligible in the retained word")

    result = {
        "status": "PASS_L253_TEMPORAL_GAUGE_ON_218_HELPER_WORD",
        "assignment_seed": SEED,
        "track": "complex supplier",
        "current_base_commit": BASE_COMMIT,
        "selected_kappa": "836330098538459/500000000000000000",
        "selected_source_manifest": selected["source_manifest"],
        "selected_certificate_sha256": selected["certificate_sha256"],
        "parent": {"pr": 1263, "head": PARENT_COMMIT, "base": "dadfea6e8a78ff6ba901705f87532a71c6f5bbb8",
                   "static_helpers": 218},
        "method_predecessor": {"pr": 1259, "head": VARYING_COMMIT},
        "selection": {"rule": "sorted PR1263 forward support, zero-based seed modulo support length",
                      "index": helper_index, "support_length": len(support), "helper": helper,
                      "static_exponent_forward": int(gauge_map[str(helper)]),
                      "static_exponent_backward": int(backward_map[str(helper)])},
        "orientations": {},
    }
    candidates = {}
    for orientation in ("forward", "backward"):
        static = static_candidates[orientation]
        require(word["start"][helper] == 0 and word["final"][helper] == 1,
                orientation + " cold/FULL interface")
        require(not any(event[0] == "residual_adapter" and event[2] == helper
                        for event in originals[orientation]), orientation + " no residual wrapper")
        require(not any(event[0] == "scalar" and event[1][0] in ("copy", "clear")
                        and ["L", helper] in event[1][1:] for event in originals[orientation]),
                orientation + " no incident COPY/clear")
        terms = varying.incident(static, helper)
        optimum = varying.optimize(terms)
        candidate = varying.transform(static, word, helper, optimum["schedule"])
        before = lib.invoice(static, "copy-init")
        after = lib.invoice(candidate, "copy-init")
        require(after["real_primitives"] - before["real_primitives"] == optimum["delta_real"],
                orientation + " dynamic-program / complete-invoice equality")
        require(optimum["delta_real"] == -91, orientation + " exact incremental optimum")
        require(lib.replay(candidate, orientation) == lib.replay(originals[orientation], orientation),
                orientation + " all 712 formal columns")
        require(lib.replay(static, orientation) == lib.replay(originals[orientation], orientation),
                orientation + " static predecessor endpoint")
        nonscalar = [event for event in originals[orientation] if event[0] != "scalar"]
        require([event for event in static if event[0] != "scalar"] == nonscalar
                and [event for event in candidate if event[0] != "scalar"] == nonscalar,
                orientation + " source/frame/paid event identity")
        require(before["paid_profile"] == after["paid_profile"], orientation + " paid profile preserved")
        require(after["charged_payload_bits"] == 192 and after["prefix_bits"] <= 192,
                orientation + " inherited local payload ceiling")
        base_invoice = parent_result["orientations"][orientation]["baseline"]
        require(after["complex_primitives"] == base_invoice["complex_primitives"] - 13182,
                orientation + " exact full-word saving")
        require(len(terms) == 96, orientation + " L253 incident ADD count")
        require(len(optimum["schedule"]) == len(terms), orientation + " full schedule")
        domain_size = optimum["domain"][1] - optimum["domain"][0] + 1
        transitions = domain_size + (len(terms) - 1) * domain_size * domain_size
        require(domain_size == 7 and transitions == 4662,
                orientation + " complete finite DP coverage")
        result["orientations"][orientation] = {
            "incident_adds": len(terms),
            "exponent_domain": optimum["domain"],
            "domain_size": domain_size,
            "dp_transition_evaluations": transitions,
            "incremental_delta_real": optimum["delta_real"],
            "incremental_saving_complex": -2 * optimum["delta_real"],
            "scheduled_scale_macros": optimum["scale_macros"],
            "baseline_static_invoice": before,
            "candidate_invoice": after,
            "total_saving_complex_vs_original": base_invoice["complex_primitives"] - after["complex_primitives"],
            "schedule": optimum["schedule"],
            "formal_endpoint": lib.replay(candidate, orientation),
            "candidate_sha256": sha(canonical(candidate)),
        }
        candidates[orientation] = candidate

    return result, candidates


def main():
    result, _ = compute()
    path = HERE / "CERTIFICATE.json"
    if "--write" in __import__("sys").argv:
        require(not path.exists(), "refusing to overwrite certificate")
        path.write_bytes(canonical(result) + b"\n")
    else:
        require(canonical(result) == canonical(json.loads(path.read_bytes())), "frozen certificate")
    print(result["status"])
    for orientation, row in result["orientations"].items():
        print(orientation, "helper", result["selection"]["helper"], "incremental_real",
              row["incremental_delta_real"], "complex", row["candidate_invoice"]["complex_primitives"],
              "saved_vs_original", row["total_saving_complex_vs_original"],
              "columns", row["formal_endpoint"]["formal_input_columns"])


if __name__ == "__main__":
    main()
