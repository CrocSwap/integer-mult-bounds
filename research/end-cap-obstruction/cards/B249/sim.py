import sys,collections,time
from feas import *
lev_empty=B(())
CF=[B(f) for f in w['center_frames']]
cache_j={}
def jn(a,b):
    k=(a,b)
    if k not in cache_j:cache_j[k]=B(list(a)+list(b))
    return cache_j[k]
def simulate(newprog,removed=()):
    """newprog: list of (tag,e). returns (ok,reason,paid Counter,mass_total). lazy frames: F=join(E,cur..)."""
    cur=list(start);paid=collections.Counter();changed=collections.Counter()
    def climb(q,U,where):
        c=cur[q]
        if c==U:return True
        if not nested(c,U):return False
        if not nested(U,end[q]):return False
        d=len(U)-len(c)
        paid[d]+=1;cur[q]=U;return True
    sec=None
    for tag,e in newprog:
        t0=tag[0]
        if t0 in 'PC':continue
        if t0=='L':
            for q in e[1:3] if e[0]=='add' else e[1:2]:
                if end[q]!=FULLB:return False,'L-low-end %s'%(tag,),None,None
            continue
        if t0=='cut':continue
        if t0=='B' and sec!='B':
            sec='B'
            for t in range(v):
                if cur[v+t]!=():return False,'target level y%d'%t,None,None
            for q,U in zip(w['centers'],CF):
                if cur[q]!=U:return False,'center frame %d'%q,None,None
            # center path paid (as audit)
            for q,U in zip(w['centers'],CF):
                served={() for e2 in w['cut'] if e2[2]==q}
                for T in sorted(served,key=lambda x:-len(x)):
                    if T!=U:paid[len(U)-len(T)]+=1
                    U=T
        regs=e[1:3] if e[0]=='add' else e[1:2]
        E=B(e[-1])
        F=E
        for q in regs:
            if not nested(cur[q],F):F=jn(F,cur[q])
        for q in regs:
            if not climb(q,F,tag):return False,'op %s reg %d F dim %d end dim %d cur %d'%(tag,q,len(F),len(end[q]),len(cur[q])),None,None
    for q in range(n):
        if q in removed:continue
        if not climb(q,end[q],'end'):return False,'final',None,None
    mass=sum(d*c for d,c in paid.items())
    return True,'ok',paid,mass
if __name__=='__main__':
    t=time.time()
    r=simulate(prog)
    print(r,time.time()-t)
