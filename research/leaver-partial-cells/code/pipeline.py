import sys,time,pickle,json;sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from pcell import *
from satcell import solve
def frames_after(W,P,n,k1):
    return frames_at(W,P,n,k1+1)
def run_key(d,P,W,n,H0,key,L=20,tl=600,log=print,nh=0):
    K=key_parts(d,W,key);dele=segment(d,W,K);sym,bad=symbolic(W,K,dele,n)
    if bad:return dict(key=key,status='window writes %s'%bad[:3])
    atoms=K['atoms'];Ys=[v+t for t in K['targets']];regs=atoms+Ys;na=len(atoms);ny=len(Ys)
    try:r,c,mu=coeffs(K,sym)
    except AssertionError as e:return dict(key=key,status='coeff %s'%e)
    cur0=frames_at(W,P,n,dele[0]);curE=frames_at(W,P,n,dele[-1]+1)
    # extra bits: equivalence classes of all target hyperplanes on the 9 initial frames
    allY=[y for y in range(v,2*v)]
    pat={}
    for y in allY:
        hp=hyper(P[y-v]);key2=tuple(0 if inside(cur0[x],hp) else 1 for x in regs)
        if any(key2):pat.setdefault(key2,[]).append(y)
    classes=[ys for k2,ys in pat.items()]
    # own bits first (one per circuit target), then other classes
    own=[[y] for y in Ys];others=[ys for ys in classes if not any(y in Ys for y in ys)]
    # keep only classes whose allowance can bind (some final allowance excludes them)
    def okF(F,ys):return all(inside(F,hyper(P[y-v])) for y in ys)
    keep=[ys for ys in others if okF(curE[K['M']],ys) or any(okF(curE[Y],ys) for Y in Ys)]
    bits=own+keep;nb=len(bits)
    def tmask(F):
        m=0
        for b,ys in enumerate(bits):
            if any(not inside(F,hyper(P[y-v])) for y in ys):m|=1<<b
        return m
    T0=[tmask(cur0[x]) for x in regs[:na]]+[0]*nh+[tmask(cur0[x]) for x in Ys]
    # later reads of atoms after the segment -> host candidates
    last=dele[-1];later={x for e in W[last+1:] for x in ((e[1],e[2]) if e[0]=='add' else (e[1],))}
    hosts=[i for i,a in enumerate(atoms) if a==K['M'] or a not in later]
    hostallow=tmask(curE[K['M']])
    Yallow=[tmask(curE[y]) for y in Ys]
    gm=lambda s:sum(1<<j for j in s)
    goalY=[gm(sym[y]) for y in Ys];Mg=gm(sym[K['M']])
    t=time.time()
    st,sol=solve(na,ny,goalY,Mg,hosts,T0,L=L,time_limit=tl,ne=nb-ny,hostallow=hostallow,Yallow=Yallow,nh=nh)
    if not sol:return dict(key=key,status='sat %s'%st,secs=time.time()-t)
    # determine host
    hregs=['NEWH%d'%i for i in range(nh)];regs=atoms+hregs+Ys
    sets=[{i} for i in range(na)]+[set() for _ in hregs]+[set() for _ in Ys]
    for a,b in sol:sets[a]|=sets[b]
    host=next(atoms[h] for h in hosts if sets[h]==set(sym[K['M']]))
    rsol=[(regs[a],regs[b]) for a,b in sol]
    used=sorted({x for g in rsol for x in g if isinstance(x,str)})
    newid={h:n+i for i,h in enumerate(used)}
    rsol=[tuple(newid.get(x,x) for x in g) for g in rsol]
    NW=build(W,K,sym,dele,rsol,host,newh=list(newid.values()))
    badr,fb,dH=check(W,NW,K,host,n+len(used),P,H0)
    return dict(key=key,status='ok' if not badr and not fb else 'check',badrows=badr[:5],frame=fb[:5],dH=dH,fee=fee(dH),
                sol=rsol,host=host,newh=len(used),gates=len(sol),deleted=len(dele),secs=time.time()-t,NW=NW if not badr and not fb else None)
if __name__=='__main__':
    d,P,W,n=load(__import__('os').environ['PC_CENSUS'],__import__('os').environ['PC_PROTO'])
    H0,_=replay(W,P,n)
    keys=[eval(x) for x in sys.argv[1:]]
    for key in keys:
        res=run_key(d,P,W,n,H0,key,nh=int(__import__('os').environ.get('NH','0')))
        print({k:v for k,v in res.items() if k!='NW'},flush=True)
