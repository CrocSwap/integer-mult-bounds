"""SPEC-forced legality checks.  Standard library only.

Part 0  SPEC text (repository files, pinned in SOURCES.json): the complex network's label
        space is F2^h with the ORDINARY dot product (upstream 03-motifs.tex), its terminal
        labels are X: U_a -> F, Y: 0 -> U_a^perp, and the chart family is
        L_U = {(u, u+v): u in U, v in U^perp} with L_F = {(z,z)} (notes/general-clifford-frames.tex).
Part 1  Exhaustive binary-symplectic checks on F2^h x F2^h, h = 4 and 5, over ALL Lagrangians:
        charts = Lagrangians split by (L_0, L_F); d(L_U,L_V) = dim U + dim V - 2 dim(U & V);
        zero-excess frames on x's route L_[q] -> L_F are exactly the charts L_U with q in U,
        on y's route L_0 -> L_{q^perp} exactly the charts with U <= q^perp; a common frame of the
        x_p cone and the y_t cone exists iff p.t = 0; charts transverse to L_[a] are exactly
        b^perp with a.b = 1; another symmetric Gram M costs d(graph M, L_F) = rank(M + I).
Part 2  Controls: with any symmetric invertible Gram M != I the light-cone equivalence
        "common frame iff p.M.t = 0" fails; the pair (L_0, L') with L' != L_F splits a different
        Lagrangian family; moving a Y endpoint q^perp -> b^perp (b != q) costs exactly 2.
Vector (x,z) is encoded as x | z<<h. omega((x,z),(x',z')) = x.z' + z.x'.
Prints PASS_SPEC_FORCED_LEGALITY."""
import itertools, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]  # repository root (research/<package>/legality.py)
def require(ok, label):
    if not ok:
        print('FAIL ' + label); sys.exit(1)
    print('ok   ' + label)
def spec_text():
    m = (ROOT / 'upstream/build/sections/03-motifs.tex').read_text(encoding='utf-8')
    flat = ' '.join(m.split())
    require('For the complex network, take instead $F=\\mathbb F_2^h$ with the ordinary dot product' in flat,
            'SPEC 03-motifs: complex labels F = F_2^h with the ordinary dot product')
    require('X_a&U_a&\\mathcalF' in flat.replace(' ', '') and 'Y_a&0&U_a^\\perp' in flat.replace(' ', ''),
            'SPEC 03-motifs: terminal labels X_a: U_a -> F and Y_a: 0 -> U_a^perp')
    g = ' '.join((ROOT / 'notes/general-clifford-frames.tex').read_text(encoding='utf-8').split())
    require('L_U=\\{(u,u+v):u\\in U,\\ v\\in U^\\perp\\}' in g and 'L_F=FL_0=\\{(z,z)\\}' in g,
            'notes/general-clifford-frames: charts L_U = {(u,u+v)} and L_F = {(z,z)}')
def pc(a): return bin(a).count('1')&1
def rank(vs):
    piv={}; r=0
    for v in vs:
        while v:
            hb=v.bit_length()-1
            if hb in piv: v^=piv[hb]
            else: piv[hb]=v; r+=1; break
    return r
def span(b):
    s={0}
    for v in b: s|={x^v for x in s}
    return frozenset(s)
def subspaces(h):
    seen=set(); out=[]
    for k in range(h+1):
        for B in itertools.combinations(range(1,1<<h),k):
            if rank(B)<k: continue
            S=span(B)
            if S in seen: continue
            seen.add(S); out.append((S,list(B)))
    return out
