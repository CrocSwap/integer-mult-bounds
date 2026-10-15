#!/usr/bin/env python3
"""Cold finite native replay of both immutable PR2339 words (NumPy required)."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
CODE = HERE / "pr2269"
WORDS = HERE.parent / "vendor/pr2339/words"


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def check_sources():
    manifest = json.loads((CODE / "FETCH.json").read_text())
    need(manifest["ref"] == "b479fc5567bc09ab9185bffe89b62594f36d74e5", "compiler head changed")
    for source_path, record in manifest["files"].items():
        p = CODE / ("vendor/clifford/clifford_exact.py" if source_path.endswith("clifford_exact.py") else Path(source_path).name)
        data = p.read_bytes()
        need(hashlib.sha256(data).hexdigest() == record["sha256"], f"changed compiler source: {p}")
        need(hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == record["git_blob"], f"git blob mismatch: {p}")
    source = json.loads((HERE.parent / "vendor/pr2339/SOURCES-PR.json").read_text())
    for variant in ("base", "extra"):
        p = WORDS / f"BORROW-WORD-80{variant}.json.gz"
        need(hashlib.sha256(p.read_bytes()).hexdigest() == source["outputs"]["words/" + p.name], f"changed input: {p}")


def main():
    need(__debug__, "assertions must remain enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="fresh output directory")
    args = parser.parse_args()
    check_sources()
    out = args.out.resolve(); out.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONINTMAXSTRDIGITS="0")
    env.pop("PYTHONOPTIMIZE", None)
    steps = []
    def run(label, script, *params):
        started = time.monotonic()
        proc = subprocess.run([sys.executable, "-B", str(script), *map(str, params)],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
        (out / (label + ".log")).write_bytes(proc.stdout)
        steps.append(dict(step=label, exit_code=proc.returncode, seconds=time.monotonic()-started))
        (out / "STEPS.json").write_text(json.dumps(steps, indent=2)+"\n")
        need(proc.returncode == 0, f"{label} failed; inspect {out / (label + '.log')}")
        print("PASS", label, flush=True)
    for variant in ("base", "extra"):
        word = WORDS / f"BORROW-WORD-80{variant}.json.gz"; local = out / variant
        run(variant+"-transport", CODE / "bw_transport.py", word, local)
        run(variant+"-emit", CODE / "bw_emit.py", local)
        run(variant+"-independent", CODE / "bw_audit_local.py", local)
        run(variant+"-wrappers", CODE / "bw_adapters.py", local / "CANONICAL-WORD.json.gz", local / "RESIDUAL-ADAPTERS.json", local / "WRAPPER-CHECKS.json")
        run(variant+"-phases", CODE / "bw_phases.py", local)
        run(variant+"-recipes", CODE / "bw_check_recipes.py", local)
        run(variant+"-orientations", HERE / "orientation_contract.py", local)
        run(variant+"-tamper", CODE / "bw_tamper.py", word, local, out / (variant+"-tamper"))
    run("lemmag", HERE / "lemmag_stage.py", out / "LEMMAG-CHECKS.json", out / "base", out / "extra")
    run("extra-file-tamper", CODE / "bw_tamper.py", WORDS / "BORROW-WORD-80extra.json.gz", out / "extra", out / "extra-tamper-files", "--files")
    print("PASS_PR2339_FINITE_NATIVE_INTERFACE_BOTH_WORDS")


if __name__ == "__main__":
    main()
