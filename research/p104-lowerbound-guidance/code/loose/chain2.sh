#!/bin/bash
# after AF2T finishes: generic control (budget 59, >=1 generic forced, E8 inactive set) then the generic campaign at 55
cd code/loose
R=$(cat arunF2T.pid)
while kill -0 $R 2>/dev/null; do sleep 30; done
export OMP_NUM_THREADS=1
P=python3
$P arun.py g59n.cnf ctl.txt GCTL59 1200
$P -c "
m=[int(x) for x in open('masks0.txt').read().split()]; m.sort(key=lambda x:-bin(x).count('1'))
open('masksG.txt','w').write('\n'.join(map(str,m))+'\n')"
$P arun.py g55n.cnf masksG.txt AG 600
