# Writer A (the IDEAL CNF writer): "fitting F2-rank <= r on the orthogonality graph of D", normalised by a pairwise
# non-orthogonal r-set S (B[S,S]=I forced => U_S=V_S=I).  Variables U_t[k]=B[t,S_k], V_s[k]=B[S_k,s]; Tseitin AND/XOR.
import subprocess, os, itertools, tempfile
from lib import nonorth_clique
KISSAT=os.environ.get('KISSAT','kissat'); DT=os.environ.get('DRAT_TRIM','drat-trim')
def cnf(G,D,r,S):
    nv=[0]; cl=[]
    def new(): nv[0]+=1; return nv[0]
    rest=[t for t in D if t not in S]
    U={t:[new() if G[t][S[k]]==0 else None for k in range(r)] for t in rest}  # U_t[k]=B[t,S_k]; forced 0 if nonorth
    V={s:[new() if G[S[k]][s]==0 else None for k in range(r)] for s in rest}
    def lit_xor(lits,c):
        # Tseitin chain: xor of lits == c
        if not lits:
            if c: cl.append([])
            return
        acc=lits[0]
        for l in lits[1:]:
            z=new(); cl.extend([[-z,acc,l],[-z,-acc,-l],[z,-acc,l],[z,acc,-l]]); acc=z
        cl.append([acc] if c else [-acc])
    for t in rest:
        for s in rest:
            if t!=s and G[t][s]==0: continue
            c=1 if t==s else 0
            prods=[]
            for k in range(r):
                a,b=U[t][k],V[s][k]
                if a is None or b is None: continue
                z=new(); cl.extend([[-z,a],[-z,b],[z,-a,-b]]); prods.append(z)
            lit_xor(prods,c)
    return nv[0],cl
def run(G,D,r,S=None,tag='x',check=True,timeout=1200,keep=None):
    if S is None: S=nonorth_clique(G,D,r)
    if S is None: return ('noS',None,0,0)
    n,cl=cnf(G,D,r,S)
    d=tempfile.mkdtemp(); f=os.path.join(d,tag+'.cnf'); p=os.path.join(d,tag+'.drat')
    with open(f,'w') as o:
        o.write(f'p cnf {n} {len(cl)}\n')
        for c in cl: o.write(' '.join(map(str,c))+' 0\n')
    out=subprocess.run([KISSAT,'-q','--no-binary',f,p],capture_output=True,text=True,timeout=timeout).stdout
    res='SAT' if 's SATISFIABLE' in out else ('UNSAT' if 'UNSATISFIABLE' in out else '?')
    ver=None
    if res=='UNSAT' and check:
        o2=subprocess.run([DT,f,p],capture_output=True,text=True,timeout=timeout).stdout
        ver='s VERIFIED' in o2
        if keep and ver:
            subprocess.run(['xz','-9e','-c',p],stdout=open(os.path.join(keep,tag+'.drat.xz'),'wb'))
    for x in (f,p):
        try: os.remove(x)
        except OSError: pass
    os.rmdir(d)
    return res,ver,n,len(cl)
