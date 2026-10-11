"""greedy rekid with 2-term (x^y) and 3-term (x^(u^v), u^v a NEW symbol) re-expressions of needed rules. objective hx2.score. usage: rekid3.py out.h start.h [ext]"""
import os,sys,pickle,time,itertools
os.environ['E8COORD']='ham'
import hx, hx2, ham1, ham2x
from hx import Fm
out=sys.argv[1]; start=sys.argv[2]; EXT=len(sys.argv)>3 and sys.argv[3]=='ext'
MAXC=int(os.environ.get('MAXC','4000'))
h=pickle.load(open(start,'rb')); V=120
if EXT:
    h0,at0=hx.load(); Bcw=hx.H2.INFO['Bcw']; fl=ham2x.frame_line
    for c in ham1.blocks:
        for k in (1,2,3):
            for S in itertools.combinations(c,k): h.sym([Bcw[c]]+[fl[q] for q in S])
base=hx2.score(h); print('base s9 %.6e Rreused %d Rraw %d'%base,flush=True)
def desc_of(w):
    seen=set(); st=[w]
    while st:
        z=st.pop()
        if z in seen: continue
        seen.add(z)
        if h.kids[z]: st.extend(h.kids[z])
    return seen
def mk(u,v):
    c=h.content[u]^h.content[v]
    f,d=Fm.closure(h.frame[u]|h.frame[v])
    h.content.append(c); h.frame.append(f); h.dim.append(d); h.kids.append((u,v)); h.need.append(set()) if False else None
    return len(h.content)-1
rnd=0
while True:
    rnd+=1; N=len(h.content)
    needed=hx.C2.needed_symbols(h)
    pairidx={}
    for x in range(N):
        cx=h.content[x]
        for y in range(x+1,N):
            pairidx.setdefault(cx^h.content[y],[]).append((x,y))
    cands=[]
    for w in needed:
        if w<V: continue
        fw=h.frame[w]; cw=h.content[w]
        pool=[u for u in range(N) if Fm.inside(h.frame[u],fw) and u!=w]
        dw=desc_of(w)   # descendants (kids tree) are allowed; ancestors of w are not -> check via anc below
        cur=tuple(sorted(h.kids[w]))
        for x,y in pairidx.get(cw,[]):
            if w in (x,y) or tuple(sorted((x,y)))==cur: continue
            f,d=Fm.closure(h.frame[x]|h.frame[y])
            if Fm.inside(f,fw): cands.append((w,x,y,None))
        for x in pool:
            r=cw^h.content[x]
            for u,v in pairidx.get(r,[]):
                if w in (u,v) or x in (u,v): continue
                if not (Fm.inside(h.frame[u],fw) and Fm.inside(h.frame[v],fw)): continue
                cands.append((w,x,u,v))
    # ancestors check helper
    def anc(u):
        seen=set(); st=[u]
        while st:
            z=st.pop()
            if z in seen: continue
            seen.add(z)
            if h.kids[z]: st.extend(h.kids[z])
        return seen
    import random
    random.Random(rnd).shuffle(cands)
    ncand=len(cands); cands=cands[:MAXC]
    best=None; t0=time.time(); nchk=0
    for w,x,u,v in cands:
        if v is None:
            y=u
            if w in anc(x) or w in anc(y): continue
            old=h.kids[w]; h.kids[w]=(x,y)
            try: sc=hx2.score(h)
            except Exception: sc=None
            h.kids[w]=old
            key=(w,(x,y))
        else:
            if w in anc(x) or w in anc(u) or w in anc(v): continue
            old=h.kids[w]; z=mk(u,v); h.kids[w]=(x,z)
            try: sc=hx2.score(h)
            except Exception: sc=None
            h.kids[w]=old
            # remove temp z
            h.content.pop(); h.frame.pop(); h.dim.pop(); h.kids.pop()
            key=(w,(x,('new',u,v)))
        nchk+=1
        if sc and (best is None or sc[0]>best[0][0]): best=(sc,key)
    print('round',rnd,'cands',ncand,'checked',nchk,'%.0fs'%(time.time()-t0),'best',None if best is None else ('%.6e'%best[0][0],best[0][1]),flush=True)
    if best is None or best[0][0]<=base[0]+1e-12: break
    (w,(x,y))=best[1]
    if isinstance(y,tuple): y=mk(y[1],y[2])
    h.kids[w]=(x,y); base=hx2.score(h)
    print('  applied',best[1],'-> s9 %.6e Rreused %d Rraw %d'%base,flush=True)
    pickle.dump(h,open(out,'wb'))
print('done s9 %.6e Rreused %d'%(base[0],base[1])); pickle.dump(h,open(out,'wb'))
