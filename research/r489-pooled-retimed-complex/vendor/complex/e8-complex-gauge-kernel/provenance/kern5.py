from kern4 import *
import math,pickle,time
def nullity(C,S):
    return len(S)-(np.linalg.matrix_rank(C[:,sorted(S)],tol=1e-8) if S else 0)
def sa(col,first,C,cand,Es,iters=30000,seed=0,init=None,T0=0.6):
    rnd=random.Random(seed);big=sorted({h for E in Es for h in cand[E]})
    allowed={h:[E for E in Es if h in set(cand[E])] for h in big}
    cls={E:set() for E in Es};asg={}
    if init:
        for E,d,p in init:
            for h in d+p:
                if E in cls:cls[E].add(h);asg[h]=E
    val={E:nullity(C,cls[E]) for E in Es}
    cur=sum(val.values());best=cur;bestasg=dict(asg);t0=time.time()
    for it in range(iters):
        T=T0*(1-it/iters)+0.02
        h=rnd.choice(big);old=asg.get(h)
        choices=allowed[h]+[None]
        new=rnd.choice(choices)
        if new==old:continue
        dv=0;newvals={}
        if old is not None:
            S=cls[old]-{h};nv=nullity(C,S);newvals[old]=nv;dv+=nv-val[old]
        if new is not None:
            S=cls[new]|{h};nv=nullity(C,S);newvals[new]=nv;dv+=nv-val[new]
        if dv>=0 or rnd.random()<math.exp(dv/T):
            if old is not None:cls[old].discard(h)
            if new is not None:cls[new].add(h);asg[h]=new
            else:asg.pop(h,None)
            for E,nv in newvals.items():val[E]=nv
            cur+=dv
            if cur>best:best=cur;bestasg=dict(asg)
    return best,bestasg
if __name__=='__main__':
    w=load();w['R']=w['report']['R'];col,first=setup(w);R=len(col)
    cand={}
    for h,F in first.items():
        for E in subspaces(F):cand.setdefault(E,[]).append(h)
    C=np.zeros((v,R))
    for h in range(R):
        for t,x in col[h].items():C[t,h]=float(x)
    Es=[E for E,G in cand.items() if len(G)>=2 and len(G)-np.linalg.matrix_rank(C[:,G])>0]
    init=pickle.load(open('kern4_best.pkl','rb'))
    print('init',sum(len(p) for E,d,p in init))
    b0=None
    for seed in range(4):
        best,asg=sa(col,first,C,cand,Es,iters=40000,seed=seed,init=init)
        print('seed',seed,'best nullity sum',best,flush=True)
        if b0 is None or best>b0[0]:b0=(best,asg)
    pickle.dump(b0,open('kern5_best.pkl','wb'))
