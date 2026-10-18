"""PR234's five-stage route and idle geometry with the label family as a parameter (Dylan Crow, with Anthropic Claude assistance;
generalizes the exact matrix checks of code/geometry527.py + global_lowering.Lowerer of the source527/p10 packages).

The original fixes H = Q^h with G = I - J/9, a reference triple line q*, and port isometries given by coordinate
permutations pi (pi^-1 = pi^T).  Here G, q* and the port isometries g_t (exact rational matrices with
g^T G g = G and g q* = +-q_t) are inputs; every formula is the original one with pi -> g and pi^T -> g^-1:
    frame projector    P_B = B^T (B G B^T)^-1 B G                     p* = q* q*^T G / <q*,q*>,  k* = I - p*
    route rho(i,t)     [[g p* g^-1, g k*], [k* g^-1, p*]] on blocks (0, i) of H^5, identity elsewhere; rho(0,t) = I
    tau(i)             exchange of blocks 0 and i;   stage projector  P (+) K (+) ... (+) K  (K = k* on blocks 1..i)
    data(i,kind)       rho(i,t) * stage_projector(i, frame(kind)) * rho(i,t),  kinds P (port line), K (its complement), H, 0
Checks for every port t: rho^2 = I; P_t idempotent of trace 1; data(i-1,H) = data(i,P) and data(i-1,K) = data(i,0)
(i = 1..4); the eight idle boundary pairs (a, b) commute with a*b = a and gap b - a idempotent of trace
(2h-2, 2h-2, h-1, h-1, 2h+2, 2h+2, 4, 4); p (I - p) = 0.  For the entrance census of the word (here: every helper
starts at frame 0, the single entrance class sigma = 0), the five-window completion: the tau-conjugates of
(I_h - P_sigma) (+) 0 are pairwise orthogonal and sum to I - completion(sigma); a duplicated window is rejected.
usage: python3 geometry_g.py e8 WORD.json[.gz]        (E8 labels, all ports)
       python3 geometry_g.py regression                (paired-cube h = 20: equals the original literal formulas)"""
import sys, json, gzip, itertools, time
import sympy as sp
def eye(n): return sp.eye(n)
class Geo:
    def __init__(self,h,G,qstar):
        self.h=h; self.M=5*h; self.G=G; self.q=qstar
        nq=(qstar.T*G*qstar)[0]; assert nq!=0
        self.pstar=qstar*(qstar.T*G)/nq; self.kstar=eye(h)-self.pstar
    def frame_projector(self,B):
        if B.rows==0: return sp.zeros(self.h)
        return B.T*(B*self.G*B.T).inv()*B*self.G
    def rho(self,stage,g,ginv):
        h,M=self.h,self.M; I=eye(M)
        if stage==0: return I
        I[:h,:h]=g*self.pstar*ginv; I[stage*h:(stage+1)*h,stage*h:(stage+1)*h]=self.pstar
        I[:h,stage*h:(stage+1)*h]=g*self.kstar; I[stage*h:(stage+1)*h,:h]=self.kstar*ginv
        return I
    def tau(self,stage):
        I=eye(self.M)
        if stage:
            for j in range(self.h): I.row_swap(j,stage*self.h+j)
        return I
    def stage_projector(self,stage,P):
        A=sp.zeros(self.M); A[:self.h,:self.h]=P
        for j in range(1,stage+1): A[j*self.h:(j+1)*self.h,j*self.h:(j+1)*self.h]=self.kstar
        return A
    def check_port(self,qt,g,ginv):
        h,M=self.h,self.M; I=eye(M); Z=sp.zeros(M)
        assert g*ginv==eye(h) and g.T*self.G*g==self.G, 'port map is not a G-isometry'
        assert g*self.q==qt or g*self.q==-qt, 'port map does not send q* to the port line'
        routes=[self.rho(i,g,ginv) for i in range(5)]
        assert all(r*r==I for r in routes)
        P=self.frame_projector(qt.T); assert P*P==P and P.trace()==1
        Ph={'P':P,'K':eye(h)-P,'H':eye(h),'0':sp.zeros(h)}
        cache={}
        def data(i,kind):
            if (i,kind) not in cache: cache[i,kind]=routes[i]*self.stage_projector(i,Ph[kind])*routes[i]
            return cache[i,kind]
        for i in range(1,5):
            assert data(i-1,'H')==data(i,'P'); assert data(i-1,'K')==data(i,'0')
        p=data(0,'P')
        pairs=[(p,data(1,'H')),(Z,data(1,'K')),(data(2,'P'),data(3,'P')),(data(2,'0'),data(3,'0')),
               (data(2,'H'),I),(data(2,'K'),I-p),(data(4,'H'),I),(data(4,'K'),I-p)]
        ranks=[]
        for a,b in pairs:
            assert a*b==b*a==a; gap=b-a; assert gap*gap==gap; ranks.append(int(gap.trace()))
        assert p*(I-p)==Z and p+(I-p)==I
        return ranks,routes,data
    def check_entrance(self,Psigma):
        h,M=self.h,self.M; Z=sp.zeros(M)
        completion=sp.diag(*([Psigma]*5)); residual=eye(M)-completion
        assert completion*completion==completion and completion.trace()==5*Psigma.trace()
        actual=[]
        for i in range(5):
            t=self.tau(i); local=sp.zeros(M); local[:h,:h]=eye(h)-Psigma; actual.append(t*local*t)
        assert sum(actual,Z)==residual
        assert all(a*b==Z for i,a in enumerate(actual) for j,b in enumerate(actual) if i!=j)
        assert sum(actual[:4]+[actual[3]],Z)!=residual
        return True
