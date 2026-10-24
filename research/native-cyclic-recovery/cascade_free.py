"""Exact finite-pass inverse for quarter-phase monomial cyclic couplers.
Apache-2.0. Standalone research leaf; this does not emit paid observations.
"""
from fractions import Fraction as Q
from pathlib import Path
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def scale(a, c):
    return (c * a[0], c * a[1])


def phase(a, e):
    for unused in range(e % 4):
        a = (-a[1], a[0])
    return a


def shift(v, w, n, labels, phases):
    # Literal U: (Uv)[k,x] = i^phases[k,x] v[k+1, x xor labels[k]].
    return [phase(v[((k+1)%w)*n+(x^labels[k])], phases[k][x])
            for k in range(w) for x in range(n)]


def decode(v, w, n, labels, phases, period):
    # Horner: I - U/2 + U^2/4 - ... + (-U/2)^(period-1).
    need(period % 2 == 0, 'even period required')
    z = [(Q(0), Q(0)) for unused in v]
    for unused in range(period):
        z = [add(a, scale(b, Q(-1, 2)))
             for a, b in zip(v, shift(z,w,n,labels,phases))]
    denominator = 1 - Q(1, 2)**period
    return [scale(a, 1/denominator) for a in z]


def compile_return(w,n,labels,phases):
    # Compile U^W as a single monomial map; never apply W live data passes.
    out=[]
    for k in range(w):
        for x in range(n):
            role=k;address=x;e=0
            for unused in range(w):
                e=(e+phases[role][address])%4
                address ^= labels[role];role=(role+1)%w
            out.append((role*n+address,e))
    return out


def apply_map(v,compiled):
    return [phase(v[j],e)for j,e in compiled]


def decode_factored(v,w,n,labels,phases,q):
    compiled=compile_return(w,n,labels,phases)
    z=list(v)
    for unused in range(w-1):
        z=[add(a,scale(b,Q(-1,2)))for a,b in zip(v,shift(z,w,n,labels,phases))]
    # S_W(U) above. V=U^W; beta=(-1/2)^W; invert I-beta V.
    beta=Q(-1,2)**w
    out=list(z)
    for unused in range(q-1):
        out=[add(a,scale(b,beta))for a,b in zip(z,apply_map(out,compiled))]
    return [scale(a,1/(1-beta**q))for a in out]


def verify_case(w,n,labels,phases,period):
    dim=w*n
    for j in range(dim):
        v=[(Q(0),Q(0)) for unused in range(dim)];v[j]=(Q(1),Q(0))
        u=v
        for unused in range(period):u=shift(u,w,n,labels,phases)
        need(u==v,'literal monomial period')
        observed=[add(a,scale(b,Q(1,2)))for a,b in zip(v,shift(v,w,n,labels,phases))]
        got=decode(observed,w,n,labels,phases,period)
        need(got==v,'inverse on actual basis column')
        q=period//w
        need(decode_factored(observed,w,n,labels,phases,q)==v,'factored inverse on actual basis column')
    return {'roles':w,'addresses':n,'dimension':dim,'period':period,
            'exact_basis_columns':dim,'monomial_passes_upper_bound':period,
            'ADD_passes_upper_bound':period,'coefficient_l1':str(Q(2)),
            'factored_monomial_passes':w+period//w-2,
            'factored_ADD_passes':w+period//w-2}


def bind_sources():
    import hashlib, ast
    root=Path(__file__).resolve().parent
    rows=json.loads((root/'CASCADE-ORIGINS.json').read_text())
    bound=[]
    for row in rows:
        source=root/row['path'];raw=source.read_bytes()
        need(hashlib.sha256(raw).hexdigest()==row['sha256'],'retained cascade source hash')
        d={'__name__':'retained_cascade'}
        exec(compile(raw,str(source),'exec'),d)
        number=row['pr']
        if number in [4818,4819]:
            ops=d['build_operators_m4']();k=ops['K'];n=16
            gs=ops['couplers']if number==4819 else[ops['G1'],ops['G2'],ops['G3']]
        else:
            # Evaluate the frozen constructor only through E3; do not run dense solvers.
            tree=ast.parse(raw);function=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='run_3in9_schedule_verification')
            body=[]
            for statement in function.body:
                body.append(statement)
                if isinstance(statement,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='E3'for t in statement.targets):break
            body.append(ast.Return(ast.Call(func=ast.Name(id='locals',ctx=ast.Load()),args=[],keywords=[])))
            f=ast.FunctionDef(name='literal_prefix',args=function.args,body=body,decorator_list=[])
            module=ast.fix_missing_locations(ast.Module(body=[f],type_ignores=[]))
            exec(compile(module,'frozen_constructor_prefix','exec'),d);ops=d['literal_prefix']();k=ops['K'];n=32
            gs=[ops['G1'],ops['G2'],ops['G3']]
        labels=list(range(1,14))if number==4819 else[1,2,4]
        for g,label in zip(gs,labels):
            for r in range(n):
                for c in range(n):
                    need(tuple(g[r][c])==((Q(1,2),Q(0))if r==(c^label)else(Q(0),Q(0))),'literal source coupler entry')
            need(d['mm'](k,g)==d['mm'](g,k),'source target/coupler conjugation')
        bound.append({'pr':number,'head':row['head'],'exact_coupler_entries':len(gs)*n*n})
    return bound


def main():
    receipts=[]
    for w,n,labels in [(3,16,[1,2,4]),(3,32,[1,2,4]),(13,16,list(range(1,14)))]:
        phases=[[0]*n for unused in range(w)]
        receipts.append(verify_case(w,n,labels,phases,2*w))
    # Noncommuting quarter-phase Pauli couplers: retain the exact phase.
    w=3;n=8;labels=[1,2,4];masks=[2,3,5];es=[1,2,3]
    phases=[[(es[k]+2*(x&masks[k]).bit_count())%4 for x in range(n)] for k in range(w)]
    receipts.append(verify_case(w,n,labels,phases,4*w))
    # Genuine phase mutation control: same inverse polynomial with one wrong U.
    v=[(Q(j%3-1),Q(j%5-2))for j in range(w*n)]
    observed=[add(a,scale(b,Q(1,2)))for a,b in zip(v,shift(v,w,n,labels,phases))]
    bad=[[0]*n for unused in range(w)]
    need(decode(observed,w,n,labels,bad,4*w)!=v,'phase-discard mutation')
    result={'status':'PASS_FINITE_MONOMIAL_CASCADE_INVERSE','new_kappa':False,
            'paid_observation_word_emitted':False,'cases':receipts,'source_binding':bind_sources(),
            'controls':['discarded phase changes decoder and is rejected']}
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
