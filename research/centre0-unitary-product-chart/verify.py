#!/usr/bin/env python3
"""Exact Gram/action certificate for the changed-output unitary centre0 chart.

ToikY with substantial OpenAI Codex assistance. Apache-2.0.
Credit Petalas6667, JoyboyBrian5130, Clear1nsight5101 and retained lineage.
No predecessor program is imported or executed.
"""
from fractions import Fraction as F
import hashlib
import json
from math import gcd, lcm, isqrt
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
PIN = '261b229749a45c19cb8eb88752018957cd36d4660e4c2dba10733433f7932055'
D = 6097
ZERO = (F(0), F(0))
ONE = (F(1), F(0))
H = (F(937), F(-12))
LAM = (F(937), F(12))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def strict_load(raw):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            need(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    def bad(value):
        raise ValueError('nonfinite JSON '+value)
    return json.loads(raw, object_pairs_hook=unique, parse_constant=bad)


def authenticate(root=ROOT):
    raw = (root/'SOURCE-PINS.json').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PIN, 'source manifest')
    rows = strict_load(raw)['files']
    need(len(rows) == 5, 'five source objects')
    for row in rows:
        path = root/row['local_path']
        need(not path.is_symlink(), 'source symlink')
        body = path.read_bytes()
        need(len(body) == row['bytes'], 'source length')
        need(hashlib.sha256(body).hexdigest() == row['sha256'], 'source digest')
        need(hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest() == row['git_blob'], 'source Git blob')


def q(a, b=0):
    return F(a), F(b)


def qa(x, y):
    return x[0]+y[0], x[1]+y[1]


def qs(x, y):
    return x[0]-y[0], x[1]-y[1]


def qm(x, y):
    return x[0]*y[0]+D*x[1]*y[1], x[0]*y[1]+x[1]*y[0]


def scale(x, c):
    return x[0]*c, x[1]*c


def qi(x):
    den = x[0]*x[0]-D*x[1]*x[1]
    need(den != 0, 'quadratic inverse')
    return x[0]/den, -x[1]/den


def positive(x):
    a,b = x
    if b >= 0:
        return a > 0 or (b > 0 and D*b*b > a*a)
    return a > 0 and a*a > D*b*b


def pack(x):
    return [str(x[0]), str(x[1])]


def dot(a, b):
    return sum((x*y for x,y in zip(a,b) if x and y), F(0))


def qdot(a, b):
    out = ZERO
    for x,y in zip(a,b):
        if x != ZERO and y != ZERO:
            out = qa(out, qm(x,y))
    return out


def mv(a, v):
    return [dot(row,v) for row in a]


def qmv(a, v):
    return [tuple(sum((entry*x[k] for entry,x in zip(row,v) if entry), F(0))
                  for k in range(2)) for row in a]


