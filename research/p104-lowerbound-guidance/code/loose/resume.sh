#!/bin/bash
# resume the F2T campaign after the J1 probe ends (PID-bound)
cd code/loose
for p in $(pgrep -f "arun.py w55j1.cnf"); do while kill -0 $p 2>/dev/null; do sleep 10; done; done
rm -f cubes/tmp_TGJ1.cnf
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
python3 arun.py f55e.cnf remF2T.txt AF2T 600 > cubes/AF2T.nohup 2>&1 &
echo $! > arunF2T.pid
wait
python3 status.py > F2T.STATUS
