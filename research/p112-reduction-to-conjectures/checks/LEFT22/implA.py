# impl A: E8 in doubled coordinates; labels = simple-root coefficients mod 2 (solve); pairs of hyperplanes of F2^8
import numpy as np, itertools, sys, pickle
R=[]
for i in range(8):
    for j in range(i+1,8):
        for si in (2,-2):
            for sj in (2,-2):
                v=[0]*8; v[i]=si; v[j]=sj; R.append(v)
for m in range(256):
    s=[(m>>k)&1 for k in range(8)]
    if sum(s)%2==0: R.append([-1 if b else 1 for b in s])
R=np.array(R); assert len(R)==240
# Bourbaki simple roots (doubled)
S=np.array([[1,-1,-1,-1,-1,-1,-1,1],[2,2,0,0,0,0,0,0],[-2,2,0,0,0,0,0,0],[0,-2,2,0,0,0,0,0],[0,0,-2,2,0,0,0,0],[0,0,0,-2,2,0,0,0],[0,0,0,0,-2,2,0,0],[0,0,0,0,0,-2,2,0]])
G=S@S.T
assert (np.diag(G)==8).all()
C=np.linalg.solve(S.T.astype(float),R.T.astype(float)).T
Ci=np.rint(C).astype(int); assert np.abs(C-Ci).max()<1e-9
# lines: pick one rep per +-
rep={}; lines=[]
for k in range(240):
    key=tuple(R[k]); neg=tuple(-R[k])
    if neg in rep: continue
    rep[key]=len(lines); lines.append(k)
assert len(lines)==120
LR=R[lines]; LL=np.array([sum(((Ci[k][b])%2)<<b for b in range(8)) for k in lines])
assert len(set(LL))==120
def vecs():
    return LR
def tab(h,cap):
    ip=LR@h
    off=[t for t in range(120) if ip[t]!=0]
    # functional a: bit parity(a&label)
    par=np.array([[bin(a&int(l)).count('1')&1 for l in LL] for a in range(256)])
    offi=np.array(off)
    masks={}
    for a in range(256):
        for b in range(a,256):
            if a==0 and b>0: pass
            m=par[a][offi]&par[b][offi]
            if a==0 or b==0: m=par[max(a,b)][offi] if max(a,b)>0 else np.zeros(len(off),int)
            # a==0 means zero functional: flat is everything -> leftover empty. skip a==0 trivial
            if a==0: continue
            if m.sum()<=cap:
                masks[frozenset(np.array(off)[m.astype(bool)].tolist())]=(a,b)
    # inclusion-minimal
    L=sorted(masks,key=len); mins=[]
    for s in L:
        if not any(m<=s for m in mins): mins.append(s)
    return off,mins,LL,LR
if __name__=="__main__":
    cap=int(sys.argv[1])
    out={}
    root=LR[0]*1
    h_root=LR[0]
    h_d7=LR[0]+LR[[t for t in range(120) if LR[0]@LR[t]==0][0]]
    assert (h_d7@h_d7)==16 and sum(1 for t in range(120) if LR[t]@h_d7==0)==42
    for name,h in (('root',h_root),('D7',h_d7)):
        off,mins,_,_=tab(h,cap)
        print(name,len(off),'minimal leftovers<=%d:'%cap, len(mins))
        from collections import Counter
        cc=Counter()
        for s in mins:
            cov = (name=='root' and (0 not in s)) # line 0 is root
            rk=0; vs=[]
            basis=[]
            for t in s:
                x=int(LL[t])
                for bb in basis: x=min(x,x^bb)
                if x: basis.append(x)
            cc[(len(s),len(basis),cov if name=='root' else None)]+=1
        for k in sorted(cc): print('  size,rank,rootcovered',k,cc[k])
        out[name]=(h,off,[sorted(s) for s in mins])
    pickle.dump((out,LR,LL),open('A_tab%d.pkl'%cap,'wb'))
