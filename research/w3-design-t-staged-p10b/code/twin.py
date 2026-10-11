"""Twin condensation (w3, PR #310 idea, ported) -- own reimplementation.
For a plane formed as BH += LO at plane frame P where both BH and LO are M starters (ZERO -> M -> P, different M frames) and LO
then leaves P -> FULL, reading nothing else: LO enters at the 1-dim line E = M_bh ∩ M_lo (sigma = 1). BH visits E first and
absorbs LO there (BH += LO at E), both then climb E -> M; the extra absorption is inverted at FULL at the very end. LO's own
dirt enters BH twice and cancels. Frame-0 completion reads of the pivots are dropped (pivot no longer sigma-0).
usage: twin.py IN OUT"""
import sys,os,json,collections,math
import numpy as np
from fractions import Fraction
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from snapio import Snap,H
from dt import kernel_int,write
def gram_ok(w): return Fraction(sum(x*x for x in w))-Fraction(sum(w)**2,9)!=0
def line_meet(S,a1,a2,b1,b2):
    chi=S.chi;M=[[Fraction(int(x)) for x in row] for row in np.stack([chi[a1],chi[a2],-chi[b1],-chi[b2]],axis=1)]
    rows=len(M);piv=[];r=0
    for c in range(4):
        pr=next((i for i in range(r,rows) if M[i][c]!=0),None)
        if pr is None: continue
        M[r],M[pr]=M[pr],M[r];pv=M[r][c];M[r]=[x/pv for x in M[r]]
        for i in range(rows):
            if i!=r and M[i][c]!=0:
                f_=M[i][c];M[i]=[a-f_*b for a,b in zip(M[i],M[r])]
        piv.append(c);r+=1
    free=[c for c in range(4) if c not in piv]
    if len(free)!=1: return None
    x=[Fraction(0)]*4;x[free[0]]=Fraction(1)
    for i,pc in enumerate(piv): x[pc]=-M[i][free[0]]
    w=[x[0]*int(chi[a1,j])+x[1]*int(chi[a2,j]) for j in range(H)]
    den=1
    for q in w: den=den*q.denominator//math.gcd(den,q.denominator)
    wi=[int(q*den) for q in w];g=0
    for q in wi: g=math.gcd(g,abs(q))
    return [q//g for q in wi]
def run(S,OUT):
    v,n,ZERO,FULL=S.v,S.n,S.ZERO,S.FULL;rec=S.rec;dim=S.dim;init=S.init;moves=S.moves;NR=len(rec)
    adst=collections.defaultdict(list);asrc=collections.defaultdict(list)
    for k in np.nonzero(rec[:,0]==1)[0]: adst[int(rec[k,1])].append(int(k));asrc[int(rec[k,2])].append(int(k))
    chain=lambda r: [init[r]]+[int(rec[k,3]) for k in moves[r]]
    elig=[]
    for k in np.nonzero((rec[:,0]==1)&(rec[:,5]==40))[0]:
        a,b,f=int(rec[k,1]),int(rec[k,2]),int(rec[k,4])
        if dim[f]!=3 or not (2*v<=a<n and 2*v<=b<n): continue
        ca,cb=chain(a),chain(b)
        if len(ca)<3 or len(cb)!=4: continue
        if not (ca[0]==ZERO and dim[ca[1]]==2 and ca[2]==f): continue
        if not (cb[0]==ZERO and dim[cb[1]]==2 and cb[2]==f and cb[3]==FULL): continue
        if ca[1]==cb[1]: continue
        xa=[int(rec[kk,2]) for kk in adst[a] if int(rec[kk,4])==ca[1]];xb=[int(rec[kk,2]) for kk in adst[b] if int(rec[kk,4])==cb[1]]
        if len(xa)!=2 or len(xb)!=2 or max(xa+xb)>=v: continue
        if [kk for kk in asrc[b] if 0<dim[int(rec[kk,4])]<H]!=[int(k)]: continue
        if [kk for kk in asrc[a] if kk<k and 0<dim[int(rec[kk,4])]<H]: continue
        if len([kk for kk in adst[b] if 0<dim[int(rec[kk,4])]<H])!=2: continue
        elig.append((int(k),a,b,f,ca[1],cb[1],xa,xb))
    nextid=max(int(x) for x in S.F)+1;newframes={};linekey={}
    remove=set();modify={};ins=collections.defaultdict(list);tail=[];initmod={};bad=0
    for (k,bh,lo,P_,Mbh,Mlo,xa,xb) in elig:
        w=line_meet(S,xa[0],xa[1],xb[0],xb[1])
        if w is None or not gram_ok(w): bad+=1;continue
        s=next(q for q in w if q!=0)
        if s<0: w=[-x for x in w]
        key=tuple(w)
        if key not in linekey:
            fid=nextid;nextid+=1;newframes[fid]={'B':[list(key)],'A':kernel_int([list(key)]),'dim':1};dim[fid]=1;linekey[key]=fid
        E=linekey[key];kb=moves[bh][0];kl=moves[lo][0]
        assert int(rec[kb,2])==ZERO and int(rec[kb,3])==Mbh and int(rec[kl,2])==ZERO and int(rec[kl,3])==Mlo
        k1=min(kb,kl);ins[k1].append([0,bh,ZERO,E,1,0]);ins[k1].append([1,bh,lo,1,E,42])
        modify[kb]=[0,bh,E,Mbh,1,0];modify[kl]=[0,lo,E,Mlo,1,0];initmod[lo]=E;tail.append([1,bh,lo,-1,FULL,43])
    piv=set(initmod)
    for k in np.nonzero(rec[:,0]==1)[0]:
        a,b,f=int(rec[k,1]),int(rec[k,2]),int(rec[k,4])
        if dim[f]==0 and (a in piv or b in piv): remove.add(int(k))
    out=[]
    for k in range(NR):
        if k in ins: out.extend(ins[k])
        if k in remove: continue
        out.append(modify.get(k,rec[k].tolist()))
    out.extend(reversed(tail))
    print('twin: eligible',len(elig),'applied',len(tail),'bad',bad,'new line frames',len(newframes),'pivot frame-0 reads removed',len(remove),'records',NR,'->',len(out))
    write(S,OUT,np.array(out,dtype=np.int32),initmod,newframes)
if __name__=='__main__': run(Snap(sys.argv[1]),sys.argv[2])
