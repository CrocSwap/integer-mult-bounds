#!/usr/bin/env bash
# FULL=1 stage of verify.sh: re-run the OWN verification of every merged package this note depends on (README sections 1 and 3-5), from the
# repository checkout that contains this package (siblings research/<pkg>/).  Each package's default verify.sh is run unchanged, sequentially
# (one package at a time, each under its own caps and timeouts).  usage: bash verify_deps.sh OUTDIR     env: PYTHON=  KISSAT=  DRAT_TRIM=
# Prints one PASS/FAIL line per package.  Total about 2-3 hours on a laptop.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); R=$(cd "$HERE/.." && pwd); ROOT=$(cd "$R/.." && pwd); OUT=${1:?outdir}; mkdir -p "$OUT"
PY="${PYTHON:-python3}"; export PYTHON="$PY"
# package : depended-on PR(s) : what the README uses
DEPS="one-sided-decoders-all-m:#2816:Lemma 3.1, R1-R4, cover.py/d7.py cover facts, direction-list completeness, g(5)=12
nine-term-outside-colspace:#2724:m=9 one-sided floor, P104 >= 56
one-sided-six-multisets:#2826:<=3 non-full corrections
e8-rank9-realisations:#2819:rank-9 classification
a2-family-decoder-floors:#2784:A2 family floors
decoder-floors-closures:#2639:label windows h=10,11; per-term floors
punctured-e8-48-56:#2806:punctured units"
echo "$DEPS" | while IFS=: read -r pkg pr what; do
  d="$R/$pkg"; [ -f "$d/verify.sh" ] || { echo "FAIL dep $pr ($pkg): no verify.sh in checkout"; continue; }
  s=$SECONDS; ( cd "$d" && nice -n 10 bash verify.sh "$OUT/$pkg" ) > "$OUT/$pkg.log" 2>&1; rc=$?
  if [ $rc = 0 ] && ! grep -q '^FAIL' "$OUT/$pkg.log"; then echo "PASS dep $pr merged and rechecked ($pkg: $what) in $((SECONDS-s))s"; else echo "FAIL dep $pr ($pkg) rc=$rc; see $OUT/$pkg.log"; fi
done
for pkg in dn-unrestricted-root-code-floor:#2719 overcomplete-rank-interface:#2694; do
  p=${pkg%%:*}; pr=${pkg##*:}
  ( cd "$ROOT" && "$PY" -I -B scripts/research_package.py --package "research/$p" ) > "$OUT/$p.log" 2>&1; rc=$?
  if [ $rc = 0 ]; then echo "PASS dep $pr merged and rechecked ($p: registered replay of its own checks)"; else echo "FAIL dep $pr ($p) rc=$rc"; fi
done
