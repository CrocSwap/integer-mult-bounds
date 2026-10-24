"""Reconstruct the 112-port conditional global witness, offline and with stdlib.

Prepared for icekylinx with GPT-6 Astra assistance. Apache-2.0.
The pinned PR493 bit operator and the explicitly listed all-size interfaces
remain dependencies. This program is a finite verifier, not a Lean proof.
"""
from pathlib import Path
from fractions import Fraction
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

if not __debug__:
    raise RuntimeError("Assertions must be enabled; do not use -O or PYTHONOPTIMIZE.")
if sys.version_info < (3, 11):
    raise RuntimeError("Python 3.11 or later is required.")
sys.dont_write_bytecode = True
sys.set_int_max_str_digits(0)
P = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--work", type=Path, required=True,
                    help="a new output directory outside this package")
args = parser.parse_args()
W = args.work.resolve()
assert W != P and P not in W.parents, "Output must be outside the package."
assert not W.exists(), "Choose a new directory; existing work is preserved."

# Validate every immutable input before creating an output directory. Text
# normalization changes only CRLF line endings; no other token is ignored.
mf = P / "MANIFEST.json"
manifest = json.loads(mf.read_text(encoding="utf-8"))
assert manifest["format"] == "sha256-lf-text-v1"
for name, entry in manifest["files"].items():
    f = P / name
    assert P in f.resolve().parents, name
    data = f.read_bytes()
    assert entry["mode"] in ("raw", "lf-text"), name
    if entry["mode"] == "lf-text":
        data = data.replace(b"\r\n", b"\n")
    assert hashlib.sha256(data).hexdigest() == entry["sha256"], name

W.mkdir(parents=True)
V = P / "vendor/pr514"
C = V / "vendor/complex"
G = C / "e8-complex-gauge-kernel"
ORIGINAL = W / "baseline514"
LOCAL = W / "local112"
BASE = W / "base112"
HOSTED = W / "hosted"
AUDIT = W / "audit"
AUDIT.mkdir()
env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1",
           PYTHONINTMAXSTRDIGITS="0", TEMP=str(W), TMP=str(W))
env.pop("PYTHONOPTIMIZE", None)
steps = []
start = time.monotonic()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def run(name, script, *argv):
    before = time.monotonic()
    print("RUN", name, flush=True)
    logfile = W / (name + ".log")
    with logfile.open("w", encoding="utf-8", newline="\n") as log:
        proc = subprocess.run(
            [sys.executable, "-B", str(V / "code/run_portable.py"),
             str(script), *map(str, argv)],
            cwd=W, env=env, stdout=log, stderr=subprocess.STDOUT)
    steps.append(dict(stage=name, exit=proc.returncode,
                      seconds=time.monotonic() - before))
    (W / "STEPS.json").write_text(json.dumps(steps, indent=2) + "\n",
                                  encoding="utf-8")
    if proc.returncode:
        print(logfile.read_text(encoding="utf-8")[-7000:], flush=True)
        raise SystemExit(proc.returncode)
    print("PASS", name, flush=True)


# Rebuild the pinned predecessor instead of trusting pre-generated local words.
run("01-pinned514-full-replay", V / "verify.py", "--work", ORIGINAL)
original = read(ORIGINAL / "RESULT.json")
assert original["kappa"] == "1391523459591829/1000000000000000000"
assert original["template_sha256"] == (
    "77767f67ed17413161d82f2a407e69b3beefef3fc44bfe582fb403bdc1705bd8")

run("02-restrict-local", P / "code/build_port112.py",
    ORIGINAL / "base/split-centres", LOCAL)
run("03-exact-word-transport", P / "code/audit_port112_transport.py", LOCAL)
run("04-emit-local", P / "code/emit_local112.py", LOCAL)
run("05-independent-local", P / "code/audit_local112.py", LOCAL)
run("06-exact-local-phases", P / "code/phases_local112.py",
    LOCAL, C / "split-centres-global/vendor")
