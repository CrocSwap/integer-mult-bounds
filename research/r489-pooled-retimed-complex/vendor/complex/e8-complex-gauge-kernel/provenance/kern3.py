"""General exact kernel (shared-donor) for the complex word: partition helpers by rank-1 entrance E; donors independent, pivots dependent."""
from kern2 import *
import itertools,random
def solve_rel(col,donors,p):
    """exact rational coefficients c_d with col[p]=sum c_d col[d] (or None)"""
    cols=sorted({t for d in donors for t in col[d]}|set(col[p]))
    if not cols:return {}
    idx={t:i for i,t in enumerate(cols)}
    M=[[Q(0)]*(len(donors)+1) for _ in cols]
    for ci,d in enumerate(donors):
        for t,x in col[d].items():M[idx[t]][ci]=x
    for t,x in col[p].items():M[idx[t]][-1]=x
    piv=[];r=0
    for c in range(len(donors)):
        pr=next((i for i in range(r,len(M)) if M[i][c]),None)
        if pr is None:continue
        M[r],M[pr]=M[pr],M[r];q=M[r][c];M[r]=[x/q for x in M[r]]
        for i in range(len(M)):
            if i!=r and M[i][c]:
                f=M[i][c];M[i]=[a-f*b for a,b in zip(M[i],M[r])]
        piv.append(c);r+=1
    for i in range(r,len(M)):
        if M[i][-1]:return None
    return {donors[c]:M[i][-1] for i,c in enumerate(piv) if M[i][-1]}
def plan_greedy(col,first,seed=0,minE=1):
    R=len(col)
    cand={}
    for h,F in first.items():
        for E in subspaces(F):cand.setdefault(E,[]).append(h)
    C=np.zeros((v,R))
    for h in range(R):
        for t,x in col[h].items():C[t,h]=float(x)
    Es=[E for E,G in cand.items() if len(G)>=2 and len(G)-np.linalg.matrix_rank(C[:,G])>0]
    free=set(range(R));groups=[]
    while True:
        best=None
        for E in Es:
            G=[h for h in cand[E] if h in free]
            if len(G)<2:continue
            rk=np.linalg.matrix_rank(C[:,G]);pv=len(G)-rk
            val=pv*len(E)
            if best is None or val>best[0]:best=(val,E,G)
        if not best or best[0]<=0:break
        val,E,G=best
        # donors: greedy independent in order of G; pivots rest
        donors=[];rows=np.zeros((v,0))
        for h in sorted(G):
            c=C[:,h:h+1]
            if np.linalg.matrix_rank(np.hstack([rows,c]))>rows.shape[1]:rows=np.hstack([rows,c]);donors.append(h)
        pivots=[h for h in G if h not in donors]
        groups.append((E,donors,pivots));free-=set(G)
    return groups
def groups_to_pre(col,groups):
    pre=[];start={};eps=0
    for E,donors,pivots in sorted(groups,key=lambda g:len(g[0])):
        for p in pivots:
            rel=solve_rel(col,donors,p)
            assert rel is not None,(E,p)
            start[2*v+p]=list(E);eps+=len(E)
            for d,c in rel.items():
                q=-c;pre.append(['add',2*v+d,2*v+p,q.numerator,q.denominator,list(E)])
    return pre,start,eps
if __name__=='__main__':
    w=load();w['R']=w['report']['R'];col,first=setup(w)
    groups=plan_greedy(col,first)
    print([(E,len(d),len(p)) for E,d,p in groups])
    pre,start,eps=groups_to_pre(col,groups)
    print('pre ops',len(pre),'eps',eps)
    rep,edges=check(w,pre=pre,start=start)
    print('exact',rep['exact_arbitrary_dirt'],rep['exact_inverse_transpose'],rep['local_profile'],'sumwidth',sum(rep['widths']),'newedges',len(edges))
    r=HM.evaluate(rep['local_profile'],rep['widths'])
    r0=HM.evaluate({1:1912,2:784,3:168,4:224,5:392,8:24},[9]*560)
    print('b',r['b'],'%+.3f%%'%(100*(r['b']/r0['b']-1)),'W',r['W'],r['banks'])
