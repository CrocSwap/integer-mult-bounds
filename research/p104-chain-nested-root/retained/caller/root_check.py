"""Exact two-pair root, all independent stage coefficients and native bases."""
from itertools import product
from algebra import Q,need,eye,matrix,multiply,inverse,add

def verify(data):
    I=eye(8);Z=[[Q(0)]*8 for _ in range(8)]
    def diag(mask):return[[Q(int(i==j and mask>>i&1))for j in range(8)]for i in range(8)]
    full=data['full_sites'];masks=data['masks'];need(full==[0,1,2,6,7,8]and masks==[3,195,195,53,53,5],'Actual two-pair root support')
    Rs=[matrix(r)for r in data['queries']];ps={i:diag(masks[full.index(i)])for i in full};K=I
    E=[[Q(int(i==0 and j==1))for j in range(8)]for i in range(8)]
    for i,R in enumerate(Rs):
        need(R!=Z and multiply(R,R)==Z,'Actual nonzero nilpotent query')
        K=multiply(add(I,R,-2),K)
        if i in ps:
            P=ps[i];need(multiply(P,R)==R and multiply(R,P)==R,'Native stage support')
            need(multiply(P,K)==multiply(K,P),'Every full-stage prefix commutant')
        if i in(2,7):continue
        C=matrix(data['bases'][str(i)]);Ci=inverse(C)
        need(multiply(multiply(Ci,R),C)==E,'Rank-one actual native query basis')
        if i in ps:
            rho=data['stage_ranks'][full.index(i)];need(multiply(multiply(Ci,ps[i]),C)==diag((1<<rho)-1),'Actual full stage basis')
    need(K==add(Z,I,-1),'Complete native shortest-root endpoint')
    for i in(1,6):
        C=matrix(data['bases'][str(i)]);Ci=inverse(C);nextR=multiply(multiply(Ci,Rs[i+1]),C)
        other=[[Q(-int(r==1 and c==0))for c in range(8)]for r in range(8)]
        need(nextR==other and ps[i]==ps[i+1],'Actual shared active pair')
        need(all(not A[r][j]and not A[j][r]for A in[E,other]for r in(2,3)for j in range(8)),'Both actual common idle coordinates')
    checks=0
    for stages in product((1,2),repeat=6):
        wanted=I
        for i,x in zip(full,stages):wanted=multiply(add(I,ps[i],x-1),wanted)
        for central in(1,-1):
            out=I
            for i,R in enumerate(Rs):
                out=multiply(add(I,R,central-1),out)
                if i in ps:out=multiply(add(I,ps[i],stages[full.index(i)]-1),out)
            need(out==add(Z,wanted,central),'All independent stage and central coefficients');checks+=1
    return{'fields':8,'full_sites':full,'stage_ranks':data['stage_ranks'],'multilinear_stage_and_character_checks':checks,'common_idle_pairs':2}
