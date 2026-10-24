"""Independent exhaustive small-space rank/lattice corroboration; Apache-2.0.
Source Clifford implementation is an explicit caller-supplied frozen input.
Dugongue with substantial OpenAI Codex assistance.
"""
from pathlib import Path
import argparse,importlib.util,sys,json,hashlib

def subspaces(n):
    out=[]
    for mask in range(1<<(1<<n)):
        if not mask&1:continue
        s={i for i in range(1<<n) if mask>>i&1}
        if all(a^b in s for a in s for b in s):out.append(s)
    return out

def basis(s):
    piv={};out=[]
    for v in sorted(s):
        w=v
        while w:
            b=w.bit_length()-1
            if b not in piv:piv[b]=w;out.append(v);break
            w^=piv[b]
    return tuple(out)

def span(vs):
    s={0}
    for v in vs:s|={x^v for x in tuple(s)}
    return s

def check(source):
    p=Path(source);spec=importlib.util.spec_from_file_location('frame_review_clifford',p)
    ce=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ce;spec.loader.exec_module(ce)
    spaces=pairs=images=0
    for n in range(1,4):
        ss=subspaces(n);spaces+=len(ss);fs=[]
        for s in ss:
            op=ce.canonical_frame(n,basis(s));fs.append(op)
            # Compute image L0 from literal Z-tableau columns, without formula.
            actual=span([x|(z<<n) for x,z,phase in op.tab[n:]])
            expected={x|(z<<n) for x in range(1<<n) for z in range(1<<n)
                      if x in s and all(((x^z)&u).bit_count()%2==0 for u in s)}
            if actual!=expected:raise ValueError('Lagrangian image formula')
            # Literal symplectic action really is involutive, phases ignored.
            square=op.then(op)
            if [(x,z) for x,z,p in square.tab]!=[(x,z) for x,z,p in ce.identity(n)]:raise ValueError('not symplectic involution')
            images+=len(actual)
        for i,a in enumerate(ss):
            for j,b in enumerate(ss):
                op=fs[i].adjoint().then(fs[j]);rank=ce.rank([x for x,z,p in op.tab[n:]])
                proposed=len(basis(a))+len(basis(b))-2*len(basis(a&b))
                if rank!=proposed:raise ValueError('rank formula')
                rec,compiled=ce.lower_child(op)
                if rec['rank']!=proposed or compiled.tab!=op.tab or compiled.zero_state()!=op.zero_state():raise ValueError('exact phase normal form')
                pairs+=1
    return dict(status='PASS_EXHAUSTIVE_SMALL_FRAME_BRIDGES',dimensions=[1,2,3],subspaces=spaces,pairs=pairs,lagrangian_vectors=images,
                clifford_source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),scope='All small subspaces and relative ranks/absolute-phase lowerings; corroborates independent universal proof, not all-dimension exhaustiveness.')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);args=ap.parse_args()
    print(json.dumps(check(args.source),indent=2))
