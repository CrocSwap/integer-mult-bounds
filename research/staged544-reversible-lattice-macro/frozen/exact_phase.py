"""Independent scalar Gaussian-integer action; no native compiler imports.
Chris R / Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0.
"""
from functools import lru_cache

N = 9
SIZE = 1 << N

def need(ok, why):
    if not ok:
        raise ValueError(why)

def rot(z, p):
    a,b=z
    return ((a,b),(-b,a),(-a,-b),(b,-a))[p%4]

def lin(cols,x):
    y=0
    for j,c in enumerate(cols):
        if x & (1<<j): y ^= c
    return y

def complete(U):
    need(len(U)<=N and all(isinstance(u,int) and 0<u<SIZE for u in U),'frame vector domain')
    independent={0}
    for u in U:
        need(u not in independent,'dependent frame basis')
        independent |= {x^u for x in independent}
    out=[]; span={0}
    for c in list(U)+[1<<j for j in range(N)]:
        if c not in span:
            out.append(c);span |= {x^c for x in span}
    need(len(out)==N, 'basis completion')
    return tuple(out)

@lru_cache(None)
def kernel(cols):
    """Construct K_G directly from its permutation and Z4 quadratic form.
    Inversion by exhaustive bijection, not Gaussian elimination/tableaux.
    """
    need(len(cols)==N, 'column arity')
    perm=tuple(lin(cols,x) for x in range(SIZE))
    need(set(perm)==set(range(SIZE)), 'singular binary map')
    back=[0]*SIZE
    for x,y in enumerate(perm):back[y]=x
    invcols=[back[1<<j] for j in range(N)]
    gram=[[((invcols[i]&invcols[j]).bit_count()+(i==j))%2 for j in range(N)]for i in range(N)]
    q=[]
    for y in perm:
        bits=[i for i in range(N) if y>>i&1]
        q.append((sum(gram[i][i] for i in bits)+2*sum(gram[i][j]for i in bits for j in bits if i<j))%4)
    return perm,tuple(q)

def mono(v, data, inverse=False):
    perm,phase=data
    if inverse:
        inv=[0]*SIZE
        for x,y in enumerate(perm): inv[y]=x
        return {inv[y]:rot(z,-phase[inv[y]])for y,z in v.items()}
    return {perm[x]:rot(z,phase[x])for x,z in v.items()}

def coordinate(v, axes, inverse=False):
    """C=((1+i)I+(1-i)X)/2; exact numerator and dyadic denominator."""
    sign=-1 if inverse else 1
    for axis in axes:
        out={}
        for x,(a,b) in v.items():
            for y,z in ((x,(a-sign*b,b+sign*a)),(x^(1<<axis),(a+sign*b,b-sign*a))):
                r,s=out.get(y,(0,0));out[y]=(r+z[0],s+z[1])
        v={x:z for x,z in out.items()if z!=(0,0)}
    return v,len(axes)

def frame(v,U,inverse=False):
    if not U:return v,0
    k=kernel(complete(U))
    v=mono(v,k,True);v,d=coordinate(v,list(range(len(U))),inverse)
    return mono(v,k),d

@lru_cache(None)
def recipe_data(rows,quad,alpha,offset,phase):
    need(len(rows)==len(quad)==len(alpha)==N,'recipe arity')
    need(all(0<=x<SIZE for x in rows+quad)and 0<=offset<SIZE,'recipe bits')
    need(all(0<=x<4 for x in alpha)and 0<=phase<4,'recipe phase range')
    need(all(((quad[i]>>j)&1)==((quad[j]>>i)&1)for i in range(N)for j in range(N)),'symmetric quadratic form')
    need(all(alpha[i]%2==((quad[i]>>i)&1)for i in range(N)),'quadratic parity')
    perm=[];phasev=[]
    for x in range(SIZE):
        perm.append(sum(((r&x).bit_count()%2)<<i for i,r in enumerate(rows))^offset)
        bits=[i for i in range(N)if x>>i&1]
        phasev.append((phase+sum(alpha[i]for i in bits)+2*sum((quad[i]>>j)&1 for i in bits for j in bits if i<j))%4)
    need(len(set(perm))==SIZE,'recipe bijection')
    return tuple(perm),tuple(phasev)

