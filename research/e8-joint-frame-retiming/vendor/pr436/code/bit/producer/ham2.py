"""Dylan Crow, with Anthropic Claude assistance; Apache-2.0. Hamming-coordinate bit-E8 design with pi-coset pairing (E8COORD=ham)."""
import os, sys, itertools, pickle
assert os.environ.get('E8COORD')=='ham'
import e8lib as E, frames as Fm
from ham1 import SH, blocks, cw_lines, frame_line, idx
V=E.V; L=E.LINES
def proj_dir(S,c):
    """projection of line S onto C_c as a normalized tuple (sign-canonical) or None if zero"""
    v=[L[S][k] if k in c else 0 for k in range(8)]
    if not any(v): return None
    f=[a for a in v if a][0]
    return tuple(a if f>0 else -a for a in v)
FRAMEOPT=[True,0,0]
P={}
LSKEYS=set()
def par(k,n):
    return P.get(k,0)%n
def build(pairing=0, fold=True):
    h=SH()
    comp={c:[c2 for c2 in blocks if not set(c)&set(c2)][0] for c in blocks}
    # L sets: lines of block c2 with projection onto C_c (c != c2, |c&c2|=2) along b-line p
    Lsets={}
    for c2 in blocks:
        for c in blocks:
            if len(set(c)&set(c2))!=2: continue
            for S in cw_lines(c2):
                p=proj_dir(S,c)
                Lsets.setdefault((c2,p),set()).add(S)
    Lsets={k:sorted(v) for k,v in Lsets.items()}
    for k,v in Lsets.items(): assert len(v)==4,(k,v)
    Lsym={}
    for (c2,p),mem in Lsets.items():
        # split into two pairs by the relative sign on the other two coordinates of c2
        oth=[q for q in c2 if p[q]==0]
        sp=par(('ls',c2,p),3); LSKEYS.add(('ls',c2,p))
        if sp==0:
            a=[s for s in mem if L[s][oth[0]]*L[s][oth[1]]>0]; b=[s for s in mem if L[s][oth[0]]*L[s][oth[1]]<0]
        else:
            q0=[q for q in c2 if p[q]!=0][0]
            a=[s for s in mem if L[s][q0]*L[s][oth[sp-1]]>0]; b=[s for s in mem if L[s][q0]*L[s][oth[sp-1]]<0]
        Lsym[(c2,p)]=h.sym([h.sym(sorted(a)),h.sym(sorted(b))])
    Msym={}
    for c in blocks:
        for (c2,p),s in Lsets.items():
            pass
    for (c2,p) in Lsets:
        # p is a b-line of the block c for which p's support pair lies: find blocks c containing supp(p) other than c2
        supp=tuple(q for q in range(8) if p[q])
        for c in blocks:
            if c!=c2 and set(supp)<=set(c):
                Msym.setdefault((c,p),[]).append(Lsym[(c2,p)])
    for k in list(Msym):
        assert len(Msym[k])==2
        Msym[k]=h.sym(sorted(Msym[k]))
    Dsym={}; Bcw={}
    for c in blocks:
        ls=cw_lines(c)
        # E(D4(c)) = all 8 codeword lines of c + 4 frame lines
        p=None
        for (c2,pp),s in Lsym.items():
            pass
        # use two complementary L-like halves: split by relative sign on (c0,c1)
        i,j=c[0],c[1]
        A=[s for s in ls if L[s][i]*L[s][j]>0]; B=[s for s in ls if L[s][i]*L[s][j]<0]
        Bcw[c]=h.sym([h.sym(sorted(A[:2])+sorted(A[2:])), h.sym(sorted(B)) ])
        Dsym[c]=h.sym([Bcw[c]]+[frame_line[q] for q in c])
    def bdir(u,w):
        """the two b-line directions in the plane span(L[u],L[w]) (vectors a+-b normalized)"""
        out=[]
        for sg in (1,-1):
            v=tuple(x+sg*y for x,y in zip(L[u],L[w]))
            f=[a for a in v if a][0]
            v=tuple(a//2 if f>0 else -a//2 for a in v)
            out.append(v)
        return out
    for c in blocks:
        cb=comp[c]
        ls=cw_lines(c)
        # pi-cosets: 4 mutually orthogonal lines
        cos=[]
        rem=set(ls)
        while rem:
            t=min(rem); Q=[t]+[s for s in rem if s!=t and E.G[t][s]==0]
            assert len(Q)==4 and all(E.G[a][b]==0 for a in Q for b in Q if a!=b)
            cos.append(Q); rem-=set(Q)
        for Q in cos:
            pr_=(pairing+par(('pair',c,min(Q)),3))%3
            pairs=[(Q[0],Q[1+pr_]),tuple(q for q in Q[1:] if q!=Q[1+pr_])]
            partner={}
            for x,y in pairs: partner[x]=y; partner[y]=x
            for t in Q:
                d=partner[t]; a,b=[q for q in Q if q not in (t,d)]
                p5,p6=sorted(bdir(a,b))
                if par(('l5',min(t,d)),2): p5,p6=p6,p5
                M=lambda p: Msym[(c,p)]
                need=[Dsym[cb], M(p5), h.sym([M(p6),a,b])]
                q1,q2=sorted(bdir(a,d)); r1,r2=sorted(bdir(b,d))
                fo=par(('fold',t),2) if fold else 2
                if fo==0:
                    need+=[h.sym([M(q1),M(q2),d]), h.sym([M(r1),M(r2)])]
                elif fo==1:
                    need+=[h.sym([M(q1),M(q2)]), h.sym([M(r1),M(r2),d])]
                else:
                    need+=[h.sym([M(q1),M(q2)]), h.sym([M(r1),M(r2)]), d]
                h.need[t]=set(need)
    for m in range(8):
        t=frame_line[m]
        if not FRAMEOPT[0]:
            h.need[t]=set([Dsym[c] for c in blocks if m not in c]+[frame_line[q] for q in range(8) if q!=m]); continue
        avoid=[c for c in blocks if m not in c]
        c0=avoid[(FRAMEOPT[1]+par(('fc0',m),7))%len(avoid)]
        ns=[q for q in range(8) if q!=m and q not in c0]
        n=ns[(FRAMEOPT[2]+par(('fn',m),3))%len(ns)]
        A6=[q for q in range(8) if q not in (m,n)]
        in6=[c for c in avoid if set(c)<=set(A6) and c!=c0]; assert len(in6)==2
        top=[c for c in avoid if n in c]; assert len(top)==4
        # pair top blocks so each pair spans a 6-dim coordinate space (always true)
        need=[Dsym[c0], h.sym([Bcw[in6[0]],Bcw[in6[1]]]+[frame_line[q] for q in A6 if q not in c0]),
              h.sym([Bcw[top[0]],Bcw[top[1]],frame_line[n]]), h.sym([Bcw[top[2]],Bcw[top[3]]])]
        h.need[t]=set(need)
    for t in range(V):
        x=0
        for u in h.need[t]: x^=h.content[u]
        assert x==Fm.HYP[t],(t,bin(x^Fm.HYP[t]).count('1'))
    return h
if __name__=='__main__':
    pr=int(sys.argv[1]) if len(sys.argv)>1 else 0
    fold=(sys.argv[2]!='nofold') if len(sys.argv)>2 else True
    h=build(pr,fold)
    pickle.dump(h,open('hier_ham2_%d_%s.pkl'%(pr,fold),'wb'))
    print('symbols',len(h.content)-V,'reads',sum(len(n) for n in h.need))
