#!/usr/bin/env python3
"""Regenerate lean/Nov15/FrameCert.lean: python3 asm.py OUT.lean   (same as: gen.py 0 DATA 24; head + data + tail_a + thms + tail_b)."""
import subprocess, sys, tempfile, os
H = os.path.dirname(os.path.abspath(__file__))
with tempfile.TemporaryDirectory() as td:
    d = os.path.join(td, "data.lean")
    subprocess.run([sys.executable, "-I", os.path.join(H, "gen.py"), "0", d, "24"], check=True, stdout=subprocess.DEVNULL)
    rd = lambda p: open(p, encoding="utf-8").read()
    out = (rd(os.path.join(H, "head.lean")) + rd(d) + rd(os.path.join(H, "tail_a.lean"))
           + rd(d + ".thms") + rd(os.path.join(H, "tail_b.lean")))
open(sys.argv[1], "w", encoding="utf-8").write(out)
