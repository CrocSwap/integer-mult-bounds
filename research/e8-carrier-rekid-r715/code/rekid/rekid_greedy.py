"""greedy loop of single rekid moves (cancelling alternatives allowed) on objective s9 of reused word; candidates recomputed every round."""
import os,sys,pickle,time
os.environ['E8COORD']='ham'
import hx, hx2
from hx import Fm
out=sys.argv[1]; start=sys.argv[2] if len(sys.argv)>2 else None
if start:
    import ham1
    h=pickle.load(open(start,'rb'))
else:
    h,atoms=hx.load(); plans=hx.default_plans(atoms); S=hx.Search(h,atoms,plans,0)
V=120
EXT=os.environ.get('EXT','0')
if EXT!='0':
    import itertools
    h0,at0=hx.load(); Bcw=hx.H2.INFO['Bcw']; fl=hx.ham1.frame_line if hasattr(hx.ham1,'frame_line') else None
    import ham2x
    from ham1 import blocks
    fl=ham2x.frame_line
    n0=len(h.content)
    for c in blocks:
        for k in (1,2,3):
            for S in itertools.combinations(c,k):
                h.sym([Bcw[c]]+[fl[q] for q in S])
    print('extended pool by',len(h.content)-n0,'symbols',flush=True)
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
    rnd+=1
    N=len(h.content)
    bycont={}
    for u in range(N): bycont.setdefault(h.content[u],[]).append(u)
    needed=hx.C2.needed_symbols(h)
    idx={}
    ns=sorted(needed)   # restrict candidate kid pool to symbols that exist (needed or not) -- use all
    for x in range(N):
        cx=h.content[x]
        for y in range(x+1,N):
            c=cx^h.content[y]
            if c in bycont: idx.setdefault(c,[]).append((x,y))
    cands=[]
    for w in needed:
        if w<V: continue
        cur=tuple(sorted(h.kids[w])); aw=None
        for x,y in idx.get(h.content[w],[]):
            if tuple(sorted((x,y)))==cur or w in (x,y): continue
            f,d=Fm.closure(h.frame[x]|h.frame[y])
            if not Fm.inside(f,h.frame[w]): continue
            if aw is None: aw=True
            cands.append((w,(x,y)))
    best=None; t0=time.time(); ncheck=0
    for w,(x,y) in cands:
        if w in anc(x) or w in anc(y): continue
        old=h.kids[w]; h.kids[w]=(x,y)
        try: sc=hx2.score(h)
        except Exception: sc=None
        h.kids[w]=old; ncheck+=1
        if sc and (best is None or sc[0]>best[0][0]): best=(sc,w,(x,y))
    print('round',rnd,'cands',len(cands),'checked',ncheck,'%.0fs'%(time.time()-t0),'best',None if best is None else ('%.6e'%best[0][0],best[0][1]),flush=True)
    if best is None or best[0][0]<=base[0]+1e-12: break
    h.kids[best[1]]=best[2]; base=best[0]
    print('  applied w',best[1],'kids',best[2],'-> s9 %.6e Rreused %d Rraw %d'%base,flush=True)
    pickle.dump(h,open(out,'wb'))
print('done s9 %.6e Rreused %d'%(base[0],base[1]))
pickle.dump(h,open(out,'wb'))
