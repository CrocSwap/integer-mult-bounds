import sys
exec(open('qb1.py').read().split("if __name__")[0])
for k in map(int,sys.argv[1:]):
    c,sup=solve(k,False); print(k,'LP',c,'chart',float(__import__('fractions').Fraction(0)) , [(x,D,tuple(int(t) for t in P)) for x,D,P in sup if x>0.3][:8],flush=True)
