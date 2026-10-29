import sys, ast
P=[]
for l in open(sys.argv[1]):
    if l.startswith('size'):
        sz=int(l.split()[1]); d=ast.literal_eval(l[l.index('{'):l.index('}')+1])
        prof=tuple(min(d.get(u,sz),sz) if u in d else sz for u in range(1,8))+(sz,)
        P.append(prof)
P=set(P)
par=[p for p in P if not any(q!=p and all(a<=b for a,b in zip(p,q)) for q in P)]
print(sys.argv[1],'pareto',sorted(par,reverse=True))
