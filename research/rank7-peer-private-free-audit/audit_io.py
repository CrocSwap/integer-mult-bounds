"""Authenticated retained inputs and fresh, bounded native artifact production.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PRIOR = "research/rank7-v45-native-cone-seed78/"
ENGINE = "research/two-sided-helper-extraction/vendor/fastnative/vendor/native/new/code/borrow/"
KERNEL = "research/frontier1094-recipes-exact-seed76/clifford.py"
WORD = "research/rank7-joint-endframes/data/WORD-{}.json.gz"
RECEIPT = "research/rank7-joint-endframes/evidence/FULL-NATIVE-RECEIPT.json"
TOOLS = ("bw_transport.py", "bw_emit.py", "bw_adapters.py", "bw_gauss.py",
         "bw_phases.py", "vendor/clifford/clifford_exact.py")
LIMIT = 64 * 1024 * 1024


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unique(pairs):
    out = dict(pairs)
    require(len(out) == len(pairs), "duplicate JSON key")
    return out


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rb") as stream:
        raw = stream.read(LIMIT + 1)
    require(len(raw) <= LIMIT, "bounded JSON input")
    return json.loads(raw, object_pairs_hook=unique)


def inputs():
    blobs = {}
    for row in read(PACKAGE / "SOURCES.json")["files"]:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        require(path.stat().st_size <= LIMIT, "bounded source input")
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash: " + row["path"])
        blobs[row["path"]] = raw
    return blobs


def load(blobs, path, name):
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / path)
    sys.modules[name] = module
    exec(compile(blobs[path], str(ROOT / path), "exec"), module.__dict__)
    return module


def generate(blobs, provider, work, phases=True):
    """Run retained producer code, never its scientific acceptance as our result."""
    for name in TOOLS:
        target = work / "tools" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blobs[ENGINE + name])
    word = work / "WORD.json.gz"
    word.write_bytes(blobs[WORD.format(provider)])
    output = work / "local"
    commands = [("bw_transport.py", [word, output]), ("bw_emit.py", [output])]
    if phases:
        commands += [("bw_adapters.py", [output / "CANONICAL-WORD.json.gz",
                         output / "RESIDUAL-ADAPTERS.json", work / "wrappers.json"]),
                     ("bw_phases.py", [output])]
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    env.pop("PYTHONOPTIMIZE", None)
    for script, arguments in commands:
        print("source stage " + provider + " " + script, file=sys.stderr, flush=True)
        p = subprocess.run([sys.executable, "-I", "-B", str(work / "tools" / script),
                            *map(str, arguments)], env=env, capture_output=True, timeout=300)
        require(p.returncode == 0, script + ": " + p.stderr.decode(errors="replace")[-2000:])
    return output


def artifacts(blobs, provider, run, phases=True):
    native_receipt = json.loads(blobs[RECEIPT])["providers"][provider]["complete_native_files"]
    names = ["LOCAL-CHECKS.json"]
    if phases:
        names += ["RESIDUAL-ADAPTERS.json", "CLIFFORD-RECIPES.json"]
    for name in names:
        require(hashlib.sha256((run / name).read_bytes()).hexdigest() == native_receipt["local/" + name],
                "retained producer artifact: " + name)
    programs = read(run / "LOCAL-PROGRAMS.json.gz")
    checks = read(run / "LOCAL-CHECKS.json")
    require(set(programs) == {"forward", "backward"}, "both orientations")
    for orientation, events in programs.items():
        require(digest(events) == checks[orientation]["sha256"], "complete emitted stream digest")
    return {
        "word": json.loads(gzip.decompress(blobs[WORD.format(provider)])),
        "canonical": read(run / "CANONICAL-WORD.json.gz"), "programs": programs,
        "recipes": read(run / "CLIFFORD-RECIPES.json") if phases else None,
        "adapters": read(run / "RESIDUAL-ADAPTERS.json") if phases else None,
    }