def e8(word):
    c=json.load(gzip.open(word,'rt') if word.endswith('.gz') else open(word))
    assert c['form']=='<x,y>/2' and c['h']==8
    h=8; G=eye(h)/2; L=[sp.Matrix(x) for x in c['lines']]; v=len(L)
    ip=lambda a,b:(a.T*G*b)[0]
    def refl(r): return eye(h)-r*(r.T*G)*2/ip(r,r)       # s_r(x) = x - 2<x,r>/<r,r> r, a G-isometry and an involution
    star=0; geo=Geo(h,G,L[star])
    # port isometries: products of root reflections (BFS over lines), g q* = +-q_t
    isom={star:(eye(h),[])}; frontier=[star]
    while frontier:
        nxt=[]
        for a in frontier:
            for r in range(v):
                if r in (a,) : continue
                if abs(ip(L[a],L[r]))==1:
                    d=L[a]-L[r] if ip(L[a],L[r])==1 else L[a]+L[r]     # a root with s_d(q_a) = +-q_r
                    S=refl(d); b=r
                    if b not in isom:
                        g=S*isom[a][0]; isom[b]=(g,isom[a][1]+[d]); nxt.append(b)
        frontier=nxt
    assert len(isom)==v
    idle=None; t0=time.time()
    for t in range(v):
        g,word_=isom[t]; ginv=g.inv()
        ranks,_,_=geo.check_port(L[t],g,ginv)
        if idle is None: idle=ranks
        assert ranks==idle==[2*h-2,2*h-2,h-1,h-1,2*h+2,2*h+2,4,4],ranks
        if t%20==0: print('  port %d/%d checked (%d reflections) %.0fs'%(t+1,v,len(word_),time.time()-t0),flush=True)
    # entrance census of the word: every helper starts at the zero frame
    nreg=2*v+c['R']; starts={c['start'][r] for r in range(2*v,nreg)}; assert starts=={c['start'][v]} and len(c['frames'][c['start'][v]])==0
    geo.check_entrance(sp.zeros(h))
    print('PASS E8 five-stage geometry: all %d ports (W(E8) reflection words as port isometries), routes involutive, stage boundaries chained,'
          ' idle gap ranks %s, D_I D_P identity; entrance census {0: %d helpers}: five-window completion exact, duplicate window rejected'%(v,idle,c['R']))
def regression():
    """paired-cube h = 20: the generalized formulas with g = pi equal the original literal ones (global_lowering.Lowerer)."""
    h=20; G=eye(h)-sp.ones(h)/9; qstar=sp.Matrix([int(i<3) for i in range(h)]); geo=Geo(h,G,qstar)
    def original_rho(stage,q):
        I=sp.eye(5*h)
        if stage==0: return I
        rest=[j for j in range(h) if j not in q]; permutation=list(q)+rest
        pi=sp.zeros(h)
        for j,dst in enumerate(permutation): pi[dst,j]=1
        pstar=qstar*(qstar.T*G)/2; p=pi*pstar*pi.T; kstar=sp.eye(h)-pstar
        I[:h,:h]=p; I[stage*h:(stage+1)*h,stage*h:(stage+1)*h]=pstar
        I[:h,stage*h:(stage+1)*h]=pi*kstar; I[stage*h:(stage+1)*h,:h]=kstar*pi.T
        return I,pi
    for q in [(0,2,4),(1,7,13),(5,11,19)]:
        ranks_ok=None
        for i in range(5):
            Io,pi=original_rho(i,q) if i else (sp.eye(5*h),None)
            if i==0: continue
            assert geo.rho(i,pi,pi.T)==Io
        _,pi=original_rho(1,q)
        qt=sp.Matrix([int(j in q) for j in range(h)])
        ranks,_,_=geo.check_port(qt,pi,pi.T)
        assert ranks==[2*h-2,2*h-2,h-1,h-1,2*h+2,2*h+2,4,4]
    print('PASS regression: on paired-cube labels (h = 20, G = I - J/9) the generalized routes equal the original literal'
          ' rho for 3 ports and every stage, and give idle ranks (38, 38, 19, 19, 42, 42, 4, 4)')
if __name__=='__main__':
    if sys.argv[1]=='e8': e8(sys.argv[2])
    else: regression()
