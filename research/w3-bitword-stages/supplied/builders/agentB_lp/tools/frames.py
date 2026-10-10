# exact frame utilities (sympy rational matrices)
import json, sys
import sympy as sp
sys.path.insert(0,'/home/claude/work/agentB/tools')
from base import *
_FR=None
def FR(d='/home/claude/work/agentA/W/out5b'):
    global _FR
    if _FR is None: _FR=json.load(open(d+'/frames.json'))['frames']
    return _FR
def Bmat(fid): return sp.Matrix(FR()[str(fid)]['B']) if FR()[str(fid)]['B'] else sp.zeros(0,24)
def rank(M): return M.rank() if M.rows else 0
def span_dim(rows): 
    if not rows: return 0
    return sp.Matrix(rows).rank()
def contains(bigrows, smallrows):
    return span_dim(list(bigrows)+list(smallrows))==span_dim(list(bigrows))
def chi(i):
    w=[0]*24
    for p in lab[i]: w[p]=1
    return w
def chit(t): return chi(t)
def ann_vec_of_target(t):
    c=chi(t); return [3*x-1 for x in c]
Gm=sp.eye(24)-sp.ones(24,24)/9
def nondeg(rows):
    if not rows: return True
    B=sp.Matrix(rows)
    Gr=B*Gm*B.T
    return Gr.det()!=0
def kernel_rows(annrows):
    """subspace {w: a.w=0 for a in annrows}"""
    if not annrows: return [list(r) for r in sp.eye(24).tolist()]
    M=sp.Matrix(annrows)
    ns=M.nullspace()
    out=[]
    for v_ in ns:
        den=sp.ilcm(*[x.q for x in v_]) if len(v_) else 1
        out.append([int(x*den) for x in v_])
    return out
def intersect(r1,r2):
    # intersection of row spaces
    if not r1 or not r2: return []
    A=sp.Matrix(r1).T; B=sp.Matrix(r2).T
    M=A.row_join(-B)
    ns=M.nullspace()
    out=[]
    for v_ in ns:
        w=A*v_[:A.cols,:]
        den=sp.ilcm(*[x.q for x in w])
        out.append([int(x*den) for x in w])
    if not out: return []
    Mm=sp.Matrix(out); 
    R=Mm.rref()[0]
    rows=[]
    for i in range(R.rows):
        rr=list(R.row(i))
        if any(rr):
            den=sp.ilcm(*[x.q for x in rr]); rows.append([int(x*den) for x in rr])
    return rows
