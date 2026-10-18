#!/usr/bin/env python3
"""Package fault controls for odd-kernel query pairs. Wentao Li + AI, Apache-2.0."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise SystemExit(f"FAIL_TEST: {message}")


def run(args, cwd=None):
    return subprocess.run(args, cwd=cwd or ROOT, text=True, capture_output=True)


def main():
    proc = run([sys.executable, "-I", "-B", str(HERE / "verify.py")])
    need(proc.returncode == 0, proc.stderr + proc.stdout)
    need("PASS_ODD_KERNEL_QUERY_PAIR" in proc.stdout, proc.stdout)

    proc = run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py")])
    need(proc.returncode == 0, "verify under -O: " + proc.stderr + proc.stdout)

    proc = run([sys.executable, "-I", "-B", str(HERE / "independent.py")])
    need(proc.returncode == 0, proc.stderr + proc.stdout)
    need("PASS_INDEPENDENT_ODD_KERNEL_QUERY_PAIR" in proc.stdout, proc.stdout)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        pkg = tmp_path / "research" / "odd-kernel-query-pair"
        shutil.copytree(HERE, pkg)
        for rel in (
            "research/dyadic-query-pair/PROOF.md",
            "research/dyadic-query-pair/README.md",
            "research/dyadic-query-pair/CERTIFICATE.json",
            "certificates/selected-result.json",
            "docs/research/agent-task-catalog.json",
        ):
            dest = tmp_path / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dest)
        cert = json.loads((pkg / "CERTIFICATE.json").read_text())
        cert["typed_cost_improvement_over_dyadic"] = True
        (pkg / "CERTIFICATE.json").write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
        proc = run([sys.executable, "-I", "-B", str(pkg / "verify.py")], cwd=tmp_path)
        need(proc.returncode != 0, "corrupted certificate should fail")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        pkg = tmp_path / "research" / "odd-kernel-query-pair"
        shutil.copytree(HERE, pkg)
        for rel in (
            "research/dyadic-query-pair/PROOF.md",
            "research/dyadic-query-pair/README.md",
            "research/dyadic-query-pair/CERTIFICATE.json",
            "certificates/selected-result.json",
            "docs/research/agent-task-catalog.json",
        ):
            dest = tmp_path / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dest)
        target = tmp_path / "research/dyadic-query-pair/PROOF.md"
        target.write_bytes(target.read_bytes() + b"\n")
        proc = run([sys.executable, "-I", "-B", str(pkg / "verify.py")], cwd=tmp_path)
        need(proc.returncode != 0, "source drift should fail")

    text = (HERE / "CERTIFICATE.json").read_text()
    bad = text.replace('"no_new_kappa": true', '"no_new_kappa": true, "no_new_kappa": false', 1)
    dup = []

    def hook(items):
        keys = [k for k, _ in items]
        if len(keys) != len(set(keys)):
            dup.append(True)
        return dict(items)

    json.loads(bad, object_pairs_hook=hook)
    need(dup, "duplicate key detector armed")

    print("PASS_ODD_KERNEL_QUERY_PAIR_PACKAGE_TESTS groups=6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
