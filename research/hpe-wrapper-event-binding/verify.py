#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bind actual emitted HPE wrappers to retained Lean literals; no new theorem."""
import argparse
import ast
import gzip
import hashlib
import json
import re
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load_module(path, name):
    # Execute these explicit local sources, never an mtime-valid .pyc instead.
    with path.open("rb") as stream:
        source = stream.read(1024 * 1024 + 1)
    if len(source) > 1024 * 1024:
        raise ValueError("local Python module exceeds 1 MiB limit")
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


binding = load_module(HERE / "binding.py", "hpe_event_binding")
require = binding.require
same = binding.same
MAX_BYTES = 32 * 1024 * 1024
LEAN = ROOT / "research/hyperplane-end-lean/HyperplaneEnd/Exact.lean"


def unique_object(items):
    result = {}
    for key, value in items:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    require(len(data) <= MAX_BYTES, "artifact exceeds 32 MiB decoded limit")
    return json.loads(data, object_pairs_hook=unique_object)


def sources():
    rows = read(HERE / "SOURCES.json")["files"]
    result = {}
    for row in rows:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            with path.open("rb") as stream:
                data = stream.read(MAX_BYTES + 1)
            require(len(data) <= MAX_BYTES, "source exceeds 32 MiB limit: " + row["path"])
            digest = hashlib.sha256(data).hexdigest()
            require(digest == row["sha256"], "source hash changed: " + row["path"])
            result[row["path"]] = digest
    return result


def literal_pairs():
    # Only parse the data records. No Lean evaluation or theorem instantiation.
    text = LEAN.read_text(encoding="utf-8")
    pairs = {}
    fields = ("quadratic_rows", "linear_Z4", "matrix_rows", "offset", "phase")
    for n in (1, 2, 3):
        matches = re.findall(rf"^def pair{n} : Pair := (.*?)\n\n", text, re.S | re.M)
        require(len(matches) == 1, "missing or duplicate Lean pair literal")
        entrance, terminal, left, right = ast.literal_eval(
            matches[0].replace("⟨", "[").replace("⟩", "]"))
        key = tuple(entrance), tuple(terminal)
        require(key not in pairs, "duplicate Lean frame pair")
        pairs[key] = {"left": dict(zip(fields, left, strict=True)),
                      "right": dict(zip(fields, right, strict=True))}
    return pairs


def fixture_module():
    # The only dynamic target is the pinned producer harness. Its audit is not called.
    path = ROOT / "research/k8-hpe450-binding/verify.py"
    return load_module(path, "hpe_k8_producer")


def audit_run(run):
    word = read(run / "CANONICAL-WORD.json.gz")
    programs = read(run / "LOCAL-PROGRAMS.json.gz")
    adapters = read(run / "RESIDUAL-ADAPTERS.json")
    require(set(programs) == {"forward", "backward"}, "both local orientations required")
    pairs = literal_pairs()
    orientations = {name: binding.check(word, programs[name], adapters, pairs)
                    for name in ("forward", "backward")}
    artifacts = {name: hashlib.sha256(json.dumps(data, sort_keys=True,
                 separators=(",", ":"), allow_nan=False).encode()).hexdigest()
                 for name, data in (("canonical_word", word), ("programs", programs),
                                    ("adapters", adapters))}
    return orientations, artifacts


def compute(run=None):
    inputs = sources()
    if run is None:
        selected = read(ROOT / "research/community-frontier1094-audit/SELECTED-SOURCE.json")
        slot = "research/gauge44-slots/construction/slots/SLOT-PINS-k8.json"
        require(selected["files"][slot] == inputs[slot], "selected slot source mismatch")
        with tempfile.TemporaryDirectory(prefix="hpe-event-binding-") as tmp:
            run = Path(tmp) / "local"
            producer = fixture_module()
            # Re-read the serialized files instead of trusting returned Python objects.
            producer.rebuild(run)
            orientations, artifacts = audit_run(run)
    else:
        orientations, artifacts = audit_run(run)
    require(sources() == inputs, "sources changed during replay")
    return {"status": "PASS_HPE_WRAPPER_EVENT_BINDING", "input_sha256": inputs,
            "canonical_json_sha256": artifacts, "orientations": orientations,
            "scope": "Actual pre/post event references, literal recipe fields and wrapper enclosure "
                     "for every non-cold HPE helper. No scalar endpoint, native lowering, "
                     "cold-helper, hosting, all-size, cost or analytic admission."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, help="check an existing emitted run instead of regenerating k8")
    parser.add_argument("--write-result", type=Path, help="create a new receipt; never overwrite")
    args = parser.parse_args()
    result = compute(args.run)
    if args.write_result:
        with args.write_result.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    elif args.run is None:
        require(same(result, read(HERE / "RESULT.json")), "receipt mismatch")
    for name, row in result["orientations"].items():
        print(f'{name}: {row["helpers"]} non-cold HPE helpers, {row["events"]} events')
    print(result["status"])


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, RecursionError) as exc:
        raise SystemExit("FAIL: " + str(exc)) from None
