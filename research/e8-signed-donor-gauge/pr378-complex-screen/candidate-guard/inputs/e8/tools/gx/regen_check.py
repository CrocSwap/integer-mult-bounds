#!/usr/bin/env python3
"""Regenerate the Lean modules of a generalised certificate (gcert/1) and compare them with this repository.

usage (from anywhere):  python3 tools/gx/regen_check.py [<certificate> <Name> <Inst>] [--keep <dir>]
default:                tools/certificate/gcert1-p11-pr193.json.gz P193 B2Gp193

Runs, into a fresh directory (a temporary one, or <dir> with --keep; never into the source tree):
    tools/gx/gxgen.py <certificate> <Name>      Python mirror of both Lean checks, then data and check modules
    tools/gx/gxrate.py <Inst> <Name>            rate lemmas, unit price list, final modules, comparator package
and compares every generated Lean file with the file of the same path in this repository, and every generated
comparator configuration with comparator/<same name>.  A generated file that this repository does not contain
is listed as "(not in the repository)".  Exit code 0 = no generated file differs and at least one was compared.

Needs only Python 3 (standard library).  No Lean is run.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT = ["tools/certificate/gcert1-p11-pr193.json.gz", "P193", "B2Gp193"]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main():
    args = sys.argv[1:]
    keep = None
    if "--keep" in args:
        i = args.index("--keep")
        keep = os.path.abspath(args[i + 1])
        del args[i:i + 2]
        if os.path.exists(keep) and os.listdir(keep):
            sys.exit("--keep: the directory must be empty or absent: " + keep)
        os.makedirs(keep, exist_ok=True)
    cert, name, inst = args if len(args) == 3 else DEFAULT
    out = keep or tempfile.mkdtemp(prefix="regen-gx-")
    print("certificate %s\n  sha256 %s" % (cert, sha(os.path.join(ROOT, cert))))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", GX_OUT=out)
    for cmd in (["tools/gx/gxgen.py", cert, name], ["tools/gx/gxrate.py", inst, name]):
        print("$ GX_OUT=<fresh directory> python3 " + " ".join(cmd), flush=True)
        r = subprocess.run([sys.executable] + cmd, cwd=ROOT, env=env)
        if r.returncode != 0:
            sys.exit("generator failed with exit code %d" % r.returncode)
    made = sorted(os.path.relpath(os.path.join(d, f), out) for d, _, fs in os.walk(out) for f in fs)
    same = diff = extra = 0
    for rel in made:
        if rel.startswith("logs/"):
            continue                                   # figures passed between the two generators
        tgt = "comparator/" + rel[4:] if rel.startswith("cmp/") else rel
        a, b = os.path.join(out, rel), os.path.join(ROOT, tgt)
        if not os.path.isfile(b):
            extra += 1
            print("(not in the repository)        %s" % tgt)
            continue
        ok = open(a, "rb").read() == open(b, "rb").read()
        same += ok
        diff += not ok
        print("%-9s %9d bytes  %s  %s" % ("IDENTICAL" if ok else "DIFFERENT", os.path.getsize(a), sha(a)[:16], tgt))
    if keep is None:
        shutil.rmtree(out)
    else:
        print("generated files kept in " + keep)
    good = diff == 0 and same > 0
    print("RESULT: %s (%d repository files reproduced byte for byte, %d different, %d generated files not in the repository)"
          % ("REPRODUCED" if good else "FAIL", same, diff, extra))
    sys.exit(0 if good else 1)


if __name__ == "__main__":
    main()