run("07-residual-wrappers", G / "code/adapters_gk.py",
    LOCAL / "CANONICAL-WORD.json.gz", LOCAL / "RESIDUAL-ADAPTERS.json",
    LOCAL / "LEMMA-A.json")
run("08-restrict-global-data", P / "code/restrict_global.py",
    ORIGINAL / "base", LOCAL, BASE)
run("09-independent-global-restriction", P / "code/audit_global_restriction.py",
    ORIGINAL / "base", BASE, AUDIT / "GLOBAL-RESTRICTION-AUDIT.json")
run("10-emit-whole-owners", P / "code/emit_async.py", G, BASE,
    P / "inputs/OWNERS112.json.gz", P / "inputs/ASYNC112-PLAN.json", HOSTED)
run("11-independent-hosted-program", P / "code/audit_async.py",
    BASE, HOSTED, AUDIT / "ASYNC-AUDIT.json")
run("12-independent-raw-reconstruction", P / "code/audit_112_independent.py",
    "--original-base", ORIGINAL / "base", "--local", LOCAL,
    "--owners", P / "inputs/OWNERS112.json.gz", "--out", AUDIT)
run("13-scalar-prefix-and-finite-invoice", P / "code/audit_async_invoice.py",
    AUDIT, BASE, HOSTED)
run("14-two-moments-and-global-assembly", P / "code/assemble.py",
    AUDIT, BASE, HOSTED, V / "inputs/PR493-EXPECTED.json")

x = read(AUDIT / "EXACT-ASSEMBLY.json")
h = read(HOSTED / "HOSTED.json")
raw = read(AUDIT / "INDEPENDENT112-RAW-AUDIT.json")
owner = read(AUDIT / "OWNERS-AND-PROFILE.json")
e = read(P / "EXPECTED.json")
for key in ("kappa", "kappa_decimal", "complex_lower", "complex_decimal",
            "bit_lower", "complex_template_sha256"):
    assert x[key] == e[key], key
assert h["template_sha256"] == e["complex_template_sha256"]
assert h["global_profile"] == owner["paid_profile"] == raw["paid_profile"] == e["global_profile"]
for key in ("live", "physical", "rank_mass", "deficit"):
    assert h[key] == raw[key] == e[key], key
assert raw["whole_owner_roles"] == e["whole_owner_roles"] == 40320
assert raw["no_emitter_or_hosting_checker_imported"]
assert raw["no_nominated_profile_or_windows_used"]
assert len(x["strict_outer_constraints"]) == e["strict_constraints"] == 47
assert all(Fraction(q) > 0 for q in x["strict_outer_constraints"].values())
assert x["outer_controls"] == ["next_grid", "zero_eta", "zero_beta", "unit_beta"]
assert all(step["exit"] == 0 for step in steps)

result = dict(
    status="PASS_CONDITIONAL_PUNCTURED112_GLOBAL_KAPPA",
    kappa=x["kappa"], kappa_decimal=x["kappa_decimal"],
    complex_lower=x["complex_lower"], bit_lower=x["bit_lower"],
    template_sha256=x["complex_template_sha256"],
    live=h["live"], physical=h["physical"], deficit=h["deficit"],
    global_profile=h["global_profile"], strict_constraints=47,
    improvement_over_pinned514=str(Fraction(x["kappa"]) / Fraction(original["kappa"]) - 1),
    whole_owner_roles=raw["whole_owner_roles"],
    all_own_stages=len(steps), pinned_predecessor_stages=len(original["stages"]),
    package_manifest_sha256=hashlib.sha256(mf.read_bytes()).hexdigest(),
    seconds=time.monotonic() - start, steps=steps,
    scope=("Finite complex restriction, exact local phases, whole physical owners, "
           "complete fee inventory, two rational moments and 47 outer inequalities "
           "checked. The unchanged PR493 bit operator, all-size compiler, "
           "common-label/mutable-basis realization, normalized Lemma A, "
           "restored-row, precision/tape and analytic-transfer contracts remain "
           "dependencies. No unconditional theorem or new Lean certification."))
(W / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(result["status"], "kappa", result["kappa_decimal"], flush=True)
