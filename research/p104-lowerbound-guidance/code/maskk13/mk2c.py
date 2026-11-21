import sys
import mk2
for a in sys.argv[1:]:
    k,ds=a.split(':')
    for d in map(int,ds.split(',')):
        r=mk2.solve(int(k),d);print('k',k,'d',d,r[0],r[1] if r[0]!='FEASIBLE' else '',flush=True)
