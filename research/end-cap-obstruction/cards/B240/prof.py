"""prof.py WORD.json.gz -> local paid profile + width inventory (frame-only replica of audit_local.py:114-146; no scalar check)."""
import gzip,json,sys
from collections import Counter
def basis(vs):
    piv={}
    for a in vs:
        while a:
            bit=a.bit_length()-1
            if bit in piv:a^=piv[bit]
            else:piv[bit]=a;break
    for k in sorted(piv):
        for j in piv:
            if j>k and piv[j]>>k&1:piv[j]^=piv[k]
    return tuple(piv[k] for k in sorted(piv,reverse=True))
def regs(e):return e[1:3] if e[0]=='add' else e[1:2]
def profile(w,trace=None):
    v,h,R=w['report']['v'],w['report']['h'],w['report']['R'];n=2*v+R
    full=basis([1<<i for i in range(h)])
    end=[full]*v+[basis([x for x in range(1,1<<h) if (x&p).bit_count()%2==0]) for p in w['ports']]+[full]*R
    for q,U in w.get('helper_final',{}).items():end[int(q)]=basis(U)
    start=[(p,) for p in w['ports']]+[()]*(v+R)
    for q,U in w.get('start_extra',{}).items():start[int(q)]=basis(U)
    cur=start.copy();paid=Counter();early=w.get('early_cleanup',[])
    tail=[w['cleanup'][i][:-1]+[U] for i,U in early]
    def climb(q,U,tag):
        U=basis(U);assert basis(cur[q]+U)==U,('nonmonotone',q,tag)
        d=len(U)-len(cur[q])
        if d:
            paid[d]+=1
            if trace is not None:trace.append((q,tag,len(cur[q]),len(U)))
        cur[q]=U
    for section in ('A','B'):
        if section=='B':
            lev={int(t):basis(U) for t,U in w.get('target_levels',{}).items()}
            for q,U in zip(w['centers'],w['center_frames']):
                U=basis(U);served={lev.get(e[1]-v,()) for e in w['cut'] if e[2]==q}
                for T in sorted(served,key=lambda x:-len(x)):
                    if T!=U:paid[len(U)-len(T)]+=1
                    U=T
        for i,e in enumerate(w[section]):
            for q in regs(e):climb(q,e[-1],(section,i))
    for i,e in enumerate(tail):
        for q in regs(e):climb(q,e[-1],('T',i))
    for q,U in enumerate(end):climb(q,U,('E',))
    inv=Counter(len(end[q])-len(start[q]) for q in range(2*v,n))
    return dict(sorted(paid.items())),dict(sorted(inv.items()))
if __name__=='__main__':
    w=json.loads(gzip.decompress(open(sys.argv[1],'rb').read()))
    p,i=profile(w);print('profile',p,'report',w['report']['local_profile']);print('inventory',i)
