#!/bin/bash
cd code/loose
R=$(cat cubesF2T.pid)
while kill -0 $R 2>/dev/null; do sleep 20; done
grep -q DONE cubes/F2T.log || exit 1
./runcubes.sh g59n.cnf ctl.txt GCTL59
./runcubes.sh g55n.cnf masks0.txt G
