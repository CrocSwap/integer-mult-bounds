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
parser.add_argument('--reuse-source522',type=Path)
args = parser.parse_args()
W = args.work.resolve()
assert W != P and P not in W.parents, "Output must be outside the package."
assert not W.exists(), "Choose a new directory; existing work is preserved."

# Validate every immutable input before creating an output directory. Text
# normalization changes only CRLF line endings; no other token is ignored.
mf = P/'MANIFEST.json'
actual={f.relative_to(P).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in P.rglob('*') if f.is_file() and f!=mf and '__pycache__' not in f.parts}
assert actual==json.loads(mf.read_text()), 'Package manifest'
W.mkdir(parents=True)
S = P / "vendor/pr523"
V = S / "vendor/pr514"
C = V / "vendor/complex"
G = C / "e8-complex-gauge-kernel"
ORIGINAL = W / "source522"
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


# Explicit completed-source reuse is fully byte-pinned; default rebuilds source522.
if args.reuse_source522:
    ORIGINAL=args.reuse_source522.resolve()
    for name,expected_hash in read(P/'REUSE-SOURCE522-INPUTS.json').items():
        assert hashlib.sha256((ORIGINAL/name).read_bytes()).hexdigest()==expected_hash,name
    source_mode='byte-pinned-completed-source522-reuse'
else:
    run('01-source522-full-replay',P/'vendor/pr522/verify.py','--work',ORIGINAL)
    source_mode='fresh-source522-complex-reconstruction'
original=read(ORIGINAL/'RESULT.json')
assert original['status']=='PASS_CONDITIONAL_ASYNCHRONOUS_COMPLEX_DERIVATIVE'
assert original['kappa']=='1402213284556683/1000000000000000000'
run("02-restrict-local", S / "code/build_port112.py",
    ORIGINAL / "base/split-centres", LOCAL)
run("03-exact-word-transport", S / "code/audit_port112_transport.py", LOCAL)
run("04-emit-local", S / "code/emit_local112.py", LOCAL)
run("05-independent-local", S / "code/audit_local112.py", LOCAL)
run("06-exact-local-phases", S / "code/phases_local112.py",
    LOCAL, C / "split-centres-global/vendor")
run("07-residual-wrappers", G / "code/adapters_gk.py",
    LOCAL / "CANONICAL-WORD.json.gz", LOCAL / "RESIDUAL-ADAPTERS.json",
    LOCAL / "LEMMA-A.json")
run("08-restrict-global-data", S / "code/restrict_global.py",
    ORIGINAL / "base", LOCAL, BASE)
run("09-independent-global-restriction", P / "code/audit_global_restriction.py",
    ORIGINAL / "base", BASE, AUDIT / "GLOBAL-RESTRICTION-AUDIT.json")
run("10-emit-whole-owners", S / "code/emit_async.py", G, BASE,
    P / "data/OWNERS.json.gz", P / "data/PLAN.json", HOSTED)
run("11-independent-hosted-program", S / "code/audit_async.py",
    BASE, HOSTED, AUDIT / "ASYNC-AUDIT.json")
run("12-independent-raw-reconstruction", P / "code/audit_112_independent.py",
    "--original-base", ORIGINAL / "base", "--local", LOCAL,
    "--owners", P / "data/OWNERS.json.gz", "--out", AUDIT)
run("13-scalar-prefix-and-finite-invoice", P / "code/audit_async_invoice.py",
    AUDIT, BASE, HOSTED)
run("14-two-moments-and-global-assembly", S / "code/assemble.py",
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
    status="PASS_PACKAGED_RANKSECTOR112_GLOBAL_KAPPA",
    kappa=x["kappa"], kappa_decimal=x["kappa_decimal"],
    complex_lower=x["complex_lower"], bit_lower=x["bit_lower"],
    template_sha256=x["complex_template_sha256"],
    live=h["live"], physical=h["physical"], deficit=h["deficit"],
    global_profile=h["global_profile"], strict_constraints=47,
    improvement_over_source522=str(Fraction(x["kappa"]) / Fraction(original["kappa"]) - 1),
    whole_owner_roles=raw["whole_owner_roles"],
    all_own_stages=len(steps), pinned_predecessor_stages=len(original["stages"]),
    source522_mode=source_mode,
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
