#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Portable exact replay of the generic parametric block cascade schedule for all m >= 4. Apache-2.0."""
from pathlib import Path
from hashlib import sha256
import json, subprocess, sys, tempfile
P = Path(__file__).resolve().parent

def need(ok, text):
    if not ok:
        raise ValueError(text)

def main():
    manifest = json.loads((P / "MANIFEST.json").read_text(encoding="utf8"))
    actual = {
        p.relative_to(P).as_posix()
        for p in P.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.name != "MANIFEST.json"
    }
    need(actual == set(manifest), "package inventory mismatch")
    for name, h in manifest.items():
        need(sha256((P / name).read_bytes()).hexdigest() == h, "package source drift: " + name)
    for row in json.loads((P / "SOURCE-PINS.json").read_text(encoding="utf8")):
        need(sha256((P / row["file"]).read_bytes()).hexdigest() == row["sha256"], "predecessor source drift: " + row["file"])
    expected = json.loads((P / "CHECKS.json").read_text(encoding="utf8"))
    with tempfile.TemporaryDirectory(prefix="generic-cascade-cache-") as cache:
        for name, want in expected.items():
            argv = [sys.executable, "-I", "-B", "-X", "pycache_prefix=" + cache]
            if sys.flags.optimize:
                argv.append("-O")
            argv.append(str(P / name))
            job = subprocess.run(argv, check=True, capture_output=True, text=True, encoding="utf8", timeout=180, cwd=P)
            got = json.loads(job.stdout)
            need(got == want, "changed mathematical receipt: " + name)
            print(got["status"])
    print("PASS_GENERIC_PARAMETRIC_CASCADE_FAMILY")

if __name__ == "__main__":
    main()
