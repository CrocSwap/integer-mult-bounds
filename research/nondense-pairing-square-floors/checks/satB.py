# AUDIT-IQ: independent minrank tools. Own clique search, own CNF (chunked direct XOR), own brute force, model decoding.
import itertools, os, subprocess, random, tempfile
KISSAT=os.environ.get('KISSAT','kissat'); DT=os.environ.get('DRAT_TRIM','drat-trim')
def rk2(rows):
    b=[];
    for x in rows:
        for y in b: x=min(x,x^y)
        if x: b.append(x)
    return len(b)
def clique(G,D,r,seed=0,tries=3000):
    """random greedy search for r pairwise NON-orthogonal lines in D"""
    rnd=random.Random(seed); D=list(D)
    for _ in range(tries):
        rnd.shuffle(D); S=[]
        for t in D:
            if all(G[t][s]!=0 for s in S): S.append(t)
            if len(S)==r: return S
    return None
def brute_mr(G,D,cap=22):
    m=len(D); free=[(a,b) for a in range(m) for b in range(m) if a!=b and G[D[a]][D[b]]==0]
    if len(free)>cap: return None
    best=m
    for bits in range(1<<len(free)):
        rows=[1<<a for a in range(m)]
        for q,(a,b) in enumerate(free):
            if bits>>q&1: rows[a]|=1<<b
        best=min(best,rk2(rows))
    return best
class CNF:
    def __init__(s): s.n=0; s.cl=[]
    def v(s): s.n+=1; return s.n
    def xor_eq(s,lits,c):
        # chunked: xor(chunk) <-> aux by direct clauses, chunk size <=3
        while len(lits)>3:
            ch,lits=lits[:3],lits[3:]; a=s.v(); s.direct(ch+[a],0); lits=lits+[a]
        if not lits:
            if c: s.cl.append([])
            return
        s.direct(lits,c)
    def direct(s,lits,c):
        # forbid every assignment of lits with parity != c
        for bits in itertools.product((0,1),repeat=len(lits)):
            if sum(bits)%2!=c: s.cl.append([(-l if b else l) for l,b in zip(lits,bits)])
def encode(G,D,r,S):
    """rank<=r fitting matrix on G_perp[D]; normalised U_S=V_S=I (B[S,S]=I forced since S pairwise non-orth)"""
    f=CNF(); rest=[t for t in D if t not in S]
    U={t:[(f.v() if G[t][S[k]]==0 else 0) for k in range(r)] for t in rest}
    V={t:[(f.v() if G[S[k]][t]==0 else 0) for k in range(r)] for t in rest}
    for t in rest:
        for s in rest:
            if t!=s and G[t][s]==0: continue
            ps=[]
            for k in range(r):
                a,b=U[t][k],V[s][k]
                if a and b:
                    p=f.v(); f.cl+= [[-p,a],[-p,b],[p,-a,-b]]; ps.append(p)
            f.xor_eq(ps,1 if t==s else 0)
    return f,U,V,rest
def solve(G,D,r,S=None,seed=0,drat=True,timeout=1200,verify_model=True):
    if S is None: S=clique(G,D,r,seed)
    if S is None: return ('noS',None)
    f,U,V,rest=encode(G,D,r,S)
    d=tempfile.mkdtemp(dir=None); fn=os.path.join(d,'a.cnf'); pf=os.path.join(d,'a.drat')
    with open(fn,'w') as o:
        o.write(f'p cnf {f.n} {len(f.cl)}\n'); o.write(''.join(' '.join(map(str,c))+' 0\n' for c in f.cl))
    p=subprocess.run([KISSAT,'--no-binary',fn,pf] if drat else [KISSAT,fn],capture_output=True,text=True,timeout=timeout)
    out=p.stdout; res='SAT' if '\ns SATISFIABLE' in '\n'+out else ('UNSAT' if 's UNSATISFIABLE' in out else '?')
    ver=None
    if res=='UNSAT' and drat:
        o2=subprocess.run([DT,fn,pf],capture_output=True,text=True,timeout=timeout).stdout
        ver=('s VERIFIED' in o2)
    if res=='SAT' and verify_model:
        val=set(int(x) for l in out.splitlines() if l.startswith('v') for x in l[1:].split() if int(x)>0)
        g=lambda x: 1 if (x and x in val) else 0
        idx={t:i for i,t in enumerate(D)}; Ufull={}; Vfull={}
        for k,sk in enumerate(S): Ufull[sk]=[int(k==q) for q in range(r)]; Vfull[sk]=[int(k==q) for q in range(r)]
        for t in rest: Ufull[t]=[g(x) for x in U[t]]; Vfull[t]=[g(x) for x in V[t]]
        B={(t,s):sum(a*b for a,b in zip(Ufull[t],Vfull[s]))%2 for t in D for s in D}
        ok=all(B[t,t]==1 for t in D) and all(B[t,s]==0 for t in D for s in D if t!=s and G[t][s]!=0)
        rows=[sum(B[t,s]<<idx[s] for s in D) for t in D]; ver=(ok and rk2(rows)<=r)
    for x in (fn,pf):
        try: os.remove(x)
        except OSError: pass
    os.rmdir(d)
    return (res,ver)
