from m19 import *
N=load19(); H0=N.H0; U=units(N,H0)
g=groups(N,U)
res=[]
for c,idx in g.items():
    for ch in cover(N,U,idx):
        if len(ch)<2: continue
        h,qs=mk(N,H0,U,ch)
        sav=sum(N.hcost(H0[i])[0] for i in ch)-N.hcost(h)[0]
        res.append((sav,len(ch),ch,c))
res.sort(key=lambda x:-x[0])
print('chains',len(res),'units merged',sum(r[1] for r in res),'positive',sum(1 for r in res if r[0]>0),'total positive saving %.1f'%sum(r[0] for r in res if r[0]>0),'total all %.1f'%sum(r[0] for r in res))
print('top',[(round(a,1),b) for a,b,_,_ in res[:15]])
# hot content: keys 56,100
for c,idx in g.items():
    ks=sorted(k for k,_ in c)
    if ks==[56,100]: print('hot x56-x100: units',len(idx),'chains',len(cover(N,U,idx)))
base=sum(N.hcost(h)[0] for h in H0); print('base',base)
pickle.dump([(a,b,ch) for a,b,ch,_ in res],open('chains19x.pkl','wb'))
