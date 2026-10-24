#!/usr/bin/env python3
"""Regenerate the Lean modules of the E8 certificate and compare them with this repository.

usage (from anywhere):  python3 tools/gx/regen_check_e8.py [--keep <dir>]

This runs tools/gx/regen_check.py, unchanged, with the arguments of the E8 certificate:

    python3 tools/gx/regen_check.py tools/certificate/gcert1-e8-r783.json.gz E8 B2Ge8

so that each certificate of this repository has one command without arguments.  Before that it checks that
the certificate file has the expected sha256.  The two generators (tools/gx/gxgen.py, tools/gx/gxrate.py)
write, into a fresh directory, the 24 Lean modules under Work/GCert/Data/ that carry the names E8 and B2Ge8
and the comparator configuration comparator/B2Ge8x.json; every generated file is compared byte for byte with
the file of the same path in this repository.  Expected last line, exit code 0:

    RESULT: REPRODUCED (25 repository files reproduced byte for byte, 0 different, 3 generated files not in the repository)

The three generated files that are not in the repository are the eight-decimal variant (ChallengeB2Ge8,
SolutionB2Ge8 and its comparator configuration), as for the certificate P193.  The exit code is that of
tools/gx/regen_check.py: 0 when no generated file differs and at least one was compared, so read the counts
of the last line as well.

Needs only Python 3 (standard library).  No Lean is run.
"""
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ARGS = ["tools/certificate/gcert1-e8-r783.json.gz", "E8", "B2Ge8"]
CERT_SHA256 = "4b92f00fc7454b9b15e6d71a3b05062792eacca0a0ca4efee46f87827d57c8aa"

extra = sys.argv[1:]
if extra and not (len(extra) == 2 and extra[0] == "--keep"):
    sys.exit(__doc__)
got = hashlib.sha256(open(os.path.join(ROOT, ARGS[0]), "rb").read()).hexdigest()
if got != CERT_SHA256:
    sys.exit("RESULT: FAIL (%s has sha256 %s, expected %s)" % (ARGS[0], got, CERT_SHA256))
sys.exit(subprocess.run([sys.executable, os.path.join(HERE, "regen_check.py")] + ARGS + extra).returncode)
