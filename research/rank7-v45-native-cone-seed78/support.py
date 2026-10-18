# SPDX-License-Identifier: Apache-2.0
"""Bounded authenticated source/artifact I/O for the opt-in audit.

Substantial OpenAI Codex assistance. Frozen producer code executes only after
source authentication, in fresh temporary tool paths with one numeric thread.
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
ENGINE = "research/two-sided-helper-extraction/vendor/fastnative/vendor/native/new/code/borrow/"
KERNEL = "research/frontier1094-recipes-exact-seed76/clifford.py"
RECEIPT = "research/rank7-joint-endframes/evidence/FULL-NATIVE-RECEIPT.json"
TOOLS = ("bw_transport.py", "bw_emit.py", "bw_adapters.py", "bw_gauss.py", "bw_phases.py", "vendor/clifford/clifford_exact.py")
WORDS = {tag: "research/rank7-joint-endframes/data/WORD-" + tag + ".json.gz" for tag in ("base", "extra")}
INPUTS = {ENGINE + f for f in TOOLS} | {KERNEL, RECEIPT, *WORDS.values()}
MAX_BYTES = 16 * 1024 * 1024


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), "duplicate JSON key")
    return result


def read_bytes(path):
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    require(len(raw) <= MAX_BYTES, "source byte capacity")
    return raw


def read(path):
    if path.suffix == ".gz":
        with gzip.open(path, "rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
        require(len(raw) <= MAX_BYTES, "decoded artifact capacity")
    else:
        raw = read_bytes(path)
    return json.loads(raw, object_pairs_hook=unique)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(raw, name, filename):
    require(len(raw) <= MAX_BYTES, "module source capacity")
    module = types.ModuleType(name)
    module.__file__ = str(filename)
    sys.modules[name] = module
    exec(compile(raw, str(filename), "exec"), module.__dict__)
    return module


def inputs():
    rows = read(PACKAGE / "SOURCES.json")["files"]
    require(len(rows) <= 16, "source inventory capacity")
    pins = {r["path"]: r["sha256"] for r in rows if r["usage"] == "input"}
    require(set(pins) == INPUTS, "exact source input closure")
    result = {}
    for name, digest in pins.items():
        raw = read_bytes(ROOT / name)
        require(sha(raw) == digest, "source hash mismatch: " + name)
        result[name] = raw
    return result


def modules(blobs):
    result = {}
    for name in ("source", "cone", "oracle", "native", "audit", "graph_controls", "controls"):
        file = PACKAGE / (name + ".py")
        result[name] = load(read_bytes(file), "v45_closed_" + name, file)
    result["kernel"] = load(blobs[KERNEL], "v45_closed_retained_kernel", ROOT / KERNEL)
    return result


def generate(blobs, tag, work, progress=None):
    require(tag in WORDS, "frozen provider name")
    tools = work / "tools"
    for name in TOOLS:
        path = tools / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blobs[ENGINE + name])
    word = work / "WORD.json.gz"
    word.write_bytes(blobs[WORDS[tag]])
    output = work / "local"
    commands = [("bw_transport.py", [word, output]), ("bw_emit.py", [output]),
                ("bw_adapters.py", [output / "CANONICAL-WORD.json.gz", output / "RESIDUAL-ADAPTERS.json", work / "wrappers.json"]),
                ("bw_phases.py", [output])]
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONOPTIMIZE", None)
    for script, args in commands:
        if progress is not None:
            progress({"source_stage": script, "provider": tag})
        result = subprocess.run([sys.executable, "-I", "-B", str(tools / script), *map(str, args)],
                                env=env, capture_output=True, timeout=300, check=False)
        require(result.returncode == 0, "source stage " + script + ": " + result.stderr.decode(errors="replace")[-2000:])
    return output


def artifacts(blobs, tag, run):
    retained = json.loads(blobs[RECEIPT])["providers"][tag]["complete_native_files"]
    for name in ("LOCAL-CHECKS.json", "RESIDUAL-ADAPTERS.json", "CLIFFORD-RECIPES.json"):
        require(sha(read_bytes(run / name)) == retained["local/" + name], "retained artifact binding: " + name)
    names = {"canonical_word": "CANONICAL-WORD.json.gz", "programs": "LOCAL-PROGRAMS.json.gz",
             "recipes": "CLIFFORD-RECIPES.json", "adapters": "RESIDUAL-ADAPTERS.json"}
    data = {key: read(run / name) for key, name in names.items()}
    checks = read(run / "LOCAL-CHECKS.json")
    for orientation, program in data["programs"].items():
        raw = json.dumps(program, sort_keys=True, separators=(",", ":")).encode()
        require(sha(raw) == checks[orientation]["sha256"], "actual program / retained digest")
    data["word"] = json.loads(gzip.decompress(blobs[WORDS[tag]]), object_pairs_hook=unique)
    return data