def decoded(rec):
    return recipe_data(tuple(rec['matrix_rows']),tuple(rec['quadratic_rows']),tuple(rec['linear_Z4']),rec['offset'],rec['phase'])

def compiler_action(v,rec):
    d=0
    if rec['right'] is not None:v=mono(v,decoded(rec['right']))
    if rec['rank']:
        v,d=coordinate(v,list(range(rec['rank'])))
    v=mono(v,decoded(rec['left']))
    return v,d

def direct_action(v,item):
    v,a=frame(v,item['entrance'],True)
    if item['kind']=='warp':v=mono(v,kernel(tuple(item['G_columns'])),item['sign']<0)
    v,b=frame(v,item['terminal'])
    return v,a+b

def equal(a,da,b,db):
    power=max(da,db)
    return {x:(r<<(power-da),s<<(power-da))for x,(r,s)in a.items()} == {x:(r<<(power-db),s<<(power-db))for x,(r,s)in b.items()}

def check_item(item):
    rec=item['recipe']
    expected=0 if item['kind']=='warp' else len(item['terminal'])-len(item['entrance'])
    need(rec['rank']==expected,'charged rank')
    support=0; phase_hist=[0]*4
    import hashlib,json
    digest=hashlib.sha256()
    for x in range(SIZE):
        a,da=direct_action({x:(1,0)},item);b,db=compiler_action({x:(1,0)},rec)
        need(equal(a,da,b,db),'phase/operator mismatch at column '+str(x))
        support+=len(a)
        # Canonical dyadic normalization makes receipt independent of implementation denominator.
        while da and all(r%2==s%2==0 for r,s in a.values()):
            a={y:(r//2,s//2)for y,(r,s)in a.items()};da-=1
        for r,s in a.values():
            if not s:phase_hist[0 if r>0 else 2]+=1
            elif not r:phase_hist[1 if s>0 else 3]+=1
        digest.update(json.dumps([x,da,sorted(a.items())],separators=(',',':')).encode())
    return dict(columns=SIZE,nonzero_coefficients=support,gaussian_axis_phase_histogram=phase_hist,operator_sha256=digest.hexdigest())

def lift_cocycle(G,H):
    """K_H K_G = K_(HG) Z_ell. Exact finite Z4 phase defect."""
    gp,gq=kernel(tuple(G));hp,hq=kernel(tuple(H))
    HG=tuple(lin(H,c)for c in G);cp,cq=kernel(HG)
    defect=[(gq[x]+hq[gp[x]]-cq[x])%4 for x in range(SIZE)]
    ell=sum((defect[1<<j]//2)<<j for j in range(N))
    need(all(d==2*((x&ell).bit_count()%2)for x,d in enumerate(defect)),'lift defect is not Z2 linear')
    need(all(hp[gp[x]]==cp[x]for x in range(SIZE)),'binary composition')
    return dict(G_columns=list(G),H_columns=list(H),product_columns=list(HG),phase_character_mask=ell,flipped_columns=sum(d==2 for d in defect))

def cocycle_certificate(items):
    Gs=sorted({tuple(item['G_columns'])for item in items if item['kind']=='warp'})
    inverses=[]
    for G in Gs:
        perm,_=kernel(G);back=[0]*SIZE
        for x,y in enumerate(perm):back[y]=x
        Gi=tuple(back[1<<j]for j in range(N));inverses.append(lift_cocycle(G,Gi))
    pairs=[lift_cocycle(G,H)for G in Gs for H in Gs]
    need([r['phase_character_mask']for r in inverses]==[0,0,0,256],'actual inverse cocycle witness')
    return dict(actual_binary_maps=len(Gs),inverse_lifts=inverses,abstract_pair_compositions=pairs,pair_composition_scope='Algebraic closure controls on the four actual maps; not asserted to be adjacent in the word.',inverse_correction='K_G inverse = Z_ell K_(G inverse), in right-to-left matrix convention')
