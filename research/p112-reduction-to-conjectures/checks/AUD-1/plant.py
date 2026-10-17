import sys,pickle,random; sys.path.insert(0,'.')
from e8 import *
F,M=pickle.load(open('fm.pkl','rb')); random.seed(7)
a1,a3,a4=S[0],S[2],S[3]
h={(0,1):a1,(1,2):a3,(2,3):a4,(0,2):a1+a3,(1,3):a3+a4,(0,3):a1+a3+a4}
order=[(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
big=[m for m in M if bin(m).count('1')>=28]
Ms=[random.choice(big) for _ in range(4)]
# 6-flat X: kernel of 3 random independent functionals
while True:
    f=random.sample(range(1,512),3)
    if f[2]!=f[0]^f[1]: break
X=mask([t for t in range(120) if all(bin(lab[t]&g).count('1')%2==0 for g in f)])
fm=mask(F[0])
T=[(mask(off(h[p]))&~fm)&(Ms[p[0]]|Ms[p[1]]|X) for p in order]
print('planted', [M.index(m) for m in Ms], '|X|',bin(X).count('1'), 'target sizes',[bin(t).count('1') for t in T])
with open('jobs_ctl_plant','w') as fo:
    fo.write('6 0 4\n'); [fo.write('%d %d\n'%(m&((1<<64)-1),m>>64)) for m in T]
