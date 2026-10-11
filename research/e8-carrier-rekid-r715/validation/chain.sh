#!/bin/bash
# usage: chain.sh WORD NAME  -- independent local legality + formal columns (5-stage, K=5 = eleven-stage) + mutants + gram
set -u
SP=/private/tmp/claude-501/-Users-mason-yarl/378ef358-ade1-45de-8708-27df77339c28/scratchpad
V=$SP/brain/validate715; P=$SP/s11x/research/e8-r740-replica32/parent436; B=$P/code/bit
PY="$SP/venv/bin/python3 -B"; WORD=$1; N=$2; O=$V/chain/$N; rm -rf $O; mkdir -p $O
export PYTHONDONTWRITEBYTECODE=1
$PY $B/export_records.py $WORD $O/records > $O/export.log 2>&1 || echo EXPORT FAIL
$PY $B/regression/stage_cohort.py $O/records $O/records $O/cin $O/cout > $O/cohort.log 2>&1 || echo COHORT FAIL
$V/bin/legality $O/cin $O/cout $O/cout/legality.json > $O/legality.log 2>&1; echo "legality rc=$?"
$V/bin/columns_h715 $O/cout/COHORT249-RECORDS.bin $O/cout/columns.json > $O/columns.out 2> $O/columns.log; echo "columns_h rc=$?"
$V/bin/columns_k5_715 $O/cout/COHORT249-RECORDS.bin $O/cout/columns_k5.json > $O/columns_k5.out 2> $O/columns_k5.log; echo "columns_k5 rc=$?"
$PY $V/chk_status.py $O > $O/status.txt 2>&1; cat $O/status.txt
$PY $B/mutate_records.py $O/records $O/cin $O/cout $V/bin/legality $V/bin/columns_k5_715 $V/bin/legality_ncopy_h > $O/mutate.log 2>&1; echo "mutate_records rc=$?"; tail -3 $O/mutate.log
$PY $B/checkers/gram_frames.py $O/records --gram e8ham --h 8 --positive 2>&1 | tail -2
