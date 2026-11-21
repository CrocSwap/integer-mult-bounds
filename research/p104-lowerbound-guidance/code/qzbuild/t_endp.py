import sys, time
from qzml import build_ml
from qzclimb2 import *
k=int(sys.argv[1]); variant=sys.argv[2]
d,C,taus=build_ml(k)
Vv,Ww,AB=build_ml.data
pieces=[];place={};pos=0;tags_old=[]
for ev in d.events:
    if ev[0]=='H': pos+=1
    else: place[len(pieces)]=pos; pieces.append(frozenset(ev[1]))
order=tuple(d.hosts); n=d.n; masks=[set(M) for M in d.masks]
dpar,tpar=build(n,k,masks,pieces,order,place)
zpar=np.concatenate([np.array([[float(x) for x in v] for v in Vv]).ravel(),np.array([[float(x) for x in w] for w in Ww]).ravel(),np.array([[float(a),float(b)] for a,b in AB]).ravel()])
idle=[i for i,S in enumerate(pieces) if len(S)==1 and place[i]==min(S)+1]
keep=[i for i in range(len(pieces)) if i not in idle]
mid=frozenset(range(1,k-1))
newP=[pieces[i] for i in keep]+[mid,mid]
pl={a:place[i] for a,i in enumerate(keep)}
pp={'end':(k,k),'start':(0,0),'mix':(0,k)}[variant]
pl[len(newP)-2]=pp[0]; pl[len(newP)-1]=pp[1]
dn,tn=build(n,k,masks,newP,order,pl)
print('val',val(n,k,masks,newP),flush=True)
oldpos={t:e for e,t in enumerate(tpar)}
mp=[]
for t in tn:
    if t[0]=='c': mp.append(oldpos[t])
    elif t[1]>=len(keep): mp.append(oldpos[('p',idle[t[1]-len(keep)])])
    else: mp.append(oldpos[('p',keep[t[1]])])
Sn=Sys(dn); rng=np.random.default_rng(0)
for tr in range(4):
    zi=warm_z(dpar,zpar,dn,mp,rng,noise=0.05*(tr+1))
    zz,nr=lm(Sn,zi,it=600); print(variant,'warm',tr,'%.2e'%nr,abok(Sn,zz),flush=True)
    if nr<1e-9: break
ok,z,S,nr=try_design(dn,tries=6,seed=3); print(variant,'random',ok,'%.2e'%nr)
