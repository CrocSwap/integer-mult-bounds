#!/usr/bin/env python3
"""Verify source pins and audit the P104 tangent-to-orbit inference."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "research/seed38-p104-orbit-regularity-audit"
MANIFEST = ROOT / PACKAGE / "SOURCES.json"


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL " + message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git_blob(data):
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def checked_run(argv):
    return subprocess.run(argv, cwd=ROOT, check=True, capture_output=True, text=True)


def verify_pins(manifest):
    for row in manifest["files"]:
        proc = subprocess.run(["git", "show", manifest["base_commit"] + ":" + row["path"]],
                              cwd=ROOT, check=True, capture_output=True)
        data = proc.stdout
        require(sha256(data) == row["sha256"], "base SHA-256 mismatch: " + row["path"])
        require(git_blob(data) == row["git_blob"], "base Git blob mismatch: " + row["path"])
    for source in manifest["external_sources"]:
        require(len(source["commit"]) == 40, "external source commit must be exact")
        for row in source["files"]:
            data = (ROOT / row["vendored_path"]).read_bytes()
            require(sha256(data) == row["sha256"], "vendored SHA-256 mismatch: " + row["vendored_path"])
            require(git_blob(data) == row["git_blob"], "vendored Git blob mismatch: " + row["vendored_path"])


def load_source_checker():
    path = ROOT / PACKAGE / "vendor/pr1292/verify.py"
    spec = importlib.util.spec_from_file_location("p1292_exact_checker", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def exhaustive_p104_kernel(module):
    rng = module.random.Random(20261013)
    frames = module.all_frames()
    require(len(frames) == 2025, "expected 2025 root frames")
    F0 = min(frames, key=sorted)
    nframes, disjoint, classes, _gens, ok = module.stabilizer_orbits(frames, F0, rng)
    require(nframes == 2025 and len(disjoint) == 1260 and len(classes) == 3 and ok,
            "pinned frame-pair class construction failed")
    counts = []
    for class_index, cls in enumerate(classes):
        F1 = min(cls, key=sorted)
        live = [i for i in range(module.N) if i not in F0 and i not in F1]
        rows, bad = module.masked_system(live)
        require(rows is not None and bad is None and len(live) == 104,
                "invalid P104 representative " + str(class_index))
        vectors = module.known_kernel(live)
        require(len(vectors) == 64 + len(live), "unexpected gauge/torus generator count")
        for vector_index, vector in enumerate(vectors):
            for row_index, row in enumerate(rows):
                value = sum(vector.get(k, 0) * x for k, x in row.items()) % module.P
                require(value == 0,
                        f"P104 class {class_index} generator {vector_index} fails row {row_index}")
        span = module.rank_mod_sparse(vectors)
        require(span == 64 + len(live) - 1 == 167,
                "P104 gauge/torus span dimension mismatch")
        counts.append((class_index, len(rows), len(vectors), span))
    return counts


def main():
    manifest = json.loads(MANIFEST.read_text())
    verify_pins(manifest)
    print("PASS_SOURCE_PINS: base and PR1292 vendor files", flush=True)

    checker = ROOT / PACKAGE / "vendor/pr1292/verify.py"
    proc = checked_run([sys.executable, "-I", "-B", str(checker)])
    print(proc.stdout, end="", flush=True)
    require("PASS_P104_MASKED_LOCAL_RIGIDITY:" in proc.stdout,
            "pinned PR1292 verifier did not reach its final marker")
    for expected in ("P104.class0(896 frames)", "P104.class1(336 frames)", "P104.class2(28 frames)"):
        require(expected in proc.stdout, "missing certificate class " + expected)
    require("PASS D.control" in proc.stdout, "negative control was not exercised")

    module = load_source_checker()
    counts = exhaustive_p104_kernel(module)
    require(len(counts) == 3 and all(rows > 0 and generators == 168 and span == 167
                                     for _, rows, generators, span in counts),
            "incomplete all-generator P104 check")
    print("PASS_ALL_P104_KERNEL_GENERATORS: classes=3 equations=" +
          ",".join(str(rows) for _, rows, _, _ in counts) +
          " generators=168/class span=167 mod=2^31-1", flush=True)
    print("PASS_P104_LOCAL_ORBIT_REGULARITY: tangent_dim=103 orbit_dim=103 classes=3 local_only no_new_kappa")


if __name__ == "__main__":
    main()
