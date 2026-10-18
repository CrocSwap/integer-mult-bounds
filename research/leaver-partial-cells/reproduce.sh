#!/usr/bin/env bash
# Partial leaver cells on #1005's k8 word: rebuild the baseline and every variant, measure, price.
# usage: bash research/leaver-partial-cells/reproduce.sh <repo root> <pinned #635 supplier dir> <fresh out dir>
# Needs Python 3.11+ (assertions on). The optional circuit search (postport.py) also needs ortools.
set -euo pipefail
MAIN=$(cd "$1" && pwd); PR635=$(cd "$2" && pwd); mkdir -p "$3"; OUT=$(cd "$3" && pwd)
HERE=$(cd "$(dirname "$0")" && pwd); PY=${PYTHON:-python3}; L8=$MAIN/research/gauge44-leaver8
MC=$MAIN/research/complex-k492-owner-repair/vendor/multicold
# 0. no-triangle base word (#645/#1005 chain, unchanged)
$PY -B $L8/construction/reproduce.py --main $MAIN --pr635 $PR635 --out $OUT/notri-base --until word
# 1. baseline: #1005's own cell driver, pins checked
$PY -B $L8/construction/leaver/reproduce_leaver.py --main $MAIN --pr635 $PR635 --word-dir $OUT/notri-base --id k8 --out $OUT/base --skip-phases
# 2. patched copy of the construction tree (partial-cell hook, successor anchoring, census dump)
cp -R $L8/construction $OUT/construction
( cd $OUT/construction
  cp leaver/cgx_leaver.py leaver/cgx_census.py; patch -s leaver/cgx_census.py < $HERE/patches/cgx_census.patch
  patch -s leaver/cgx_leaver.py < $HERE/patches/cgx_leaver.patch
  patch -s leaver/reproduce_leaver.py < $HERE/patches/reproduce_leaver.patch
  cp notri/port_stage_x.py notri/port_stage_x_rep.py; patch -s notri/port_stage_x_rep.py < $HERE/patches/port_stage_x.patch )
# 3. delivery census of the cell word (byte-identical word, plus CENSUS.pkl)
mkdir -p $OUT/census; cp $OUT/base/TRI.json $OUT/base/CODED-CELLS.json $OUT/census/
( cd $OUT/census && XPARAM=$L8/construction/notri/PRIO6.json MULTICOLD_SOURCE=$MC PYTHONINTMAXSTRDIGITS=0 \
  $PY -B $OUT/construction/leaver/cgx_census.py $OUT/notri-base/hamming $OUT/census/raw $OUT/census/TRI.json > census.log )
cmp <(gzip -dc $OUT/census/raw/FULL-WORD.json.gz) <(gzip -dc $OUT/base/raw/FULL-WORD.json.gz)
export PC_CENSUS=$OUT/census/raw/CENSUS.pkl PC_PROTO=$OUT/notri-base/hamming/PROTOTYPE.json PC_PORTED=$OUT/base/port3/FULL-WORD.json.gz PC_MAIN=$MAIN PC_OUT=$OUT
# 4. raw-level checks (exact rows, frames) of the templates
( cd $OUT && $PY -B $HERE/code/template.py all > raw-template-yy.txt )
# 5. variants through the native chain
run() { name=$1; keys=$2; shift 2
  rm -rf $OUT/$name
  env "$@" PORT_REPAIR=1 PCELL_LATE=1 PCELLS=$HERE/$keys PCELL_TOOLS=$HERE/code \
    $PY -B $OUT/construction/leaver/reproduce_leaver.py --main $MAIN --pr635 $PR635 --word-dir $OUT/notri-base --id k8 \
    --out $OUT/$name --record-pins --skip-phases > $OUT/$name.log 2>&1 || true
  if [ -d $OUT/$name/local ] && [ -f $OUT/$name/local/LOCAL-PROGRAMS.json.gz ]; then
    ( cd $PR635/research/complex-571-cold14-st2/code && MULTICOLD_SOURCE=$MC $PY -B $HERE/code/prefix_trace.py $OUT/$name/local 2>&1 | grep PREFIX | cut -c1-60 > $OUT/$name.prefix ) || true
  fi; }
( cd $PR635/research/complex-571-cold14-st2/code && MULTICOLD_SOURCE=$MC $PY -B $HERE/code/prefix_trace.py $OUT/base/local | grep PREFIX | cut -c1-60 > $OUT/base.prefix )
run v1-yy-entering   KEYS-ALL16.json      PCELL_X=1
run v2-two-kept      KEYS-ALL16.json      PCELL_V2=1 PORT_SUCC=1 PCELL_MOVEOWN=1
run v3-fresh-all16   KEYS-ALL16.json      PCELL_V3=1 PORT_SUCC=1 PCELL_MOVEOWN=1
run v3-fresh-4567    KEYS-CLASS4567.json  PCELL_V3=1 PORT_SUCC=1 PCELL_MOVEOWN=1
run v3-fresh-one     KEYS-ONE.json        PCELL_V3=1 PORT_SUCC=1 PCELL_MOVEOWN=1
# 6. collect profiles, pairing, audit outcome, coefficient bits, price
$PY -B $HERE/code/collect.py $OUT
