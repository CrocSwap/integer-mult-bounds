"""native: PR635's native local chain on a gauge44-lineage FULL-WORD (as construction/frames/reproduce_frames.py
step 4): transport audit -> ledgers -> local replay -> wrappers -> phases.  usage: python -B native.py WORD.json.gz OUT_DIR"""
import json, os, subprocess, sys, time
from pathlib import Path
from paths import ROOT as IMB
UP = IMB / "research/complex-sw4-frame8/vendor/pr635/research/complex-571-cold14-st2"
SRC = IMB / "research/complex-k492-owner-repair/vendor/multicold"; BASE = SRC / "vendor/pr558"; PARENT = BASE / "vendor/pr552"
ROUTING = PARENT / "complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz"
def main():
    word = Path(sys.argv[1]).resolve(); out = Path(sys.argv[2]).resolve(); out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1", PYTHONINTMAXSTRDIGITS="0", MULTICOLD_SOURCE=str(SRC), GAIN_PR564_SOURCE=str(SRC))
    for k in ("PYTHONOPTIMIZE", "XPARAM", "EXTRAH", "PAIRING_RANKS", "DIAG", "HYBBUDGET", "PR635_CODE"): env.pop(k, None)
    steps = []
    def run(label, script, *args):
        t = time.monotonic(); cmd = [sys.executable, "-B", str(SRC / "code/run_portable.py"), str(script), *map(str, args)]
        with (out / (label + ".log")).open("w") as f: rc = subprocess.call(cmd, env=env, stdout=f, stderr=subprocess.STDOUT)
        steps.append(dict(step=label, exit_code=rc, seconds=round(time.monotonic() - t, 1))); (out / "STEPS.json").write_text(json.dumps(steps, indent=2))
        print(("PASS" if rc == 0 else "FAIL"), label, f"{time.monotonic()-t:.0f}s", flush=True)
        if rc: print((out / (label + ".log")).read_text()[-1500:]); sys.exit(1)
    local = out / "local"
    run("native", UP / "code/hpe_audit_and_transport.py", "--raw", word, "--routing", ROUTING, "--out", local)
    run("ledgers", UP / "code/hpe_emit_local.py", local)
    run("local-replay", UP / "code/hpe_audit_local.py", local)
    run("wrappers", UP / "code/hpe_adapters_local.py", local / "CANONICAL-WORD.json.gz", local / "RESIDUAL-ADAPTERS.json", local / "WRAPPER-CHECKS.json")
    run("phases", BASE / "code/phases_full.py", local, PARENT / "complex-global/vendor531/vendor/clifford")
    print("DONE", local, flush=True)
if __name__ == "__main__": main()
