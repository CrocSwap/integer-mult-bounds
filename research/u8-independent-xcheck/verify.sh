#!/usr/bin/env bash
# Usage: verify.sh OUT   where OUT holds PR869's chain output (x4/ and b0/ from reproduce_jx.py / reproduce_barch.py)
# and PR869 is checked out at REPO (default: current directory). Needs Python 3.11+ with numpy, sympy, mpmath.
set -euo pipefail
OUT=$1; REPO=${REPO:-.}; PY=${PY:-python3}; HERE=$(cd "$(dirname "$0")" && pwd)
sha() { gzip -dc "$1" | shasum -a 256 | cut -c1-64; }
X4=$OUT/x4/jx/FULL-WORD.json.gz; U8=$OUT/b0/barch/FULL-WORD.json.gz
test "$(sha $X4)" = 1e1d99ba7aab877d6b573c41f7030ee73de9a52fee51d0a822ddaae71251999f
test "$(sha $U8)" = 090fd574747fbf9628e70cb9beb792732914cfa52e1df147579fe4dbccc68c5a
W='"widths":{"4":80,"5":32,"7":54,"8":122,"9":216}'
X4C="{\"profile\":{\"1\":2548,\"2\":338,\"3\":430,\"4\":194,\"5\":56,\"8\":8},$W}"
U8C="{\"profile\":{\"1\":2548,\"2\":338,\"3\":446,\"4\":162,\"5\":72,\"8\":8},$W}"
$PY "$HERE/xcheck.py" "$X4" "$X4C"
$PY "$HERE/xcheck.py" "$U8" "$U8C"
$PY "$HERE/controls.py" "$U8" "$U8C"
for f in "$OUT"/b0/barch-controls/*.json.gz; do
  n=$(basename "$f" .json.gz); r=$($PY "$HERE/xcheck.py" "$f" 2>&1 | tail -1 || true)
  case $n in C0|recipe) [[ $r == PASS ]];; *) [[ $r == FAIL* ]];; esac
  echo "PR869 control $n: $r"
done
C=1733427039589844234749/1000000000000000000000000
$PY "$HERE/price.py" "$REPO/research/gauge44-barch/data/PLAN.json" '{"1":2548,"2":338,"3":446,"4":162,"5":72,"8":8}' \
  $C 1664715366696537282003/1000000000000000000000000 830974347582517/500000000000000000
echo PASS_U8_INDEPENDENT_XCHECK
