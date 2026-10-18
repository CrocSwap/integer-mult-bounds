#!/usr/bin/env python3
"""Compute the per-term fitting-minrank floors lo_j of the 26 E6 square decoders (data/e6_square_decoders.json) with kissat and write
data/e6_joint_plan.json: for each decoder the term supports' dense ranks, the floors lo_j (each lo_j > 1 is backed by an UNSAT instance
'floor_<d>_<j>' at rank lo_j - 1, re-checkable with run.py) and the number of cap vectors (c_j >= lo_j, sum c_j = 35).
Floors are only lower bounds that are used for the exhaustive enumeration of cap vectors, so their exactness is not needed -- only that
rank B[R_j,A_j] >= lo_j for every admissible B, which is exactly the UNSAT instance at lo_j - 1."""
import os, sys, json, subprocess, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import instances as I
from satgen import *
from dirs import *
KISSAT = os.environ.get('KISSAT', shutil.which('kissat') or 'kissat')
L = UNITS['E6'][0]; Br = b0rows(L)
D = json.load(open(os.path.join(I.DATA, 'e6_square_decoders.json')))
def status(R, A, r, tmp):
    c = I.block_instance(L, R, A, r); open(tmp, 'w').write(c.dimacs())
    o = subprocess.run([KISSAT, '-q', tmp], capture_output=True, text=True, timeout=1800).stdout
    return 'UNSAT' if 'UNSATISFIABLE' in o else ('SAT' if 'SATISFIABLE' in o else 'UNKNOWN')
cache = {}; plan = []
tmp = os.path.join(sys.argv[1] if len(sys.argv) > 1 else '/tmp', 'mkplan.cnf')
for d, dec in enumerate(D['decoders']):
    lo = []; dense = []
    for j in range(6):
        R = support(L, dec['X'][j]); A = support(L, dec['Y'][j]); dn = blk(Br, R, A); dense.append(dn)
        key = (tuple(R), tuple(A))
        if key not in cache:
            r = dn
            while r > 1:
                st = status(R, A, r - 1, tmp)
                assert st != 'UNKNOWN'
                if st == 'SAT': r -= 1
                else: break
            cache[key] = r
        lo.append(cache[key])
    plan.append(dict(decoder=d, dense=dense, lo=lo))
    print(d, dense, lo, flush=True)
json.dump(dict(total=35, plan=plan), open(os.path.join(I.DATA, 'e6_joint_plan.json'), 'w'), indent=0)
