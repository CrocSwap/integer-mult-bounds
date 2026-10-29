#!/usr/bin/env bash
# Verification of research/one-sided-padding-lemma (no kappa claim).  usage: bash verify.sh    PYTHON=/path/to/python (needs sympy)
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1
fail=0; ok(){ echo "PASS $1"; }; bad(){ echo "FAIL $1"; fail=1; }
"$PY" -c "import sympy" 2>/dev/null || { echo "FAIL python needs sympy (PYTHON=...)"; exit 1; }
OUT=$(mktemp -d "${TMPDIR:-/tmp}/padver.XXXXXX")
echo "== 0. manifest"
(cd "$HERE" && grep -v '^#' MANIFEST.sha256 | shasum -a 256 -c - >"$OUT/m.out" 2>&1) && ok "MANIFEST.sha256 (all files match)" || { bad "manifest"; cat "$OUT/m.out"; }
echo "== 1. pad.py (implementation 1: root-vector rank_F2 vs label formula)"
timeout 1200 "$PY" -B "$HERE/checks/pad.py" >"$OUT/pad.log" 2>&1 || bad "pad.py exit"
[ "$(grep -c 'diff 8$' "$OUT/pad.log")" = 5 ] && grep -q '^PAD OK' "$OUT/pad.log" && ok "pad.py: 5 decoders (coordinate, root swaps k=1..4), exact over Q, cost(P120)=cost(P112)+8 by both costs" || bad "pad.py output"
grep -E 'cost \(A,B\)= \(([0-9]+), \1\)' "$OUT/pad.log" | wc -l | grep -q 5 && ok "pad.py: the two cost computations agree on every decoder" || bad "pad.py A=B"
echo "== 2. pad_audit.py (implementation 2: own E8, own labels, subspace algebra, with merging)"
timeout 1200 "$PY" -B "$HERE/checks/pad_audit.py" >"$OUT/aud.log" 2>&1 || bad "pad_audit.py exit"
[ "$(grep -c 'ok=True' "$OUT/aud.log")" = 12 ] && grep -q 'ALL diff==8: True n= 12' "$OUT/aud.log" && ok "pad_audit.py: 12 decoders, each exact over Q (P112 and E8), padded cost = normalised cost + 8" || bad "pad_audit.py output"
diff -q "$OUT/aud.log" "$HERE/expected/pad_audit.out" >/dev/null && ok "pad_audit.py output identical to expected/pad_audit.out" || bad "expected output differs"
rm -rf "$OUT"
[ $fail = 0 ] && echo "ALL PASS" || { echo "SOME FAILED"; exit 1; }
