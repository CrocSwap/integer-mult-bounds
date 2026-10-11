"""exhaustive single rekid moves: re-express a needed rule w as x^y with x,y other EXISTING symbols (cancellation allowed),
frame(x)|frame(y) inside frame(w), acyclic. objective s9 of reused word (hx2.score)."""
import os,sys,pickle,time
os.environ['E8COORD']='ham'
import hx, hx2
from hx import Fm
h,atoms=hx.load(); plans=hx.default_plans(atoms)
S=hx.Search(h,atoms,plans,0)   # sets needs (same as default)
V=120; N=len(h.content)
base=hx2.score(h); print('base s9 %.6e Rreused %d Rraw %d'%base,flush=True)
bycont={}
for u in range(N): bycont.setdefault(h.content[u],[]).append(u)
idx={}
for x in range(N):
    for y in range(x+1,N):
        c=h.content[x]^h.content[y]
        if c in bycont: idx.setdefault(c,[]).append((x,y))
def anc(u,seen=None):
    seen=set() if seen is None else seen
    st=[u]
    while st:
        z=st.pop()
        if z in seen: continue
        seen.add(z)
        if h.kids[z]: st.extend(h.kids[z])
    return seen
needed=hx.C2.needed_symbols(h)
cands=[]
for w in needed:
    if w<V: continue
    cur=tuple(sorted(h.kids[w]))
    for x,y in idx.get(h.content[w],[]):
        if tuple(sorted((x,y)))==cur or w in (x,y): continue
        f,d=Fm.closure(h.frame[x]|h.frame[y])
        if not Fm.inside(f,h.frame[w]): continue
        if w in anc(x) or w in anc(y): continue
        cands.append((w,(x,y),bool(h.content[x]&h.content[y])))
print('candidates',len(cands),'cancelling',sum(c for _,_,c in cands),flush=True)
res=[]
t0=time.time()
for w,(x,y),canc in cands:
    old=h.kids[w]; h.kids[w]=(x,y)
    try: sc=hx2.score(h)
    except Exception as e: sc=None
    h.kids[w]=old
    res.append((sc,w,(x,y),canc))
res=[r for r in res if r[0]]
res.sort(key=lambda r:-r[0][0])
print('time',time.time()-t0)
for r in res[:10]: print('s9 %.6e Rr %d Rraw %d'%r[0],'w',r[1],'dim',h.dim[r[1]],'sz',bin(h.content[r[1]]).count('1'),'kids',r[2],'canc',r[3])
better=[r for r in res if r[0][0]>base[0]+1e-12]
print('improving single rekids:',len(better),'; equal:',sum(1 for r in res if abs(r[0][0]-base[0])<=1e-12))
