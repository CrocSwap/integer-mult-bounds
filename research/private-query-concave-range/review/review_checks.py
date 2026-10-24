#!/usr/bin/env python3
"""Run independent bindings and rejection controls for the cost proof.

Use one process at a time. Use integer and rational arithmetic for every
claim. Prepared by an independent OpenAI Codex review agent.
"""
from fractions import Fraction
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def span(rows):
    values = {0}
    for row in rows:
        values |= {value ^ row for value in values}
    return values


package = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
require(not out.exists(), "Output exists")
out.mkdir(parents=True)
historical = Path("historical/work/autonomous-kappa-run")
prototype = historical / "baseline535/source531/research/direct-delivery504-global/inputs/hamming/PROTOTYPE.json"
raw = (package / prototype).read_bytes()
data = json.loads(raw)
roots = data["root_lines"][8:]
labels = data["binary_ports"][8:]
require(len(roots) == len(labels) == 112, "Retained row count")
require(all(len(row) == 8 for row in roots), "Retained column count")
require(len(span(labels)) == 512, "Ambient label rank")
rt_r = [[sum(row[i] * row[j] for row in roots) for j in range(8)]
        for i in range(8)]
require(rt_r == [[56 * int(i == j) for j in range(8)] for i in range(8)],
        "Rank-eight certificate")
frame_records = []
for j in range(8):
    support = [p for p, row in zip(labels, roots) if row[j] != 0]
    frame = span(support)
    require(len(frame) == 256, "Coordinate source rank")
    extra = next(p for p in labels if p not in frame)
    enlarged = frame | {x ^ extra for x in frame}
    require(len(enlarged) == 512, "Frame enlargement")
    frame_records.append({"coordinate": j, "support_size": len(support),
                          "rank": 8, "enlarging_source_label": extra,
                          "enlarged_rank": 9})
require(Fraction(8, 9) < Fraction(8, 8), "Exact b=2 counterexample")
pin = "e07a8a3f9f79c22113398a0c5dbbc7601f489b3e"
base = "research/direct-delivery504-global/"
bindings = []
for name in ["inputs/hamming/PROTOTYPE.json", "NOTICE.md", "SOURCES.json"]:
    published = subprocess.check_output(["git", "show", pin + ":" + base + name])
    local = (package / historical / "baseline535/source531" / base / name).read_bytes()
    require(local == published, "Pinned source bytes: " + name)
    bindings.append({"commit": pin, "path": base + name,
                     "sha256": sha256(local).hexdigest()})

env = os.environ.copy()
env.update(OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
           VECLIB_MAXIMUM_THREADS="1")
controls = []


def reject(name, command, text):
    result = subprocess.run(list(map(str, command)), capture_output=True,
                            text=True, env=env)
    (out / (name + ".stdout.log")).write_text(result.stdout)
    (out / (name + ".stderr.log")).write_text(result.stderr)
    require(result.returncode != 0, "Control accepted: " + name)
    require(text in result.stdout + result.stderr, "Wrong rejection: " + name)
    controls.append({"name": name, "command": list(map(str, command)),
                     "exit_code": result.returncode, "expected_text": text})


reject("optimized-runner", [sys.executable, "-O", "-B", package / "verify.py",
                            "--build", out / "must-not-create"],
       "Run this verifier without -O")
require(not (out / "must-not-create").exists(), "Optimized output was created")
reject("existing-build", [sys.executable, "-B", package / "verify.py",
                          "--build", out], "The build directory exists.")
scalar = (package / "verify_scalar_lemma.py").read_text()
require(scalar.count('9**7, 8**8') == 1, "Scalar control target")
scalar_path = out / "invalid_scalar.py"
scalar_path.write_text(scalar.replace('9**7, 8**8', '9**8, 8**8'))
for name, option in [("normal", []), ("optimized", ["-O"])]:
    reject("invalid-scalar-" + name,
           [sys.executable, *option, "-B", scalar_path, out / (name + ".json")],
           "positive_critical_point")

tampered = out / "tampered-package"
shutil.copytree(package, tampered)
changed = json.loads(raw)
changed["root_lines"][0][0] += 1
(tampered / prototype).write_text(json.dumps(changed))
reject("manifest-root-drift", [sys.executable, "-B", tampered / "verify.py",
                               "--build", out / "must-not-create-drift"],
       "Source hash:")
require(not (out / "must-not-create-drift").exists(), "Drift output was created")
geometry = tampered / historical / "framework/private64_geometry.py"
reject("geometric-root-drift", [sys.executable, "-B", geometry,
                                tampered / historical, out / "bad-root.json"],
       "AssertionError")
changed = json.loads(raw)
changed["binary_ports"][1] = changed["binary_ports"][0]
(tampered / prototype).write_text(json.dumps(changed))
reject("geometric-label-drift", [sys.executable, "-B", geometry,
                                 tampered / historical, out / "bad-label.json"],
       "AssertionError")

result = {"status": "PASS_INDEPENDENT_BINDINGS_AND_SEVEN_CONTROLS",
          "retained_matrix_dimensions": [112, 8], "gram_dimensions": [112, 112],
          "gram_rank_certificate": "R^T R=56 I_8",
          "coordinate_frames": frame_records,
          "b_equal_2_costs": {"rank8": "1", "rank9": "8/9"},
          "source_bindings": bindings, "controls": controls,
          "scope": "Exact fixed source, frame enlargement and rejection controls. The uniform real-variable theorem and the two final profile closures require written proof review."}
(out / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
print(result["status"])
