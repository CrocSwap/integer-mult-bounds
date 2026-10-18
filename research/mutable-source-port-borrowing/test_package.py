#!/usr/bin/env python3
"""Real relocated executions and on-disk failure controls, including -O."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def run(path, cwd):
    return subprocess.run([sys.executable, "-O", "-B", str(path / "verify.py")],
                          cwd=cwd, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, timeout=120)


def main():
    rejected = []
    with tempfile.TemporaryDirectory(prefix="mutable-port-check-") as scratch:
        root = Path(scratch)
        positive = root / "read-only-export"
        shutil.copytree(HERE, positive, ignore=shutil.ignore_patterns("__pycache__"))
        try:
            if os.name == "posix":
                for p in positive.rglob("*"):
                    p.chmod(0o555 if p.is_dir() else 0o444)
                positive.chmod(0o555)
            good = run(positive, root)
            require(good.returncode == 0 and "PASS_MUTABLE_SOURCE_PORT_BORROWING" in good.stdout,
                    "relocated positive failed: " + good.stdout)
        finally:
            positive.chmod(0o700)
            for p in positive.rglob("*"):
                p.chmod(0o700 if p.is_dir() else 0o600)

        defects = {
            "certificate-undercharge": "certificate differs",
            "certificate-boolean": "certificate differs",
            "source-drift": "predecessor SHA256 drift",
            "source-omission": "missing or duplicate predecessor source",
            "missing-restore-code": "fixture word disagreement",
        }
        for name, expected in defects.items():
            path = root / name
            shutil.copytree(HERE, path, ignore=shutil.ignore_patterns("__pycache__"))
            if name.startswith("certificate-"):
                filename = path / "CERTIFICATE.json"
                value = json.loads(filename.read_text())
                if name == "certificate-undercharge":
                    value["fixtures"][0]["stats"]["commands"] -= 1
                else:
                    value["schema_version"] = True
                filename.write_text(json.dumps(value))
            elif name == "source-drift":
                filename = path / "references/PR1057-borrow.py"
                filename.write_bytes(filename.read_bytes() + b"\n# unpinned drift\n")
            elif name == "source-omission":
                filename = path / "PREDECESSORS.json"
                value = json.loads(filename.read_text())
                value[-1] = value[0].copy()
                filename.write_text(json.dumps(value))
            else:
                filename = path / "engine.py"
                content = filename.read_text()
                before = "return result if sign > 0 else inverse(result)"
                require(content.count(before) == 1, "code mutation target drifted")
                filename.write_text(content.replace(before, "return result[:-1] if sign > 0 else inverse(result)"))
            bad = run(path, root)
            require(bad.returncode != 0 and expected in bad.stdout and "PASS_MUTABLE" not in bad.stdout,
                    "corruption accepted or wrong failure: " + name + "\n" + bad.stdout)
            rejected.append(name)
    print("PASS_MUTABLE_PORT_PACKAGE relocation=1 corruptions=" + str(len(rejected)))


if __name__ == "__main__":
    main()
