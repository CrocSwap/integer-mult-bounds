# 60 random small E8 line subsets (|D| 6-10): exhaustive brute-force minrank over ALL fitting B (free entries = orthogonal pairs)
# must equal the SAT threshold of BOTH CNF writers (SAT at mr, UNSAT at mr-1, DRAT-verified; SAT models decoded and re-checked as fitting).
import random, sys
from lib import *
import satA, satB
L=lines(e8_roots()); G=[[int(dot(a,b)) for b in L] for a in L]
rnd=random.Random(7); done=0; bad=0; seen=set()
for _ in range(4000):
    if done>=60: break
    D=sorted(rnd.sample(range(120),rnd.randint(6,10))); key=tuple(D)
    m=satB.brute_mr(G,D,cap=20)
    if m is None or key in seen or m<2: continue
    S1=nonorth_clique(G,D,m); S0=nonorth_clique(G,D,m-1)
    if S1 is None or S0 is None: continue
    seen.add(key)
    a=satB.solve(G,D,m,S1); b=satB.solve(G,D,m-1,S0)
    ta=satA.run(G,D,m,S1,tag='a1'); tb=satA.run(G,D,m-1,S0,tag='a0')
    ok=(a==('SAT',True) and b==('UNSAT',True) and ta[0]=='SAT' and tb[:2]==('UNSAT',True))
    bad+=not ok; done+=1
    print(len(D),'brute',m,'writerB',a,b,'writerA',ta[0],tb[:2],'OK' if ok else 'MISMATCH',flush=True)
print('BRUTE-vs-CNF instances',done,'mismatches',bad)
print('PASS brute force = both CNF writers on 60 instances' if done==60 and bad==0 else 'FAIL brute-vs-CNF')
sys.exit(0 if done==60 and bad==0 else 1)
