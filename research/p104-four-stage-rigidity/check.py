#!/usr/bin/env python3
"""Exact local coefficient-space checker. New code: @CubeJerry/OpenAI; Apache-2.0."""
from fractions import Fraction as F
from itertools import combinations
import json
from pathlib import Path
from hashlib import sha1, sha256

def mat(a): return [[F(x) for x in row] for row in a]
def eye(n): return [[F(i == j) for j in range(n)] for i in range(n)]
def zero(n,m=None): return [[F(0) for _ in range(n if m is None else m)] for _ in range(n)]
def add(a,b): return [[x+y for x,y in zip(ar,br)] for ar,br in zip(a,b)]
def scale(a,s): return [[x*s for x in r] for r in a]
def sub(a,b): return add(a,scale(b,-1))
def mul(a,b): return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]
def tr(a): return sum(a[i][i] for i in range(len(a)))
def catcol(a,b): return [r+s for r,s in zip(a,b)]
def rank(a):
    a=[r[:] for r in a]; k=0
    for j in range(len(a[0])):
        p=next((p for p in range(k,len(a)) if a[p][j]),None)
        if p is None: continue
        a[k],a[p]=a[p],a[k]; z=a[k][j]; a[k]=[x/z for x in a[k]]
        for p in range(len(a)):
            if p!=k:
                z=a[p][j];a[p]=[x-z*y for x,y in zip(a[p],a[k])]
        k+=1
    return k
def inv(a):
    n=len(a);a=catcol(a,eye(n))
    for j in range(n):
        p=next(p for p in range(j,n) if a[p][j]);a[j],a[p]=a[p],a[j]
        z=a[j][j];a[j]=[x/z for x in a[j]]
        for p in range(n):
            if p!=j:
                z=a[p][j];a[p]=[x-z*y for x,y in zip(a[p],a[j])]
    return [r[n:] for r in a]
def require(t,s):
    if not t: raise ValueError(s)
def canonical(n):
    u=[[[F(j==i)] for j in range(n)] for i in range(n)]+[[[F(-(-1)**j)] for j in range(n)]]
    v=[[[F((i>j)-(i<j)) for j in range(n)]] for i in range(n+1)]
    r=[mul(x,y) for x,y in zip(u,v)]
    b=[]; p=eye(n)
    for x in r: p=mul(sub(eye(n),scale(x,2)),p);b.append(p)
    require(p==scale(eye(n),-1),'full central endpoint')
    return u,v,r,b
def odd(n,i):
    u=[[F(j==i)] for j in range(n)]; a=[[F((-1)**j if j<=i else 0)] for j in range(n)]
    h=[[F(j<=i) for j in range(n)]];v=[[F((i>j)-(i<j)) for j in range(n)]]
    return add(mul(u,h),mul(a,v))

def closure_tests():
    count=0
    for n in range(4,22,2):
        u,v,r,b=canonical(n)
        for i in range(1,n,2):
            e=odd(n,i)
            require(mul(e,e)==e and rank(e)==2,'odd projector')
            require(mul(e,b[i])==mul(b[i],e),'odd prefix')
            for j in range(n+1):
                if j==i:continue
                if not (j%2==1 or j==0 and i>=3 or j==n and i<=n-3):continue
                a=catcol(u[j],mul(e,u[j]));c=v[j]+mul(v[j],e)
                require(rank(a)==rank(c)==2,'closure dimension')
                require(mul(c,a)==zero(2),'closure zero pairing')
                count+=1
    return count

def source6398():
    data=authenticate_root()
    n=data['fields'];u,v,r,b=canonical(n)
    ps={i:mat(data['sites'][i]['projector']) for i in data['full_sites']}
    for i,p in ps.items():
        require(mul(p,p)==p,'source idempotent')
        require(mul(p,r[i])==mul(r[i],p)==r[i],'source compatibility')
        require(mul(p,b[i])==mul(b[i],p),'source prefix')
    for p,q in combinations(ps.values(),2):require(mul(p,q)==mul(q,p),'source stage commutation')
    h=mat(data['input_basis']);hi=mat(data['output_basis'])
    require(mul(h,hi)==eye(n),'source basis')
    # Expand all sixteen independent-stage monomials by chronological multiplication.
    for sign in (1,-1):
        poly={0:eye(n)}
        for i in range(n+1):
            query=add(eye(n),scale(r[i],sign-1))
            poly={m:mul(query,c) for m,c in poly.items()}
            if i in ps:
                bit=1<<data['full_sites'].index(i);p=ps[i];out={}
                for m,c in poly.items():
                    out[m]=mul(sub(eye(n),p),c);out[m|bit]=mul(p,c)
                poly=out
        for mask in range(16):
            expected=zero(n)
            for k,row in enumerate(data['masks']):
                if sum(bit<<j for j,bit in enumerate(row))==mask:expected[k][k]=F(sign)
            require(mul(mul(hi,poly[mask]),h)==expected,'source literal endpoint')
    return [int(tr(p)) for p in ps.values()]