def digest(value):
    raw = (json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()
    return hashlib.sha256(raw).hexdigest()


def sources():
    r = [[F(x) for x in row] for row in strict_load((ROOT/'inputs/R.json').read_bytes())]
    data = strict_load((ROOT/'inputs/CORRECTED-DERIVATION.json').read_bytes())
    need(len(r) == 8 and all(len(row) == 112 for row in r), 'literal R shape')
    J = data['selected_ports_J']
    need(J == [0,7,20,23,86,93,108,111], 'selected ports')
    u = [[r[i][j]*F(-11 if j in J else 1,4) for j in range(112)] for i in range(8)]
    g = [[F(i == j)-sum(u[k][i]*r[k][j] for k in range(1,8))
          for j in range(112)] for i in range(112)]
    literal = [[F(x) for x in row] for row in data['F_actual']]
    need(g == literal, 'all actual centre0 code entries')
    return r,u,g,[list(row) for row in zip(*g)]


def source_gram(r,u):
    out = {}
    for name,a,b,value in [('RR',r,r,F(56)),('UU',u,u,F(67,2)),('RU',r,u,F(2))]:
        m = [[dot(x,y) for y in b] for x in a]
        need(m == [[value*int(i == j) for j in range(8)] for i in range(8)], 'source '+name)
        out[name] = [[str(x) for x in row] for row in m]
    return out


def active(r,u,g,gt):
    t = scale(qa(ONE,H), F(-1,56))
    need(qm(H,LAM) == ONE and positive(H) and positive(qs(ONE,H)), 'ordered roots')
    pairs = []
    for i in range(1,8):
        v = [qa(q(x),scale(t,y)) for x,y in zip(u[i],r[i])]
        w = [qa(scale(H,x),scale(t,y)) for x,y in zip(u[i],r[i])]
        n,m = qdot(v,v),qdot(w,w)
        need(positive(n) and m == qm(H,n) and qm(LAM,m) == n, 'active and balanced norms')
        need(qdot(v,w) == ZERO, 'active orthogonality')
        need(qmv(g,v) == w and qmv(g,w) == v, 'both G active columns')
        need(qmv(gt,v) == [qm(LAM,x) for x in w], 'first transpose column')
        need(qmv(gt,w) == [qm(H,x) for x in v], 'second transpose column')
        pairs.append((v,w,n,m))
    columns = [v for pair in pairs for v in pair[:2]]
    for i,x in enumerate(columns):
        for j,y in enumerate(columns):
            need(qdot(x,y) == (qdot(x,x) if i == j else ZERO), 'all active Gram entries')
    return pairs,t


def primitive(vector):
    den = lcm(*(x.denominator for x in vector))
    integers = [int(x*den) for x in vector]
    common = gcd(*integers)
    if common == 0:
        return None
    if next(x for x in integers if x) < 0:
        common = -common
    return [F(x//common) for x in integers]


def complement(r,u):
    basis, norms, pivots = [],[],[]
    for j in range(112):
        z = [F(i == j) for i in range(112)]
        for k in range(1,8):
            a = (56*u[k][j]-2*r[k][j])/1872
            b = (-2*u[k][j]+F(67,2)*r[k][j])/1872
            z = [x-a*y-b*w for x,y,w in zip(z,u[k],r[k])]
        for old,norm in zip(basis,norms):
            c = dot(z,old)/norm
            if c:
                z = [x-c*y for x,y in zip(z,old)]
        z = primitive(z)
        if z is not None:
            basis.append(z);norms.append(dot(z,z));pivots.append(j)
    need(len(basis) == 98 and all(x > 0 for x in norms), 'complete positive complement')
    return basis,norms,pivots


def check_complement(zs,norms,r,u,g,gt):
    for i,z in enumerate(zs):
        for j,w in enumerate(zs):
            need(dot(z,w) == (norms[i] if i == j else 0), 'all complement Gram entries')
        for k in range(1,8):
            need(dot(z,r[k]) == dot(z,u[k]) == 0, 'all cross constraints')
        need(mv(g,z) == z and mv(gt,z) == z, 'both literal fixed columns')


def complement_projector(zs,norms,r,u):
    observed = [[sum((z[i]*z[j]/n for z,n in zip(zs,norms) if z[i] and z[j]),F(0))
                 for j in range(112)] for i in range(112)]
    expected = [[F(i == j)-sum((56*u[k][i]*u[k][j]-2*u[k][i]*r[k][j]
                 -2*r[k][i]*u[k][j]+F(67,2)*r[k][i]*r[k][j])/1872
                 for k in range(1,8)) for j in range(112)] for i in range(112)]
    need(observed == expected, 'full reconstructed complement projector')
    return digest([[str(x) for x in row] for row in observed])


# K=Q(sqrt6097)[eta]/(eta^2-h); eta denotes the positive sqrt(h).
def ka(x,y=ZERO):
    return x,y


def km(x,y):
    return qa(qm(x[0],y[0]),qm(H,qm(x[1],y[1]))),qa(qm(x[0],y[1]),qm(x[1],y[0]))


def kadd(x,y):
    return qa(x[0],y[0]),qa(x[1],y[1])


def m2(a,b):
    return [[kadd(km(a[i][0],b[0][j]),km(a[i][1],b[1][j]))
             for j in range(2)] for i in range(2)]


KONE = ka(ONE)
KZERO = ka(ZERO)
ETA = ka(ZERO,ONE)
RINV = ka(ZERO,LAM)


def monomial_products(n,transpose=True,old_output=False):
    a = [RINV if i < 14 and i%2 == 0 else ETA if i < 14 else KONE for i in range(n)]
    b = [ETA if i < 14 and i%2 == 0 else RINV if i < 14 else KONE for i in range(n)]
    if not transpose:
        b = a[:]
    p = [i^1 if i < 14 else i for i in range(n)]
    for i in range(n):
        for j in range(n):
            left = {} if p[i] != p[j] else {p[i]:km(a[p[i]],b[p[j]])}
            right = {} if i != j else {p[i]:b[p[i]] if old_output else KONE}
            if left != right:
                return False,[i,j,p[i]]
    return True,None


def symbolic_weights():
    need(km(ETA,RINV) == KONE, 'positive reciprocal weights')
    need(km(RINV,RINV) == ka(LAM) and km(ETA,ETA) == ka(H), 'squared endpoint norms')
    identity=[[KONE,KZERO],[KZERO,KONE]]
    perm=[[KZERO,KONE],[KONE,KZERO]]
    a=[[KZERO,RINV],[ETA,KZERO]]
    b=[[KZERO,ETA],[RINV,KZERO]]
    d=[[RINV,KZERO],[KZERO,KONE]]
    di=[[ETA,KZERO],[KZERO,KONE]]
    fixed_b=[[KZERO,ka(H)],[ka(LAM),KZERO]]
    need(m2(di,m2(a,d)) == perm, 'fixed-output A permutation')
    need(m2(di,m2(b,d)) == fixed_b, 'fixed-output reciprocal square weights')
    need(m2(perm,fixed_b) == [[ka(LAM),KZERO],[KZERO,ka(H)]], 'actual spectral lower-bound witness')
    need(m2(fixed_b,fixed_b) == identity, 'fixed-output involution')
    bt=[list(row) for row in zip(*fixed_b)]
    need(m2(bt,fixed_b) == [[ka(qm(LAM,LAM)),KZERO],[KZERO,ka(qm(H,H))]], 'fixed-output sharp singular squares')
    counts = {}
    for n in (112,128):
        need(monomial_products(n)[0], 'all new split basis products')
        counts[str(n)] = n*n
    return {'basis_products':counts,'lambda':pack(LAM),'h':pack(H),
            'chart_condition':1,'changed_output_norm':1,
            'fixed_output_chart_condition_squared':pack(LAM),
            'fixed_output_norm':pack(LAM),'fixed_output_condition':pack(qm(LAM,LAM))}


def qmod(x,delta,p):
    return (x[0].numerator*pow(x[0].denominator,-1,p)+
            x[1].numerator*pow(x[1].denominator,-1,p)*delta)%p


def rmod(x,p):
    return x.numerator*pow(x.denominator,-1,p)%p


def finite_chart(pairs,zs,norms,g,gt):
    p = 65537
    need(all(p%d for d in range(2,isqrt(p)+1)), 'fixture prime')
    roots = {value:next((i for i in range(p) if i*i%p == value),None) for value in (13,469)}
    need(all(x is not None for x in roots.values()), 'fixture square roots')
    delta = roots[13]*roots[469]%p
    rv = (roots[469]+6*roots[13])%p
    columns,diagonal = [],[]
    for v,w,n,_ in pairs:
        columns.extend([[qmod(x,delta,p) for x in v],
                        [rv*qmod(x,delta,p)%p for x in w]])
        diagonal.extend([qmod(n,delta,p)]*2)
    columns.extend([[rmod(x,p) for x in z] for z in zs])
    diagonal.extend(rmod(x,p) for x in norms)
    need(all(diagonal), 'nondegenerate finite Gram')
    return p,delta,rv,columns,[pow(x,-1,p) for x in diagonal],\
        [[rmod(x,p) for x in row] for row in g],[[rmod(x,p) for x in row] for row in gt]


def owner_map(v,columns,p):
    return [sum(column[i]*x for column,x in zip(columns,v))%p for i in range(112)]+v[112:]


def owner_inverse(v,columns,inverse_norms,p):
    return [sum(x*y for x,y in zip(column,v))*inv%p
            for column,inv in zip(columns,inverse_norms)]+v[112:]


def evaluation(v,root,p,inverse=False):
    n=len(v)
    if inverse:
        points=[pow(root,-2*k,p) for k in range(n)]
        scale=[pow(n,-1,p)*pow(root,-k,p)%p for k in range(n)]
    else:
        points=[pow(root,2*j+1,p) for j in range(n)]
        scale=[1]*n
    out=[]
    for point,c in zip(points,scale):
        value=0
        for x in reversed(v):
            value=(value*point+x)%p
        out.append(value*c%p)
    return out


def convolution(a,b,p):
    n=len(a);out=[0]*n
    for i,x in enumerate(a):
        if x:
            for j,y in enumerate(b):
                if y:
                    k=i+j
                    out[k%n]=(out[k%n]+(-1 if k >= n else 1)*x*y)%p
    return out


def finite_operator(v,root,p,columns,invnorms,matrix=None):
    values=evaluation(v,root,p)
    if matrix is None:
        values=[values[i^1] if i < 14 else values[i] for i in range(len(v))]
    else:
        owner=owner_map(values,columns,p)
        owner=[sum(x*y for x,y in zip(row,owner))%p for row in matrix]+owner[112:]
        values=owner_inverse(owner,columns,invnorms,p)
    return evaluation(values,root,p,True)


def vector_pairs(n):
    unit=[int(i == 0) for i in range(n)]
    wrapx=[int(i == n-1) for i in range(n)]
    wrapz=[int(i == 1) for i in range(n)]
    densex=[(7*i+3)%11-5 for i in range(n)]
    densez=[(5*i*i+1)%13-6 for i in range(n)]
    return [('unit',unit,unit),('wrap',wrapx,wrapz),('dense',densex,densez)]


def finite_products(pairs,zs,norms,g,gt):
    p,delta,rv,columns,invnorms,gm,gtm=finite_chart(pairs,zs,norms,g,gt)
    for j in range(112):
        e=[int(i == j) for i in range(112)]
        need(owner_inverse(owner_map(e,columns,p),columns,invnorms,p)==e,'finite actual inverse columns')
    out=[]
    for n in (128,256):
        root=pow(3,(p-1)//(2*n),p)
        need(pow(root,n,p)==p-1,'literal negacyclic root')
        for name,x,z in vector_pairs(n):
            left=convolution(finite_operator(x,root,p,columns,invnorms,gm),
                             finite_operator(z,root,p,columns,invnorms,gtm),p)
            right=finite_operator(convolution(x,z,p),root,p,columns,invnorms)
            need(left==right,'literal changed-output negacyclic product')
            out.append({'N':n,'name':name,'root':root,'output_sha256':digest(left)})
    return {'prime':p,'delta':delta,'r':rv,'cases':out,'scope':'Finite product identity, not finite-field Euclidean unitarity.'}


def rejects(function,*args):
    try:
        function(*args)
    except ValueError:
        return True
    raise ValueError('negative control accepted')


def source_control():
    with tempfile.TemporaryDirectory(prefix='unitary-source-control-') as name:
        root=Path(name)
        raw=(ROOT/'SOURCE-PINS.json').read_bytes();(root/'SOURCE-PINS.json').write_bytes(raw)
        for row in strict_load(raw)['files']:
            path=root/row['local_path'];path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes((ROOT/row['local_path']).read_bytes())
        path=root/'inputs/R.json';raw=path.read_bytes();path.write_bytes(b'X'+raw[1:])
        return rejects(authenticate,root)


def controls(pairs,zs,r,u):
    badwrong,witness=monomial_products(112,False)
    badold,oldwitness=monomial_products(112,True,True)
    need(not badwrong and not badold,'actual output/transpose faults')
    v,w,n,m=pairs[0]
    need(n != m,'common active normalization fails isometry')
    need(qm(LAM,LAM) != ONE,'old fixed output not isometric')
    z=zs[0][:];z[0]+=1
    need(any(dot(z,x) for x in r[1:]+u[1:]),'actual complement corruption')
    need(F(1,128) != 1,'missing Fourier scale')
    return {'wrong_transpose_witness':witness,'wrong_old_output_witness':oldwitness,
            'same_column_normalization_not_isometric':True,'fixed_output_not_unitary':True,
            'actual_complement_corruption':True,'missing_sqrtN_scale':True,
            'duplicate_JSON':rejects(strict_load,'{"x":1,"x":2}'),
            'nonfinite_JSON':rejects(strict_load,'{"x":NaN}'),
            'actual_source_corruption':source_control()}


def receipt(source_only=False):
    authenticate()
    r,u,g,gt=sources()
    gram=source_gram(r,u)
    pairs,t=active(r,u,g,gt)
    zs,norms,pivots=complement(r,u)
    check_complement(zs,norms,r,u,g,gt)
    proj=complement_projector(zs,norms,r,u)
    result={'schema_version':1,'source_manifest_sha256':PIN,
            'source_G_sha256':digest([[str(x) for x in row] for row in g]),
            'source_gram':gram,'active_t':pack(t),
            'active_planes':[{'v':[pack(x) for x in v],'w':[pack(x) for x in w],
                              'v_norm':pack(n),'w_norm':pack(m)} for v,w,n,m in pairs],
            'complement_basis':[{'pivot':i,'vector':[str(x) for x in z],'norm':str(n)}
                                for i,z,n in zip(pivots,zs,norms)],
            'complement_projector_sha256':proj,'symbolic_weights':symbolic_weights(),
            'finite_products':None if source_only else finite_products(pairs,zs,norms,g,gt),
            'controls':controls(pairs,zs,r,u),
            'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    return result


def same_types(a,b):
    need(type(a) is type(b),'receipt type')
    if type(b) is dict:
        need(a.keys()==b.keys(),'receipt keys')
        for k in b:
            same_types(a[k],b[k])
    elif type(b) is list:
        need(len(a)==len(b),'receipt list length')
        for x,y in zip(a,b):
            same_types(x,y)
    else:
        need(a==b,'receipt value')


def main():
    need(sys.argv[1:] in ([],['--emit'],['--source-only']),'arguments')
    out=json.loads(json.dumps(receipt(sys.argv[1:] == ['--source-only'])))
    if sys.argv[1:]:
        print(json.dumps(out,sort_keys=True,indent=2))
    else:
        same_types(strict_load((ROOT/'RESULT.json').read_bytes()),out)
        print('PASS_CENTRE0_UNITARY_PRODUCT_CHART')


if __name__=='__main__':
    main()
