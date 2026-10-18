"""ev.py: fast frame-profile evaluator for tail programs (lazy frames) on top of the post-B snapshot of #1018."""
import gzip,json,collections,sys
import prof,price
from fractions import Fraction as F
B=prof.basis;regs=prof.regs
W=__import__('os').environ['EO_ROOT']+'/inputs/words/w1018.json.gz'
w=json.loads(gzip.decompress(open(W,'rb').read()))
v=112;R=w['report']['R'];n=2*v+R;h=9
full=B([1<<i for i in range(h)])
end=[full]*v+[B([x for x in range(1,1<<h) if (x&p).bit_count()%2==0]) for p in w['ports']]+[full]*R
for q,U in w['helper_final'].items():end[int(q)]=B(U)
start=[(p,) for p in w['ports']]+[()]*(v+R)
for q,U in w['start_extra'].items():start[int(q)]=B(U)
# post-B snapshot with paid so far
def snapshot():
    cur=start.copy();paid=collections.Counter()
    def climb(q,U):
        U=B(U);d=len(U)-len(cur[q])
        if d:paid[d]+=1
        cur[q]=U
    for sec in('A','B'):
        if sec=='B':
            lev={int(t):B(U) for t,U in w['target_levels'].items()}
            for q,U in zip(w['centers'],w['center_frames']):
                U=B(U);served={lev.get(e[1]-v,()) for e in w['cut'] if e[2]==q}
                for T in sorted(served,key=lambda x:-len(x)):
                    if T!=U:paid[len(U)-len(T)]+=1
                    U=T
        for e in w[sec]:
            for q in regs(e):climb(q,e[-1])
    return cur,paid
CUR0,PAID0=snapshot()
early=w['early_cleanup']
TAIL0=[w['cleanup'][i][:-1] for i,U in early]   # ops without frame
REST=[e for i,e in enumerate(w['cleanup']) if i not in {i for i,_ in early}]
def profile(tail,frames=None):
    """tail: list of ops (no frame). lazy frames unless frames[k] given (list of tuples). returns (profile dict or None, finalframes)"""
    cur=CUR0.copy();paid=collections.Counter(PAID0);fr=[]
    for k,e in enumerate(tail):
        rs=regs(e);U=B(frames[k]) if frames and frames[k] is not None else ()
        for q in rs:U=B(U+cur[q])
        for q in rs:
            d=len(U)-len(cur[q])
            if d:paid[d]+=1
            cur[q]=U
        fr.append(U)
    for q in range(n):
        if B(cur[q]+end[q])!=end[q]:return None,fr
        d=len(end[q])-len(cur[q])
        if d:paid[d]+=1
    return {str(k):c for k,c in sorted(paid.items())},fr
_cache={}
def kappa(p):
    k=json.dumps(p,sort_keys=True)
    if k not in _cache:_cache[k]=F(price.kappa(p))
    return _cache[k]
if __name__=='__main__':
    p,fr=profile(TAIL0);print(p, w['report']['local_profile'])
    print(float(kappa(p)))
    # frames equal original?
    print(sum(1 for k,(i,U) in enumerate(early) if B(U)!=fr[k]),'non-lazy gates')
