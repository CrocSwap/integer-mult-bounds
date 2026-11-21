"""MAINPLACE mp2: numeric build attempts (scout) of the unique k8 law-clean nested chain (8-cycle chords)."""
import sys,os
os.chdir('code/rescuebuild');sys.path.insert(0,'.')
from rb15 import *
F=frozenset;k=8;A=F(range(8))
X=F({0,1,2,3});Y=F({0,4,5,6})
R=[(A,[X,A-X]),(A,[Y,A-Y]),(X,[F({0,1}),F({2,3})]),(A-X,[F({4,5}),F({6,7})]),(Y,[F({0,4}),F({5,6})]),(A-Y,[F({1,2}),F({3,7})])]
R+=[(p,[]) for p in [F({0,1}),F({2,3}),F({4,5}),F({6,7}),F({0,4}),F({5,6}),F({1,2}),F({3,7})]]
print('value',chat(k,R),flush=True)
for w in range(4):
    Q=anywalk(k,w);S=FSys(k,R,Q);nr,z=S.solve(w,tries=6);print('fixed walk',w,'res %.2e'%nr,flush=True)
ok,info,S,z,Q=jbuild(k,R,starts=3);print('JOINT',ok,info,flush=True)
if ok:
    import pickle;pickle.dump((R,[q.tolist() for q in Q],z.tolist()),open('code/mainplace/k8build.pkl','wb'))
