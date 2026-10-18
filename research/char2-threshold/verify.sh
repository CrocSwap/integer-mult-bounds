#!/usr/bin/env bash
# One-command verification of research/char2-threshold (no kappa claim): exact F2 costs of the full-orthogonal-pattern pairings of root units D4, D5, D6, E6, E7, E8
# (and A4-A6 as upper bounds) against T^2, and the exact minimum cost of a Fano Levi-graph realisation over Q at T = 4, 5.  Step 0 checks the package against
# MANIFEST.sha256 and every pin of SOURCES.json and stops hard on any mismatch.  Single process; standard library Python and a C compiler only.
#   usage: bash verify.sh [/fresh/output/dir]     (inside a checkout or `git archive` of the repository; nothing outside the package is read)
#   set PYTHON to choose the interpreter (>= 3.11), CC for the compiler.  Not re-run here: the annealing / clique / lattice-pool searches and the numerical (Levenberg-Marquardt) realisability runs (README, RECORDED).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/char2-threshold.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; CC="${CC:-cc}"; export PYTHONDONTWRITEBYTECODE=1
T0=$SECONDS
echo "== 0. manifest and provenance"
if ! "$PY" -B "$HERE/scripts/provenance.py" | tee "$OUT/provenance.log" | sed 's/^/   /' || grep -q '^FAIL' "$OUT/provenance.log" \
   || [ "$(grep -c '^PASS' "$OUT/provenance.log")" != 2 ]; then
  echo "step 0 FAILED"; exit 1
fi
R="$OUT/tree"; mkdir -p "$R" "$OUT/logs" "$R/bin"
cp -R "$HERE/checks" "$HERE/lib" "$HERE/data" "$HERE/c" "$R/"
export C2T_BIN="$R/bin"
E_="$PY -B $R/checks/expect.py"
run() { local n=$1; shift; ( cd "$R/checks" && "$@" > "$OUT/logs/$n.log" 2>&1; echo $? > "$OUT/logs/$n.rc" ); }
chk() { local l=$1 n=$2; shift 2; $E_ "$l" "$OUT/logs/$n.log" "$@" | tee -a "$OUT/all.out"; }

echo "== G0 compile the C program from source"
if "$CC" -O2 -o "$R/bin/kgap" "$R/c/kgap.c" -lm > "$OUT/logs/cc.log" 2>&1; then echo "PASS G0.compile  kgap" | tee -a "$OUT/all.out"; else echo "FAIL G0.compile  see $OUT/logs/cc.log" | tee -a "$OUT/all.out"; fi

echo "== G1 root units: exact decoders and F2 costs against T^2"
run units $PY -B units.py
chk G1.D-ties units --has '^UN D4 v=12 T=4 .*decoder exact \(M = Gram\): True; B admissible: True; .*block ranks \[3, 3, 3, 3\]; cost 12; T\^2 = 16; cost - v = 0$' \
    --has '^UN D5 v=20 T=5 .*decoder exact \(M = Gram\): True; B admissible: True; .*block ranks \[4, 4, 4, 4, 4\]; cost 20; T\^2 = 25; cost - v = 0$' \
    --has '^UN D6 v=30 T=6 .*decoder exact \(M = Gram\): True; B admissible: True; .*block ranks \[5, 5, 5, 5, 5, 5\]; cost 30; T\^2 = 36; cost - v = 0$'
chk G1.E6-tie units --has '^UN E6 v=36 T=6 .*decoder exact \(M = Gram\): True; B admissible: True; stored basis and stored B .*block ranks \[6, 6, 6, 6, 6, 6\]; cost 36; T\^2 = 36; cost - v = 0$' \
    --has '^UN E6 B0 in the stored basis costs 36; in the first-independent basis 37$'
chk G1.E7-gain units --has '^UN E7 v=63 T=7 rank\(L\)=7 decoder exact \(M = Gram\): True; B admissible: True; .*block ranks \[7, 7, 7, 7, 7, 7, 7\]; cost 49; T\^2 = 49; cost - v = -14$'
chk G1.E8-gain units --has '^UN E8 v=120 T=8 rank\(L\)=8 decoder exact \(M = Gram\): True; B admissible: True; .*block ranks \[9, 9, 9, 9, 9, 9, 9, 9\]; cost 72; T\^2 = 64; cost - v = -48$'
chk G1.A-above units --has '^UN A4 v=10 T=4 .*cost 16; T\^2 = 16; cost - v = 6$' --has '^UN A5 v=15 T=5 .*cost 25; T\^2 = 25; cost - v = 10$' --has '^UN A6 v=21 T=6 .*cost 36; T\^2 = 36; cost - v = 15$' --absent 'Traceback' --absent 'False'

echo "== G2 Fano Levi graph over Q: exact minimum cost"
run fano $PY -B fano.py
chk G2.fano-T4 fano --has '^FL T=4: rank\(P Q\^T\) = 4 with all 4 blocks nonempty: True; zero pattern contains a Fano plane .* True; 7 distinct points True, diagonals nonzero True, .*exact minimum F2 cost over all 2\^f admissible B = 9, v = 7, cost - v = 2$'
chk G2.fano-T5 fano --has '^FL T=5: rank\(P Q\^T\) = 5 with all 5 blocks nonempty: True; zero pattern contains a Fano plane .* True; 7 distinct points True, diagonals nonzero True, .*exact minimum F2 cost over all 2\^f admissible B = 13, v = 7, cost - v = 6$' --absent 'Traceback'

EXPECT=8
npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out")
echo "== done in $((SECONDS - T0))s: $((npass + 2)) PASS (2 in step 0), $nfail FAIL; logs in $OUT"
[ "$nfail" = 0 ] && [ "$npass" = "$EXPECT" ] || { echo "FAILED: expected $EXPECT assertion PASS lines after step 0, got $npass PASS / $nfail FAIL"; exit 1; }
