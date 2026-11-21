import itertools, sys, subprocess, tempfile, os, time
from nv import *
def net_eqs(labs,nodes,order,edges,Q):
    """nodes: list of (a,b); order=list of node indices topological; edges list (j,k) j->k (j before k). returns (vars,eqs) or None if diag impossible"""
    n=len(labs); m=len(nodes)
    A=[[i for i,q in enumerate(labs) if q in nd[0]] for nd in nodes]
    B=[[i for i,q in enumerate(labs) if all(dot(q,y)==0 for y in nd[1])] for nd in nodes]
    vars_=[]; F={};G={};H={}
    for k in range(m):
        for p in A[k]: F[k,p]=f"f{k}_{p}"; vars_.append(F[k,p])
        for t in B[k]: G[t,k]=f"g{t}_{k}"; vars_.append(G[t,k])
    for (j,k) in edges: H[k,j]=f"h{k}_{j}"; vars_.append(H[k,j])
    # path sums Np[k][j]: poly string of sum over paths j->..->k (k==j ->'1')
    paths={}
    def P(k,j):
        if (k,j) in paths: return paths[k,j]
        if k==j: r=['1']
        else:
            r=[]
            for (i,kk) in edges:
                if kk==k and (i==j or reach(j,i)):
                    for s in P(i,j): r.append(f"{H[k,i]}*{s}" if s!='1' else H[k,i])
        paths[k,j]=r; return r
    adj={}
    for (i,k) in edges: adj.setdefault(i,[]).append(k)
    def reach(a,b):
        st=[a];seen=set()
        while st:
            x=st.pop()
            if x==b: return True
            for y in adj.get(x,[]):
                if y not in seen: seen.add(y); st.append(y)
        return False
    eqs=[]
    for t in range(n):
        for p in range(n):
            if not Q[t][p]: continue
            terms=[]
            for k in range(m):
                if (t,k) not in G: continue
                for j in range(m):
                    if (j,p) not in [(jj,pp) for (jj,pp) in ()] and (j,p) in F and (j==k or reach(j,k)):
                        for s in P(k,j):
                            terms.append(f"{G[t,k]}*{s}*{F[j,p]}" if s!='1' else f"{G[t,k]}*{F[j,p]}")
            if t==p:
                if not terms: return None
                vars_.append(f"z{t}"); eqs.append("("+"+".join(terms)+f")*z{t}-1")
            elif terms: eqs.append("+".join(terms))
    return vars_,eqs
def run_sing(vars_,eqs,timeout=60):
    src=f"ring r=0,({','.join(vars_)}),dp;\noption(redSB);\nideal I={','.join(eqs)};\nideal G=std(I);\nif (size(G)==1 && deg(G[1])==0) {{ print(\"INFEASIBLE\"); }} else {{ print(\"FEASIBLE\"); }}\nquit;\n"
    with tempfile.NamedTemporaryFile('w',suffix='.sing',delete=False) as f: f.write(src); fn=f.name
    try: out=subprocess.run(['Singular','-q',fn],capture_output=True,text=True,timeout=timeout).stdout.strip()
    except subprocess.TimeoutExpired: out='TIMEOUT'
    os.unlink(fn); return out
