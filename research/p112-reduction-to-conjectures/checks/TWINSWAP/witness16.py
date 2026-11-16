# Exact tightness witnesses in WALL's OPEN class: (1,1), m=10, Lemma-D normalised, |J_P|,|J_Q| >= 3, cost 64 (E_Q+E_P = 16).
# Start: two-sided swap member (k_r,k_c)=(1,1) (|J_P|=|J_Q|=2), inflate frame terms with outside components cancelling at the swap line.
from swapfam import feasible_search, build_family
from lib import *
b,ex=feasible_search(1,1); Jr,Jc,rows,cols=ex; r,rp=rows[0],cols[0]
def inflate(mode):
    Xh,Yh,E,F,names=build_family(*ex,verbose=False)
    Xh=[(list(x),list(x2)) for x,x2 in Xh]; Yh=[(list(y),list(y2)) for y,y2 in Yh]
    iR=names.index('row-swap delta'); iC=names.index('col-swap delta')
    fx=[k for k,nm in enumerate(names) if nm=='frame fx']; fy=[k for k,nm in enumerate(names) if nm=='frame fy']
    def xfr(k): return [i for i in range(8) if Xh[k][0][i]!=0]
    def yfr(k): return [i for i in range(8) if Yh[k][0][i]!=0]
    # column side: y-frame term k with r' in Off(f_i): add y2_k = -(C'y_k)(r'), fix x of col-delta term
    def col_inflate(k):
        val=sum(Fr(C[rp][i],2)*Yh[k][0][i] for i in range(8)); assert val!=0
        Yh[k][1][0]=-val
        vC=Yh[iC][1][0]
        Xh[iC]=([a - (-val/vC)*b for a,b in zip(Xh[iC][0],Xh[k][0])],Xh[iC][1])
    def row_inflate(k):
        val=sum(Fr(C[r][i],2)*Xh[k][0][i] for i in range(8)); assert val!=0
        Xh[k][1][0]=-val
        vR=Xh[iR][1][0]
        Yh[iR]=([a - (-val/vR)*b for a,b in zip(Yh[iR][0],Yh[k][0])],Yh[iR][1])
    candC=[k for k in fy if Yh[k][0] and sum(Fr(C[rp][i],2)*Yh[k][0][i] for i in range(8))!=0 and len(yfr(k))==1]
    candR=[k for k in fx if sum(Fr(C[r][i],2)*Xh[k][0][i] for i in range(8))!=0 and len(xfr(k))==1]
    if mode=='disjoint':
        col_inflate(candC[0]); row_inflate(candR[0]); tag=('Q+',names[candC[0]],'P+',names[candR[0]])
    else:
        # same frame term on both sides: a y-frame term k with r' in its column Off and r in Off(x_k)
        both=[k for k in fy+fx if sum(Fr(C[rp][i],2)*Yh[k][0][i] for i in range(8))!=0 and sum(Fr(C[r][i],2)*Xh[k][0][i] for i in range(8))!=0]
        k=both[0]; col_inflate(k); row_inflate(k)
        # restore x2.y2 = 0 by giving the col-delta term an x2 part (its y-inside is 0, so the J_P circuit is untouched)
        s=Xh[k][1][0]*Yh[k][1][0]
        Xh[iC]=(Xh[iC][0],[-s/Yh[iC][1][0]])
        tag=('K-term',names[k])
    P,Q=build(Xh,Yh,E,F)
    bad=check(P,Q,masked=False); cs=costs(P,Q)
    JP=[k for k in range(len(Xh)) if any(Xh[k][1])]; JQ=[k for k in range(len(Yh)) if any(Yh[k][1])]
    # Lemma D: no two proportional p's or q's
    def prop(u,v):
        nz=[t for t in range(n) if u[t]!=0 or v[t]!=0]
        if any((u[t]==0)!=(v[t]==0) for t in nz): return False
        c=v[nz[0]]/u[nz[0]]; return all(v[t]==c*u[t] for t in nz)
    pp=[(i,j) for i in range(len(P)) for j in range(i+1,len(P)) if prop(P[i],P[j]) or prop(Q[i],Q[j])]
    s=[9-c for c in cs]
    print(mode,tag,'m',len(P),'PQ^T=N0 mismatches',bad,'cost',sum(cs),'|J_P|',len(JP),'|J_Q|',len(JQ),'K',sorted(set(JP)&set(JQ)),'proportional pairs',pp)
    print('   per-term (name,cost):',list(zip(names,cs)),' sum(s-1)=',sum(x-1 for x in s))
inflate('disjoint'); inflate('shared')
