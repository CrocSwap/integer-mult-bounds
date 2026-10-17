import re,ast
from cov3 import *
import cov3
SRCH2='../SC-B2/srch2'
def load_gens(fn):
    txt=open(fn).read()
    txt=txt[txt.rindex('[ [ '):] if '[ [ ' in txt else txt
    txt=txt.replace('\\\n','')
    gens=ast.literal_eval(re.sub(r'\s+',' ',txt.strip()))
    return [[x-1 for x in p] for p in gens]
def cover_set4(T,ws,gens,verbose=False,tmo=300):
    T=list(T); ws=sorted(ws,reverse=True)
    capall=sum(g[w] for w in ws)
    if len(T)>capall: return False
    big=[w for w in ws if w>=5]; small=[w for w in ws if w<5]
    capsmall=sum(g[w] for w in small); smallds=tuple(sorted(small,reverse=True))
    slack=capall-len(T)
    tg=Tgt(T); pos={t:i for i,t in enumerate(T)}
    Tset=set(T)
    for p in gens: assert all((p[t] in Tset) for t in T)
    d=tempfile.mkdtemp()
    files={};lists={}
    for w in set(big):
        L=max(1,g[w]-slack)
        lst=tg.level(w,L); lists[w]=lst
        if verbose: print(' level',w,'L',L,len(lst),flush=True)
        fn=os.path.join(d,'c%d.txt'%w)
        with open(fn,'w') as f:
            for m in lst: f.write("%d %d\n"%split(m))
        files[w]=fn
    w0=big[0]; lst=lists[w0]; idx={m:i for i,m in enumerate(lst)}
    # orbit reps via union-find
    par=list(range(len(lst)))
    def find(x):
        while par[x]!=x:
            par[x]=par[par[x]]; x=par[x]
        return x
    permT=[[pos[p[t]] for t in T] for p in gens]
    for pt in permT:
        for i,m in enumerate(lst):
            m2=0
            for b in bits(m): m2|=1<<pt[b]
            j=idx[m2]   # KeyError if not closed
            a,b2=find(i),find(j)
            if a!=b2: par[a]=b2
    reps=sorted({find(i) for i in range(len(lst))})
    if verbose: print(' orbits of first-level flats',len(reps),flush=True)
    ff=os.path.join(d,'first.txt'); open(ff,'w').write("\n".join(map(str,reps)))
    args=[SRCH2,str(len(T)),str(capsmall),str(len(big))]
    for w in big: args+=[str(w),files[w]]
    args.append(ff)
    t0=time.time()
    try: r=subprocess.run(args,capture_output=True,text=True,timeout=tmo)
    except subprocess.TimeoutExpired:
        r=None
    if r is None:
        res=None
    else:
        if verbose: print(' srch',r.stderr.strip(),round(time.time()-t0,1),flush=True)
        res=False
        for ln in r.stdout.splitlines():
            if ln=='FULL': res=True;break
            lo,hi=map(int,ln.split()); m=lo|(hi<<64)
            if carcov.can_cover(tuple(lab[tg.T[i]] for i in bits(m)),smallds,0,{}): res=True;break
    for fn in os.listdir(d): os.remove(os.path.join(d,fn))
    os.rmdir(d)
    return res
