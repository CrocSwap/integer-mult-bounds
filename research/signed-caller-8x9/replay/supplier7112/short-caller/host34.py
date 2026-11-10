from fractions import Fraction as Q
from collections import Counter
import hashlib,json,sys
from pathlib import Path

N=34

def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def z(m,n):return [[Q(0)]*n for _ in range(m)]
def m(a,b):
    bt=list(zip(*b));return [[sum(x*y for x,y in zip(row,col) if x and y) for col in bt] for row in a]
def tr(a):return [list(c) for c in zip(*a)]
def add(a,b,s=1):return [[x+s*y for x,y in zip(r,t)] for r,t in zip(a,b)]
def sc(a,s):return [[s*x for x in r] for r in a]
def msum(a,rows,cols):
    r=z(rows,cols)
    for t in a:r=add(r,t)
    return r

def rref(A,n):
    d=[list(r) for r in A if any(r)];p=[];i=0
    for j in range(n):
        k=next((k for k in range(i,len(d)) if d[k][j]),None)
        if k is None:continue
        d[k],d[i]=d[i],d[k];d[i]=[x/d[i][j] for x in d[i]]
        for k,r in enumerate(d):
            if k!=i and r[j]:d[k]=[a-r[j]*b for a,b in zip(r,d[i])]
        p.append(j);i+=1
    return d[:i],p

def inv(A):
    n=len(A);r,p=rref([a+b for a,b in zip(A,eye(n))],n)
    assert len(p)==n
    return [a[n:] for a in r]

def null(A,n):
    R,p=rref(A,n);free=[i for i in range(n) if i not in p];out=[]
    for f in free:
        v=z(1,n)[0];v[f]=Q(1)
        for r,i in zip(R,p):v[i]=-r[f]
        out.append(v)
    return out

def block_lu(H):
    U=[[b for b in row] for row in H];L=[[eye(2) if i==j else z(2,2) for j in range(8)] for i in range(8)]
    for k in range(8):
        P=inv(U[k][k])
        for i in range(k+1,8):
            f=m(U[i][k],P);L[i][k]=f
            for j in range(k,8):U[i][j]=add(U[i][j],m(f,U[k][j]),-1)
    assert all(H[i][j]==msum((m(L[i][k],U[k][j]) for k in range(8)),2,2) for i in range(8) for j in range(8))
    return U

def presentation(signs=None):
    R=[[Q(0),Q(2)],[Q(-1,2),Q(0)]];J=sc(R,-1);I=eye(2)
    # Prefix A_i avoids A_9 through left i<=8, and avoids −I through right i<=17.
    signs=signs or [-1,1]*4+[1,-1,1,-1,1,-1,1,-1,1,1]
    assert len(signs)==18
    Jv=[sc(J,s) for s in signs];W=[sc(add(I,j,-1),Q(1,2)) for j in Jv]
    A=I;Phi=[];prefix=[]
    for w,j in zip(W,Jv):Phi.append(m(A,w));A=m(A,j);prefix.append(A)
    assert A==sc(I,-1) and prefix[8]==J
    G=add(R,I,-1);L=inv(add(R,I));K=inv(G)
    bridge=tr(eye(N)[:2]);U=[]
    for side in (0,1):
        start=9*side
        block_coeff=[m(L if side==0 else K,sc(Phi[start+j],4 if side==0 else -4)) for j in range(8)]
        upper=block_lu([[add(b,sc(I,-2)) if i==j else b for j,b in enumerate(block_coeff)] for i in range(8)])
        offset=2+16*side;cols=[]
        for j in range(8):
            a=m(L if side==0 else K,sc(Phi[start+j],2));block=m(bridge,a)
            for i in range(8):block[offset+2*i:offset+2*i+2]=upper[i][j]
            cols.append(block)
        cols.append(add(sc(bridge,1 if side==0 else -1),msum(cols,N,2),-1))
        U.extend(cols)
    UB=tr([c for b in U[:-1] for c in tr(b)]);IB=inv(UB)
    Y=[]
    for i in range(18):
        rows=z(2,N)
        for j in range(17):
            x=sc(Phi[j],2)
            if i==j:x=add(x,sc(I,-2))
            for t in range(2):rows[t][2*j:2*j+2]=x[t]
        y=m(rows,IB)
        assert all(m(y,u)==add(sc(phi,2),sc(I,-2) if i==j else z(2,2)) for j,(u,phi) in enumerate(zip(U,Phi)))
        Y.append(y)
    return U,Y,W,Jv,signs

def coord_mask(i):
    half,j=divmod(i,9);start=2+16*half
    return [0,1]+list(range(start,start+2*min(j+1,8)))

def extend(v,ids):
    a=z(1,N)[0]
    for j,x in zip(ids,v):a[j]=x
    return a

def project(v,w):
    return m(tr([v]),[w])

