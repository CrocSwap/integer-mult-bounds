#!/usr/bin/env python3
"""Replay reordered JP8 macros through the unchanged pinned native checkers."""

import argparse
import copy
import gzip
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
MODULE_SPEC = importlib.util.spec_from_file_location("jp8_batching_verify", HERE / "verify.py")
VERIFY = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(VERIFY)
require = VERIFY.require


def validate_blocks(ops, blocks):
    order = [index for block in blocks for index in block["original_indices"]]
    require(sorted(order) == list(range(len(ops))), "block indices are not a permutation")
    require(len({tuple(block["source"]) for block in blocks}) == len(blocks), "repeated source group")
    for block in blocks:
        require(all(ops[index][2] == block["source"] for index in block["original_indices"]),
                "block contains another source")
    return order


def run_inherited(script, output):
    # -E ignores PYTHONOPTIMIZE, and no -O is forwarded even if this driver
    # was launched with it. Check the child interpreter before every audit.
    subprocess.run([sys.executable, "-E", "-B", "-c",
                    "import sys; assert __debug__ and sys.flags.optimize == 0"], check=True)
    completed = subprocess.run([sys.executable, "-E", "-B", str(script), str(output)],
                               capture_output=True, text=True)
    (output / (script.stem + ".log")).write_text(completed.stdout + completed.stderr)
    require(completed.returncode == 0, "inherited checker failed; see " + str(output / (script.stem + ".log")))
    print(completed.stdout, end="", flush=True)


def run(output):
    output = output.expanduser().resolve()
    require(not output.exists(), "output directory already exists; refusing to overwrite")
    require(not output.is_relative_to(HERE), "output must be scratch outside this package")
    word, programs, _, selected_checks = VERIFY.inputs()
    candidates = VERIFY.read_json(HERE / "CANDIDATE.json")
    expected = VERIFY.read_json(HERE / "EXPECTED.json")
    orders = {}
    bounds = {}
    for name in ("forward", "backward"):
        start, stop, ops = VERIFY.panel(word, programs[name], name == "backward")
        candidate, blocks = VERIFY.construct(ops)
        require(candidate == candidates[name], "candidate certificate mismatch")
        require(blocks == expected["orientations"][name]["blocks"], "block certificate mismatch")
        VERIFY.check_panel(ops, candidate)
        orders[name] = validate_blocks(ops, blocks)
        bounds[name] = (start, stop)

    touched = {reg for gate in word["compensation"] for reg in gate[1:3]}
    wrapped = {r for r in range(2 * word["v"], 2 * word["v"] + word["R"])
               if word["start"][r] != 0 or word["final"][r] != 1}
    require(word["frames"][0] == [], "frame zero is not empty")
    require(all(word["start"][r] == 0 for r in touched), "nonzero entrance frame")
    require(not touched & wrapped, "compensation touches a residual-wrapped register")

    reordered = copy.deepcopy(word)
    reordered["compensation"] = [word["compensation"][i] for i in orders["forward"]]
    require({k: v for k, v in reordered.items() if k != "compensation"}
            == {k: v for k, v in word.items() if k != "compensation"}, "non-panel word changed")
    output.mkdir(parents=True)
    (output / "CANONICAL-WORD.json.gz").write_bytes(
        gzip.compress(VERIFY.canonical(reordered), mtime=0))

    code = VERIFY.ROOT / "research/complex-k492-owner-repair/code"
    for script in ("hpe_emit_local.py", "hpe_audit_local.py"):
        run_inherited(code / script, output)

    emitted = VERIFY.read_json(output / "LOCAL-PROGRAMS.json.gz")
    checks = VERIFY.read_json(output / "LOCAL-CHECKS.json")
    audit = VERIFY.read_json(output / "INDEPENDENT-LOCAL-REPLAY.json")
    require(audit["status"] == "PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY",
            "native audit did not pass")
    require(len(audit["negative_controls_rejected"]) == 25, "native control count changed")
    receipt = {
        "status": "PASS_UNCHANGED_NATIVE_COMPENSATION_REPLAY",
        "source_pins_semantic_sha256": VERIFY.digest(VERIFY.read_json(HERE / "SOURCES.json")),
        "input_canonical_semantic_sha256": VERIFY.digest(word),
        "reordered_canonical_semantic_sha256": VERIFY.digest(reordered),
        "compensation_additions": len(word["compensation"]),
        "forward_permutation_sha256": VERIFY.digest(orders["forward"]),
        "independent_backward_permutation_sha256": VERIFY.digest(orders["backward"]),
        "native_backward_uses_forward_permutation": True,
        "primitive_backward_permutation_differs": orders["forward"] != orders["backward"],
        "all_compensation_registers_at_frame_zero": True,
        "compensation_touches_no_residual_wrappers": True,
        "child_assertions_enabled": True,
        "orientations": {},
        "native_controls_rejected": audit["negative_controls_rejected"],
        "scope": (
            "Unchanged pinned emitter and native scalar/frame/wrapper checker on the "
            "forward-reordered canonical compensation. Native backward macros retain "
            "the dual of this forward order; the candidate backward primitive program "
            "uses its separately checked source permutation of the same commuting panel. "
            "This does not admit the primitive lowering into a global invoice."
        ),
    }
    for name in ("forward", "backward"):
        start, stop = bounds[name]
        require(checks[name]["sha256"] == VERIFY.digest(emitted[name]), "native semantic program binding")
        require(emitted[name][:start] == programs[name][:start]
                and emitted[name][stop:] == programs[name][stop:], "non-panel native event changed")
        native_panel = emitted[name][start:stop]
        old_panel = programs[name][start:stop]
        require(native_panel == [old_panel[i] for i in orders["forward"]], "native permutation changed")
        require(Counter(map(VERIFY.digest, native_panel)) == Counter(map(VERIFY.digest, old_panel)),
                "native panel multiset changed")
        for field in ("events", "scalar_macros", "real_component_primitive_bound", "paid_profile",
                      "all_columns", "private_centers_cleared",
                      "private_coefficient_stream_cleared_after_each_macro"):
            require(checks[name][field] == selected_checks[name][field], "native bound changed: " + field)
        require(audit["local"][name]["all_exact_columns"] == VERIFY.N, "native column count")
        require(audit["local"][name]["private_work_erased"], "native work was not erased")
        require(audit["local"][name]["prefix_l1_upper"]
                == expected["orientations"][name]["before"]["prefix_l1_upper"], "native prefix changed")
        receipt["orientations"][name] = {
            "program_semantic_sha256": VERIFY.digest(emitted[name]),
            "nonpanel_events_sha256": VERIFY.digest(emitted[name][:start] + emitted[name][stop:]),
            "panel_events": [start, stop],
            "macro_checks": checks[name],
            "native_replay": audit["local"][name],
            "paid_profile": audit["paid_profiles"][name],
        }
    (output / "NATIVE.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("PASS_UNCHANGED_NATIVE_COMPENSATION_REPLAY columns=716 controls=25", flush=True)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path,
                        help="new scratch directory outside this package; never overwritten")
    args = parser.parse_args()
    run(args.output)


if __name__ == "__main__":
    main()
