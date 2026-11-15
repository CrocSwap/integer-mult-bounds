"""NETCOMPILE circ.py (own code): a frame-window of w7546 as a circuit.
Window = all stays at frames in S (default: nonzero subspaces of a seed frame G).  Wires = public registers with a stay in S.
Each wire's window segment is contiguous in time (public registers only ascend; checked).  Base gates = the ops at frames
in S, in program order.  T = product of the base gates on wire coordinates (exit contents in the basis of entry contents),
computed mod p.  Co-presence schedule = per frame, the time intervals during which each wire sits there."""
import sys, collections, random
sys.path.insert(0,'inputs/DCUT'); from core import *
from fractions import Fraction as Q
P=2**31-1
import os
WPATH=os.environ.get('SUP_BASE','inputs/ATTACK/RECHART/hit_rechart_1.json.gz')
def qm(s):
    q=Q(s); return q.numerator%P*pow(q.denominator%P,P-2,P)%P
f=xlogx
class Base:
    def __init__(s,W=None):
        s.W=W or pk.load(WPATH); W=s.W; s.m=Model(W); m=s.m; s.n=m.n
        s.prog=W['program']
        # stays per register: list of [frame, t_arr, t_dep] (program indices; t_arr=-1 initial; t_dep=len final)
        s.stays=collections.defaultdict(list); cur={}
        for r in range(s.n): s.stays[r].append([W['initial'][r],-1,None])
        for i,e in enumerate(s.prog):
            if e[0]=='MOVE':
                r=e[1]; s.stays[r][-1][2]=i; s.stays[r].append([e[3],i,None])
            elif e[0]=='INIT': s.stays[e[1]].append([e[2],i,None])
            elif e[0]=='CLEAR': s.stays[e[1]][-1][2]=i
        for r,L in s.stays.items():
            if L[-1][2] is None: L[-1][2]=len(s.prog)
        s.dim=m.dim
    def sub(s,a,b): return (s.m.mask[a]&~s.m.mask[b])==0
    def downset(s,G,Z=3):
        return {F for F in range(len(s.m.frames)) if F!=Z and s.sub(F,G)}
class Window:
    def __init__(s,B,S):
        s.B=B; s.S=set(S); n=B.n; prog=B.prog
        wires=[]
        for r in range(B.n):
            L=B.stays[r]; idx=[i for i,st in enumerate(L) if st[0] in s.S]
            if not idx: continue
            assert idx==list(range(idx[0],idx[-1]+1)), ('non-contiguous',r)
            wires.append(r)
        own=[r for r in range(n,B.m.N) if any(st[0] in s.S for st in B.stays.get(r,[]))]
        s.owned=own
        s.wires=wires; s.wi={r:i for i,r in enumerate(wires)}; s.nw=len(wires)
        s.seg={}   # wire -> (prev_frame or None, [stays in S], next_frame or None)
        for r in wires:
            L=B.stays[r]; idx=[i for i,st in enumerate(L) if st[0] in s.S]
            prev=L[idx[0]-1][0] if idx[0]>0 else None
            nxt=L[idx[-1]+1][0] if idx[-1]+1<len(L) else None
            s.seg[r]=(prev,[list(L[i]) for i in idx],nxt)
        s.gates=[]  # (t, op, a, b, coef) at frames in S
        cur=list(B.W['initial'])+[None]*B.W['owned_fields']
        for i,e in enumerate(prog):
            op=e[0]
            if op=='MOVE': cur[e[1]]=e[3]; continue
            if op in('INIT','CLEAR'):
                cur[e[1]]=e[2] if op=='INIT' else None; continue
            fr=e[3] if op=='SCALE' else e[4]
            if fr in s.S:
                if op=='SCALE': s.gates.append((i,'S',e[1],None,e[2],fr))
                else: s.gates.append((i,op,e[1],e[2],e[3],fr))
        s.T=None if s.owned else s.product(s.gates)
    def product(s,gates):
        nw=s.nw; wi=s.wi
        C=[{i:1} for i in range(nw)]
        for g in gates:
            t,op,a,b,c,fr=g
            if op=='S':
                q=qm(c); C[wi[a]]={k:v*q%P for k,v in C[wi[a]].items()}
            else:
                q=qm(c); A=wi[a]; Bv=C[wi[b]]
                if op=='COPY': C[A]={}
                R=C[A]
                for k,v in Bv.items():
                    nv=(R.get(k,0)+q*v)%P
                    if nv: R[k]=nv
                    else: R.pop(k,None)
        return C
    def loss(s, segs=None):
        """window-attributable loss: sum over wires of loss(route) - loss(route without window interior stops)"""
        segs=segs or s.seg; B=s.B; tot=0.0
        for r in s.wires:
            prev,st,nxt=segs[r]
            ch=([prev] if prev is not None else [])+[x[0] for x in st]+([nxt] if nxt is not None else [])
            full=s._route(r,segs)
            tot+=full
        return tot
    def _route(s,r,segs):
        """loss of the whole route of r with its window part replaced by segs[r]"""
        B=s.B; L=B.stays[r]; prev,st,nxt=segs[r]
        idx=[i for i,x in enumerate(L) if x[0] in s.S]
        fr=[x[0] for x in L[:idx[0]]]+[x[0] for x in st]+[x[0] for x in L[idx[-1]+1:]]
        steps=sum(f(B.dim[b]-B.dim[a]) for a,b in zip(fr,fr[1:]))
        return f(B.dim[fr[-1]]-B.dim[fr[0]])-steps
    def schedule(s,segs=None):
        """per frame: list of (t_arr,t_dep,wire)"""
        segs=segs or s.seg; sch=collections.defaultdict(list)
        for r in s.wires:
            for F,a,d in segs[r][1]: sch[F].append((a,d,r))
        return sch
def rank_mod(rows,cols,C):
    """rank of submatrix C[rows][cols] (C list of dict rows) mod P via flint"""
    from flint import nmod_mat
    cl={c:j for j,c in enumerate(cols)}
    if not rows or not cols: return 0
    M=nmod_mat(len(rows),len(cols),P)
    for i,r in enumerate(rows):
        for k,v in C[r].items():
            j=cl.get(k)
            if j is not None: M[i,j]=v
    return M.rank()
if __name__=='__main__':
    B=Base(); G=int(sys.argv[1]) if len(sys.argv)>1 else 244
    Wd=Window(B,B.downset(G))
    print('G',G,'wires',Wd.nw,'owned in window',len(Wd.owned),'gates',len(Wd.gates),'window loss route-sum %.3f'%Wd.loss())
    print('T nnz',sum(len(r) for r in Wd.T),'rank',rank_mod(list(range(Wd.nw)),list(range(Wd.nw)),Wd.T))
