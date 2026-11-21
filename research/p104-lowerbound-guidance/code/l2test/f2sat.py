# exact F2 minrank <= r feasibility via kissat. M_pq = w_p.u_q ; M_pp=1, M_pq=0 for odd pairs (Q=1), free for even.
from base import *
import subprocess, tempfile, os, time
def encode(X,r,clique):
    n=len(X); q=Q[np.ix_(X,X)]; nv=[0]; cl=[]
    def new(): nv[0]+=1; return nv[0]
    U=[[new() for _ in range(r)] for _ in range(n)]; Wv=[[new() for _ in range(r)] for _ in range(n)]
    def xor_chain(lits,rhs):
        # parity of lits == rhs ; chunked by 3
        cur=lits[0]; 
        for l in lits[1:]:
            z=new()
            # z = cur xor l
            cl.extend([[-z,cur,l],[-z,-cur,-l],[z,-cur,l],[z,cur,-l]]); cur=z
        cl.append([cur] if rhs else [-cur])
    for p in range(n):
        for s in range(n):
            if q[p,s]:   # odd (incl diag)
                prods=[]
                for k in range(r):
                    a=new(); x,y=Wv[p][k],U[s][k]
                    cl.extend([[-a,x],[-a,y],[a,-x,-y]]); prods.append(a)
                xor_chain(prods,1 if p==s else 0)
    # symmetry: clique members get unit vectors u
    for i,c in enumerate(clique):
        for k in range(r): cl.append([U[c][k]] if k==i else [-U[c][k]])
    return nv[0],cl
def solve(X,r,tl=1200):
    w,c=omega(X); idx={p:i for i,p in enumerate(X)}; clique=[idx[p] for p in c][:r]
    nv,cl=encode(X,r,clique)
    fn=tempfile.mktemp(suffix='.cnf',dir='/tmp') if False else '<tmpdir>'%(len(X),r)
    with open(fn,'w') as f:
        f.write('p cnf %d %d\n'%(nv,len(cl)))
        for c_ in cl: f.write(' '.join(map(str,c_))+' 0\n')
    t0=time.time()
    try: o=subprocess.run(['kissat','-q','--time=%d'%tl,fn],capture_output=True,text=True,timeout=tl+30).stdout
    except subprocess.TimeoutExpired: return 'TIMEOUT',time.time()-t0
    os.remove(fn)
    st='SAT' if 's SATISFIABLE' in o else 'UNSAT' if 's UNSATISFIABLE' in o else 'UNKNOWN'
    return st,time.time()-t0
if __name__=='__main__':
    import sys
    n=int(sys.argv[1]); u=int(sys.argv[2]); X=sections(n)[u]
    for r in [int(a) for a in sys.argv[3:]]:
        print(n,u,len(X),'r',r,solve(X,r,tl=300),flush=True)
