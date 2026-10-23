import sys,pickle,os; sys.path.insert(0,'.')
from e8 import *
F,M=pickle.load(open('fm.pkl','rb'))
Fi=[tuple(sorted(x)) for x in F]
def wr(name,R,X1,targets):
    with open('jobs/'+name,'w') as f:
        f.write('%d %d %d\n'%(R,X1,2 if len(targets)==1 else 4))
        for m in targets: f.write('%d %d\n'%(m&((1<<64)-1),m>>64))
os.makedirs('jobs',exist_ok=True)
Sd=S.astype(float)
# (c) A3 chain alpha1-alpha3-alpha4 (Bourbaki), pairs 01,02,03,12,13,23
a1,a3,a4=S[0],S[2],S[3]
h={ (0,1):a1,(1,2):a3,(2,3):a4,(0,2):a1+a3,(1,3):a3+a4,(0,3):a1+a3+a4 }
order=[(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
offm=[mask(off(h[p])) for p in order]
print('|Off| chain',[bin(m).count('1') for m in offm])
D5=[np.array(r) for r in lines if all(np.dot(r,x)==0 for x in (a1,a3,a4))]; print('D5 lines',len(D5))
reps,sz=orbits(Fi,[refl_perm(r) for r in D5]); print('W(D5) frame orbits',len(reps),sz,sum(sz))
for k,i in enumerate(reps):
    fm=mask(Fi[i])
    for x1 in (0,1): wr('c_f%d_x%d'%(k,x1),6,x1,[m&~fm for m in offm])
for x1 in (0,1): wr('c_noframe_x%d'%x1,6,x1,offm)
wr('ctl_c_R7_x0',7,0,[m&~mask(Fi[reps[0]]) for m in offm])
# (a) Levi types: coweight omega_m
names={1:'D7',2:'A7',3:'A1A6',4:'A1A2A4',5:'A4A3',6:'D5A2',7:'E6A1',8:'E7root'}
for m in range(1,9):
    e=np.zeros(8); e[m-1]=1; w=np.linalg.solve(Sd,e)
    om=mask(off(w)); gens=[refl_perm(S[i]) for i in range(8) if i!=m-1]
    reps2,sz2=orbits(Fi,gens); print(names[m],'|Off|',bin(om).count('1'),'frame orbits',len(reps2),sum(sz2))
    for k,i in enumerate(reps2):
        for x1 in (0,1): wr('a_%s_f%d_x%d'%(names[m],k,x1),6,x1,[om&~mask(Fi[i])])
    # T3 / T3+1: three 7-flats, no frame
    for x1 in (0,1): wr('t3_%s_x%d'%(names[m],x1),7,x1,[om])
