#!/usr/bin/env bash
# One-command verification of research/root-unit-decoder-lemmas (no kappa claim): two lemmas on root-unit decoders under #446 Theorem C, the
# erratum ERR1 to #595, and the D5 three-total SAT instance (regeneration and hash only).  Step 0 checks the package against MANIFEST.sha256 and
# every pin of SOURCES.json and stops hard on any mismatch.  Then five check groups run one after the other (single process, numpy and
# python-sat only) and print one PASS/FAIL line per assertion.  Exit status 0 only if every assertion passes.
#   usage: bash verify.sh [/fresh/output/dir]     (inside a checkout or `git archive` of the repository; nothing outside the package is read)
#   needs python3 >= 3.11 with numpy and python-sat (requirements.txt); set PYTHON to choose the interpreter.  No solver is run.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/root-unit-decoder-lemmas.XXXXXX")}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1
T0=$SECONDS
echo "== 0. manifest and provenance"
if ! "$PY" -B "$HERE/scripts/provenance.py" | tee "$OUT/provenance.log" | sed 's/^/   /' || grep -q '^FAIL' "$OUT/provenance.log" \
   || [ "$(grep -c '^PASS' "$OUT/provenance.log")" != 2 ]; then
  echo "step 0 FAILED"; exit 1
fi
# work tree: scripts write scratch files here, never into the package
R="$OUT/tree"; mkdir -p "$R" "$OUT/logs"
cp -R "$HERE/checks" "$HERE/lib" "$HERE/sat" "$HERE/SOURCES.json" "$R/"
export TMPDIR="$OUT/tmp"; mkdir -p "$TMPDIR"
E_="$PY -B $R/checks/expect.py"
run() { local n=$1; shift; ( cd "$R/checks" && "$@" > "$OUT/logs/$n.log" 2>&1; echo $? > "$OUT/logs/$n.rc" ); }
chk() { local l=$1 n=$2; shift 2; $E_ "$l" "$OUT/logs/$n.log" "$@" | tee -a "$OUT/all.out"; }

echo "== G1 Lemma A: T <= 2 table and instances"
run lemma_a $PY -B lemma_a.py
for u in A3 A4 A5 A6 A7 A8 D4; do chk G1.closed-$u lemma_a --has "^$u v=[0-9]+ w=[0-9]+ h0=[0-9]+ budget cst<=[0-9]+ Tmax=[12] CLOSED by T<=2 lemma$"; done
for u in D5 D6 D7 D8 E6 E7; do chk G1.open-$u lemma_a --has "^$u v=[0-9]+ w=[0-9]+ h0=[0-9]+ budget cst<=[0-9]+ Tmax=[3-9] OPEN \(T>=3 needed\)$"; done
chk G1.tmax-values lemma_a --has "^D5 v=20 w=4 h0=5 budget cst<=14 Tmax=3 " --has "^D6 v=30 w=5 h0=5 budget cst<=21 Tmax=4 " --has "^D7 v=42 w=6 h0=6 budget cst<=28 Tmax=4 " \
    --has "^D8 v=56 w=7 h0=7 budget cst<=36 Tmax=5 " --has "^E6 v=36 w=5 h0=5 budget cst<=25 Tmax=5 " --has "^E7 v=63 w=7 h0=7 budget cst<=40 Tmax=5 "
chk G1.proof-inequalities lemma_a --has "^TOTAL instances 2100 violations 0 tight 238 min\(r1\+r2-v\) 0$" --count "violations 0 tight" 8 --absent "Traceback"

