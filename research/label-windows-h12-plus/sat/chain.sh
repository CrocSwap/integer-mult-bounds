#!/usr/bin/env bash
# usage: chain.sh JOBFILE LOGFILE [FILTER_REGEX]
# One sequential chain (run at most two chains at once, nice 10).  Job line: "ENV h l k pairindex X|P46", ENV = comma-separated hk3.py flags.
# Per job: hk3.py writes the CNF; its sha256 is logged; kissat 4.0.4 -q --no-binary (timeout 1200) writes a DRAT proof; drat-trim -t 1200 checks it
# (timeout 1500).  CNF and proof are deleted afterwards.  Resumable: a key already logged "drat VERIFIED" is skipped.  Never CaDiCaL.
# env: PYTHON (python3 with numpy+networkx), KISSAT, DRAT_TRIM, WORK (scratch dir, default mktemp).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); PKG=$(dirname "$HERE")
PY=${PYTHON:-python3}; KS=${KISSAT:-kissat}; DT=${DRAT_TRIM:-drat-trim}
JF=$1; LOG=$2; FILT=${3:-.}
WORK=${WORK:-$(mktemp -d "${TMPDIR:-/tmp}/h12plus.XXXXXX")}; mkdir -p "$WORK"
shalg() { if command -v sha256sum >/dev/null; then sha256sum "$1" | cut -d' ' -f1; else shasum -a 256 "$1" | cut -d' ' -f1; fi; }
while read -r envs h l k i pf; do
  [ -z "${h:-}" ] && continue
  case $pf in X) PK=$PKG/data/pairsX.json;; P46) PK=$PKG/data/pairs46.json;; *) echo "bad pair set $pf"; exit 2;; esac
  key="$envs h$h l$l k$k pair $i $pf"
  echo "$key" | grep -Eq "$FILT" || continue
  if grep -F "$key :" "$LOG" 2>/dev/null | grep -q 'drat VERIFIED'; then continue; fi
  cnf=$WORK/${pf}_${h}_${l}${k}_${i}.cnf; t0=$(date +%s)
  if ! env $(echo "$envs" | tr ',' ' ') "$PY" "$HERE/hk3.py" "$h" "$l" "$k" "$PK" "$i" "$cnf" >/dev/null 2>&1; then echo "$key : GENFAIL" >> "$LOG"; continue; fi
  sha=$(shalg "$cnf")
  r=$(timeout 1200 nice -n 10 "$KS" -q --no-binary "$cnf" "$cnf.drat" | head -1); t1=$(date +%s)
  if [[ "$r" == *UNSAT* ]]; then
    v=$(timeout 1500 nice -n 10 "$DT" "$cnf" "$cnf.drat" -t 1200 2>&1 | grep -a -m1 -o 'NOT VERIFIED\|VERIFIED\|TIMEOUT'); [ -z "$v" ] && v=NOOUT
  else v="-"; fi
  echo "$key : $r : cnf $sha : kissat $((t1-t0))s : drat $v : total $(( $(date +%s)-t0 ))s" >> "$LOG"
  rm -f "$cnf" "$cnf.drat"
done < "$JF"
echo "DONE $JF" >> "$LOG"
