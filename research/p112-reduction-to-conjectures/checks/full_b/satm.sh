#!/usr/bin/env bash
# satm.sh WK: JOINT2 satM.py (impl B). It reads JOINT/dpP.txt (written by JOINT/gen.py: header "P NP NG _ _", labels, per-root Off sets), which is NOT in this package
# (KILL-A8/dat_4.txt has a different layout), and the shipped record JOINT2/satM_p4.out contains only the line "maximal masks 43180" (no solver verdict;
# KILL-A8/satM_p4.kissat.out is a truncated kissat log with no status line).  So this step cannot be rerun and reports NOT-RERUNNABLE; the p=4 claim rests on satP.py (+DRAT) and KILL-A8 pc.c / AUD-1 cov.c / SECOND s2.c.
HERE=$(cd "$(dirname "$0")/.." && pwd)
[ -f "$HERE/JOINT/dpP.txt" ] && echo "dpP.txt present: wire satM.py here" 
echo "NOT-RERUNNABLE JOINT2 satM.py: input JOINT/dpP.txt absent from package; recorded satM_p4.out = '$(head -n 1 "$HERE/JOINT2/satM_p4.out")' only (no verdict)"
echo "STEP-FAIL JOINT2 satM.py not rerunnable"
