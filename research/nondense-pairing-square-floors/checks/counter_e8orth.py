# E8 orthogonal root normals alpha _|_ beta: D = lines non-orthogonal to both, |D| = 24, dense rank 9 (dense block value), mr2 = 6 exactly.
import sys
from lib import *
import satA, satB
L=lines(e8_roots()); G=[[int(dot(a,b)) for b in L] for a in L]
a=0; b=next(t for t in range(120) if G[a][t]==0)
D=[t for t in range(120) if G[a][t]!=0 and G[b][t]!=0]
dr=dense_rank(G,D)
R=[t for t in range(120) if G[a][t]!=0]; Ab=[t for t in range(120) if G[b][t]!=0]
block=rank2([sum(1<<i for i,s in enumerate(Ab) if s==t or G[t][s]==0) for t in R])   # dense B[R(alpha),R(beta)]
r6=satB.solve(G,D,6,nonorth_clique(G,D,6)); r5=satB.solve(G,D,5,nonorth_clique(G,D,5))
A6=satA.run(G,D,6,None,tag='o6'); A5=satA.run(G,D,5,None,tag='o5')
print('|D|',len(D),'dense rank on D x D',dr,'dense block rank B[R,A]',block,'writerB rank6',r6,'rank5',r5,'writerA rank6',A6[0],'rank5',A5[:2])
ok=len(D)==24 and block==9 and dr==6 and r6==('SAT',True) and r5==('UNSAT',True) and A6[0]=='SAT' and A5[:2]==('UNSAT',True)
print('PASS E8 orthogonal normals: |D|=24, mr2 = 6 on D, dense block value 9 (per-term block claim false; only usable by overcomplete decoders)' if ok else 'FAIL e8 orth')
sys.exit(0 if ok else 1)
