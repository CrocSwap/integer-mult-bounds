#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound concrete k8 label translation; Lean replay is check_lean.py."""
import argparse
import copy
import hashlib
import json
import runpy
import tempfile
from pathlib import Path

import generate
from translate import label, observe, require, translate

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREDECESSOR = "research/k8-hpe450-binding/verify.py"


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def source_check(root=ROOT):
    rows = read(HERE / "SOURCES.json")["files"]
    require(len(rows) <= 32, "source inventory bound")
    result = {}
    for row in rows:
        if row["usage"] != "input":
            continue
        path = (root / row["path"]).resolve()
        require(path.is_relative_to(root.resolve()), "source path")
        require(digest(path.read_bytes()) == row["sha256"], "source drift: " + row["path"])
        result[row["path"]] = row["sha256"]
    selected = read(root / "research/community-frontier1094-audit/SELECTED-SOURCE.json")
    slot = "research/gauge44-slots/construction/slots/SLOT-PINS-k8.json"
    require(selected["files"][slot] == result[slot], "selected slot binding")
    return result


def rebuild(out, root=ROOT):
    source_check(root)
    # run_path executes the authenticated .py bytes without using a .pyc cache.
    predecessor = runpy.run_path(str(root / PREDECESSOR))
    return predecessor["rebuild"](out, root)


def final_labels(c):
    result = []
    for r, frame in enumerate(c["final"]):
        wrapped = r >= 224 and (c["start"][r] != 0 or frame != 1)
        tag = "post" if 112 <= r < 224 else "done" if wrapped else None
        result.append(label(frame, tag, r))
    return result


def controls(c, original):
    cases = []
    source = next(i for i, e in enumerate(original) if e[:2] == ["adapter", "old_to_new"] and e[2] < 112)
    wrapper = next(i for i, e in enumerate(original) if e[:2] == ["residual_adapter", "pre"])
    private = [(i, e) for i, e in enumerate(original) if e[0] == "scalar" and e[1][0] == "copy"]
    copier = private[0][0] if private else next(
        i for i, e in enumerate(original) if e[0] == "scalar" and e[1][0] == "clear")
    climber = next(i for i, e in enumerate(original) if e[0] == "climb")
    cases.append(("drop_source_adapter", source, None))
    cases.append(("drop_pre_wrapper", wrapper, None))
    changed = copy.deepcopy(original[copier])
    changed[2] = (changed[2] + 1) % 1004
    cases.append(("wrong_copy_frame" if private else "wrong_private_clear_frame", copier, changed))
    changed = copy.deepcopy(original[climber])
    changed[-3] = (changed[-3] + 1) % 1004
    cases.append(("wrong_climb_source", climber, changed))
    changed = copy.deepcopy(original[wrapper])
    changed[4:] = [1]
    cases.append(("wrong_wrapper_terminal", wrapper, changed))
    rejected = []
    for name, index, replacement in cases:
        bad = copy.deepcopy(original)
        if replacement is None:
            bad.pop(index)
        else:
            bad[index] = replacement
        try:
            start, events, _ = translate(c, bad)
            observe(start, events)
        except ValueError as exc:
            rejected.append({"name": name, "reason": str(exc)})
        else:
            raise ValueError("accepted semantic control: " + name)
    return rejected


def formal_receipt_check(canonical, programs, directory):
    receipt = read(HERE / "KERNEL.json")
    require(receipt["status"] == "PASS_K8_LEAN_LABEL_KERNEL", "kernel receipt status")
    require(encoded(receipt["inputs"]) == encoded(source_check()), "kernel input binding")
    for field, path in (("checkpoint_sha256", "TreeCheckpoint.lean"),
                        ("generator_sha256", "generate.py"),
                        ("translation_sha256", "translate.py")):
        require(receipt[field] == digest((HERE / path).read_bytes()), "formal source drift: " + path)
    generated = {}
    for name in ("Forward", "Backward"):
        start, events, _ = translate(canonical, programs[name.lower()])
        for path in generate.emit(directory, name, start, events):
            generated[path.name] = digest(path.read_bytes())
    require(encoded(generated) == encoded(receipt["generated_sha256"]), "generated Lean source drift")
    return {"kernel_receipt_sha256": digest(encoded(receipt)),
            "generated_modules": len(generated), "fresh_lean_build": False}


def compute():
    inputs = source_check()
    with tempfile.TemporaryDirectory(prefix="k8-lean-label-") as temporary:
        c, programs, _, pins = rebuild(Path(temporary) / "local")
        results = {}
        for name in ("forward", "backward"):
            start, events, indices = translate(c, programs[name])
            final = observe(start, events)
            require(final[:704] == final_labels(c), "final local label boundary")
            counts = {kind: sum(e[0] == kind for e in events)
                      for kind in ("add", "scale", "copy", "clear", "relabel")}
            results[name] = {"serialized_events": len(programs[name]),
                             "semantic_events": len(events), "constructors": counts,
                             "translation_sha256": digest(encoded([start, events])),
                             "source_indices_sha256": digest(encoded(indices)),
                             "final_labels_sha256": digest(encoded(final)),
                             "private_final_labels": final[704:],
                             "controls": controls(c, programs[name])}
        formal = formal_receipt_check(c, programs, Path(temporary))
        require(source_check() == inputs, "inputs changed during replay")
    return {"status": "PASS_K8_LEAN_LABEL_TRANSLATION", "inputs": inputs,
            "canonical_sha256": pins["canonical_sha256"],
            "program_sha256": pins["program_sha256"], "orientations": results, "formal_binding": formal,
            "formal_replay": "check_lean.py --lake-project formal/lean",
            "scope": "Finite translation and label observation. Fresh Lean compilation is separate; "
                     "RecipesExact, scalar endpoints, physical hosting and supplier admission are not checked."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path)
    args = parser.parse_args()
    result = compute()
    if args.write_result:
        with args.write_result.open("x") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    else:
        require(encoded(result) == encoded(read(HERE / "RESULT.json")), "receipt mismatch")
    print(result["status"] + " orientations=2 semantic_events=49514 controls=10 no_new_kappa")


if __name__ == "__main__":
    main()
