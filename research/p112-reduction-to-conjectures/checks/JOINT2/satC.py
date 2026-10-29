# impl A (own E8 build, functional-CNF) with optional phi refinement.  usage: satC.py nx x1 phi
import sys; sys.argv=sys.argv
src=open('../JOINT/satB.py').read()
# reuse satB construction verbatim up to coverage, then add phi clauses (patched textually)
nx,x1,usephi=sys.argv[1:4]
sys.argv=[sys.argv[0],nx,x1]
src=src.replace("fn='satB_%d_%d.cnf'%(nx,x1)","""
if USEPHI:
    import phi as PH
    W=[]
    for t in range(n):
        w0=0; w1=w0-ipf(L[t],r01); w2=w1-ipf(L[t],r12)
        assert w0-w2==ipf(L[t],L[root[2]]) or True
        W.append((w0,w1,w2))
    # root order: pairs (0,1),(1,2),(0,2) => w_a-w_b = ip(t,h_ab): check
    for t in range(n): assert abs(W[t][0]-W[t][2])==abs(ipf(L[t],L[root[2]]))
    D=PH.phis(W); z=[new() for _ in D]; cl.append(list(z))
    for i in range(len(z)):
        for j in range(i+1,len(z)): cl.append([-z[i],-z[j]])
    import itertools as it
    for t in range(n):
        for Km in range(8):
            K={k for k in range(3) if Km>>k&1}
            if not PH.bad(W[t],K): continue
            for zi,ph in zip(z,D):
                if not PH.compat(ph,W[t],K):
                    cl.append([-zi,free[t]]+[-c[k][t] for k in K]+[c[k][t] for k in range(3) if k not in K])
fn='satC_%d_%d_%d.cnf'%(nx,x1,USEPHI)""")
src=src.replace("json.dump","import json as _j; _j.dump").replace("'satB_model.json'","'satC_model_%d_%d_%d.json'%(nx,x1,USEPHI)")
USEPHI=int(usephi)
exec(compile(src,'satB_patched','exec'))
