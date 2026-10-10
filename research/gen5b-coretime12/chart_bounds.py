"""Original exact constructions and factor programs for all 18 changed charts.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction as F
from math import gcd,lcm
import hashlib,json
import source_data as sd
import check_coretime
import exact_geometry as geo
def rref(A):
    A=[[F(x)for x in row]for row in A];piv=[]
    for j in range(len(A[0])if A else 0):
        q=next((i for i in range(len(piv),len(A))if A[i][j]),None)
        if q is None:continue
        i=len(piv);A[i],A[q]=A[q],A[i];v=A[i][j];A[i]=[x/v for x in A[i]]
        for k in range(len(A)):
            if k!=i and A[k][j]:
                v=A[k][j];A[k]=[a-v*b for a,b in zip(A[k],A[i])]
        piv.append(j)
        if len(piv)==len(A):break
    return A,piv


def primitive(v):
    d=lcm(*(F(x).denominator for x in v));v=[int(F(x)*d)for x in v];g=gcd(*v)
    assert g;return [x//g for x in v]


def nullspace(A,n=24):
    R,piv=rref(A);out=[]
    for free in range(n):
        if free in piv:continue
        v=[F(0)]*n;v[free]=1
        for i,j in enumerate(piv):v[j]=-R[i][free]
        out.append(primitive(v))
    return out


def factor(B):
    n=len(B);A=[[F(x)for x in row]for row in B];ops=[];det=F(1)
    for j in range(n):
        pivot=next(i for i in range(j,n)if A[i][j])
        if pivot!=j:A[pivot],A[j]=A[j],A[pivot];ops.append(('swap',j,pivot,F(1)));det=-det
        v=A[j][j];det*=v
        if v!=1:A[j]=[x/v for x in A[j]];ops.append(('scale',j,j,1/v))
        for i in range(n):
            if i!=j and A[i][j]:
                q=-A[i][j];A[i]=[x+q*y for x,y in zip(A[i],A[j])];ops.append(('add',i,j,q))
    assert A==[[int(i==j)for j in range(n)]for i in range(n)]
    # Independently replay inverse operations from I and recover B.
    C=[[F(i==j)for j in range(n)]for i in range(n)]
    for kind,i,j,q in reversed(ops):
        if kind=='swap':C[i],C[j]=C[j],C[i]
        elif kind=='scale':C[i]=[x/q for x in C[i]]
        else:C[i]=[x-q*y for x,y in zip(C[i],C[j])]
    assert C==B
    return dict(determinant=det,factors=ops,count=len(ops),
      max_numerator=max((abs(q.numerator)for kind,i,j,q in ops),default=1),
      max_denominator=max((q.denominator for kind,i,j,q in ops),default=1))


def serial(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):serial(v)for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [serial(v)for v in x]
    return x


def endpoint_columns(candidate,w,frames):
    gauges={z['role']:z for z in w['gauges']}
    sigma=frames[str(gauges[candidate['helper']]['frame'])]['a']
    endpoint=frames[str(candidate['new_endpoint'])]['a']
    common=frames[str(candidate['common_frame'])]['a']
    assert gauges[candidate['helper']]['dim']==21
    assert len(rref(sigma)[1])==3 and len(rref(sigma+endpoint)[1])==3
    assert len(rref(common)[1])==2 and len(rref(common+endpoint)[1])==2
    P=geo.projector(sigma);E=geo.projector(endpoint);I=geo.eye(24)
    assert geo.mul(P,E)==P and geo.mul(E,P)==P
    residual=geo.add(E,P,-1);completion=geo.add(I,residual,-1)
    assert geo.mul(residual,residual)==residual and sum(residual[i][i]for i in range(24))==2
    assert geo.mul(completion,completion)==completion and sum(completion[i][i]for i in range(24))==22
    residual_columns,_=geo.integer_columns(residual,2)
    entrance_columns,_=geo.integer_columns(P,21)
    exterior_columns,_=geo.integer_columns(geo.add(I,E,-1),1)
    columns=residual_columns+entrance_columns+exterior_columns
    assert len(rref(list(zip(*columns)))[1])==24
    gram=lambda a,b:9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)
    assert all(gram(a,b)==0 for a in columns[:2]for b in columns[2:])
    assert all(gram(a,columns[-1])==0 for a in columns[:23])
    return columns


def run():
    candidate=check_coretime.run(minimal=True)
    w=sd.read_json('gen5bit/selected/bit/word_p12.json.gz')
    frames=sd.read_json('gen5bit/selected/bit/frames_p12.json.gz')['frames']
    pins=sd.read_json('expected/kernel-pins.json')
    undone={c['old_restored_helper']for c in candidate['candidates']}
    assert len(candidate['candidates'])==12 and len(undone)==6
    gauges={z['role']:z for z in w['gauges']};matrices=[]
    for c in candidate['candidates']:
        matrices.append(('new_rank2',c['helper'],endpoint_columns(c,w,frames)))
    for role in sorted(undone):
        ann=frames[str(gauges[role]['frame'])]['a'];assert len(ann)==4
        residual=[primitive([15*x-sum(a)for x in a])for a in ann]
        entrance=nullspace(ann);assert len(entrance)==20
        assert all(9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)==0 for a in residual for b in entrance)
        matrices.append(('reverted_rank4',role,residual+entrance))
    out=[]
    for kind,role,cols in matrices:
        assert len(cols)==24 and all(len(c)==24 for c in cols)
        B=[list(row)for row in zip(*cols)];f=factor(B)
        assert f['max_numerator']<2**80 and f['max_denominator']<2**80
        out.append(dict(kind=kind,role=role,basis_columns=cols,**f))
    assert len(out)==18
    largest=max(z['count']for z in out)
    retained=pins['max_chart_factors'];assert retained==576
    bound=max(retained,largest)+119+120
    assert bound==pins['normalizer_factor_bound']==815
    stock=pins['literal_stock']-15;roles=pins['physical_R']
    selectors=600*((stock-1)+roles*120*bound)
    assert selectors<2**40
    return dict(status='PASS_CHANGED_CHART_FACTORIZATION_BOUNDS',charts=len(out),
        max_changed_chart_factors=largest,retained_chart_factor_bound=retained,
        combined_normalizer_factor_bound=bound,selector_calls_bound=selectors,
        selector_bound_less_than_2_power_40=True,
        max_factor_numerator=max(z['max_numerator']for z in out),
        max_factor_denominator=max(z['max_denominator']for z in out),
        source_head=sd.HEAD,factor_programs=out,
        scope='All changed chart constructions, exact inverse factor replay and selector bounds; retained finite-compiler and unchanged-stage hypotheses remain conditional.')
