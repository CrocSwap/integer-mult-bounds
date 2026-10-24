"""Exact small-space phase-form checks; Apache-2.0.
Dugongue with substantial OpenAI Codex assistance.
The Clifford implementation is a caller-specified frozen source input.
"""
from pathlib import Path
import importlib.util,sys,argparse,json,hashlib

def rank(vs):
    piv={}
    for v in vs:
        while v:
            i=v.bit_length()-1
            if i not in piv:piv[i]=v;break
            v^=piv[i]
    return len(piv)

def basis(s):
    out=[]
    for x in sorted(s):
        if rank(out+[x])>len(out):out.append(x)
    return out

def span(vs):
    s={0}
    for v in vs:s|={x^v for x in tuple(s)}
    return s

def spaces(n):
    return [s for mask in range(1<<(1<<n)) if mask&1
            for s in [{i for i in range(1<<n) if mask>>i&1}]
            if all(x^y in s for x in s for y in s)]

def check(path):
    p=Path(path);sp=importlib.util.spec_from_file_location('phase_form_ce',p)
    ce=importlib.util.module_from_spec(sp);sys.modules[sp.name]=ce;sp.loader.exec_module(ce)
    def mul(A,B,n):
        cols=ce.transpose(B,n)
        return tuple(sum(((row&col).bit_count()%2)<<j for j,col in enumerate(cols)) for row in A)
    total=pairs=0
    # Reversing the actual gauge order erases the new inverse-image form.
    wrong=ce.canonical_frame(1,[1]).then(ce.diag(1,(1,)))
    wrong_image=span([x|(z<<1) for x,z,phase in wrong.adjoint().tab[1:]])
    if wrong_image=={0,1}:raise ValueError('wrong-orientation control was not distinguished')
    lowered=0
    for n in range(1,4):
        charts=[];lagrangians=set()
        for U in spaces(n):
            B=basis(U);d=len(B);H=ce.transpose(ce.basis_extend(B,n),n);Hi=ce.inv(H,n)
            ps=[(i,j) for i in range(d) for j in range(i,d)]
            for mask in range(1<<len(ps)):
                S=[0]*n
                for k,(i,j) in enumerate(ps):
                    if mask>>k&1:S[i]^=1<<j;S[j]^=(1<<i) if i!=j else 0
                Q=mul(ce.transpose(Hi,n),mul(S,Hi,n),n)
                F=ce.diag(n,Q).then(ce.canonical_frame(n,B))
                actual=span([x|(z<<n) for x,z,phase in F.adjoint().tab[n:]])
                expected={x|(z<<n) for x in U for z in range(1<<n)
                          if all(((x^z)&u).bit_count()%2==((ce.mv(Q,x)&u).bit_count()%2) for u in U)}
                if actual!=expected:raise ValueError('inverse-chart construction')
                lagrangians.add(tuple(sorted(actual)));charts.append((U,Q,F))
        if len(charts)!=len(lagrangians) or len(charts)!={1:3,2:15,3:135}[n]:raise ValueError('all Lagrangians')
        for U,Q,F in charts:
            for V,R,G in charts:
                I=basis(U&V);D=[sum((((ce.mv(Q,x)^ce.mv(R,x))&y).bit_count()%2)<<j for j,y in enumerate(I)) for x in I]
                wanted=len(basis(U))+len(basis(V))-2*len(I)+rank(D)
                actual=rank([x for x,z,phase in F.adjoint().then(G).tab[n:]])
                if wanted!=actual:raise ValueError('phase rank formula')
                if pairs%97==0:
                    op=F.adjoint().then(G);rec,compiled=ce.lower_child(op)
                    if rec['rank']!=wanted or compiled.tab!=op.tab or compiled.zero_state()!=op.zero_state():raise ValueError('absolute phase lowering')
                    lowered+=1
                pairs+=1
        total+=len(charts)
    return dict(status='PASS_EXHAUSTIVE_PHASE_FORM_CONSTRUCTION_AND_RANK',dimensions=[1,2,3],lagrangians=total,ordered_pairs=pairs,exact_phase_lowerings=lowered,wrong_orientation_control='REJECTED',
                source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),scope='All small Lagrangian charts and pair ranks; finite corroboration, not proof of a useful actual-word phase-flow solution.')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);args=ap.parse_args()
    print(json.dumps(check(args.source),indent=2))
