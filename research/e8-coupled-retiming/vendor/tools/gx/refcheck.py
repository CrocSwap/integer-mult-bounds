#!/usr/bin/env python3
"""Reference check of a certificate of format gcert/1 (written for this repository; the check itself is gx.check1).

usage: python3 tools/gx/refcheck.py [<certificate.json[.gz]>] [noscalar]
default certificate: tools/certificate/gcert1-p11-pr193.json.gz

Loads the file and runs `gx.check1`: sizes and normal forms, the frame of every register along the program
(nesting, equal frames at every addition), the block list and the count of unit moves, and, unless `noscalar`
is given, the exact scalar identity.  Prints ACCEPTED and the statistics of the run, or the rule that failed.
Python 3, standard library only; no Lean.
"""
import sys
import time
import gxpaths
import gx
import gxrun

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "noscalar"]
    path = args[0] if args else gxpaths.REPO + "tools/certificate/gcert1-p11-pr193.json.gz"
    t0 = time.time()
    c = gxrun.load(path)
    st = {}
    try:
        gx.check1(c, scalar="noscalar" not in sys.argv, stats=st)
    except AssertionError as e:
        print("REJECTED: %s" % e)
        sys.exit(1)
    print("ACCEPTED by gx.check1: h=%d v=%d R=%d N=%d gates A=%d B=%d; stats %s (%.1fs)" % (
        c["h"], c["v"], c["R"], c["N"], len(c["A"]), len(c["B"]), st, time.time() - t0))
