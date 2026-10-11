"""stack test: FP hierarchy (nesttax b1) + greedy rekid (2-term, existing + E-pool incl. FP-pair chains). usage fp_rg.py out.h"""
import os,sys,pickle,time,itertools
os.environ['E8COORD']='ham'
import fpbuild as FB, hx, hx2, ham1, ham2fpx
from hx import Fm
out=sys.argv[1]
h,P=FB.build_fp(1,0); V=120
fl=ham2fpx.frame_line
cwmask={}
for c in ham1.blocks:
    m=0
    for s in ham1.cw_lines(c): m|=1<<s
    cwmask[c]=m
Bcw={}
for u in range(V,len(h.content)):
    for c in ham1.blocks:
        if h.content[u]==cwmask[c] and h.dim[u]==4: Bcw[c]=u
assert len(Bcw)==14
n0=len(h.content)
for c in ham1.blocks:
    for k in (1,2,3):
        for S in itertools.combinations(c,k): h.sym([Bcw[c]]+[fl[q] for q in S])
    prs=[(a,b) for a,b in itertools.combinations(c,2) if (a,b) in P]
    for a,b in prs:
        fp=h.sym([fl[a],fl[b]])
        e=h.sym([Bcw[c],fp])
        for q in c:
            if q not in (a,b): h.sym([e,fl[q]])
print('pool extended by',len(h.content)-n0,flush=True)
base=hx2.score(h); print('base s9 %.6e Rreused %d Rraw %d'%base,flush=True)
def anc(u):
    seen=set(); st=[u]
    while st:
        z=st.pop()
        if z in seen: continue
        seen.add(z)
        if h.kids[z]: st.extend(h.kids[z])
    return seen
rnd=0
while True:
    rnd+=1; N=len(h.content)
    bycont={}
    for u in range(N): bycont.setdefault(h.content[u],[]).append(u)
    needed=hx.C2.needed_symbols(h)
    idx={}
    for x in range(N):
        cx=h.content[x]
        for y in range(x+1,N):
            c=cx^h.content[y]
            if c in bycont: idx.setdefault(c,[]).append((x,y))
    cands=[]
    for w in needed:
        if w<V: continue
        cur=tuple(sorted(h.kids[w]))
        for x,y in idx.get(h.content[w],[]):
            if tuple(sorted((x,y)))==cur or w in (x,y): continue
            f,d=Fm.closure(h.frame[x]|h.frame[y])
            if Fm.inside(f,h.frame[w]): cands.append((w,(x,y)))
    best=None; t0=time.time(); nchk=0
    for w,(x,y) in cands:
        if w in anc(x) or w in anc(y): continue
        old=h.kids[w]; h.kids[w]=(x,y)
        try: sc=hx2.score(h)
        except Exception: sc=None
        h.kids[w]=old; nchk+=1
        if sc and (best is None or sc[0]>best[0][0]): best=(sc,w,(x,y))
    print('round',rnd,'cands',len(cands),'checked',nchk,'%.0fs'%(time.time()-t0),'best',None if best is None else ('%.6e'%best[0][0],best[0][1]),flush=True)
    if best is None or best[0][0]<=base[0]+1e-12: break
    h.kids[best[1]]=best[2]; base=best[0]
    print('  applied w',best[1],'kids',best[2],'-> s9 %.6e Rreused %d Rraw %d'%base,flush=True)
    pickle.dump(h,open(out,'wb'))
print('done s9 %.6e Rreused %d'%(base[0],base[1])); pickle.dump(h,open(out,'wb'))
