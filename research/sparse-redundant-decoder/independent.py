#!/usr/bin/env python3
"""Separate affine-plane geometry and nine-coordinate rank oracle.
No imports from the primary or any predecessor implementation.
Philipp / mightyOil; substantial OpenAI Codex GPT-6 Astra assistance; Apache-2.0.
"""
import hashlib
import itertools
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent

def ensure(ok,why):
    if not ok:raise ValueError(why)

def rank(vs):
    rows=list(vs)
    pos=0
    for bit in range(max(rows,default=0).bit_length()):
        at=next((i for i in range(pos,len(rows)) if rows[i]>>bit&1),None)
        if at is None:continue
        rows[pos],rows[at]=rows[at],rows[pos]
        for i in range(pos+1,len(rows)):
            if rows[i]>>bit&1:rows[i]^=rows[pos]
        pos+=1
    return pos

def generated(bs):
    return sorted(xor_selected(bs,m) for m in range(1<<len(bs)))

def xor_selected(bs,m):
    out=0
    for k,x in enumerate(bs):
        if m>>k&1:out^=x
    return out

def independent_basis(vs):
    out=[]
    for v in vs:
        if rank(out+[v])>len(out):out.append(v)
    return out

def roots():
    rs=[]
    planes=[]
    for support in itertools.combinations(range(8),4):
        if xor_selected(list(support),15):continue
        planes.append(support)
        for signs in itertools.product((-1,1),repeat=3):
            r=[0]*8;r[support[0]]=1
            for i,s in zip(support[1:],signs):r[i]=s
            rs.append(tuple(r))
    ensure(len(planes)==14 and len(rs)==112,'affine planes and signed lines')
    return sorted(rs)

def run():
    cert=json.loads((HERE/'CERTIFICATE.json').read_text())
    rs=roots();n=len(rs)
    ensure(all(sum(r[j]*r[k] for r in rs)==(56 if j==k else 0) for j in range(8) for k in range(8)), 'real rank eight')
    ensure(hashlib.sha256(json.dumps(rs,sort_keys=True,separators=(',',':')).encode()).hexdigest()==cert['root_digest'],'separate root reconstruction')
    pair=[[((sum(a*b for a,b in zip(x,y))//2)+1)%2 for y in rs] for x in rs]
    fullcols=[sum(pair[i][j]<<i for i in range(n)) for j in range(n)]
    code_basis=independent_basis(fullcols)
    ensure(len(code_basis)==9,'binary code rank')
    # Give each length-112 function independent coordinates in F2^9.
    encoding={xor_selected(code_basis,c):c for c in range(512)}
    labels=[sum((b>>i&1)<<k for k,b in enumerate(code_basis)) for i in range(n)]
    supports=[[i for i,r in enumerate(rs) if r[j]] for j in range(8)]+[[i for i,r in enumerate(rs) if sum(r[:3])]]
    wbs=[independent_basis([encoding[fullcols[i]] for i in y]) for y in supports]
    ensure(list(map(len,wbs))==[8]*8+[9], 'all column code dimensions')
    selected=[wbs[k] for k in (0,1,2,8)]
    functions=[[i for i,u in enumerate(labels) if (u&w).bit_count()%2] for w in range(512)]
    vals=[r[:3]+(0,) for r in rs]
    images=[[sum(((u&w).bit_count()%2)<<k for k,w in enumerate(ws)) for u in labels] for ws in selected]
    def nullity(anchor,vecs,other):
        # Stack actual linear equations on coefficients of W_other.
        forced=set().union(*(functions[w] for w in vecs))
        equations=[images[other][i] for i in forced if vals[i][anchor]!=vals[i][other]]
        return len(selected[other])-rank(equations)
    planes=[];singles=[]
    for a in range(3):
        ws=generated(selected[a]);total=0
        for ii,x in enumerate(ws[1:],1):
            for y in ws[ii+1:]:
                if x^y <= y:continue
                other=[k for k in range(4) if k!=a]
                dims=[nullity(a,[x,y],k) for k in other]
                ensure(dims==[0,0,1],'independent complete plane nullities')
                total+=1
        ensure(total==10795,'all planes')
        planes.append(total)
        counts={}
        for x in ws[1:]:
            d=nullity(a,[x],3);counts[str(d)]=counts.get(str(d),0)+1
        ensure(counts=={'1':1,'2':254},'single-vector nullities')
        singles.append(counts)
    for expected in cert['witnesses']:
        tag=expected['name']
        if tag=='zero':ts=[0]*n
        elif tag.startswith('coordinate_'):ts=[r[int(tag[-1])] for r in rs]
        else:ts=[2 if i==40 else 0 for i in range(n)]
        left=[[r[k]-(t if k<3 else 0) for k in range(8)]+[t] for r,t in zip(rs,ts)]
        right=[list(r)+[sum(r[:3])] for r in rs]
        for i in range(n):
            for j in range(n):
                ensure(sum(left[i][k]*right[j][k] for k in range(9))==sum(rs[i][k]*rs[j][k] for k in range(8)),'witness every entry')
        costs=[]
        for k in range(9):
            xs=[i for i in range(n) if left[i][k]]
            costs.append(rank([sum(pair[i][j]<<h for h,j in enumerate(supports[k])) for i in xs]))
        ensure(costs==expected['costs'] and sum(costs)==expected['total'],'direct rectangle ranks')
    ensure(cert['plane_count']==sum(planes) and cert['single_vectors']==765,'receipt census coverage')
    ensure(cert['minimum']==64 and cert['all_active_minimum']==65 and cert['equality_shifts']==['0','r0','r1','r2'],'receipt theorem statement')
    ensure(cert['planes']==[{'anchor':a,'partner_order':[k for k in range(4) if k!=a],'counts':{'0,0,1':10795}} for a in range(3)],'receipt complete plane sections')
    ensure(cert['single_vector_census']==[{'anchor':a,'dimensions':s} for a,s in enumerate(singles)],'receipt complete single sections')
    print('PASS_INDEPENDENT_SPARSE_DECODER affine_planes=14 deficiency_planes=32385 nullity_equations=exact witnesses=5 entries=62720')

if __name__=='__main__':run()
