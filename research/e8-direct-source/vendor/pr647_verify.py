"""Independent referee checks. Only Python standard library; never imports candidate code.

All mathematical decisions use integers/Fraction. Decimal is display only.
The tests corroborate the universal arguments in REFEREE-REPORT.md; they
are not a runtime realization of the enormous padded E8 algorithm.
"""
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations, product
from collections import Counter
from pathlib import Path
import hashlib, json, math, time
from decimal import Decimal, localcontext

import argparse,sys
if not __debug__:
    raise SystemExit('Refusing optimized Python: exact checks require assertions; no result was written.')
ROOT=Path(__file__).resolve().parent
RESULT={'checker_origin':'Packaged adaptation of the independent Codex adversarial referee checker; mathematical constructors preserved; no contributor imports','checks':{}}

def record(name, data):
    RESULT['checks'][name] = data
    print(name + ': PASS', flush=True)

def trim(a):
    a=list(a)
    while a and not a[-1]: a.pop()
    return a

def pa(a,b):
    r=[Q(0)]*max(len(a),len(b))
    for i,x in enumerate(a): r[i]+=x
    for i,x in enumerate(b): r[i]+=x
    return trim(r)

def pm(a,b):
    if not a or not b: return []
    r=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        if x:
            for j,y in enumerate(b):
                if y: r[i+j]+=x*y
    return trim(r)

def pd(a,b):
    a=trim(a);b=trim(b); assert b
    r=[Q(0)]*max(0,len(a)-len(b)+1)
    while len(a)>=len(b):
        j=len(a)-len(b); c=a[-1]/b[-1];r[j]=c
        for i,x in enumerate(b): a[i+j]-=c*x
        a=trim(a)
    return trim(r),a

@lru_cache(None)
def phi(n):
    a=[Q(-1)]+[Q(0)]*(n-1)+[Q(1)]
    for d in range(1,n):
        if n%d==0:
            a,rem=pd(a,phi(d)); assert not rem
    return tuple(a)

class Field:
    def __init__(self,n):
        self.n=n;self.mod=phi(n);self.degree=len(self.mod)-1
        self.zero=self.v(0);self.one=self.v(1);self.z=self.v([0,1])
    def v(self,a):
        if isinstance(a,E): assert a.f is self; return a
        if isinstance(a,(int,Q)): a=[Q(a)]
        return E(self,tuple(pd(list(a),self.mod)[1]))

class E:
    __slots__=('f','a')
    def __init__(self,f,a):self.f=f;self.a=a
    def __add__(self,b):b=self.f.v(b);return self.f.v(pa(self.a,b.a))
    __radd__=__add__
    def __neg__(self):return self.f.v([-x for x in self.a])
    def __sub__(self,b):return self+-self.f.v(b)
    def __rsub__(self,b):return self.f.v(b)+-self
    def __mul__(self,b):b=self.f.v(b);return self.f.v(pm(self.a,b.a))
    __rmul__=__mul__
    def inv(self):
        assert self.a
        r0=list(self.f.mod);r1=list(self.a);s0=[];s1=[Q(1)]
        while r1:
            q,r=pd(r0,r1);r0,r1=r1,r;s0,s1=s1,pa(s0,[-x for x in pm(q,s1)])
        assert len(r0)==1 and r0[0]
        return self.f.v([x/r0[0] for x in s0])
    def __truediv__(self,b):return self*self.f.v(b).inv()
    def __rtruediv__(self,b):return self.f.v(b)*self.inv()
    def __pow__(self,k):
        if k<0:return self.inv()**(-k)
        a=self;r=self.f.one
        while k:
            if k&1:r=r*a
            a=a*a;k//=2
        return r
    def __eq__(self,b):return self.a==self.f.v(b).a
    def conj(self):
        return sum((x*self.f.z**(-j) for j,x in enumerate(self.a)),self.f.zero)

def mm(A,B):
    return [[sum((A[i][k]*B[k][j] for k in range(len(B))),0) for j in range(len(B[0]))] for i in range(len(A))]
def mt(A):return list(map(list,zip(*A)))
def eye(n,one=Q(1)):return [[one if i==j else 0*one for j in range(n)] for i in range(n)]
def diag(a):return [[a[i] if i==j else 0*a[i] for j in range(len(a))] for i in range(len(a))]