echo "== G2 window table"
run windows $PY -B windows.py
chk G2.D5 windows --has "^D5 v=20 w=4 3w=12 2v/3->14 N: h7-8 13 \| top N=13 \(3w\+1=13\) \| all N <= ceil\(2v/3\): True$"
chk G2.D6 windows --has "^D6 v=30 w=5 3w=15 2v/3->20 N: h7 20, h8 19, h9-10 18, h11-13 17, h14-17 16 \| top N=16 \(3w\+1=16\) \| all N <= ceil\(2v/3\): True$"
chk G2.D7 windows --has "^D7 v=42 w=6 3w=18 2v/3->28 N: h7 28, h8 27, h9 26, h10 25, h11-12 24, h13-14 23, h15-17 22, h18-19 21, h20-21 20, h22-24 19 \| top N=19 \(3w\+1=19\) \| all N <= ceil\(2v/3\): True$"
chk G2.D8 windows --has "^D8 v=56 w=7 3w=21 2v/3->38 N: h7 37, h8 35, h9 34, h10 33, h11 32, h12-13 31, h14-15 30, h16-17 29, h18 28, h19-20 27, h21-22 26, h23-24 25, h25-26 24, h27 23, h28-29 22 \| top N=22 \(3w\+1=22\) \| all N <= ceil\(2v/3\): True$"
chk G2.E6 windows --has "^E6 v=36 w=5 3w=15 2v/3->24 N: h8 23, h9 22, h10-11 21, h12-14 20, h15-17 19, h18-19 18, h20-22 17, h23-25 16 \| top N=16 \(3w\+1=16\) \| all N <= ceil\(2v/3\): True$"
chk G2.E7 windows --has "^E7 v=63 w=7 3w=21 2v/3->42 N: h8 40, h9 38, h10 37, h11 36, h12-13 35, h14 34, h15-16 33, h17 32, h18-19 31, h20-21 30, h22 29, h23-24 28, h25 27, h26-27 26, h28-29 25, h30 24, h31-32 23, h33 22 \| top N=22 \(3w\+1=22\) \| all N <= ceil\(2v/3\): True$"
chk G2.two-thirds windows --has "^max N\(h\)/v over the listed windows 0\.6667 \(2/3 = 0\.6667\); every window covered by ceil\(2v/3\): True$"

echo "== G3 Lemma B: lift identity"
run lemma_b $PY -B lemma_b.py
chk G3.random-decoders lemma_b --has "^PART1 instances 720 violations 0$" --count "random decoders x lifts 180 violations 0" 4
chk G3.E6-dyadic lemma_b --count "^E6 v 36 T 6 lift .*: identity True sum rank_Q >= [0-9]+ >= v True \| sum rank_F2 B0 blocks 37 < v False$" 3
chk G3.E7-dyadic lemma_b --count "^E7 v 63 T 7 lift .*: identity True sum rank_Q >= [0-9]+ >= v True \| sum rank_F2 B0 blocks 49 < v True$" 3
chk G3.E8-dyadic lemma_b --count "^E8 v 120 T 8 lift .*: identity True sum rank_Q >= [0-9]+ >= v True \| sum rank_F2 B0 blocks 72 < v True$" 3 --has "^E8 v 120 T 8 lift B0 itself \(0/1 lift\): identity True sum rank_Q >= 426 "
chk G3.fano-illustration lemma_b --has "^FANO incidence 7x7: rank_F2 4 rank_Q 7 \(illustration only\)$"

echo "== G4 ERR1: dyadic decoders"
run err1 $PY -B err1.py
chk G4.E8 err1 --has "^E8 v 120 totals 8 exact P Q\^T == G: True dyadic: True rankF2 B0 9$" --has "^E8 M = G has M_tt != 0 and M_ts = 0 where B0_ts = 1: True \| totals 8 < rankF2 B0 9: True$" --has "^E8 block ranks r_j \[9, 9, 9, 9, 9, 9, 9, 9\] sum 72$"
chk G4.E6 err1 --has "^E6 v 36 totals 6 exact P Q\^T == G: True dyadic: True rankF2 B0 7$" --has "^E6 M = G has M_tt != 0 and M_ts = 0 where B0_ts = 1: True \| totals 6 < rankF2 B0 7: True$" --has "^E6 block ranks r_j \[6, 7, 6, 6, 6, 6\] sum 37$"
chk G4.A-series err1 --has "^A4 M = G .*totals 4 < rankF2 B0 5: True$" --has "^A6 M = G .*totals 6 < rankF2 B0 7: True$" --has "^A8 M = G .*totals 8 < rankF2 B0 9: True$"
chk G4.all-exact err1 --count "exact P Q\^T == G: True dyadic: True" 6 --absent "exact P Q\^T == G: False" --absent "Traceback"

echo "== G5 D5 three-total CNF"
( cd "$R/sat" && "$PY" -B gen.py D5 3 4,4,4 "$OUT/d5_zr.cnf" --sb --C7 --zero --rref > "$OUT/logs/gen.log" 2>&1; echo $? > "$OUT/logs/gen.rc" )
chk G5.generator gen --has "vars 11131 clauses 39835$"
"$PY" -B "$R/checks/cnfcheck.py" "$OUT/d5_zr.cnf" "$R/SOURCES.json" | tee -a "$OUT/all.out"

npass=$(grep -c '^PASS' "$OUT/all.out"); nfail=$(grep -c '^FAIL' "$OUT/all.out")
echo "== done in $((SECONDS - T0))s: $((npass + 2)) PASS (2 in step 0), $nfail FAIL; logs in $OUT"
[ "$nfail" = 0 ] && [ "$npass" = 33 ] || { echo "FAILED: expected 33 assertion PASS lines after step 0, got $npass PASS / $nfail FAIL"; exit 1; }
