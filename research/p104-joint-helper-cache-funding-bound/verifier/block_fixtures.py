#!/usr/bin/env python3
"""Independent exact adversarial fixtures for the finite block funding lift."""
from fractions import Fraction as Q
from itertools import combinations
import json
def need(ok,label):
    if not ok:raise ValueError(label)
def axpy(a,b,q):
    for h,v in b.items():
        z=a.get(h,0)+q*v
        if z:a[h]=z
        else:a.pop(h,None)
def reduce(row,b):
    row=row.copy()
    for p in sorted(b,reverse=True):
        if row.get(p):axpy(row,b[p],-row[p])
    return row
def basis(rows):
    b={}
    for row in rows:
        v=reduce(row,b)
        if v:
            p=max(v);b[p]={h:Q(a)/v[p] for h,a in v.items()}
    return b
def restrict(rows,cols):
    cols=set(cols);return [{h:a for h,a in r.items() if h in cols} for r in rows]
def rank(rows):return len(basis(rows))
def tensor(rows,D):return [{D*h+a:Q(v) for h,v in row.items()} for row in rows for a in range(D)]
def prefix(rows,R,D):return [rank(restrict(rows,[D*h+a for h,r in enumerate(R) if r<=k for a in range(D)])) for k in range(10)]
def greedy(rows,R,D,weights):
    p=prefix(rows,R,D)
    return sum((Q(p[k]-p[k-1],D)*weights[k] for k in range(1,10)),Q(0))
def exhaustive(rows,R,D,weights):
    d=rank(rows);candidates=[]
    for cols in combinations(range(len(R)*D),d):
        if rank(restrict(rows,cols))==d:
            candidates.append((sum((Q(weights[R[c//D]],D) for c in cols),Q(0)),list(cols)))
    need(candidates,'column basis exists');return min(candidates)
def rejects(action,label):
    try:action()
    except ValueError:return
    raise ValueError('negative control accepted: '+label)
def mm(A,B):return [[sum(A[i][k]*B[k][j] for k in range(len(A))) for j in range(len(A))] for i in range(len(A))]
def blockrows(blocks,D):return [{D*h+j:Q(M[a][j]) for h,M in enumerate(blocks) for j in range(D) if M[a][j]} for a in range(D)]
def I(D):return [[int(i==j) for j in range(D)] for i in range(D)]
def run():
    results=[]
    for D in [2,3]:
        ident=I(D)
        A=[[int(j==i+1) for j in range(D)] for i in range(D)]
        K=[[2*int(i==j and i<D-1) for j in range(D)] for i in range(D)]
        B=[[K[i][j]-A[i][j] for j in range(D)] for i in range(D)]
        C=[[ident[i][j]-A[i][j]-B[i][j] for j in range(D)] for i in range(D)]
        need(mm(A,B)!=mm(B,A),'genuinely noncommuting preparation operators')
        P=tensor([{3:Q(1),h:Q(1)} for h in range(3)],D)
        target=tensor([{3:Q(1)}],D)
        Z=tensor([{0:Q(1),1:Q(-1)}],D)
        U=blockrows([A,B,C],D);W=Z+U
        need(rank(Z)==D and rank(W)==2*D,'whole cache adds D independent directions')
        need(all(not reduce(c,basis(P+U)) for c in target),'exact full cache recovery')
        need(all(reduce(c,basis(P+Z)) for c in target),'zero relations alone do not enable cache')
        R=[1,2,4];G=tensor([{0:Q(1),1:Q(-1)},{0:Q(1)}],D)
        wp=prefix(W,R,D);gp=prefix(G,R,D)
        need(wp[-1]==gp[-1] and all(a<=b for a,b in zip(wp,gp)),'generic prefix domination')
        need(wp[2]==2*D-1 and gp[2]==2*D,'strict non-tensor prefix loss')
        prices=[]
        for k in range(1,10):
            weights={r:Q(min(r,k)) for r in range(1,10)}
            blockprice,cols=exhaustive(W,R,D,weights);genericprice,gcols=exhaustive(G,R,D,weights)
            need(blockprice==greedy(W,R,D,weights) and genericprice==greedy(G,R,D,weights),'exhaustive and greedy agree')
            need(genericprice==weights[1]+weights[2] and blockprice>=genericprice,'block price cannot beat scalar gamma')
            prices.append(dict(generator=k,block_price=str(blockprice),scalar_gamma=str(genericprice),block_basis=cols,generic_basis=gcols))
        lost13=[D*h+a for h in [0,2] for a in range(D)]
        lost12=[D*h+a for h in [0,1] for a in range(D)]
        need(rank(restrict(W,lost13))==rank(W),'whole-field debit contains a basis')
        rejects(lambda:need(rank(restrict(W,lost12))==rank(W),'retained whole X3 arbitrary'),'false retained surjectivity')
        partial=tensor([{0:Q(1)}],D)[:-1];partialW=Z+partial
        recovered=[not reduce(c,basis(P+partialW)) for c in target]
        need(sum(recovered)==D-1,'partial cache recovers only D-1 entries')
        rejects(lambda:need(all(recovered),'whole output required'),'partial-output full credit')
        weights={r:Q(r) for r in range(1,10)}
        pp,_=exhaustive(partialW,R,D,weights)
        need(pp<weights[1]+weights[2],'partial-output loophole would be underfunded')
        # Independent tensor groups overlap on every original coordinate.
        G1=tensor([{0:Q(1),1:Q(1)}],D);G2=tensor([{0:Q(1),1:Q(-1)}],D)
        need(rank(G1+G2)==rank(G1)+rank(G2),'direct sum before Laplace')
        whole,unused=exhaustive(G1+G2,[1,4],D,weights)
        local1,_=exhaustive(G1,[1,4],D,weights);local2,_=exhaustive(G2,[1,4],D,weights)
        need(whole>=local1+local2,'Laplace composition despite overlapping supports')
        rejects(lambda:need(rank(G1+G1)==rank(G1)+rank(G1),'direct sum required'),'double-spent dependent groups')
        results.append(dict(D=D,A=A,B=B,C=C,noncommuting=True,rank_zero=rank(Z),rank_whole=rank(W),actual_prefix=wp,generic_prefix=gp,prices=prices,partial_output_recovered=recovered,partial_price=str(pp),laplace=dict(global_price=str(whole),sum_local_prices=str(local1+local2)),controls=dict(false_retained_surjectivity='REJECTED',partial_output_full_credit='REJECTED',dependent_group_double_spend='REJECTED')))
    return dict(status='PASS_EXACT_ADVERSARIAL_BLOCK_FIXTURES',dimensions=[2,3],fixtures=results,
        scope='Exact noncommuting non-tensor controls for the written finite block proof; no physical admission.')

if __name__=='__main__':
    print(json.dumps(run(),indent=2,sort_keys=True))
