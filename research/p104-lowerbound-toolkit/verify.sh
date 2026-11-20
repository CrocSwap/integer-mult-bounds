#!/bin/bash
# Full check: (1) package + Python side (incl. FrameCert byte-identical regeneration), (2) guarded sequential Lean build
# of the 351-module closure and #print axioms of every headline theorem (lean/check.sh).
# Needs python3 (stdlib) and, for step 2, elan with the pinned toolchain + `lake exe cache get` for Mathlib.
# Env passed through to the build: RSS_CAP_KB (per-file RSS guard, default 3500000; 0 = off), WAIT_IDLE=1.
set -eu
cd "$(dirname "$0")"
python3 -B verify.py
( cd lean && ./check.sh )
