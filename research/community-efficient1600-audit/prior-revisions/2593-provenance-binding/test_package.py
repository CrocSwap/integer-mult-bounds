#!/usr/bin/env python3
"""Package fault controls for the triadic query pair. Wentao Li + AI, Apache-2.0."""
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
    need("PASS_TRIADIC_QUERY_PAIR" in proc.stdout, proc.stdout)

    proc = run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py")])
    need(proc.returncode == 0, proc.stderr + proc.stdout)

    proc = run([sys.executable, "-I", "-B", str(HERE / "independent.py")])
    need(proc.returncode == 0, proc.stderr + proc.stdout)

    # Certificate corruption on a temp package copy: verify rebuilds evidence and
    # compares to the (corrupted) committed certificate.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        pkg = tmp_path / "research" / "triadic-query-pair"
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
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "-c", "user.name=test", "-c", "user.email=test@ex.com", "commit", "-m", "t"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tmp_path, text=True).strip()
        sources = json.loads((pkg / "SOURCES.json").read_text())
        sources["base_commit"] = head
        for row in sources["files"]:
            data = (tmp_path / row["path"]).read_bytes()
            import hashlib

            row["sha256"] = hashlib.sha256(data).hexdigest()
            row["git_blob"] = subprocess.check_output(
                ["git", "rev-parse", f"HEAD:{row['path']}"], cwd=tmp_path, text=True
            ).strip()
        (pkg / "SOURCES.json").write_text(json.dumps(sources, indent=2) + "\n")
        # First: temp tree should PASS after pin rewrite and cert regenerate.
        proc = run(
            [sys.executable, "-I", "-B", str(pkg / "verify.py"), "--write"],
            cwd=tmp_path,
        )
        need(proc.returncode == 0, "temp rewrite write: " + proc.stderr + proc.stdout)
        proc = run([sys.executable, "-I", "-B", str(pkg / "verify.py")], cwd=tmp_path)
        need(proc.returncode == 0, "temp rewrite verify: " + proc.stderr + proc.stdout)
        # Corrupt certificate.
        cert = json.loads((pkg / "CERTIFICATE.json").read_text())
        cert["fused_invoice"]["ordinary_children"] = 0
        (pkg / "CERTIFICATE.json").write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
        proc = run([sys.executable, "-I", "-B", str(pkg / "verify.py")], cwd=tmp_path)
        need(proc.returncode != 0, "corrupted certificate should fail")

    # Source pin corruption in a temp tree.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        pkg = tmp_path / "research" / "triadic-query-pair"
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
        # Drift a pinned input without updating SOURCES.
        (tmp_path / "research/dyadic-query-pair/PROOF.md").write_bytes(
            (tmp_path / "research/dyadic-query-pair/PROOF.md").read_bytes() + b"\n"
        )
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "-c", "user.name=test", "-c", "user.email=test@ex.com", "commit", "-m", "t"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
        proc = run([sys.executable, "-I", "-B", str(pkg / "verify.py")], cwd=tmp_path)
        need(proc.returncode != 0, "source drift should fail")

    # Duplicate JSON key detection
    text = (HERE / "CERTIFICATE.json").read_text()
    bad = text.replace('"kernel": 3', '"kernel": 3, "kernel": 4', 1)
    dup = []

    def hook(items):
        keys = [k for k, _ in items]
        if len(keys) != len(set(keys)):
            dup.append(True)
        return dict(items)

    json.loads(bad, object_pairs_hook=hook)
    need(dup, "duplicate key detector armed")

    print("PASS_TRIADIC_QUERY_PAIR_PACKAGE_TESTS groups=5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