def run(h):
    M=(1<<h)-1
    def V(x,z): return x|(z<<h)
    def om(a,b): return pc((a&M)&(b>>h))^pc((a>>h)&(b&M))
    subs=subspaces(h)
    def perp(S): return frozenset(y for y in range(1<<h) if all(not pc(y&s) for s in S))
    def basis(S):
        b=[]
        for v in sorted(S):
            if v and rank(b+[v])>len(b): b.append(v)
        return b
    # all Lagrangians: L = {(w,y): w in W, y.w' = beta(w,w') for w' in W} + (0, W^perp), beta symmetric on W
    lag=set()
    for W,_ in subs:
        Wb=basis(W); k=len(Wb); Wp=basis(perp(W))
        sols={}
        for y in range(1<<h): sols.setdefault(tuple(pc(y&w) for w in Wb),y)
        pairs=[(i,j) for i in range(k) for j in range(i,k)]
        for bits in range(1<<len(pairs)):
            beta=[[0]*k for _ in range(k)]
            for n,(i,j) in enumerate(pairs):
                if bits>>n&1: beta[i][j]=beta[j][i]=1
            gens=[V(Wb[i],sols[tuple(beta[i])]) for i in range(k)]+[V(0,v) for v in Wp]
            lag.add(span(gens))
    cnt=1
    for i in range(1,h+1): cnt*=(1<<i)+1
    require(len(lag)==cnt and all(len(L)==1<<h and not any(om(a,b) for a in L for b in L) for L in lag),
            'h=%d: %d Lagrangians = prod(2^i+1), all isotropic of size 2^h'%(h,cnt))
    L0=span([V(0,1<<i) for i in range(h)]); LF=span([V(1<<i,1<<i) for i in range(h)])
    def d(A,B): return h-(len(A&B).bit_length()-1)
    chart={S:span([V(u,u) for u in basis(S)]+[V(0,v) for v in basis(perp(S))]) for S,_ in subs}
    cset=set(chart.values())
    split={L for L in lag if (len(L&L0).bit_length()-1)+(len(L&LF).bit_length()-1)==h}
    require(cset<=lag and len(cset)==len(subs) and split==cset,
            'h=%d: charts (%d) = Lagrangians split by (L_0, L_F)'%(h,len(subs)))
    bad=sum(d(chart[A],chart[B])!=len(basis(A))+len(basis(B))-2*len(basis(A&B)) for A,_ in subs for B,_ in subs)
    require(bad==0,'h=%d: d(L_U,L_V) = dim U + dim V - 2 dim(U & V) on all %d chart pairs'%(h,len(subs)**2))
    norm1=[q for q in range(1,1<<h) if pc(q)]
    line=lambda q: chart[span([q])]; hyp=lambda q: chart[perp(span([q]))]
    bad2=0; G1={}; G2={}
    for q in norm1:
        g1={Mq for Mq in lag if d(line(q),Mq)+d(Mq,LF)==d(line(q),LF)}
        g2={Mq for Mq in lag if d(L0,Mq)+d(Mq,hyp(q))==d(L0,hyp(q))}
        e1={chart[S] for S,_ in subs if q in S}; e2={chart[S] for S,_ in subs if S<=perp(span([q]))}
        bad2+=(g1!=e1)+(g2!=e2); G1[q]=g1; G2[q]=g2
    require(bad2==0,'h=%d: over ALL Lagrangians, zero-excess frames on [q]->F are the charts U containing q, on 0->q^perp the charts U <= q^perp (%d norm-one q)'%(h,len(norm1)))
    bad3=n3=0
    for p_ in norm1:
        for t in norm1:
            if p_==t: continue
            n3+=1; bad3+=bool(G1[p_]&G2[t])!=(pc(p_&t)==0)
    require(bad3==0,'h=%d: light cone: a common frame of the x_p and y_t cones exists iff p.t = 0 (%d pairs)'%(h,n3))
    own=sum(bool(G1[q]&G2[q]) for q in norm1)
    require(own==0,'h=%d: own pair: no common frame of x_q and y_q cones (q.q = 1) for all %d q'%(h,len(norm1)))
    bad5=0
    for a in range(1,1<<h):
        tr={S for S,_ in subs if d(chart[span([a])],chart[S])==h}
        bad5+=tr!={perp(span([b])) for b in range(1,1<<h) if pc(a&b)}
    require(bad5==0,'h=%d: charts transverse to L_[a] are exactly b^perp with a.b = 1 (all a != 0)'%h)
    mv=[d(hyp(q),hyp(b)) for q in range(1,1<<h) for b in range(1,1<<h) if b!=q]
    require(set(mv)=={2},'h=%d: moving a Y end q^perp -> b^perp (b != q) costs exactly 2 (%d pairs)'%(h,len(mv)))
    # control: another symmetric invertible Gram Mg breaks the dot-product light cone
    if h==4:
        def graph(Mx): return span([V(1<<i,Mx[i]) for i in range(h)])
        bad7=n7=fails=0
        for rows in itertools.product(range(1<<h),repeat=h):
            if any(((rows[i]>>j)&1)!=((rows[j]>>i)&1) for i in range(h) for j in range(h)): continue
            if rank(list(rows))<h: continue
            n7+=1; S=[rows[i]^(1<<i) for i in range(h)]
            bad7+=d(graph(rows),LF)!=rank(S)
            if list(rows)!=[1<<i for i in range(h)]:
                Mt=lambda t: sum(((pc(rows[i]&t))<<i) for i in range(h))
                fails+=any(bool(G1[p_]&G2[t])!=(pc(p_&Mt(t))==0) for p_ in norm1 for t in norm1 if p_!=t)
        require(n7==448 and bad7==0,'h=4: all 448 symmetric invertible Grams M: d(graph M, L_F) = rank(M + I)')
        require(fails==n7-1,'control h=4: for every one of the %d Grams M != I the rule "common frame iff p.M.t = 0" fails'%(n7-1))
        Lp=next(L for L in sorted(lag,key=sorted) if L!=LF and len(L&L0)==1)
        split2={L for L in lag if (len(L&L0).bit_length()-1)+(len(L&Lp).bit_length()-1)==h}
        require(split2!=cset,'control h=4: splitting by (L_0, L\') with L\' != L_F transverse to L_0 gives a different family')
if __name__=='__main__':
    spec_text()
    for h in (4,5): run(h)
    print('PASS_SPEC_FORCED_LEGALITY')
