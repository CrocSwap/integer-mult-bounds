"""Admit the signed-read CK lowering into a fresh PR626 frontier replay.

Usage, after `make frontier626-verify` (or scripts/verify_frontier626.py
--work WORK) has passed:

    python3 -B research/ck-signed-coefficient-routes/admission.py \
        --work WORK --out FRESH_DIR

Checks, in order:
1. Native identity: the freshly replayed CK provider has byte-identical
   programs to those this package replays, so its native frame/wrapper/phase
   admission covers the signed lowering's unchanged event stream.
2. Live work: the fresh invoice hosts coefficient work as two dedicated
   physical registers, never borrowed by children or wrappers.
3. Re-issued invoice: the retained invoice code recomputes every finite
   inequality with the signed CK counts.
4. Precision: the CK provider's deepest fraction and the global prefix are
   unchanged.
5. Assembly: the retained assembly and its admission controls rerun on the
   re-issued invoice and reproduce the selected kappa exactly.

Apache-2.0. Joseph / AmazedBot with Anthropic Claude assistance.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PKG = ROOT / "research/complex-k492-owner-repair"
S = PKG / "vendor/multicold"
RETAINED = S / "vendor/pr558/vendor/pr552/complex-global/vendor531/evidence/audit/PREFIX-AND-INVOICE.json"


def need(ok, why):
    if not ok:
        raise SystemExit("ADMISSION FAILED: " + why)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def payload_sha(path):
    raw = path.read_bytes()
    return hashlib.sha256(gzip.decompress(raw) if path.suffix == ".gz" else raw).hexdigest()


def step(name, script, *args, out, spec=PKG / "data/SPEC.json"):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
               PYTHONINTMAXSTRDIGITS="0", MULTICOLD_SOURCE=str(S),
               GAIN_PR564_SOURCE=str(S), WITNESS_SPEC=str(spec))
    for key in ("PYTHONOPTIMIZE", "WITNESS_DISCOVER"):
        env.pop(key, None)
    log = out / (name + ".log")
    with log.open("w") as f:
        code = subprocess.call([sys.executable, "-B", str(S / "code/run_portable.py"),
                                str(script), *map(str, args)],
                               stdout=f, stderr=subprocess.STDOUT, env=env, cwd=ROOT)
    need(code == 0, f"{name} failed; see {log}")
    print("PASS", name, flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", type=Path, required=True, help="passed frontier626 work directory")
    ap.add_argument("--out", type=Path, required=True, help="fresh output directory")
    a = ap.parse_args()
    need(not sys.flags.optimize, "assertions must be enabled")
    work, out = a.work.resolve(), a.out.resolve()
    need(not out.exists(), "output directory must be fresh")
    G = work / "complex/mixed-global"
    need((work / "STEPS.json").exists() and (work / "RESULT.json").exists(),
         "work directory lacks a completed frontier626 run")
    need(all(s["exit_code"] == 0 for s in read(work / "STEPS.json")), "frontier626 run did not pass")
    expected = read(HERE / "EXPECTED.json")
    pins = read(HERE / "SOURCES.json")["files"]

    # 1. Native identity of the CK event stream.
    ck = G / "base/providers/ck"
    pinned = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/"
    for name in ("LOCAL-PROGRAMS.json.gz", "LOCAL-CHECKS.json", "INDEPENDENT-LOCAL-REPLAY.json"):
        need(payload_sha(ck / name) == pins[pinned + name]["payload_sha256"],
             f"fresh CK {name} differs from the programs this package replays")
    replay = read(ck / "INDEPENDENT-LOCAL-REPLAY.json")
    need(replay["status"] == "PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY",
         "fresh CK native replay status")
    need(all(replay["local"][o]["private_work_erased"] for o in ("forward", "backward")),
         "fresh CK native replay must erase private work")

    # 2. Coefficient work is dedicated physical stock.
    old_invoice = read(G / "audit/PREFIX-AND-INVOICE.json")
    stock = old_invoice["physical_stock_identity"]
    need(stock["coefficient_work"] == 2 and sum(stock.values()) == old_invoice["physical"],
         "coefficient work must be two dedicated physical registers")

    # 3. Re-issue the invoice with signed CK counts.
    out.mkdir(parents=True)
    audit = out / "mixed-global/audit"
    audit.mkdir(parents=True)
    for name in ("OWNERS-AND-PROFILE.json", "ASYNC-AUDIT.json"):
        shutil.copy2(G / "audit" / name, audit / name)
    for name in ("base", "hosted"):
        (out / "mixed-global" / name).symlink_to(G / name, target_is_directory=True)
    step("signed-invoice", HERE / "revise_invoice.py", "--base", G / "base", "--hosted", G / "hosted",
         "--audit", audit, "--out", audit, "--retained-invoice", RETAINED, out=out)
    new_invoice = read(audit / "PREFIX-AND-INVOICE.json")
    need(all(new_invoice["strict_checks"].values()), "a finite inequality fails")
    ck_old, ck_new = old_invoice["providers"]["ck"], new_invoice["providers"]["ck"]
    for o in ("forward", "backward"):
        need(ck_new["local"][o]["real_component_primitives"]
             == expected["programs"][o]["real_primitives"]["signed"], "signed CK count not used")

    # 4. Precision is unchanged at provider and global level.
    depth_old = max(expected["programs"][o]["original_max_fraction_bits"] for o in ("forward", "backward"))
    depth_new = max(expected["programs"][o]["max_fraction_bits"] for o in ("forward", "backward"))
    need(depth_new == depth_old, "CK provider fractional depth increased")
    need(new_invoice["global_prefix_bits"] == old_invoice["global_prefix_bits"], "global prefix changed")
    need(new_invoice["global_prefix_bits"] < new_invoice["charged_prefix_bits"], "global prefix allowance")

    # 5. Retained assembly and its controls on the re-issued invoice. The
    # retained SPEC pins the CK provider's complete contract; exactly that one
    # entry is replaced by the re-issued contract. Every other pin, including
    # kappa, the global profile and the control counts, is retained unchanged.
    spec = read(PKG / "data/SPEC.json")
    contract = {k: v for k, v in new_invoice["providers"]["ck"].items() if k != "artifacts"}
    old_contract = spec["providers"]["ck"]["complete_contract"]
    changed = sorted(k for k in set(old_contract) | set(contract)
                     if old_contract.get(k) != contract.get(k))
    need(set(changed) <= {"local", "local_primitive_bound"}, "unexpected contract change: %s" % changed)
    spec["providers"]["ck"]["complete_contract"] = contract
    replaced = ["providers.ck.complete_contract." + k for k in changed]
    for o in ("forward", "backward"):
        key = "expected_local." + o
        pinned_local = spec["providers"]["ck"][key]
        fresh = {k: contract["local"][o][k] for k in pinned_local}
        moved = sorted(k for k in pinned_local if pinned_local[k] != fresh[k])
        need(set(moved) <= {"real_component_primitives", "prefix_l1",
                            "coefficient_work_primitive_count"},
             "unexpected local recount change: %s" % moved)
        spec["providers"]["ck"][key] = fresh
        replaced += ["providers.ck.%s.%s" % (key, k) for k in moved]
    revised_spec = out / "SPEC-SIGNED-CK.json"
    revised_spec.write_text(json.dumps(spec, indent=2) + "\n")
    step("signed-assembly", PKG / "code/assemble.py", S, out / "mixed-global", out / "ASSEMBLY.json",
         out=out, spec=revised_spec)
    step("signed-admission-controls", PKG / "code/assembly_controls.py", "--source-package", S,
         "--owner", audit / "OWNERS-AND-PROFILE.json", "--invoice", audit / "PREFIX-AND-INVOICE.json",
         "--out", out / "ASSEMBLY-CONTROLS.json", out=out, spec=revised_spec)
    spec_expected = spec["expected"]
    need(len(read(out / "ASSEMBLY-CONTROLS.json")["rejected_controls"])
         == spec_expected["assembly_controls_rejected"], "assembly controls")
    old_asm, new_asm = read(work / "complex/ASSEMBLY.json"), read(out / "ASSEMBLY.json")
    for key in ("kappa", "kappa_decimal", "conservative_kappa_decimal", "complex_lower", "bit_lower"):
        need(new_asm[key] == old_asm[key], "assembly changed " + key)

    receipt = {
        "status": "PASS_CK_SIGNED_ADMISSION_PR626",
        "kappa": new_asm["kappa"], "kappa_unchanged": True,
        "native_ck_programs_identical": True,
        "spec_entries_replaced": replaced,
        "coefficient_work_physical_registers": stock["coefficient_work"],
        "ck_real_primitives": {o: {"original": ck_old["local"][o]["real_component_primitives"],
                                   "signed": ck_new["local"][o]["real_component_primitives"]}
                               for o in ("forward", "backward")},
        "ck_local_primitive_bound": {"original": ck_old["local_primitive_bound"],
                                     "signed": ck_new["local_primitive_bound"]},
        "selected_real_component_primitives": {"original": old_invoice["selected_real_component_primitives"],
                                               "signed": new_invoice["selected_real_component_primitives"]},
        "conservative_pervertex_used": {"original": old_invoice["conservative_pervertex_used"],
                                        "signed": new_invoice["conservative_pervertex_used"]},
        "ck_max_fraction_bits": {"original": depth_old, "signed": depth_new},
        "global_prefix_bits": new_invoice["global_prefix_bits"],
        "strict_checks": new_invoice["strict_checks"],
        "scope": ("Admission into the historical PR626 composition only. Savings include "
                  "predecessor copy/power/positive-read lowering; 926 forward primitives are "
                  "attributable to signed reads. Inherited all-size, realization, hosting, "
                  "precision/tape and analytic assumptions remain conditional."),
    }
    text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    (out / "ADMISSION.json").write_text(text)
    need(text == (HERE / "ADMISSION.json").read_text(), "receipt differs from ADMISSION.json")
    print("PASS_CK_SIGNED_ADMISSION_PR626 kappa=unchanged "
          f"selected_primitives={receipt['selected_real_component_primitives']['original']}"
          f"->{receipt['selected_real_component_primitives']['signed']}")


if __name__ == "__main__":
    main()
