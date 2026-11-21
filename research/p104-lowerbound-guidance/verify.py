#!/usr/bin/env python3
"""Checks of the p104-lowerbound-guidance package (standard library only; Lean is NOT run here).

1. File pins: MANIFEST.sha256, both directions.  2. lean_extra/*.lean: no sorry/admit/native_decide/axiom/opaque/unsafe/
implemented_by/extern/ofReduceBool outside comments and strings (sources only, not rebuilt).  3. Scrub scan: no owner
name/email/local absolute paths/session links in any stored text file.  4. Exact certificates: certs/verify_q0.py,
certs/verify_q1.py.  5. Witnesses: data/q0_callers/check_all.py, data/direct_sum/check.py, data/tight55_gap/check.py,
code/ctcover/ctsplit.py (R = 2 < mass 3), code/decomp/dc1.py (DECOMP word).  6. Evidence file for ZIGZAG present.

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
"""
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parent
FORBIDDEN = ["sorry", "admit", "native_decide", "axiom", "opaque", "unsafe", "implemented_by", "extern", "ofReduceBool"]
SCRUB = re.compile(r"mason|ellerbroek|gmail|/Users/|claude\.ai/code|session_0", re.I)
TEXT = {".md", ".py", ".sh", ".c", ".lean", ".json", ".txt", ".log", ".out", ".sha256", ".tsv", ".toml"}


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def strip_lean(src):
    out, i, n, depth = [], 0, len(src), 0
    while i < n:
        if src.startswith("/-", i):
            depth += 1; i += 2; continue
        if depth:
            if src.startswith("-/", i):
                depth -= 1; i += 2
            else:
                i += 1
            continue
        if src.startswith("--", i):
            j = src.find("\n", i); i = n if j < 0 else j; continue
        if src[i] == '"':
            j = i + 1
            while j < n and src[j] != '"':
                j += 2 if src[j] == "\\" else 1
            i = j + 1; continue
        out.append(src[i]); i += 1
    return "".join(out)


def files():
    for p in sorted(PKG.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
            yield p


def manifest():
    pins = {}
    for line in (PKG / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        h, _, rel = line.partition("  ")
        pins[rel] = h
    seen = {}
    for p in files():
        rel = p.relative_to(PKG).as_posix()
        if rel == "MANIFEST.sha256":
            continue
        seen[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    if set(pins) != set(seen):
        fail("MANIFEST file set differs: missing %s, extra %s" % (sorted(set(pins) - set(seen))[:5], sorted(set(seen) - set(pins))[:5]))
    bad = [r for r in pins if pins[r] != seen[r]]
    if bad:
        fail("hash mismatch: %s" % bad[:5])
    print("manifest: %d files pinned" % len(pins))


def lean_tokens():
    n = 0
    for p in sorted((PKG / "lean_extra").glob("*.lean")):
        code = strip_lean(p.read_text(encoding="utf-8"))
        for w in FORBIDDEN:
            if re.search(r"(?<![A-Za-z0-9_.])" + w + r"(?![A-Za-z0-9_])", code):
                fail("%s contains forbidden token %s" % (p.name, w))
        n += 1
    print("lean_extra: %d sources, no forbidden tokens outside comments" % n)


def scrub():
    n = 0
    for p in files():
        if p.suffix in TEXT or p.name in ("LICENSE", "NOTICE.md"):
            if p.name == "verify.py":
                continue
            t = p.read_text(encoding="utf-8", errors="replace")
            m = SCRUB.search(t)
            if m:
                fail("scrub: %s contains %r" % (p.relative_to(PKG), m.group(0)))
            n += 1
    print("scrub: %d text files clean" % n)


def run(argv, cwd, must, no_dash_i=False):
    r = subprocess.run([sys.executable, "-B"] + ([] if no_dash_i else ["-I"]) + argv, cwd=str(PKG / cwd),
                       capture_output=True, text=True, timeout=500)
    out = r.stdout + r.stderr
    if r.returncode != 0:
        fail("%s failed:\n%s" % (argv, out[-1500:]))
    for s in must:
        if s not in out:
            fail("%s: expected %r in output:\n%s" % (argv, s, out[-1500:]))
    print("ok: %s %s" % (cwd, " ".join(argv)))
    return out


def main():
    manifest()
    lean_tokens()
    scrub()
    run(["verify_q0.py"], "certs", ["PASS", "k=72", "BELOW", "128.85007"])
    run(["verify_q1.py"], "certs", ["PASS", "k77 [", "BELOW"])
    run(["check_all.py"], "data/q0_callers", ["PASS 15"])
    run(["check.py"], "data/direct_sum", ["PASS"])
    run(["check.py"], "data/tight55_gap", ["PASS"])
    out = run(["ctsplit.py"], "code/ctcover", ["mass >= 3 over every field"], no_dash_i=True)
    if out.count("R 2 odd pattern") != 2 and out.count(" R 2 ") != 2:
        fail("ctsplit: expected R = 2 over both GF(2) and Q")
    run(["dc1.py"], "code/decomp", ["ALL OK"], no_dash_i=True)
    if not (PKG / "code/unify/evidence/zzcx.log.txt").exists():
        fail("missing ZIGZAG evidence log")
    print("PASS")


if __name__ == "__main__":
    main()