def authentication():
    source=json.loads((ROOT/'SOURCE.json').read_text())
    rows=source['included_proof_sources']
    blobs=[]
    for row in rows:
        data=(ROOT/row['file']).read_bytes()
        digest=hashlib.sha256(data).hexdigest()
        assert digest==row['sha256'],row['file']
        if 'git_blob' in row:
            got=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            assert got==row['git_blob'],row['file']
            blobs.append({'file':row['file'],'git_blob':got})
    manifest=ROOT/'SHA256SUMS.json'
    if manifest.exists():
        for name,wanted in json.loads(manifest.read_text()).items():
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==wanted,name
    record('source_byte_authentication',{'included_source_blobs':blobs,'verbatim_Pro_provider_proof':True})

def shears():
    f=Field(4);i=f.z;a=(1+i)/2;C=[[a,(1-i)/2],[(1-i)/2,a]];S=diag([f.one,i]);H=[[f.one,f.one],[f.one,-f.one]]
    assert mm(mm(S,C),S)==[[a*v for v in row] for row in H]
    K=mm(mm(mm(mm(H,diag([f.v(2),f.one])),H),diag([f.v(-3),f.one])),H)
    assert K==[[f.v(-8),f.v(-10)],[f.zero,f.v(-6)]]
    def upper(t):
        assert t!=0
        D=diag([4*t/5,f.one]);inv=diag([5/(4*t),f.one])
        return mm(mm(mm(D,diag([f.v(Q(-1,8)),f.v(Q(-1,6))])),K),inv)
    count=0
    for d in [1,2,5]:
        for r,s in product(range(-4,5),repeat=2):
            mu=f.v(Q(r,d))+Q(s,d)*i
            t1=1+mu*mu.conj();t2=mu-t1
            assert t1!=0 and t2!=0
            assert mm(upper(t1),upper(t2))==[[f.one,mu],[f.zero,f.one]]
            count+=1
    D=diag([f.one,-i]);assert [[a*x for x in row] for row in mm(mm(D,H),D)]==C
    assert mm(C,C)==[[f.zero,f.one],[f.one,f.zero]]
    record('fixed_six_C_phase_and_zero_shear',{'coefficients':count,'positive_C':True,'WHT_identity':True})

