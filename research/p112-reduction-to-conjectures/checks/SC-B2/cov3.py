import sys,os,subprocess,tempfile,time
from cov2 import *
TMO=400
SRCH='../SC-B2/srch'
def cover_set3(T,ws,verbose=False):
    T=list(T); ws=sorted(ws,reverse=True)
    capall=sum(g[w] for w in ws)
    if len(T)>capall: return False
    big=[w for w in ws if w>=5]; small=[w for w in ws if w<5]
    capsmall=sum(g[w] for w in small); smallds=tuple(sorted(small,reverse=True))
    slack=capall-len(T)
    tg=Tgt(T)
    d=tempfile.mkdtemp()
    files={}
    for w in set(big):
        L=max(1,g[w]-slack)
        lst=tg.level(w,L)
        if verbose: print(' level',w,'L',L,len(lst),flush=True)
        fn=os.path.join(d,'c%d.txt'%w)
        with open(fn,'w') as f:
            for m in lst: f.write("%d %d\n"%split(m))
        files[w]=fn
    if not big:
        raise SystemExit('no big pieces')
    args=[SRCH,str(len(T)),str(capsmall),str(len(big))]
    for w in big: args+=[str(w),files[w]]
    t0=time.time()
    try: r=subprocess.run(args,capture_output=True,text=True,timeout=TMO)
    except subprocess.TimeoutExpired:
        for fn in files.values(): os.remove(fn)
        os.rmdir(d); return None
    if verbose: print(' srch',r.stderr.strip(),round(time.time()-t0,1),flush=True)
    res=False; seen=0
    for ln in r.stdout.splitlines():
        if ln=='FULL': res=True;break
        lo,hi=map(int,ln.split()); m=lo|(hi<<64); seen+=1
        if carcov.can_cover(tuple(lab[tg.T[i]] for i in bits(m)),smallds,0,{}): res=True;break
    for fn in files.values(): os.remove(fn)
    os.rmdir(d)
    if verbose: print(' leaves checked',seen)
    return res
