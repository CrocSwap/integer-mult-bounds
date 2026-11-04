"""Exact rational common-projector and common-idle decomposition checks."""
from itertools import product
from algebra import Q,need,eye,matrix,multiply,inverse,add

def rank(a):
    a=[r[:]for r in a];i=0
    for j in range(len(a[0])):
        k=next((k for k in range(i,len(a))if a[k][j]),None)
        if k is None:continue
        a[i],a[k]=a[k],a[i];c=a[i][j];a[i]=[x/c for x in a[i]]
        for k in range(len(a)):
            if k!=i:
                c=a[k][j];a[k]=[x-c*y for x,y in zip(a[k],a[i])]
        i+=1
    return i

def verify(data):
    I=eye(8);Z=[[Q(0)]*8 for _ in range(8)]
    def diag(mask):return [[Q(int(i==j and mask>>i&1))for j in range(8)]for i in range(8)]
    Rs=[matrix(r)for r in data['queries']];full=data['full_sites'];masks=data['masks']
    ps={i:diag(masks[full.index(i)])for i in full};K=I
    E=[[Q(int(i==0 and j==1))for j in range(8)]for i in range(8)]
    for i,R in enumerate(Rs):
        need(rank(R)==1 and multiply(R,R)==Z,'Rank-one square-zero literal query')
        K=multiply(add(I,R,-2),K)
        if i in ps:
            P=ps[i]
            need(multiply(P,R)==R and multiply(R,P)==R,'Full-stage support')
            need(multiply(P,K)==multiply(K,P),'Exact stage-prefix commutation')
        if i==2:continue
        C=matrix(data['bases'][str(i)]);Ci=inverse(C)
        need(multiply(multiply(Ci,R),C)==E,'Source native query coordinates')
        if i in ps:
            rho=data['stage_ranks'][full.index(i)]
            need(multiply(multiply(Ci,ps[i]),C)==diag((1<<rho)-1),'Source native stage coordinates')
    need(K==add(Z,I,-1),'Complete shortest-query endpoint')
    need(ps[1]==ps[2]and rank(ps[1])==4,'Adjacent full sites share actual rank-four stage support')
    C=matrix(data['bases']['1']);Ci=inverse(C);R2=multiply(multiply(Ci,Rs[2]),C)
    expected=[[Q(-int(i==1 and j==0))for j in range(8)]for i in range(8)]
    need(R2==expected,'Second query is minus the opposite active shear')
    need(all(not Rs_i[r][j] and not Rs_i[j][r]for Rs_i in [E,R2]for r in(2,3)for j in range(8)),
         'Both actual idle coordinates are disjoint from both queries')
    checks=0
    for stages in product((1,2),repeat=5):
        wanted=I
        for i,x in zip(full,stages):wanted=multiply(add(I,ps[i],x-1),wanted)
        for S in(1,-1):
            out=I
            for i,R in enumerate(Rs):
                out=multiply(add(I,R,S-1),out)
                if i in ps:out=multiply(add(I,ps[i],stages[full.index(i)]-1),out)
            need(out==add(Z,wanted,S),'All independent multilinear stage coefficients')
            checks+=1
    return {'fields':8,'queries':9,'full_sites':full,'stage_ranks':data['stage_ranks'],
            'stage_degree_per_variable':1,'characters_and_stage_nodes':checks,
            'common_idle_directions':2,'common_idle_stages':[1,2],'common_active_queries':['E01','-E10']}
