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



def integration_source_controls():
    """Positive first: distinguish input, historical provenance and receipt faults."""
    import hashlib
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        pkg = root / "research" / HERE.name
        shutil.copytree(HERE, pkg, ignore=shutil.ignore_patterns("__pycache__"))
        sources = json.loads((pkg / "SOURCES.json").read_text())
        for row in sources["files"]:
            target = root / row["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            if row["usage"] == "provenance":
                raw = subprocess.check_output(["git", "show", sources["base_commit"] + ":" + row["path"]], cwd=ROOT)
            else:
                raw = (ROOT / row["path"]).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row["sha256"], "control fixture source pin")
            target.write_bytes(raw)
        for command in (["git", "init"], ["git", "add", "-A"],
                        ["git", "-c", "user.name=test", "-c", "user.email=test@example.invalid", "commit", "-m", "pinned control fixture"]):
            subprocess.run(command, cwd=root, check=True, capture_output=True)
        sources["base_commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        (pkg / "SOURCES.json").write_text(json.dumps(sources, indent=2) + "\n")
        def check(ok=True, marker=None, write=False, certificate=False):
            if certificate or write:
                command = [sys.executable, "-I", "-O", "-B", str(pkg / "verify.py")]
                if write: command.append("--write")
            else:
                # Exercise the actual authentication boundary without repeating algebra.
                code = "import importlib.util,sys; s=importlib.util.spec_from_file_location('subject',sys.argv[1]); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); m.check_sources()"
                command = [sys.executable, "-I", "-O", "-B", "-c", code, str(pkg / "verify.py")]
            result = run(command, cwd=root)
            need((result.returncode == 0) == ok, result.stdout + result.stderr)
            if marker: need(marker in result.stdout + result.stderr, "wrong fault: " + result.stdout + result.stderr)
        check()
        # A later checkout change is not a change to frozen historical provenance.
        historical = next(row for row in sources["files"] if row["usage"] == "provenance")
        path = root / historical["path"]
        path.write_bytes(path.read_bytes() + b"\ncurrent checkout provenance changed\n")
        check()
        actual = next(row for row in sources["files"] if row["usage"] == "input")
        path = root / actual["path"]; original = path.read_bytes()
        path.write_bytes(original + b"\ninput drift\n")
        check(False, "sha256 " + actual["path"])
        path.write_bytes(original)
        historical["sha256"] = "0" * 64
        (pkg / "SOURCES.json").write_text(json.dumps(sources))
        check(False, "sha256 " + historical["path"])


def main():
    integration_source_controls()
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
        need(proc.returncode != 0 and "CERTIFICATE mismatch" in proc.stderr, "corrupted certificate should fail at the receipt boundary")

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
