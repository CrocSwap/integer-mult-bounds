#!/bin/bash
# usage: rebuild.sh <design.json> <outdir>
set -e
D=$1; O=$2
python3 /home/claude/work/agentB/build/build_lp.py /home/claude/work/agentA/W/out5b /home/claude/work/agentB/lines_out5b.pkl $D $O --mode ${3:-exch}
/home/claude/work/agentB/build/verify $O $O/resid.txt
python3 /home/claude/work/agentB/build/addcomp.py $O
/home/claude/work/verifyT/checkT $O $O/249-records.bin
python3 /home/claude/work/eval/cost.py $O
python3 /home/claude/work/agentB/tools/localD.py $O
