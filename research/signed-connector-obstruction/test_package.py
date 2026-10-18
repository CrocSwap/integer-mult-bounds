#!/usr/bin/env python3
"""Relocation, deterministic generation and fail-closed package controls."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run(root, script):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(root/script)],
                          cwd=root.parent, text=True, capture_output=True)


def snapshot(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def main():
    with tempfile.TemporaryDirectory(prefix="signed connector check ") as d:
        root = Path(d)/"relocated package"
        shutil.copytree(ROOT, root)
        before = snapshot(root)
        result = run(root, "verify.py")
        require(result.returncode == 0, result.stderr)
        require(before == snapshot(root), "default verification mutated the package")
        result = run(root, "generate.py")
        require(result.returncode == 0, result.stderr)
        require(before == snapshot(root), "certificate regeneration was not byte-identical")
        certificate = json.loads((root/"CERTIFICATE.json").read_text())
        mutations = [
            ("missing query", lambda c: c["canonical"]["word"].pop()),
            ("missing path class", lambda c: c["distinct_path_masks"].pop()),
            ("missing obstructed pattern", lambda c: c["obstructed_patterns"].pop()),
            ("unpaid leaf", lambda c: c["recursive"].update(leaf_calls=307)),
            ("unpaid dirty row", lambda c: c["recursive"].update(dirty_arrays=3)),
            ("unpaid minimum", lambda c: c["canonical"].update(minimum_queries=12)),
        ]
        controls = 0
        for label, mutate in mutations:
            edited = json.loads(json.dumps(certificate))
            mutate(edited)
            (root/"CERTIFICATE.json").write_text(json.dumps(edited))
            result = run(root, "verify.py")
            require(result.returncode != 0 and "ValueError" in result.stderr,
                    "accepted mutation: " + label)
            controls += 1
        (root/"CERTIFICATE.json").write_bytes((ROOT/"CERTIFICATE.json").read_bytes())
        for relative in ("EXPECTED.json", "sources/PR934-README.md", "SOURCES.json"):
            p = root/relative
            original = p.read_bytes()
            if relative == "EXPECTED.json":
                changed = json.loads(original)
                changed["support_attained"] -= 1
                p.write_text(json.dumps(changed))
            elif relative == "SOURCES.json":
                changed = json.loads(original)
                changed["retained_files"][0]["sha256"] = "0"*64
                p.write_text(json.dumps(changed))
            else:
                p.write_bytes(original+b"\ncorruption control\n")
            result = run(root, "verify.py")
            require(result.returncode != 0 and "ValueError" in result.stderr,
                    "accepted mutation: " + relative)
            p.write_bytes(original)
            controls += 1
        require(before == snapshot(root), "controls did not restore relocated package")
    print(f"PASS_SIGNED_CONNECTOR_PACKAGE relocation=1 regeneration=1 corruptions={controls}")


if __name__ == "__main__":
    main()
