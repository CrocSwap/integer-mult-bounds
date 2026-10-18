# ZPIN2 pinz2.py: ZPIN's zero-aware model (pinz.py, unchanged) + rule ZA2 (THEORY.md §4):
# in the residue Sigma_a=Sigma_b=empty, supp y (supp x) is not contained in any A2 triangle S (else S ⊆ Sigma_b (Sigma_a) by rigidity on E8\S).
import sys, itertools, argparse
from pinz import *
def triangles():
    out=set()
    for i in range(N):
        for j in range(i+1,N):
            if G[i][j]==0: continue
            s=1 if G[i][j]>0 else -1; v=[a-s*b for a,b in zip(E[i],E[j])]
            k=[k for k in range(N) if all(a==b for a,b in zip(v,E[k])) or all(a==-b for a,b in zip(v,E[k]))][0]
            out.add(tuple(sorted((i,j,k))))
    return sorted(out)
def add_za2(m):
    TR=triangles(); assert len(TR)==1120
    for S in TR:
        for kind in 'rc': m.add('ZA2',[m.XS((kind,u)) for u in m.off if u not in S])
def add_zcl(m):
    # ZCL (CONDITIONAL on rigidity with extra zeros on E8 \ C for every maximal 7- and 8-clique C; OPEN): D' and D are not cliques,
    # i.e. each contains an orthogonal pair.
    for kind in 'rc':
        lits=[]
        for u in m.off:
            for t in m.off:
                if u<t and G[u][t]==0:
                    d=m.v(('and2',('x',kind,u),('x',kind,t)))
                    m.add('def',[-d,m.XS((kind,u))]); m.add('def',[-d,m.XS((kind,t))]); m.add('def',[d,-m.XS((kind,u)),-m.XS((kind,t))])
                    lits.append(d)
        m.add('ZCL',lits)
def add_nopure(m):
    # scope restriction NOPURE: no off-frame row/column vanishes on its F-tetrad (implied by: every line has <= 3 extra zeros in its row and in its column)
    for kind in 'rc':
        for u in m.off: m.add('NOPURE',[m.NZ((kind,u),i) for i in m.Tof[u]])
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--scope',default='z'); ap.add_argument('--res',type=int,default=1)
    ap.add_argument('--ng',default='rc'); ap.add_argument('--zrig',type=int,default=1); ap.add_argument('--za2',type=int,default=1); ap.add_argument('--frame',type=int,default=0); ap.add_argument('--zcl',type=int,default=0); ap.add_argument('--nopure',type=int,default=0)
    A=ap.parse_args()
    m=Model(frames()[A.frame],A.scope)
    if A.res: m.add_residue()
    m.add_notgram(tuple(A.ng)); m.add_rank()
    if A.zrig: m.add_zrig()
    if A.za2: add_za2(m)
    if A.zcl: add_zcl(m)
    if A.nopure: add_nopure(m)
    print(m.dump(A.out))
