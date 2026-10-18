import os
import sys,time,pickle,itertools
sys.path.insert(0,(__import__('os').environ['HM_ROOT']+'/cards/B155'))
from ex import *   # O,s,B,d,pairs,pr_of,moves,tgt,EMPTY,R0,K0,T0,pre_targets
from collections import defaultdict,Counter
# ---- move universe
M=[]
for p in pairs:
    for m in moves(p): M.append(m)          # ('h2r',j,pre_i,t) / ('r2h',j,ins_pos,t,h)
# deferral moves: pre-read i of target t moved to just after t's later climb j (frame contains h's)
cur=list(d['start']);F=O.join
for e in s['A']:
    rs=regs(e);f=e[-1]
    for q in rs:f=F(f,cur[q])
    for q in rs:cur[q]=f
for k,c in enumerate(d['centers']):cur[c]=F(cur[c],d['center_frames'][k])
hist=defaultdict(list)
for i,e in enumerate(B):
    rs=regs(e);f=e[-1]
    for q in rs:f=F(f,cur[q])
    for q in rs:
        if cur[q]!=f: hist[q].append((i,f))
        cur[q]=f
for i,e in enumerate(B[:120]):
    if not(e[0]=='add' and tgt(e[1]) and e[2]>=224):continue
    t,h=e[1],e[2]
    cg=next(j for j in range(i+1,len(B)) if B[j][1]==h)
    hfr=[f for (j,f) in hist[h] if j<=i][-1] if any(j<=i for j,_ in hist[h]) else d['start'][h]
    nx=[(j,f) for j,f in hist[t] if j>i]
    for j,f in nx:
        if O.sub(hfr,f) and j<cg and not any(B[k][0]=='add' and B[k][2]==t for k in range(i+1,j+1)):
            M.append(('def',i,j,t)); break
def build_all(mvs):
    Bn=[list(e) for e in B];dele=set();ins=defaultdict(list)
    for m in mvs:
        if m[0]=='h2r': Bn[m[1]][2]=pr_of[m[1]]['r'];dele.add(m[2])
        elif m[0]=='r2h':
            p=pr_of[m[1]];Bn[m[1]][2]=p['h'];g=B[m[1]]
            ins[m[2]].append(['add',m[3],p['h'],-g[3],g[4],EMPTY])
        else:
            dele.add(m[1]);ins[m[2]+1].append(list(B[m[1]]))
    out=[]
    for i,e in enumerate(Bn):
        out+=ins.get(i,[])
        if i not in dele: out.append(e)
    out+=ins.get(len(Bn),[])
    s2=dict(s);s2['B']=out;return s2
def valid(mvs):
    idx=[m[1] for m in mvs]
    if len(set(idx))<len(idx): return False
    pre=[m[2] for m in mvs if m[0]=='h2r']
    return len(set(pre))==len(pre) and not (set(pre)&{m[1] for m in mvs if m[0]=='def'})
def V(mvs):
    r=O.evaluate(build_all(mvs));return frozenset(r['fin_raise'])|frozenset(('c',c) for c in r['cen_viol']),r
def _p(ab):
    a,b=ab
    if not valid([M[a],M[b]]): return None
    return V([M[a],M[b]])[0]
if __name__=='__main__':
    from multiprocessing import Pool
    n=len(M);print(n,'moves',Counter(m[0] for m in M),flush=True)
    sg=[V([m])[0] for m in M]
    print('singles legal',sum(1 for v in sg if not v),flush=True)
    t0=time.time()
    prs=[(a,b) for a in range(n) for b in range(a+1,n)]
    with Pool(2) as P: res=P.map(_p,prs,chunksize=500)
    pv={ab:v for ab,v in zip(prs,res) if v is not None}
    print(len(pv),'pairs',time.time()-t0,flush=True)
    from pairsio import dump_pairs
    dump_pairs((M,sg,pv),os.environ.get('PAIRS_OUT','pairs.json.gz'))
