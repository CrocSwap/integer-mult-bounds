"""Source-bound precision refinement; complete baseline and changed release are mandatory.

Credit Nick Petalas/PR3054, dcharb78/PR3042 and the retained native/outer lineage.
Substantial OpenAI Codex assistance. Apache-2.0."""

import ast
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from fractions import Fraction as Q
from pathlib import Path
import argparse

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--baseline-work", type=Path, required=True)
parser.add_argument("--work", type=Path, required=True)
a = parser.parse_args()
BASELINE = a.baseline_work.resolve()
WORK = a.work.resolve()
PKG = ROOT / "research/rank7-t740-carrier-skips"


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def read(p):
    return json.loads(p.read_bytes())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, x):
    p.write_text(json.dumps(x, indent=2, sort_keys=True) + "\n")


def load(p, name):
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


need(os.name == "posix" and not sys.flags.optimize, "POSIX and assertions required")
need(not WORK.is_relative_to(P), "replay workspace outside published package")
binding = load(P / "verify.py", "refinement_source_binding")
binding.authenticate()
sys.path.insert(0, str(PKG))
m = load(PKG / "reproduce.py", "credited_3054_reproduce")
r = read(BASELINE / "RESULT.json")
stages = read(BASELINE / "STAGES.json")
need(
    r["status"] == "PASS_T740_SIX_SKIP_COMPLETE_RELEASE", "mandatory completed baseline"
)
for s in stages:
    need(
        s["exit_code"] == 0
        and sha(BASELINE / (s["stage"] + ".log")) == s["log_sha256"],
        "baseline stage and exact log",
    )
need(
    m.check_release(BASELINE, BASELINE / "pr3042", r["fill_sha256"], stages) == r,
    "full source-bound baseline rederived",
)
need(not WORK.exists(), "fresh refinement work")
WORK.mkdir()
recipe = read(BASELINE / "RECIPE.json")["commands"]
derive = [c.copy() for n, c in recipe if n == "derive-closed-adapters"]
need(len(derive) == 1, "one unchanged adapter derivation")
c = derive[0]
need(
    c == binding.expected_command("derive-closed-adapters", BASELINE, sys.executable),
    "exact source-pinned derivation command; only workspace/interpreter paths relocate",
)
c[c.index("--out") + 1] = str(WORK / "adapters-original")
subprocess.run(c, check=True)
original = BASELINE / "run/adapters/admit_extension.py"
reference = WORK / "adapters-original/admit_extension.py"
need(
    reference.read_bytes() == original.read_bytes(),
    "fresh original adapter derivation equality",
)
body = reference.read_text()
edits = read(P / "PRECISION-EDITS.json")
edits = [x for x in edits if not x["old"].startswith(("COMPARISONS = {", "choices="))]
need(len(edits) == 6, "only declared precision changes")
for e in edits:
    need(body.count(e["old"]) == 1, "one exact precision preimage: " + e["old"])
    body = body.replace(e["old"], e["new"])


def checks(t):
    tree = ast.parse(t)
    return sum(isinstance(x, ast.Assert) for x in ast.walk(tree)), sum(
        isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id == "need"
        for x in ast.walk(tree)
    )


need(
    checks(body) == checks(reference.read_text()),
    "all assertion and explicit check counts retained",
)
adapter = WORK / "admit_precision30.py"
adapter.write_text(body)
save(
    WORK / "DERIVATION.json",
    dict(
        reference_sha256=sha(reference),
        candidate_sha256=sha(adapter),
        replacements=edits,
    ),
)
command = [c.copy() for n, c in recipe if n == "complete-admission"]
need(len(command) == 1, "one complete admission command")
command = command[0]
need(
    command == binding.expected_command("complete-admission", BASELINE, sys.executable),
    "exact source-pinned complete admission command",
)
command[:3] = [sys.executable, "-B", str(adapter)]
command[command.index("--work") + 1] = str(WORK / "candidate")
sys.path.insert(0, str(P))
nom = load(P / "verify.py", "refinement_arithmetic").calculate()
need(Q(r["kappa"]) == Q(nom["previous"]), "exact current comparison point")
env = dict(
    os.environ,
    PYTHONDONTWRITEBYTECODE="1",
    PYTHONINTMAXSTRDIGITS="0",
    OPENBLAS_NUM_THREADS="1",
    OMP_NUM_THREADS="1",
)
for k in (
    "PYTHONOPTIMIZE",
    "PYTHONPATH",
    "WITNESS_SPEC",
    "WITNESS_RECORD",
    "WITNESS_DISCOVER",
):
    env.pop(k, None)
print("START_FULL_PRECISION30_ADMISSION", flush=True)
with (WORK / "complete-admission.log").open("w") as log:
    subprocess.run(command, check=True, env=env, stdout=log, stderr=subprocess.STDOUT)
a = read(WORK / "candidate/RESULT.json")
release = read(WORK / "candidate/release/RELEASE-RECEIPT.json")
need(
    a["status"] == "PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE"
    and release["status"] == "PASS_RELEASE",
    "complete actual candidate release",
)
need(
    Q(a["kappa"]) == Q(nom["kappa"]) == Q(release["kappa_decimal"]) > Q(r["kappa"]),
    "actual exact improved released point",
)
for k in (
    "profile",
    "fill_sha256",
    "order_sha256",
    "dispatch_sha256",
    "source_manifest_sha256",
    "native_receipt_sha256",
):
    need(
        a[k] == read(BASELINE / "run/candidate/RESULT.json")[k],
        "unchanged physical/source/native input " + k,
    )
need(
    a["release_receipt_sha256"] == sha(WORK / "candidate/release/RELEASE-RECEIPT.json"),
    "actual terminal receipt hash",
)
save(
    WORK / "RESULT.json",
    dict(
        status="PASS_T740_SIX_SKIP_PRECISION30_COMPLETE_RELEASE",
        kappa=a["kappa"],
        previous=r["kappa"],
        gain=str(Q(a["kappa"]) - Q(r["kappa"])),
        baseline_complete=True,
        candidate_complete=True,
        admission_sha256=sha(WORK / "candidate/RESULT.json"),
        release_sha256=sha(WORK / "candidate/release/RELEASE-RECEIPT.json"),
    ),
)
print("PASS_T740_SIX_SKIP_PRECISION30_COMPLETE_RELEASE", a["kappa"], flush=True)
