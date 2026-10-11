import numpy as np,pickle,sys
from gauge2 import *
from kern5 import sa
from kern6 import asg_to_groups,groups_to_pre
from kern import subspaces,setup
w=load();w['R']=w['report']['R'];col,first=setup(w);R=len(col)
C=np.zeros((v,R))
for h in range(R):
    for t,x in col[h].items():C[t,h]=float(x)
eps0,gauge=pickle.load(open('gauge4_best_1.pkl','rb'))
r0=HM.evaluate({1:1912,2:784,3:168,4:224,5:392,8:24},[9]*560)
prof,widths=gauge_profile(w,(),{},gauge,None)
r=HM.evaluate(prof,widths,exact=True)
print('gauge-only per-centre: n',len(gauge),'eps',eps0,'b',r['b'],'%+.3f%%'%(100*(r['b']/r0['b']-1)),r['W'],r['banks'])
cand_all={}
for h,F in first.items():
    for E in subspaces(F):cand_all.setdefault(E,[]).append(h)
cand={E:[h for h in G if h not in gauge] for E,G in cand_all.items()}
Es=[E for E,G in cand.items() if len(G)>=2 and len(G)-np.linalg.matrix_rank(C[:,G])>0]
print('kernel classes available on rest',len(Es))
best=None
if Es:
    for seed in range(2):
        b_,asg=sa(col,first,C,cand,Es,iters=40000,seed=seed)
        if best is None or b_>best[0]:best=(b_,asg)
    groups=asg_to_groups(C,best[1]);pre,start,eps=groups_to_pre(col,groups)
else:pre,start,eps=[],{},0
prof,widths=gauge_profile(w,pre,start,gauge,None)
r=HM.evaluate(prof,widths,exact=True)
print('gauge+kernel: kernel eps',eps,'total eps',sum(len(E) for E in gauge.values())+eps,'b',r['b'],'%+.3f%%'%(100*(r['b']/r0['b']-1)),r['W'],r['banks'],r['hosted'])
pickle.dump((pre,start,gauge,None),open('v4_sel.pkl','wb'))
