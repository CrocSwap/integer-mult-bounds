#!/bin/sh
# Draft local checks for the complex gauge/kernel words.
#   CXG_BASE : output directory of `python -B research/idle-axis-hosting/verify.py $CXG_BASE` (PR #442 replay; contains parent/changed/)
#   CXG_REPO : checkout of PR #442's tree (research/split-centres-global, research/idle-axis-hosting)
#   PY       : python with numpy + scipy (hosted-b model); stdlib python is enough for the other steps
#   PHASES=1 : also replay the exact Gaussian phase recipes of every used frame transition (about 160 s per word)
# usage: sh check.sh /absolute/new/output/dir
set -e
: "${CXG_BASE:?}"; : "${CXG_REPO:?}"; PY=${PY:-python3}; OUT=${1:?new output dir}
PKG=$(cd "$(dirname "$0")" && pwd); export CXG_PKG=$PKG CXG_BASE CXG_REPO PYTHONDONTWRITEBYTECODE=1
mkdir -p "$OUT"
for w in kernel79 gauge80 gauge80-kernel42; do
  d="$OUT/$w"; mkdir -p "$d"
  cp -RL "$CXG_BASE/parent/changed/split-centres" "$d/split-centres"
  cp -RL "$CXG_BASE/parent/changed/work" "$d/work"
  cp "$PKG/data/words/$w/FULL-WORD.json.gz" "$d/split-centres/FULL-WORD.json.gz"
  echo "== $w: arbitrary-dirt + inverse-transpose replay, frame chain, paid profile"; (cd "$d" && python3 -B "$PKG/code/audit_cxg.py" | tail -3)
  echo "== $w: emitted program, literal scalar replay (forward and backward, 800 columns, centre lifetimes)"; (cd "$d" && python3 -B "$PKG/code/emit_cxg.py" | tail -2)
  if [ -n "$PHASES" ]; then echo "== $w: exact Gaussian phase recipes (all used edges)"; (cd "$d" && python3 -B "$PKG/code/phases_cxg.py" | tail -1); fi
done
echo "== entrance-adapter evidence (nec3: tableau shapes, nec4: lower_child equality for every entrance frame)"
(cd "$PKG/code" && python3 -B nec3.py && $PY -B nec4.py)
echo "== hosted b (exact moment engine) per tool"; (cd "$PKG/code" && CXG_OUT="$OUT" $PY -B final_eval.py | cut -c1-200)
