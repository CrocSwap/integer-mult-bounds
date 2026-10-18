"""rebind: private copy of a gauge44-lineage owner package whose PLAN (data/PLAN.json, or --plan REL) is rebound
to a new native local dir with UNCHANGED helper widths/ports/centres (owner map reused byte-for-byte).  The global profile
changes by calls x (new local - old local); the deficit identity is asserted.  The SPEC's word-dependent provider keys and
its expected block (except gain_baseline_kappa) are removed and data.plan_sha256 is re-pinned, so discovery + unpin +
freeze_spec re-derive them.  usage: python -B rebind.py SRC_PKG LOCAL OUT_PKG [--plan data/PLAN.json --spec data/SPEC.json --T 8]"""
import argparse, gzip, hashlib, json, os, shutil, sys
from collections import Counter
from pathlib import Path
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rebind_plan(plan, local, code_dir, spec_path, T):
    reg = plan["provider_registry"]["gauge44"]; V = 112
    c = json.load(gzip.open(local / "CANONICAL-WORD.json.gz")); checks = json.loads((local / "LOCAL-CHECKS.json").read_text(encoding="utf-8"))
    widths = [len(c["frames"][c["final"][r]]) - len(c["frames"][c["start"][r]]) for r in range(2 * V, 2 * V + c["R"])]
    assert widths == reg["widths"], "helper widths differ: owner map cannot be reused"
    assert c["ports"] == reg["ports"] and c["centers"] == reg["centers"], "ports/centres differ"
    sys.path.insert(0, str(code_dir)); os.environ["WITNESS_SPEC"] = str(spec_path); os.environ["WITNESS_DISCOVER"] = "1"
    from generated_identity import artifact_identities
    old_local = {int(k): v for k, v in reg["actual_paid_profile"].items()}; new_local = {int(k): v for k, v in checks["forward"]["paid_profile"].items()}
    assert new_local == {int(k): v for k, v in checks["backward"]["paid_profile"].items()}
    calls = len(plan["provider_calls"]); assert calls == 9 * T, (calls, T)
    prof = Counter({int(k): v for k, v in plan["profile"].items()})
    for r, n in old_local.items(): prof[r] -= calls * n
    idle = {r: n for r, n in prof.items() if n}; assert all(n > 0 for n in idle.values()), idle
    prof = Counter(idle)
    for r, n in new_local.items(): prof[r] += calls * n
    assert 73 * 896 * T - sum(r * n for r, n in prof.items()) == 320 * T, "deficit"
    reg["artifact_sha256"] = {n: sha(local / n) for n in reg["artifact_sha256"]}
    reg["artifact_semantic_sha256"] = artifact_identities(local)
    reg["actual_paid_profile"] = checks["forward"]["paid_profile"]
    reg["orientation_program_sha256"] = {o: checks[o]["sha256"] for o in ("forward", "backward")}
    for call in plan["provider_calls"]: call["local_program_sha256"] = checks[call["orientation"]]["sha256"]
    plan["profile"] = {str(k): v for k, v in sorted(prof.items()) if v}
    plan["status"] = plan.get("status", "") + " | rebound to a new local word (widths and owners unchanged)"
    plan.pop("runtime_source_plan_sha256", None)
    return idle, old_local, new_local
def strip_spec(spec_path, plan_path):
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8")); spec["data"]["plan_sha256"] = sha(plan_path)
    for k in ("expected_profile", "artifact_semantic_sha256", "phase_edges", "native_negative_controls"): spec["providers"]["gauge44"].pop(k, None)
    for k in list(spec["expected"].keys()):
        if k != "gain_baseline_kappa": spec["expected"].pop(k)
    Path(spec_path).write_text(json.dumps(spec, indent=1) + "\n", encoding="utf-8", newline="\n")
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("local"); ap.add_argument("out")
    ap.add_argument("--plan", default="data/PLAN.json"); ap.add_argument("--spec", default="data/SPEC.json"); ap.add_argument("--T", type=int, default=8)
    a = ap.parse_args(); src, local, out = Path(a.src).resolve(), Path(a.local).resolve(), Path(a.out).resolve()
    assert not out.exists(); shutil.copytree(src, out)
    plan = json.loads((out / a.plan).read_text(encoding="utf-8"))
    idle, old, new = rebind_plan(plan, local, out / "code", out / a.spec, a.T)
    (out / a.plan).write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8", newline="\n"); strip_spec(out / a.spec, out / a.plan)
    print("rebound", a.plan, "| T", a.T, "| idle", dict(sorted(idle.items())), "| old local", old, "| new local", new, "| plan sha", sha(out / a.plan)[:12])