def paired_groups(X,Y,half):
    out=[]
    for local in range(8):
        start=9*half+local+1;end=9*(half+1);ids=coord_mask(start)
        yc=[r for y in Y[start:end] for r in y]+[w for v,w in out]
        xr=[r for x in X[start:end] for r in tr(x)]+[v for v,w in out]
        cols=[extend(v,ids) for v in null([[r[i] for i in ids] for r in yc],len(ids))]
        rows=[extend(v,ids) for v in null([[r[i] for i in ids] for r in xr],len(ids))]
        pair=m(rows,tr(cols)) if rows and cols else []
        pr=len(rref(pair,len(cols))[1]);assert pr>=2,(half,local,len(cols),len(rows),pr)
        for k in range(2):
            a,b=next((i,j) for i,r in enumerate(rows) for j,v in enumerate(cols) if m([r],tr([v]))[0][0])
            v,w=cols[b],rows[a];u=m([w],tr([v]))[0][0];w=[x/u for x in w]
            out.append((v,w));cols=[[a-b*m([w],tr([c]))[0][0] for a,b in zip(c,v)] for c in cols];rows=[[a-b*m([r],tr([v]))[0][0] for a,b in zip(r,w)] for r in rows]
    assert m([w for v,w in out],tr([v for v,w in out]))==eye(16)
    return out

def verify(caller):
    U,Y,W,J,signs=presentation();S=z(N,2);F=eye(N);X=[];stages=[];P=[];T=[]
    for i,(u,y,w,j) in enumerate(zip(U,Y,W,J)):
        x=add(u,sc(m(S,w),2));X.append(x);assert m(F,x)==u
        local=m(y,x);assert add(eye(2),local)==sc(j,-1)
        mask=set(coord_mask(i));E=[[Q(k==r and k in mask) for r in range(N)] for k in range(N)]
        assert all(k in mask for k,r in enumerate(x) if any(r)) and all(k in mask for r in y for k,v in enumerate(r) if v)
        assert m(F,E)==m(E,F),(i,'prefix commutation')
        p=m(m(x,inv(local)),y);assert m(E,p)==m(p,E)==p
        P.append(p);T.append(E);F=add(F,m(u,y));S=add(S,u)
    assert F==sc(eye(N),-1) and S==z(N,2)
    groups=[[] for h in range(2)];core_singletons=0
    for i,(e,p) in enumerate(zip(T,P)):
        half,local=divmod(i,9);seen=groups[half][:2*local]
        remaining=add(e,p,-1)
        for v,w in seen:
            q=project(v,w);assert m(q,p)==m(p,q)==z(N,N) and m(e,q)==m(q,e)==q
            remaining=add(remaining,q,-1)
        assert m(remaining,remaining)==remaining
        d=sum(remaining[j][j] for j in range(N));assert d==len(coord_mask(i))-2
        core_singletons+=int(d)
        stages.append({'stage':i+1,'target_rank':len(coord_mask(i)),'grouped_idle_fields':len(seen),'singleton_idle_fields':int(d)})
    assert core_singletons==176
    old_t=Counter(1+8*sum(d[2:]) for d in caller['types']['B']['diagonal']);target=Counter(1+8*sum(i in coord_mask(j) for j in range(18)) for i in range(N));target[9]+=4
    assert target==old_t
    old_p=Counter(8*len(e[3]) for e in caller['events'] if e[:2]==['B','IDLE_ONE']);old_p[1]=4
    paid=Counter({8:core_singletons,9:4})
    delta=old_p.copy();delta.subtract(paid)
    assert sum(r*c for r,c in delta.items())==0
    ideal=Counter({8*length:4 for length in range(1,9)});ideal[8]+=32;ideal[9]+=4
    ideal_delta=old_p.copy();ideal_delta.subtract(ideal)
    assert +ideal_delta==Counter({8:4,1:4}) and -ideal_delta==Counter({9:4})
    return {'status':'PASS_FORMAL_HOST34_PHASE_IDLE_STAGE_LOCAL','HOST_signs':signs,'HOST_core_fields':N,'literal_native_beta_retained':'1/2','QUERYs':0,
      'phase_only_body_outputs':4,'phase_only_paid_rank':9,'body_masks_exact':True,'stages':stages,
      'productive_rank_histogram':dict(sorted(target.items())),'paid_rank_histogram':dict(sorted(paid.items())),'stage_local_signed_gain_per_port':{r:c for r,c in delta.items() if c},'unrealized_grouping_signed_gain_per_port':{r:c for r,c in ideal_delta.items() if c},
      'literal_caller_lowering_verified':False,'ordinary_invoice_verified':False,'fixed_tape_verified':False}

if __name__=='__main__':
    raw=Path(sys.argv[1]).read_bytes();assert hashlib.sha256(raw).hexdigest()=='3828d53e80ea97e8b866320f081af20b6b93bfebd58b95b56b85a7afe151af5e'
    print(json.dumps(verify(json.loads(raw)),indent=2))
