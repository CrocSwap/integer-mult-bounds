# one-invocation step histogram (x, y, helpers separately) of a bitE8/1 word
import json,gzip,sys
from collections import Counter
def hist(path):
    w=json.load(gzip.open(path)); v,R=w['v'],w['R']; n=2*v+R
    fr=[set(f) for f in w['frames']]
    import os; os.environ['E8COORD']='ham'
    sys.path.insert(0,'.'); import frames as Fm
    mask=[sum(1<<s for s in f) for f in w['frames']]
    dim=[Fm.dim(m) if m else 0 for m in mask]
    cur=list(w['start']); H={'x':Counter(),'y':Counter(),'h':Counter()}
    def kind(r): return 'x' if r<v else ('y' if r<2*v else 'h')
    def go(r,f):
        if cur[r]==f: return
        a,b=mask[cur[r]],mask[f]
        assert a&~b==0,('not nested',r)
        H[kind(r)][dim[f]-dim[cur[r]]]+=1; cur[r]=f
    for ph in ('D','A','B','C'):
        for f,d,srcs in w[ph]:
            for r in [d]+srcs: go(r,f)
    for r in range(n): go(r,w['final'][r])
    return H,R
if __name__=='__main__':
    for p in sys.argv[1:]:
        H,R=hist(p)
        print(p.split('/')[-1],'R',R,{k:dict(sorted(c.items())) for k,c in H.items()},'helper mass',sum(k*z for k,z in H['h'].items()))