def authenticate_root():
    data=Path(__file__).with_name('SOURCE6398_ROOT.json').read_bytes()
    blob=sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    require(blob=='b59f1ea89aca17f0a76131743c12f2c724421df8','source6398 Git blob')
    return json.loads(data)

def authenticate_sources():
    root=Path(__file__).parent
    sources=json.loads((root/'ORIGINS.json').read_text())
    for source in sources['files']:
        data=(root/source['local_path']).read_bytes()
        require(len(data)==source['bytes'],'source byte count')
        require(sha256(data).hexdigest()==source['sha256'],'source SHA256')
        require(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==source['git_blob'],'source Git blob')
    return len(sources['files'])

def coordinate_basis(n):
    u,_,_,_=canonical(n)
    columns=[u[0],u[1],u[n-1],u[n]]
    for j in range(2,n-2):
        columns.append([[F(k==j)-F(k==n-2)] for k in range(n)])
    return [[column[row][0] for column in columns] for row in range(n)]

def extend(a,n,identity=False):
    out=eye(n) if identity else zero(n)
    for i,row in enumerate(a):
        for j,x in enumerate(row):out[i][j]=x
    return out

def tensor(a,q):
    return [[a[i//q][j//q]*F(i%q==j%q) for j in range(len(a[0])*q)] for i in range(len(a)*q)]

def literal_word(n,q,r,ps,h,hi,masks):
    d=n*q;count=0
    for sign in (1,-1):
        poly={0:eye(d)}
        for i in range(n+1):
            query=add(eye(d),scale(r[i],sign-1))
            poly={m:mul(query,c) for m,c in poly.items()}
            if i in ps:
                bit=1<<list(ps).index(i);p=ps[i];out={}
                for m,c in poly.items():
                    out[m]=mul(sub(eye(d),p),c);out[m|bit]=mul(p,c)
                poly=out
        for mask in range(16):
            expected=zero(d)
            for k,label in enumerate(masks):
                if label==mask:expected[k][k]=F(sign)
            require(mul(mul(hi,poly[mask]),h)==expected,'extended literal endpoint')
            count+=1
    return count

def extended_attainment():
    data=authenticate_root();s6=coordinate_basis(6);s6i=inv(s6)
    source_ps=[mat(data['sites'][i]['projector']) for i in data['full_sites']]
    source_h=mat(data['input_basis']);count=0;cases=[]
    for n,q in ((6,1),(8,1),(10,1),(12,1),(6,2),(6,3)):
        sn=coordinate_basis(n);sni=inv(sn)
        require(all(x.denominator==1 for row in sni for x in row),'unimodular extension')
        u,v,rs,bs=canonical(n);r=[tensor(x,q) for x in rs];b=[tensor(x,q) for x in bs]
        sites=[0,1,n-1,n]
        ps={i:tensor(mul(mul(sn,extend(mul(mul(s6i,p),s6),n)),sni),q) for i,p in zip(sites,source_ps)}
        h0=mul(sn,extend(mul(s6i,source_h),n,True));h=tensor(h0,q);hi=inv(h)
        labels=[15,3,12,0,4,2]+[0]*(n-6);masks=[label for label in labels for _ in range(q)]
        for i,p in ps.items():
            require(mul(p,p)==p,'extension idempotence')
            require(mul(p,r[i])==mul(r[i],p)==r[i],'extension compatibility')
            require(mul(p,b[i])==mul(b[i],p),'extension prefix')
        for p,t in combinations(ps.values(),2):require(mul(p,t)==mul(t,p),'extension commutation')
        count+=literal_word(n,q,r,ps,h,hi,masks)
        require([rank(p) for p in ps.values()]==[2*q,3*q,3*q,2*q],'extension ranks')
        cases.append([n,q])
    return {'cases':cases,'formal_coefficient_matrices':count}

def block_rigidity_tests():
    count=0
    for q in range(1,6):
        ident=eye(q);m=eye(q);g=eye(q);k=eye(q)
        for j in range(q-1):
            m[j][j+1]=F(j+2);g[j+1][j]=F(j+3);k[j][j+1]=F(j+4)
        mi=inv(m);gi=inv(g);ki=inv(k)
        # Dense invertible factors need not commute with M or each other.
        vb=mul(m,gi);ub=g;vc=mul(scale(mi,-1),ki);uc=k
        require(mul(vb,ub)==m and mul(vc,uc)==scale(mi,-1),'own extra Gram')
        base_b=add(scale(mi,-1),mul(add(ident,mi),sub(ident,m)))
        base_c=add(m,mul(scale(add(ident,m),-1),sub(ident,mi)))
        require(base_b==scale(m,-1) and base_c==mi,'ordered block signs')
        for z in range(q+1):
            if z:
                left=[row[:z] for row in vb];right=uc[:z]
                require(rank(mul(left,right))==z,'shared sector rank')
                require(mul(left,right)!=zero(q),'positive shared sector rejects')
            count+=1
    return count

def false_hypothesis_controls():
    n=6;u,v,r,b=canonical(n);e1=odd(n,1);e3=odd(n,3)
    require(mul(e1,r[0])==mul(r[0],e1)==r[0],'near endpoint compatibility')
    require(mul(e1,b[0])==mul(b[0],e1),'near endpoint prefix')
    require(2*rank(e1)<5,'near endpoint disproves unqualified pair floor')
    require(mul(e1,e3)!=mul(e3,e1),'noncommuting odd stages control')
    star=sub(mul(u[1],v[3]),mul(u[3],v[1]))
    require(mul(star,star)==star and rank(star)==2,'missing prefix projector')
    for i in (1,3):
        require(mul(star,r[i])==mul(r[i],star)==r[i],'missing prefix compatibility')
        require(mul(star,b[i])!=mul(b[i],star),'actual prefix is necessary')
    return ['near_endpoint_floor_false','mutual_commutation_required','actual_prefix_required']

def sector_census():
    counts=[]
    for q in range(1,6):
        survivors=[]
        # Sector order: AB,CD,BC,ABC,BCD,ABCD,B-only,C-only.
        for w in range(q,2*q+1):
            for s in range(2*q-w+1):
                for t in range(2*q-w+1):
                    x=2*q-w-s;y=2*q-w-t
                    for z in range(3*q+1):
                        b=3*q-(x+z+s+t+w);c=3*q-(y+z+s+t+w)
                        if min(b,c)<0:continue
                        union=x+y+z+s+t+w+b+c
                        if union-b<4*q or union-c<4*q:continue
                        survivors.append([x,y,z,s,t,w,b,c])
        expected=[[q,q,z,0,0,q,q-z,q-z] for z in range(q+1)]
        require(sorted(survivors)==sorted(expected),'complete integer sector census')
        accepted=[s for s in survivors if s[2]==0]
        require(accepted==[[q,q,0,0,0,q,q,q]],'equality profile unique after block obstruction')
        counts.append({'q':q,'before_cross_gram':len(survivors),'after_cross_gram':len(accepted)})
    return counts

def endpoint_mutations():
    data=authenticate_root();n=6;u,v,r,b=canonical(n)
    ps={i:mat(data['sites'][i]['projector']) for i in data['full_sites']}
    h=mat(data['input_basis']);hi=mat(data['output_basis']);masks=[15,3,12,0,4,2]
    mutants=[]
    missing_query=[x for x in r];missing_query[2]=zero(n)
    mutants.append(('omitted_thin_query',missing_query,ps))
    p_mut={i:p for i,p in ps.items()};unit=zero(n);unit[5][5]=F(1)
    p_mut[1]=sub(ps[1],mul(mul(h,unit),hi))
    mutants.append(('omitted_independent_stage_coordinate',r,p_mut))
    rejected=[]
    for name,queries,stages in mutants:
        try:literal_word(n,1,queries,stages,h,hi,masks)
        except ValueError as error:
            require(str(error)=='extended literal endpoint','mutation rejection reason')
            rejected.append(name)
        else:raise ValueError('endpoint mutation accepted: '+name)
    return rejected

if __name__=='__main__':
    print(json.dumps({'source_files':authenticate_sources(),'zero_pair_closures':closure_tests(),'source6398_ranks':source6398(),
        'attainment':extended_attainment(),'coupled_block_cases':block_rigidity_tests(),'sector_census':sector_census(),
        'false_hypothesis_controls':false_hypothesis_controls(),'endpoint_mutations':endpoint_mutations()},sort_keys=True))