def newton_toeplitz():
    widths=[];roots=0;chunks=0
    for r in range(1,13):
        f=Field(r)
        for exponent in range(1,r+1):
            if math.gcd(exponent,r)!=1:continue
            u=f.z**exponent;F=[[u**(j*k) for k in range(r)] for j in range(r)]
            h=[f.one]
            for j in range(1,r):h.append(h[-1]*(1-u**j));assert h[-1]!=0
            N=[[math.prod([u**j-u**s for s in range(k)],start=f.one) if j>=k else f.zero for k in range(r)] for j in range(r)]
            T=[[1/h[j-k] if j>=k else f.zero for k in range(r)] for j in range(r)]
            right=[(-1)**k*u**(k*(k-1)//2) for k in range(r)]
            assert mm(mm(diag(h),T),diag(right))==N
            assert mm(mm(N,diag([1/N[j][j] for j in range(r)])),mt(N))==F
            coeff=[1/x for x in h];g=[1/coeff[0]]
            for j in range(1,r):g.append(-sum((coeff[s]*g[j-s] for s in range(1,j+1)),f.zero)/coeff[0])
            Ti=[[g[j-k] if j>=k else f.zero for k in range(r)] for j in range(r)]
            assert mm(T,Ti)==eye(r,f.one)
            if r>1:
                p=r//2
                E0=[[sum((coeff[j-nu]*g[nu-k] for nu in range(k,p)),f.zero) for k in range(p)] for j in range(p,r)]
                for row in range(p+1,r):
                    for col in range(1,p):
                        assert E0[row-p][col]-E0[row-p-1][col-1]==-coeff[row-p]*g[p-col]
                # All rectangles, not just a single principal chunk.
                for lo,hi in combinations(range(r-p+1),2):
                    for left,rightend in combinations(range(p+1),2):
                        M=[x[left:rightend] for x in E0[lo:hi]];a=len(M);e=len(M[0])
                        disp=[[M[j][k]-(M[j-1][k-1] if j and k else f.zero) for k in range(e)] for j in range(a)]
                        v=[-coeff[lo+j] for j in range(a)];w=[g[p-left-k] for k in range(e)]
                        R=[[disp[j][k]-v[j]*w[k] for k in range(e)] for j in range(a)]
                        assert all(R[j][k]==0 for j in range(1,a) for k in range(1,e))
                        terms=[(v,w),([f.one]+[f.zero]*(a-1),R[0]),([R[j][0] if j else f.zero for j in range(a)],[f.one]+[f.zero]*(e-1))]
                        assert [[sum((sum((vv[j-l]*ww[k-l] for l in range(min(j,k)+1)),f.zero) for vv,ww in terms),f.zero) for k in range(e)] for j in range(a)]==M
                        chunks+=1
            roots+=1
        widths.append(r)
    record('primitive_newton_triangular_inverse_displacement',{'widths':widths,'primitive_roots':roots,'all_rectangles':chunks,'no_cyclic_inverse_substitution':True})

def sparse_add(dst,src,c=Q(1)):
    for k,v in list(src.items()):
        new=dst.get(k,Q(0))+c*v
        if new:dst[k]=new
        else:dst.pop(k,None)

def dag_replay():
    cases=0;negative=0
    for g in range(1,18):
        e=3;a=4
        edges=[]
        for v in range(g):
            edges.append([(v%(e+v),Q((-1)**v*(v+1),3)),((2*v+1)%(e+v),Q(v+2,5))])
        outputs=[0,e+g-1,1,e+g//2]
        source=[{j:Q(1)} for j in range(e)];target=[{e+j:Q(1)} for j in range(a)];dirty=[{e+a+j:Q(1)} for j in range(g)]
        def sweep(z, suppress=False, undo=False):
            for v in (reversed(range(g)) if undo else range(g)):
                for j,c in (reversed(edges[v]) if undo else edges[v]):
                    if suppress and j<e:continue
                    sparse_add(z[v],source[j] if j<e else z[j-e],-c if undo else c)
        zero=[{} for _ in range(g)];sweep(zero)
        desired=[dict(source[j] if j<e else zero[j-e]) for j in outputs]
        y=[dict(d) for d in target];z=[dict(d) for d in dirty]
        sweep(z)
        for v,j in enumerate(outputs):sparse_add(y[v],source[j] if j<e else z[j-e])
        sweep(z,undo=True); assert z==dirty
        if y!=[{**target[j],**desired[j]} for j in range(a)]:negative+=1
        sweep(z,suppress=True)
        for v,j in enumerate(outputs):
            if j>=e:sparse_add(y[v],z[j-e],-1)
        sweep(z,suppress=True,undo=True)
        assert z==dirty
        expect=[dict(d) for d in target]
        for j in range(a):sparse_add(expect[j],desired[j])
        assert y==expect
        cases+=1
    assert negative>0
    record('dirty_DAG_all_symbolic_columns',{'DAGs':cases,'arbitrary_helpers':True,'direct_source_reads':True,'omitted_compensation_negative_controls':negative})

def popcount(x):return bin(x).count('1')
def bitdot(x,y):return popcount(x&y)%2
def bitmv(A,y):return sum(bitdot(row,y)<<j for j,row in enumerate(A))
def bitmt(A):return tuple(sum(((A[j]>>k)&1)<<j for j in range(len(A))) for k in range(len(A)))
def bitmm(A,B):
    n=len(A)
    return tuple(math.prod([],start=1)*xor_many(B[j] for j in range(n) if (row>>j)&1) for row in A)
def xor_many(it):
    v=0
    for x in it:v^=x
    return v
def biteye(n):return tuple(1<<j for j in range(n))
def bitadd(A,B):return tuple(a^b for a,b in zip(A,B))
def outer(p,n):return tuple(p if (p>>j)&1 else 0 for j in range(n))
def bdiag(A):return sum(((x>>j)&1)<<j for j,x in enumerate(A))
def indep(words):
    piv={};basis=[]
    for x0 in words:
        x=x0
        while x:
            j=x.bit_length()-1
            if j in piv:x^=piv[j]
            else:piv[j]=x;basis.append(x0);break
    return basis
def onbasis(P):
    n=len(P);basis=indep(bitmt(P));c=bdiag(P);out=[]
    while basis:
        options=[x for x in basis if bitdot(x,x)]
        assert options,'alternating image'
        u=next((x for x in options if len(basis)==1 or x!=c),None)
        if u is None:
            u=options[0]
            even=next(x for x in basis if x!=u and not bitdot(x,x))
            u^=even
        assert bitdot(u,u) and (len(basis)==1 or u!=c)
        out.append(u);c^=u
        basis=indep(x^(u if bitdot(x,u) else 0) for x in basis)
    return out

def check_phase(P):
    n=len(P);I=biteye(n);assert bitmt(P)==P and bitmm(P,P)==P
    B=onbasis(P);K=onbasis(bitadd(P,I));A=bitmt(tuple(B+K));s=len(B)
    assert bitmm(bitmt(A),A)==I
    assert xor_projectors(B,n)==P
    delta=0
    for j in range(n):
        col=bitmv(P,1<<j);total=sum((b>>j)&1 for b in B)
        assert (popcount(col)-total)%2==0
        delta|=(((popcount(col)-total)//2)%2)<<j
    points=[0]+[1<<j for j in range(n)]+[(1<<j)|(1<<k) for j in range(n) for k in range(j)]
    for y in points:
        lhs=popcount(bitmv(P,y))%4
        child=sum(bitdot(b,y) for b in B)%4
        assert lhs==(child+2*bitdot(delta,y))%4
        assert -lhs%4==(child+2*bitdot(delta^bdiag(P),y))%4
    return s, bool(delta)

def xor_projectors(basis,n):
    P=(0,)*n
    for b in basis:P=bitadd(P,outer(b,n))
    return P

def e8_provider():
    n=9;I=biteye(n);ports=[];roots=[]
    for S in combinations(range(n),3):
        ports.append(sum(1<<j for j in S));roots.append([Q(int(j in S))-Q(1,3) for j in range(n)])
    for a,b in combinations(range(n),2):
        ports.append(((1<<n)-1)^(1<<a)^(1<<b));roots.append([Q(int(j==a)-int(j==b)) for j in range(n)])
    assert len(set(ports))==120
    G=[[sum((x*y for x,y in zip(u,v)),Q(0))/2 for v in roots] for u in roots]
    A=[r[:8] for r in roots];A=mt(A)
    B=[[Q(1,2)*(r[j]-r[8]) for j in range(8)] for r in roots]
    assert mm(B,A)==G
    assert mm(G,G)==[[15*x for x in row] for row in G]
    K=[[Q(int(j==k))-G[j][k] for k in range(120)] for j in range(120)]
    counts={'K':sum(x!=0 for row in K for x in row),'A':sum(x!=0 for row in A for x in row),'B':sum(x!=0 for row in B for x in row)}
    assert counts=={'K':6720,'A':736,'B':456}
    assert all(not bitdot(ports[j],ports[k]) for j in range(120) for k in range(120) if K[j][k])
    # Independently generate depth-one helper core from the mathematical specification.
    frames={};moves=[];adds=[];roles=[]
    def alloc(P=(0,)*n):
        j=len(roles);roles.append(j);frames[j]=(0,)*n
        if P!=(0,)*n:move(j,P)
        return j
    def move(j,P):
        old=frames[j]
        assert bitmm(old,P)==old and bitmm(P,old)==old
        moves.append(bitadd(old,P));frames[j]=P
    def add(t,s,c):
        assert frames[t]==frames[s]
        adds.append((t,s,c))
    inputs=[alloc(outer(p,n)) for p in ports]
    rootloading=list(moves);moves.clear()
    outputs=[alloc(bitadd(I,outer(p,n))) for p in ports]
    for t in range(120):
        for a in range(120):
            if K[t][a]:
                z=alloc(outer(ports[a],n));add(z,inputs[a],Q(1));move(z,bitadd(I,outer(ports[t],n)));add(outputs[t],z,K[t][a]);move(z,I)
    gathers=[alloc(I) for _ in range(8)]
    for a in range(120):
        move(inputs[a],I)
        for j in range(8):
            if A[j][a]:add(gathers[j],inputs[a],A[j][a])
    assert len(roles)==6968 and len(adds)==14176
    core_moves=list(moves)
    for z in outputs:move(z,I)
    endpoint_moves=moves[len(core_moves):]
    all_local=rootloading+core_moves+endpoint_moves
    # Source line-to-full, target zero-to-cap; private center descents have rank 9.
    all_local += [bitadd(I,outer(p,n)) for p in ports]*2+[I]*8
    hist=Counter(len(indep(bitmt(P))) for P in all_local)
    globalhist=Counter({s:3*v for s,v in hist.items()});globalhist[2]+=240
    assert dict(sorted(globalhist.items()))=={1:41040,2:240,7:20160,8:1440,9:48}
    R=len(roles);v=120
    def core(z,transpose=False,inverse=False):
        seq=reversed(adds) if transpose or inverse else adds
        for t,s,c in seq:
            if transpose:t,s=s,t
            sparse_add(z[t],z[s],-c if inverse else c)
    def read(z):
        out=[dict(z[j]) for j in outputs]
        for t in range(v):
            for j in range(8):
                if B[t][j]:sparse_add(out[t],z[gathers[j]],B[t][j])
        return out
    clean=[{} for _ in range(R)]
    for t,j in enumerate(inputs):clean[j]={t:Q(1)}
    core(clean);assert read(clean)==[{t:Q(1)} for t in range(v)]
    # Full symbolic live input set, including every dirty helper independently.
    H=[{j:Q(1)} for j in range(R)];x=[{R+t:Q(1)} for t in range(v)];y=[{R+v+t:Q(1)} for t in range(v)]
    z=[dict(d) for d in H];old=[dict(d) for d in H];core(old)
    for t,resp in enumerate(read(old)):sparse_add(y[t],resp,-1)
    for t,j in enumerate(inputs):sparse_add(z[j],x[t])
    core(z)
    for t,resp in enumerate(read(z)):sparse_add(y[t],resp)
    core(z,inverse=True)
    for t,j in enumerate(inputs):sparse_add(z[j],x[t],-1)
    assert z==H
    assert y==[{R+v+t:Q(1),R+t:Q(1)} for t in range(v)]
    # Independently materialize inverse-adjoint logical chronology.
    z=[dict(d) for d in H];x=[{R+t:Q(1)} for t in range(v)];y=[{R+v+t:Q(1)} for t in range(v)]
    jt=[{} for _ in range(R)]
    for t,j in enumerate(outputs):sparse_add(jt[j],y[t])
    for j in range(8):
        for t in range(v):
            if B[t][j]:sparse_add(jt[gathers[j]],y[t],B[t][j])
    core(jt,transpose=True)
    for j in range(R):sparse_add(z[j],jt[j])
    for t,j in enumerate(inputs):sparse_add(x[t],z[j],-1)
    for t,s,c in adds:sparse_add(z[s],z[t],-c)
    for t,j in enumerate(outputs):sparse_add(z[j],y[t],-1)
    for j in range(8):
        for t in range(v):
            if B[t][j]:sparse_add(z[gathers[j]],y[t],-B[t][j])
    for t,s,c in reversed(adds):sparse_add(z[s],z[t],c)
    for t,j in enumerate(inputs):sparse_add(x[t],z[j])
    assert z==H and x==[{R+t:Q(1),R+v+t:Q(-1)} for t in range(v)]
    unique=set(all_local);with_phase=0
    for P in unique:
        rank,nontrivial=check_phase(P);with_phase+=nontrivial
    assert with_phase>0
    record('E8_depth_one_core_dirty_both_orientations',{'ports':v,'nonzero_counts':counts,'helpers':R,'core_ADDs':len(adds),'independent_symbolic_live_columns':R+2*v,'global_histogram':dict(sorted(globalhist.items())),'rank_mass':sum(s*c for s,c in globalhist.items()),'defect':27*7208-sum(s*c for s,c in globalhist.items()),'distinct_phase_projectors':len(unique),'nonzero_phase_translations':with_phase,'private_arrays':R+120+8})
    # Exact owner geometry, including literal nonsymmetric port-basis construction.
    m=27;I27=biteye(m);H0=tuple((1<<j) if j<9 else 0 for j in range(m))
    Qs=[(0,)*m,tuple((1<<j) if 10<=j<18 else 0 for j in range(m)),tuple((1<<j) if 10<=j<18 or 19<=j<27 else 0 for j in range(m))]
    routes=[]
    for p in ports:
        zero=next(j for j in range(9) if not (p>>j)&1)
        swap=list(I)
        swap[0],swap[zero]=swap[zero],swap[0]
        w=p^(1<<zero);At=bitmm(bitadd(I,outer(w,9)),tuple(swap))
        assert bitmm(bitmt(At),At)==I and bitmv(At,1)==p
        basis=bitmt(At)
        for c in [1,2]:
            rho=I27
            for j in range(1,9):rho=bitadd(rho,outer(basis[j]^(1<<(9*c+j)),m))
            assert bitmt(rho)==rho and bitmm(rho,rho)==I27
            P=outer(p,m);cap=bitadd(H0,P)
            def conj(T):return bitmm(bitmm(rho,T),bitmt(rho))
            assert conj(bitadd(H0,Qs[c-1]))==bitadd(P,Qs[c])
            assert conj(bitadd(cap,Qs[c-1]))==Qs[c]
            assert conj(bitadd(H0,Qs[c]))==bitadd(H0,Qs[c])
            assert conj(bitadd(cap,Qs[c]))==bitadd(cap,Qs[c])
            routes.append(rho)
    assert mm(mm([[Q(1),0],[Q(1),Q(1)]],[[Q(1),Q(-1)],[0,Q(1)]]),[[Q(1),0],[Q(1),Q(1)]])==[[Q(0),Q(-1)],[Q(1),Q(0)]]
    finalbits=tuple((1<<j) if j in [9,18] else 0 for j in range(m));check_phase(finalbits)
    owner=bitmm(routes[0],routes[-1]);assert bitmm(owner,bitmt(owner))==I27
    blocks=[tuple((1<<j) if 9*c<=j<9*(c+1) else 0 for j in range(m)) for c in range(3)]
    owned=[bitmm(bitmm(owner,P),bitmt(owner)) for P in blocks]
    assert bitadd(bitadd(owned[0],owned[1]),owned[2])==I27
    assert all(bitmm(owned[j],owned[k])==(0,)*m for j in range(3) for k in range(3) if j!=k)
    record('E8_owner_cover_projector_chronology',{'port_routes':len(routes),'literal_inverse_transposes':True,'global_FBF':True,'helper_windows_orthogonal_complete':True,'final_rank_two_phase':True})
    moment(globalhist)

def log_upper(x,terms=36):
    x=Q(x);assert x>=1
    shifts=0
    while x>2:x/=2;shifts+=1
    def unit(y):
        u=(y-1)/(y+1)
        series=sum((2*u**(2*j+1)/Q(2*j+1) for j in range(terms)),Q(0))
        tail=2*u**(2*terms+1)/((2*terms+1)*(1-u*u))
        return series+tail
    val=unit(x)+shifts*unit(Q(2))
    # Upward dyadic round is another exact inequality.
    d=1<<100;return Q((val.numerator*d+val.denominator-1)//val.denominator,d)

def moment(hist):
    kappa=Q(1,15000);m=27;W=7208
    upper=Q(0)
    for s,c in hist.items():
        z=kappa*log_upper(Q(m,s));assert 0<=z<1
        exp=sum((z**j/Q(math.factorial(j)) for j in range(5)),Q(0))+z**5/(120*(1-z/6))
        upper+=s*c*exp
    slack=m*W-upper;assert slack>1
    p=1-kappa;a=m*m+(W-1).bit_length();assert a==742
    # Gap normalized by row padding without needing |O(27,2)|.
    gap_lower=Q(1,m*(1<<a))
    with localcontext() as ctx:
        ctx.prec=60;disp=str(Decimal(slack.numerator)/Decimal(slack.denominator))
    record('strict_moment_and_padding',{'kappa':str(kappa),'alpha':str(p),'slack_lower_numerator':str(slack.numerator),'slack_lower_denominator':str(slack.denominator),'slack_lower_decimal_display':disp,'padding_bits':a,'normalized_gap_lower':str(gap_lower),'max_child_rank':max(hist),'strict_descent':'sk <= ell-a-b < ell, k>=1','all_padding_roles_are_actual_inputs':True})

def sector_checks():
    f=Field(4);C=[[(1+f.z)/2,(1-f.z)/2],[(1-f.z)/2,(1+f.z)/2]]
    cases=[[[[1,0]]],[[[2,0],[1]],[[1,0]]],[[[3,1],[0],[2]],[[2,0],[1]]],[[[2,0],[3,1]],[[0],[2,1]],[[1,0]]]]
    # Exhaust all order/pair-position choices on small two-axis layouts.
    for a in range(2,6):
        for b in range(2,6):
            cases.append([[[a-1,0]]+[[j] for j in range(1,a-1)],[[b-1,0]]+[[j] for j in range(1,b-1)]])
    maxR=0;columns=0
    for blocks in cases:
        rad=[sum(map(len,axis)) for axis in blocks];R=math.prod(rad);maxR=max(R,maxR)
        tau=[math.prod(rad[j+1:]) for j in range(len(rad))]
        mapping={};sectors=[];prefixnodes=sum(math.prod(rad[:j]) for j in range(len(rad)+1));assert prefixnodes<2*R
        for selected in product(*blocks):
            q=[len(B) for B in selected];S=0;Qprefix=1
            for j,B in enumerate(selected):
                previous=sum(len(A) for A in blocks[j][:blocks[j].index(B)])
                S+=Qprefix*previous*tau[j];Qprefix*=len(B)
            for t in product(*[range(len(B)) for B in selected]):
                Iaddr=0;o=0
                for j,tt in enumerate(t):Iaddr=Iaddr*rad[j]+selected[j][tt];o=o*q[j]+tt
                mapping[Iaddr]=S+o
            sectors.append((S,Qprefix,q.count(2)))
        assert sorted(mapping.values())==list(range(R))
        assert sorted(j for S,w,k in sectors for j in range(S,S+w))==list(range(R))
        inv={v:k for k,v in mapping.items()}
        # Exact operator comparison on every independent input column.
        for Iaddr in range(R):
            digits=[];x=Iaddr
            for r in reversed(rad):digits.append(x%r);x//=r
            digits=digits[::-1];choices=[]
            for j,d in enumerate(digits):
                B=next(B for B in blocks[j] if d in B)
                choices.append([(out,C[B.index(out)][B.index(d)]) for out in B] if len(B)==2 else [(d,f.one)])
            direct={}
            for selected in product(*choices):
                out=0;c=f.one
                for j,(d,z) in enumerate(selected):out=out*rad[j]+d;c=c*z
                direct[out]=c
            packed=mapping[Iaddr];S,w,k=next(sec for sec in sectors if sec[0]<=packed<sec[0]+sec[1]);b=packed-S
            actual={}
            for out in range(w):
                d=popcount(out^b);actual[inv[S+out]]=C[0][0]**(k-d)*C[0][1]**d
            assert actual==direct;columns+=1
    record('ragged_ordered_sector_full_operators',{'layouts':len(cases),'independent_columns':columns,'largest_width':maxR,'prefix_nodes_lt_2R':True,'all_packed_addresses_bijective':True})

def isprime(p):return p>=2 and all(p%d for d in range(2,math.isqrt(p)+1))
def working(N):
    primes=[];r=1;p=3
    while True:
        if isprime(p):
            if r*p>2*N:break
            r*=p;primes.append(p)
        p+=2
    q=1
    while r*q<2*N:q*=2
    L=r*q;aux=1<<((16*L-1).bit_length());D=2*N*L*aux
    return primes,p,q,L,D,aux

def roots_crt():
    lengths=list(range(1,4097))+[2**j-1 for j in range(13,81)]+[2**j for j in range(13,81)]+[10**j+7 for j in range(4,45)]
    exhaustive=0;phasepairs=0;records=[]
    for N in lengths:
        primes,nextp,q,L,D,aux=working(N)
        assert 2*N<=L<4*N and q<2*nextp
        assert D<1024*N**3 and D%(2*N)==0 and D%L==0
        factors=primes+([q] if q>1 else [])
        for r in factors:
            assert D%r==0
            for power in range(0,(8*r).bit_length()):
                order=1<<power
                if order<=8*r:assert D%order==0
        ds=[pow(L//r,-1,r) for r in factors];Es=[(L//r)*d for r,d in zip(factors,ds)]
        assert all(E%r==1 for E,r in zip(Es,factors))
        assert all(E%r==0 for j,E in enumerate(Es) for k,r in enumerate(factors) if j!=k)
        if L<=100:
            assert sorted(sum(E*d for E,d in zip(Es,digits))%L for digits in product(*[range(r) for r in factors]))==list(range(L))
            for j,k in product(range(L),repeat=2):
                assert (j*k-sum((L//r)*d*(j%r)*(k%r) for r,d in zip(factors,ds)))%L==0
                phasepairs+=1
            exhaustive+=1
        if N<=16 or N in [4096,2**80,10**44+7]:records.append({'N':str(N),'L':str(L),'D':str(D),'factors':factors,'root_aux':str(aux)})
    record('working_lengths_master_root_CRT',{'lengths':len(lengths),'CRT_exhaustive_cases':exhaustive,'CRT_phase_pairs':phasepairs,'largest_N':str(max(lengths)),'records':records})

def fourier(x,root):
    n=len(x)
    return [sum((val*root**(j*k) for k,val in enumerate(x)),root.f.zero) for j in range(n)]

def chirp():
    checked=[];wrong_sign=0
    for N in [1,2,3,4,5,6,7,8,9,10,12]:
        _,_,_,L,D,_=working(N);order=math.lcm(2*N,L);assert D%order==0
        f=Field(order);eta=f.z**(order//(2*N));omega=f.z**(order//L);zeta=eta**2
        x=[f.v(Q((-1)**j*(j+1),j+2)) for j in range(N)]
        a=[eta**(j*j)*x[j] if j<N else f.zero for j in range(L)]
        b=[f.zero]*L
        for u in range(-N+1,N):b[u%L]=eta**(-u*u)
        assert len({u%L for u in range(-N+1,N)})==2*N-1
        fa=fourier(a,omega);fb=fourier(b,omega);fp=fourier([v*w for v,w in zip(fa,fb)],omega)
        convolution=[fp[-j%L]/L for j in range(L)]
        actual=[eta**(j*j)*convolution[j] for j in range(N)]
        direct=fourier(x,zeta);assert actual==direct
        if N>=3 and fourier(x,zeta.inv())!=direct:wrong_sign+=1
        checked.append({'N':N,'L':L,'cyclotomic_order':order,'degree':f.degree})
    assert wrong_sign>0
    record('exact_three_transform_chirp',{'cases':checked,'negative_root_convention_detected':wrong_sign,'fixed_kernel_forward_transform_charged':True})

def exponent_scope():
    alpha=Q(14999,15000);beta=4-alpha;saving=Q(1,30000)
    assert beta==Q(45001,15000) and (1-saving)-alpha==saving
    # An explicit absorption range: u=log log N, beta log u <= u/30000.
    # For u>=10^7, log u <= sqrt(u), and sqrt(u)>=30000 beta is
    # sufficient; choosing u>=10^10 is a conservative exact threshold.
    assert 10**10>=(30000*beta)**2
    f=Field(3);assert f.z*f.z+f.z+1==0
    record('exponents_root_scope',{'alpha':str(alpha),'beta':str(beta),'eventual_log_exponent':str(1-saving),'absorption_sufficient':'log log N >= 10^10 (natural logs); no practical crossover claim','root_free_F3_obstruction':'zeta_3 has nonrational imaginary part sqrt(3)/2; Q(i) closed under field operations'})

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check',action='store_true',help='compare the deterministic complete receipt with RESULTS.json')
    ap.add_argument('--write',type=Path,help='write a fresh receipt; does not alter package sources')
    args=ap.parse_args()
    if args.check and args.write:ap.error('choose --check or --write')
    for func in [authentication,shears,dag_replay,e8_provider,sector_checks,roots_crt,newton_toeplitz,chirp,exponent_scope]:func()
    RESULT['status']='ALL_EXACT_CHECKS_PASSED'
    canonical=json.dumps(RESULT,indent=2,sort_keys=True)+'\n'
    if args.write:
        args.write.write_text(canonical)
    else:
        expected=json.loads((ROOT/'RESULTS.json').read_text())
        assert json.loads(canonical)==expected,'complete deterministic receipt changed'
    print('ALL_EXACT_CHECKS_PASSED',flush=True)

if __name__=='__main__':main()
