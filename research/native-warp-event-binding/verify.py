#!/usr/bin/env python3
"""Source-bound warp-event audit and controls for issue #4571.

Apache-2.0. Prepared by 1337isnot1337 with substantial OpenAI Codex assistance.
The original report is by jwr404; canonical-map audit credit is retained in README.
"""
from collections import Counter
from copy import deepcopy
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from warp_frames import WarpFrameAudit, audit, need, read_json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CORE = ROOT / "research/kappa-native-resume/native-source/rebased-core/converted"
TAGS = ("THREE-base", "THREE-extra", "FOUR-base", "FOUR-extra")


def authenticate():
    manifest = read_json(HERE / "SOURCES.json")
    for row in manifest["files"]:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            need(hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
                 "Changed live source: " + row["path"])


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rejected(action, expected):
    try:
        action()
    except ValueError as error:
        need(expected in str(error), "Control failed for an unintended reason: " + str(error))
        return str(error)
    raise ValueError("Invalid warp unexpectedly accepted: " + expected)


def selected_word():
    # Authenticate first, then import retained modules only in an isolated child
    # with an empty bytecode-cache namespace. No native phase replay is launched.
    code = ("import json,sys;sys.path.insert(0,sys.argv[1]);import native_joint;"
            "c,p,*_=native_joint.construct();print(json.dumps({'canonical':c,'programs':p}))")
    with tempfile.TemporaryDirectory(prefix="warp-constructor-cache-") as cache:
        run = subprocess.run(
            [sys.executable, "-I", "-B", "-X", "pycache_prefix=" + cache,
             "-c", code, str(ROOT / "research/joint-helper-lattice")],
            capture_output=True, text=True, check=True, timeout=120)
    result = json.loads(run.stdout)
    return result["canonical"], result["programs"]


def signed_controls():
    # G has order three: e0 -> e1 -> e2 -> e0. Thus testing its sign is
    # meaningful, unlike a sign control built from an involutive permutation.
    canonical = {"h": 9, "frames": [[], [1], [2], [4], [1, 2]],
                 "warps": [{"op": 1, "G_columns": [2, 4, 1, 8, 16, 32, 64, 128, 256],
                            "from_frame": 1, "to_frame": 2}]}
    checker = WarpFrameAudit(canonical)
    checker.check(1, 1, 2)
    checker.check(-1, 2, 1)
    controls = {}
    controls["wrong_positive_sign"] = rejected(lambda: checker.check(1, 2, 1), "G does not carry")
    controls["wrong_negative_sign"] = rejected(lambda: checker.check(-1, 1, 2), "G does not carry")
    controls["same_dimension_wrong_subspace"] = rejected(lambda: checker.check(1, 1, 3), "G does not carry")
    for label, operator, old, new, message in (
        ("zero_operator", 0, 1, 2, "unknown or zero"),
        ("unknown_operator", 2, 1, 2, "unknown or zero"),
        ("negative_frame", 1, -1, 2, "invalid frame ID"),
        ("missing_frame", 1, 1, 99, "invalid frame ID"),
        ("boolean_operator", True, 1, 2, "unknown or zero"),
    ):
        controls[label] = rejected(lambda: checker.check(operator, old, new), message)
    bad = deepcopy(canonical)
    bad["warps"][0]["G_columns"][1] = bad["warps"][0]["G_columns"][0]
    controls["singular_G"] = rejected(lambda: WarpFrameAudit(bad), "Singular G")
    bad = deepcopy(canonical)
    bad["warps"].append(deepcopy(bad["warps"][0]))
    controls["duplicate_operator"] = rejected(lambda: WarpFrameAudit(bad), "distinct positive")
    bad = deepcopy(canonical)
    bad["frames"][4] = [1, 1]
    controls["dependent_basis"] = rejected(lambda: WarpFrameAudit(bad), "Dependent frame basis")
    bad = deepcopy(canonical)
    bad["warps"][0]["to_frame"] = 3
    controls["wrong_canonical_transport"] = rejected(lambda: WarpFrameAudit(bad), "G does not carry")
    controls["truncated_event"] = rejected(
        lambda: checker.program([["warp", ["L", 0], 1, 1]]), "invalid warp event shape")
    # Relabeling/rebasing a space is allowed; equality concerns spans, not lists.
    equivalent = {"h": 9, "frames": [[1, 2], [3, 1]],
                  "warps": [{"op": 1, "G_columns": [1 << i for i in range(9)],
                             "from_frame": 0, "to_frame": 1}]}
    WarpFrameAudit(equivalent).check(-1, 1, 0)
    return controls


def legacy_counterexample(canonical, programs):
    legacy = load(ROOT / "research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py",
                  "frozen_buffer_replay")
    result = {}
    for direction, program in programs.items():
        rebound = deepcopy(canonical)
        rebound["local_profile"] = dict(Counter(e[-1] for e in program
                                               if e[0] in ("climb", "center")))
        original = legacy.replay(program, rebound, [], direction == "backward", False)
        mutant = deepcopy(program)
        need(mutant[3] == ["warp", ["L", 273], -59, 0, 0] and
             mutant[4] == ["warp", ["L", 273], 59, 0, 0], "Pinned issue #4571 probe")
        mutant[3][4] = 1
        mutant[4][3] = 1
        accepted = legacy.replay(mutant, rebound, [], direction == "backward", False)
        need(original["free_warp_operator_endpoint_matches"] and
             accepted["free_warp_operator_endpoint_matches"], "Legacy endpoint control")
        need(original["paid_profile"] == accepted["paid_profile"], "Legacy profile unchanged")
        error = rejected(lambda: audit(canonical, {direction: mutant}), "G does not carry")
        result[direction] = {"legacy_original_accepted": True, "legacy_mutant_accepted": True,
                             "paid_profile_unchanged": accepted["paid_profile"],
                             "new_audit_rejection": error}
    return result


def run():
    authenticate()
    fixtures = {}
    for tag in TAGS:
        canonical = read_json(CORE / (tag + "-CANONICAL.json.gz"))
        programs = read_json(CORE / (tag + "-NATIVE-WORD.json.gz"))
        fixtures[tag] = audit(canonical, programs)
    canonical, programs = selected_word()
    fixtures["selected-PR4470"] = audit(canonical, programs)
    candidate = read_json(ROOT / "research/pr4610-warp-substitution-check/PR4610-ACTUAL-WORD.json.gz")
    fixtures["archived-PR4610"] = audit(candidate["canonical"], candidate["programs"])
    need(all(row["operators"] == 72 and row["warp_events"] == {"forward": 240, "backward": 240}
             for row in fixtures.values()), "Pinned fixture coverage")
    return {"status": "PASS_NATIVE_WARP_EVENT_BINDING", "fixtures": fixtures,
            "total_warp_events": sum(sum(row["warp_events"].values()) for row in fixtures.values()),
            "rejection_controls": signed_controls(),
            "issue_4571": legacy_counterexample(canonical, programs),
            "new_kappa_claimed": False,
            "limits": ["No frozen verifier changed or automatically guarded",
                       "No full Clifford phase, all-column, endpoint or paid-profile admission",
                       "Archived PR4610 transport acceptance is not supplier admission"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate the scoped JSON receipt")
    args = parser.parse_args()
    result = json.loads(json.dumps(run()))
    if args.write:
        (HERE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    expected = read_json(HERE / "RESULT.json")
    need(result == expected, "Deterministic warp-event audit receipt")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
