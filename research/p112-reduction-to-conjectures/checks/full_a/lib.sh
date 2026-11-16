# shared helpers for full_a.sh (FULL-A reruns).  Sourced by each step script.
FA="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; WK="${WK:-$FA/work}"; mkdir -p "$WK"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY="${PYTHON:-python3}"; $PY -c 'import numpy' 2>/dev/null || PY=/usr/bin/python3; export PY
pass() { echo "PASS FULL-A $1: $2"; }
fail() { echo "FAIL FULL-A $1: $2"; }
# eq LABEL FILE1 FILE2 DESC : byte-equal check
eq() { if cmp -s "$2" "$3"; then pass "$1" "$4"; else fail "$1" "$4 (differs: $2 vs $3)"; fi; }
# want LABEL ACTUAL EXPECTED DESC
want() { if [ "$2" = "$3" ]; then pass "$1" "$4 = $3"; else fail "$1" "$4: got '$2' expected '$3'"; fi; }
