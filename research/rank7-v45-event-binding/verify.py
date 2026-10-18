#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Regenerate genuine native events and bind one cold helper's direct operations."""
import argparse
import gzip
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import types
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ENGINE = "research/two-sided-helper-extraction/vendor/fastnative/vendor/native/new/code/borrow/"
KERNEL = "research/frontier1094-recipes-exact-seed76/clifford.py"
RECEIPT = "research/rank7-joint-endframes/evidence/FULL-NATIVE-RECEIPT.json"
WORDS = {tag: f"research/rank7-joint-endframes/data/WORD-{tag}.json.gz"
         for tag in ("base", "extra")}
TOOLS = ("bw_transport.py", "bw_emit.py", "bw_adapters.py", "bw_gauss.py",
         "vendor/clifford/clifford_exact.py")
INPUTS = set(WORDS.values()) | {ENGINE + n for n in TOOLS} | {KERNEL, RECEIPT}
MAX_BYTES = 16 * 1024 * 1024


def load(raw, name):
    if len(raw) > MAX_BYTES:
        raise ValueError("module byte capacity")
    module = types.ModuleType(name)
    sys.modules[name] = module
    exec(compile(raw, name, "exec"), module.__dict__)
    return module


events = load((PACKAGE / "events.py").read_bytes(), "v45_event_inventory")
native = load((PACKAGE / "native.py").read_bytes(), "v45_native_binding")
require = events.require


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), "duplicate JSON key")
    return result


def read(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    require(len(raw) <= MAX_BYTES, "decoded artifact capacity")
    return json.loads(raw, object_pairs_hook=unique)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def sources():
    rows = read(PACKAGE / "SOURCES.json")["files"]
    require(len(rows) <= 16, "source inventory capacity")
    pins = {r["path"]: r["sha256"] for r in rows if r["usage"] == "input"}
    require(set(pins) == INPUTS, "exact live source inventory")
    blobs = {}
    for name, digest in pins.items():
        with (ROOT / name).open("rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
        require(len(raw) <= MAX_BYTES and sha(raw) == digest, "input SHA256 " + name)
        blobs[name] = raw
    return blobs


def generate(blobs, tag, work):
    tools = work / "tools"
    for name in TOOLS:
        target = tools / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blobs[ENGINE + name])
    word = work / "WORD.json.gz"
    word.write_bytes(blobs[WORDS[tag]])
    output = work / "local"
    commands = [("bw_transport.py", [word, output]), ("bw_emit.py", [output]),
                ("bw_adapters.py", [output / "CANONICAL-WORD.json.gz",
                                    output / "RESIDUAL-ADAPTERS.json", work / "wrappers.json"])]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
    env.pop("PYTHONOPTIMIZE", None)
    for script, args in commands:
        result = subprocess.run([sys.executable, "-I", "-B", str(tools / script),
                                 *map(str, args)], env=env, capture_output=True,
                                text=True, timeout=120, check=False)
        require(result.returncode == 0, script + " failed: " + result.stderr[-2000:])
    bind_receipt(blobs, tag, output)
    return output


def bind_receipt(blobs, tag, output):
    receipt = json.loads(blobs[RECEIPT])["providers"][tag]["complete_native_files"]
    # These uncompressed receipts bind exact program digests and wrapper bytes.
    for name in ("LOCAL-CHECKS.json", "RESIDUAL-ADAPTERS.json"):
        require(sha((output / name).read_bytes()) == receipt["local/" + name],
                "PR2979 native receipt " + name)


def recipes(blobs, adapters, binding):
    compiler = load(blobs[ENGINE + TOOLS[-1]], "v45_candidate_compiler")
    kernel = load(blobs[KERNEL], "v45_independent_kernel")
    key = binding["recipe_key"]
    recipe = adapters["recipes"][key]
    require(recipe["frame"] == 0 and
            events.same(recipe["terminal_vectors"], events.W), "selected adapter record")
    wrapper = native.wrappers(kernel, recipe, events.W, require)
    climbs = []
    for phase, clock, row in binding["inventory"]:
        if row[0] != "climb":
            continue
        old, new = row[1:3]
        op = compiler.canonical_frame(9, tuple(old)).adjoint().then(
            compiler.canonical_frame(9, tuple(new)))
        candidate, _compiled = compiler.lower_child(op)
        candidate = json.loads(json.dumps(candidate))
        native.check(kernel, candidate, old, new, require)
        climbs.append({"phase": phase, "scalar_clock": clock, "old": old, "new": new,
                       "rank": row[3], "recipe": candidate})
    require([c["rank"] for c in climbs] == [1, 1, 1, 1, 2, 1], "six actual climbs")
    return {"selected_wrapper": recipe, "wrapper_semantics": wrapper, "climbs": climbs}


def audit(blobs, tag, run):
    word = json.loads(gzip.decompress(blobs[WORDS[tag]]))
    canonical = read(run / "CANONICAL-WORD.json.gz")
    programs = read(run / "LOCAL-PROGRAMS.json.gz")
    adapters = read(run / "RESIDUAL-ADAPTERS.json")
    require(set(programs) == {"forward", "backward"}, "both orientations")
    bindings = {name: events.check(word, canonical, programs[name], name == "backward")
                for name in ("forward", "backward")}
    return {"orientations": bindings,
            "native": recipes(blobs, adapters, bindings["forward"]),
            "canonical_json_sha256": {name: sha(json.dumps(value, sort_keys=True,
                 separators=(",", ":")).encode()) for name, value in
                 (("word", canonical), ("programs", programs), ("adapters", adapters))}}


def compute(run=None):
    blobs = sources()
    providers = {}
    for tag in ("base", "extra"):
        if run is None:
            with tempfile.TemporaryDirectory(prefix="v45-event-") as tmp:
                output = generate(blobs, tag, Path(tmp))
                providers[tag] = audit(blobs, tag, output)
        else:
            providers[tag] = audit(blobs, tag, run / tag)
    require(sources() == blobs, "source changed during replay")
    inventories = {}
    for provider in providers.values():
        for binding in provider["orientations"].values():
            inventory = binding.pop("inventory")
            digest = sha(json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode())
            inventories[digest] = inventory
            binding["inventory_sha256"] = digest
    status = "PASS_V45_DIRECT_EVENT_BINDING" if run is None else "PASS_V45_SUPPLIED_DIRECT_EVENT_CHECK"
    return {"status": status, "schema_version": 1,
            "native_receipt_bound": run is None,
            "input_sha256": {name: sha(raw) for name, raw in blobs.items()},
            "providers": providers, "inventories": inventories,
            "scope": "Direct helper249/private953 events and selected inverse wrappers; "
                     "other registers' native/warp dependencies and physical admission remain open."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--run", type=Path, help="existing base/extra emitted directories")
    args = parser.parse_args()
    result = compute(args.run)
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        if args.run is None:
            require(events.same(result, read(PACKAGE / "RESULT.json")), "receipt mismatch")
        print(result["status"])


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, IndexError,
            subprocess.TimeoutExpired) as exc:
        raise SystemExit("FAIL: " + str(exc)) from None
