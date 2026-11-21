# L2TEST netlib: exact-mod-p network evaluator (YC level sum, DX cut, drops, junk) for legal graded relay networks.
import numpy as np, json, itertools
from fractions import Fraction as Fr
P=2147483647
WD='<research-tree>/cards/WILD/'
G104=np.load(WD+'REBASET1/G104.npy').astype(int); L=json.load(open(WD+'REBASET1/lines104.json'))
dot=lambda a,b: bin(a&b).count('1')&1
Qm=np.array([[dot(a,b) for b in L] for a in L])
F0=[0,6,16,22,29,36,45,95]; Ah=G104[:,F0]
def span(vs):
    b=[]
    for v in vs:
        for x in b: v=min(v,v^x)
        if v: b.append(v)
    return b
def inspan(b,v):
    for x in b: v=min(v,v^x)
    return v==0
def f2dim(vs): return len(span(vs))
def rankp(M,p=P):
    M=np.array(M,dtype=np.int64)%p
    if M.size==0: return 0
    r=0; rows,cols=M.shape
    for c in range(cols):
        if r==rows: break
        nz=np.nonzero(M[r:,c])[0]
        if len(nz)==0: continue
        i=nz[0]+r
        if i!=r: M[[r,i]]=M[[i,r]]
        M[r]=(M[r]*pow(int(M[r,c]),p-2,p))%p
        idx=np.nonzero(M[:,c])[0]; idx=idx[idx!=r]
        if len(idx): M[idx]=(M[idx]-(M[idx,c][:,None]*M[r][None,:])%p)%p
        r+=1
    return r
class Net:
    def __init__(s,n): s.n=n; s.nodes=[]   # node: dict aB,bB,F(dict port->val mod p),G(dict),rel{j:val}
    def add(s,aB,bB,F,G,rel=None):
        s.nodes.append(dict(aB=span(aB),bB=span(bB),F=F,G=G,rel=rel or {})); return len(s.nodes)-1
    def adim(s,k): return len(s.nodes[k]['aB'])
    def bdim(s,k): return len(s.nodes[k]['bB'])
    def legal(s):
        bad=[]
        for k,nd in enumerate(s.nodes):
            if not all(inspan(nd['aB'],b) for b in nd['bB']): bad.append(('b!<=a',k))
            for t,v in nd['F'].items():
                if v%P and not inspan(nd['aB'],L[t]): bad.append(('gather',k,t))
            for t,v in nd['G'].items():
                if v%P and any(dot(L[t],b) for b in nd['bB']): bad.append(('deposit',k,t))
            for j,v in nd['rel'].items():
                assert j<k
                if v%P and not all(inspan(nd['aB'],b) for b in s.nodes[j]['bB']): bad.append(('relay',j,k))
        return bad
    def drop(s): return sum(s.adim(k)-s.bdim(k) for k in range(len(s.nodes)))
    def Cl(s,l): return [k for k in range(len(s.nodes)) if s.bdim(k)<l<=s.adim(k)]
    def N(s):
        m=len(s.nodes); Nm=np.zeros((m,m),dtype=object)
        for k in range(m):
            Nm[k,k]=1
            for j,v in s.nodes[k]['rel'].items():
                for g in range(m):
                    if Nm[j,g]%P: Nm[k,g]=(Nm[k,g]+v*Nm[j,g])%P
        return Nm
    def mats(s):
        m=len(s.nodes); n=s.n
        Fm=np.zeros((m,n),dtype=np.int64); Gm=np.zeros((m,n),dtype=np.int64)
        for k,nd in enumerate(s.nodes):
            for t,v in nd['F'].items(): Fm[k,t]=v%P
            for t,v in nd['G'].items(): Gm[k,t]=v%P
        return Fm,Gm
    def M(s):
        Fm,Gm=s.mats(); Nm=s.N().astype(np.int64)
        X=(Nm@Fm)%P if False else np.array([[sum(int(Nm[d,g])*int(Fm[g,t]) for g in range(len(s.nodes)) if Nm[d,g]) %P for t in range(s.n)] for d in range(len(s.nodes))],dtype=object)
        return X,Gm
    def check(s):
        X,Gm=s.M(); n=s.n
        Mm=(Gm.T.astype(object)@X)%P
        ok=all(Mm[t,t]%P==1 for t in range(n)) and all(Mm[a,b]%P==0 for a in range(n) for b in range(n) if a!=b and Qm[a,b])
        return ok,Mm
    def levels(s,hmax=9):
        m=len(s.nodes); n=s.n
        Fm,Gm=s.mats(); Nm=s.N()
        Xs=np.array([[sum(int(Nm[d,g])*int(Fm[g,t]) for g in range(m) if Nm[d,g])%P for t in range(n)] for d in range(m)],dtype=object)  # N F  (m x n)
        out=[]
        for l in range(1,hmax+1):
            C=s.Cl(l)
            # YC: sources a>=l, sinks b<l: M = sum_d G_d (sum_{g src} N[d,g]F_g)
            src=[g for g in range(m) if s.adim(g)>=l]; snk=[d for d in range(m) if s.bdim(d)<l]
            if src and snk:
                Y=np.array([[sum(int(Nm[d,g])*int(Fm[g,t]) for g in src if Nm[d,g])%P for t in range(n)] for d in snk],dtype=np.int64)
                Myc=(Gm[snk].T.astype(object)@Y.astype(object))%P; ryc=rankp(Myc.astype(np.int64))
            else: ryc=0
            # DX DP
            X=[]; 
            for k,nd in enumerate(s.nodes):
                acc=[np.zeros(n,dtype=object) for _ in range(3)]
                sflag=int(s.adim(k)>=l); f0=2 if (sflag and s.bdim(k)<l) else sflag
                acc[f0]=acc[f0]+Fm[k].astype(object)
                for j,v in nd['rel'].items():
                    for f in range(3):
                        if not any(X[j][f]): continue
                        if f==2: nf=2
                        else:
                            s2=int(f==1 or s.adim(k)>=l); nf=2 if (s2 and s.bdim(k)<l) else s2
                        acc[nf]=acc[nf]+v*X[j][f]
                X.append([a%P for a in acc])
            rows=[d for d in range(m) if any(X[d][2])]
            if rows:
                Xm=np.array([X[d][2] for d in rows],dtype=object); Mdx=(Gm[rows].T.astype(object)@Xm)%P
                rdx=rankp(Mdx.astype(np.int64))
            else: rdx=0
            out.append((l,len(C),ryc,rdx))
        return out
    def report(s,name,hmax=9):
        lv=s.levels(hmax); D=s.drop(); assert D==sum(c for _,c,_,_ in lv),(D,lv)
        yc=sum(r for _,_,r,_ in lv); dx=sum(r for *_,r in lv)
        loss=sum(max(0,8-r) for l,c,_,r in lv if 2<=l<=8); junk=sum(c-r for l,c,_,r in lv)
        viol = loss>junk
        return dict(name=name,D=D,YC=yc,DX=dx,loss=loss,junk=junk,viol=viol,lv=[(l,c,y,x) for l,c,y,x in lv if c or y or x])
