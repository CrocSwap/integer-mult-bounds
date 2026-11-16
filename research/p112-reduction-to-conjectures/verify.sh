#!/usr/bin/env bash
# Verification of research/p112-reduction-to-conjectures.   usage: bash verify.sh [fresh/output/dir]
# PYTHON=/path/to/python (needs numpy; default python3), FULL=1 adds the heavy reruns (see PROOF_MAP.md; chunked, each < 20 min).
# At most 3 processes at a time; every process under `timeout 1200`; default run about 8 minutes.  No claim in this package is a kappa claim.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$(mktemp -d "${TMPDIR:-/tmp}/p112red.XXXXXX")}; mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$HERE"/*) echo "output dir must be outside the package"; exit 2;; esac
PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
C="$HERE/checks"; : > "$OUT/all.out"
note() { echo "$@" | tee -a "$OUT/all.out"; }
echo "== 0. manifest"
"$PY" -B "$C/manifest_check.py" | tee -a "$OUT/all.out" | sed 's/^/   /'; [ "${PIPESTATUS[0]}" = 0 ] || { echo "step 0 FAILED"; exit 1; }
echo "== 1. ledger recomputed from ledger2 + new_kills; compared with the shipped ledger3"
"$PY" -B "$C/build_ledger3.py" "$OUT/ledger3.csv" | tee -a "$OUT/all.out" | sed 's/^/   /'
cmp -s "$OUT/ledger3.csv" "$HERE/data/ledger3_consolidated.csv" && note "PASS ledger3_consolidated.csv reproduced byte-for-byte" || note "FAIL ledger3 differs"
echo "== 2. rerunnable checks (each: directory, command, required output line)"
export PY C OUT
run() { # name dir required-regex cmd...
  local n=$1 d=$2 req=$3; shift 3
  ( cd "$C/$d" && timeout 1200 "$@" > "$OUT/$n.log" 2>&1 ); local rc=$?
  if [ $rc = 0 ] && grep -Eq "$req" "$OUT/$n.log"; then echo "PASS $n"; else echo "FAIL $n (rc=$rc, required /$req/)"; fi; }
export -f run
jobs_list() { cat <<EOT
row19_D4 SEVEN valid.5-configs.0 $PY -B r19b.py
BUDA11_i2 BUDA11 E.every.line $PY -B chk2.py
BUDA11_i1 BUDA11 ^B.ok $PY -B chk1.py
BUDA11_i3 AUD-3 ^B.ok $PY -B buda_mine.py
CONJG2_lists AUD-3 e1.surv $PY -B land_mine.py 8 1,2,3
F7_i3 AUDIT-TS 41431.*1976 $PY -B f7a.py
BK_i3 AUDIT-TS ^8.*684 $PY -B bk3.py
KILL6C_i1 KILL-6C ALL.CERTS.OK $PY -B verB.py
KILL6C_i2 AUD-2 ALL.OK $PY -B chk6c.py
GRRC2_i2 AUD-2 ALL.OK $PY -B chkgrrc.py
TheoremS_slack_i1 RDEP3 zero-slack.pairs $PY -B slack1.py
TheoremS_slack_i2 RDEP3 tables.agree $PY -B slack2.py
WALL_cat AUDIT-IMP rootswap.*[[][]]$ $PY -B ind_e8.py
WALL_coloop AUDIT-IMP True$ $PY -B ind_coloop.py
E6_dimcover RES116 ^84$ $PY -B verify_e6.py
EOT
}
jobs_list | xargs -P 3 -L1 bash -c 'run "$@"' _ 2>&1 | sort | tee -a "$OUT/all.out"
if [ "${FULL:-0}" = 1 ]; then
  echo "== 3. FULL=1: heavy reruns (see PROOF_MAP.md column 'FULL'); run them chunked, each under timeout 1200"
  bash "$HERE/checks/full.sh" "$OUT" 2>&1 | tee -a "$OUT/all.out"
fi
nf=$(grep -Ec '^(FAIL|FULL-FAIL)' "$OUT/all.out"); np=$(grep -c '^PASS' "$OUT/all.out")
if [ "$nf" = 0 ] && [ "$np" -ge 17 ]; then echo "ALL PASS ($np checks)"; else echo "SOME FAILED ($nf failures, $np passes)"; exit 1; fi
