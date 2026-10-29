#!/usr/bin/env bash
# Provenance check for data/rows_input.csv.   usage: bash provenance/reproduce.sh    PYTHON=...  FULL=1 (also reruns generator/land7.py, about 6 minutes, needs numpy+scipy)
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); PY="${PYTHON:-python3}"; export PYTHONDONTWRITEBYTECODE=1
OUT=$(mktemp -d "${TMPDIR:-/tmp}/prov.XXXXXX")
SRC="$HERE/generator/land7.out"
if [ "${FULL:-0}" = 1 ]; then
  echo "== rerun land7.py 7 (about 6 min)"; "$PY" -B "$HERE/generator/land7.py" 7 > "$OUT/land7.out" || { echo "FAIL land7.py"; exit 1; }
  cmp -s "$OUT/land7.out" "$HERE/generator/land7.out" && echo "PASS land7 rerun identical to recorded land7.out" || { echo "FAIL land7 rerun differs from recorded land7.out"; exit 1; }
  SRC="$OUT/land7.out"
fi
echo "== dominance filter on $(basename "$SRC")"
OUT="$OUT" "$PY" -B "$HERE/dominance_filter.py" "$SRC" || { echo "FAIL filter"; exit 1; }
"$PY" -B "$HERE/check_rows.py" "$OUT/open_rows.json"
