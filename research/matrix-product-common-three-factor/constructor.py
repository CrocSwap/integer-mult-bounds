"""Common ABA constructor, retaining Nick Petalas PR4805 linear algebra.
JoyboyBrian, substantial OpenAI Codex assistance; Apache-2.0.
"""
import importlib.util
from pathlib import Path

def load_source(root):
    path=Path(root)/'research/matrix-algebra-three-factor/verify.py'
    spec=importlib.util.spec_from_file_location('retained_matrix_constructor',path)
    module=importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module

def construct(source,target,q):
    """Return three factors with right vectors e1,e2,e1; no free endpoints.

    Finite executable domain is prime fields 2,3,5,7 and 1<=m<=4.
    The written proof is independent of these corroboration limits.
    """
    s=source;m=len(target)//2
    s.check(q in (2,3,5,7) and 1<=m<=4 and len(target)==2*m,'constructor domain')
    s.check(all(len(row)==2*m and all(type(x) is int and 0<=x<q for x in row) for row in target),'field matrix')
    top=target[:m]
    rows=s.basis(top,q)
    for e in s.identity(2*m):
        if len(rows)==m:break
        if not s.inside(e,rows,q):rows=s.basis([*rows,e],q)
    t=tuple(rows)
    a=tuple(s.solve(s.transpose(t),row,q) for row in top)
    s.check(len(t)==m and all(row is not None for row in a),'row completion')
    n=(*t,*target[m:])
    # PR4805's graph construction, now at a fixed chart. Full top rank
    # gives dim ker(pi|im N)=rank N-m <= rank of the second block column.
    w=s.basis(s.columns(n),q);v=s.basis(s.columns(n)[m:],q)
    wm=s.transpose(w)
    k=[tuple(z[0] for z in s.matmul(wm,s.transpose([c]),q)) for c in s.kernel(wm[:m],q)]
    u=s.common_complement(w,v,k,q)
    system=s.transpose([*s.columns(n)[m:],*u])
    solutions=[s.solve(system,c,q) for c in s.columns(n)[:m]]
    s.check(all(z is not None for z in solutions),'graph lift')
    f=s.transpose([z[:m] for z in solutions])
    first=s.transpose(s.columns(n)[:m]);second=s.transpose(s.columns(n)[m:])
    graph=tuple(s.add(x,s.scale(-1,y,q),q) for x,y in zip(first,s.matmul(second,f,q),strict=True))
    e,lower=graph[:m],graph[m:]
    b=tuple(s.solve(s.transpose(e),row,q) for row in lower)
    s.check(all(row is not None for row in b),'graph projection')
    upper_right,bottom_right=second[:m],second[m:]
    d=tuple(s.add(x,s.scale(-1,y,q),q) for x,y in zip(bottom_right,s.matmul(b,upper_right,q),strict=True))
    one=s.identity(m);zero=tuple((0,)*m for _ in range(m))
    # Absorb diag(a,I) into the first e1 update. No component-dependent
    # free chart, internal-coordinate map, or target conjugation is used.
    p=(*s.join(a,zero),*s.join(b,one))
    r=(*s.join(one,upper_right),*s.join(zero,d))
    z=(*s.join(e,zero),*s.join(f,one))
    return (p,r,z)
