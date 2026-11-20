#!/bin/bash
# Full check: (1) package + Python side, (2) regenerate the 340 large data modules byte-identical,
# (3) guarded sequential Lean build of the 703-module closure and #print axioms of every headline (lean/check.sh).
# Needs python3 (stdlib) and, for step 3, elan with the pinned toolchain + `lake exe cache get` for Mathlib.
# Env passed through to the build: RSS_CAP_KB (per-file RSS guard, default 3500000; 0 = off), WAIT_IDLE=1.
set -eu
cd "$(dirname "$0")"
python3 -B verify.py
python3 -B tools/regen.py
python3 -B verify.py
( cd lean && ./check.sh )
