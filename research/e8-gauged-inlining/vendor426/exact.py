"""Exact helpers for the changed finite witness; Apache-2.0, Codex assistance."""
import gzip,json,pathlib
from collections import Counter
from fractions import Fraction as Q
def read(path):
    p=pathlib.Path(path);raw=p.read_bytes();return json.loads(gzip.decompress(raw)if p.suffix=='.gz'else raw)
def rawmap(c):
    n=2*c['v']+c['R'];rows=[{i:Q(1)}for i in range(n)]
    def add(t,s,q):
        for k,v in list(s.items()):
            z=rows[t].get(k,Q(0))+q*v
            if z:rows[t][k]=z
            else:rows[t].pop(k,None)
    def run(gs):
        for g in gs:
            for r,a,b in g[3]:
                t,s=(r,g[2])if g[0]=='out'else(g[2],r);add(t,rows[s],Q(a,b))
    run(c['A']);tot={k:dict(rows[r])for k,r,f in c['ret']}
    for t,es in enumerate(c['scat']['table']):
        for k,a,b in es:add(c['v']+t,tot[k],Q(a,b))
    run(c['B']);return rows,tot
def rehist(c):
    from vendor.source376.two_alias import inside
    dim=list(map(len,c['frames']));cur=c['start'].copy();H={k:Counter()for k in'xysc'};v=c['v']
    def climb(r,f):
        assert inside(tuple(c['frames'][cur[r]]),tuple(c['frames'][f])),(r,cur[r],f)
        d=dim[f]-dim[cur[r]]
        if d:H['x'if r<v else'y'if r<2*v else's'][d]+=1
        cur[r]=f
    for phase in('A','B'):
        if phase=='B':
            for k,r,f in c['ret']:assert cur[r]==f;H['c'][dim[f]]+=1
        for g in c[phase]:
            for r in[g[2]]+[t for t,a,b in g[3]]+(g[4]if g[0]=='out'else[]):climb(r,g[1])
    for r,f in enumerate(c['final']):climb(r,f)
    c['blocks']={k:{str(r):n for r,n in sorted(h.items())}for k,h in H.items()};c['N']=sum(r*n for h in H.values()for r,n in h.items());return c
