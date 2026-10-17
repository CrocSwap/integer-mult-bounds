# GRRC with oracle answered by impl B on demand (timeout => conservative 'coverable'); records which negative facts were used.
import grrc, json, subprocess, sys
from qB import qB
TYPES=[('D7',78),('E6A1',83),('E6',84),('A7',92),('D5A2',97),('A1A6',98),('A4A3',104),('A1A2A4',106)]
LOG=json.load(open('Blog.json')) if __import__('os').path.exists('Blog.json') else {}
TO=int(sys.argv[1]) if len(sys.argv)>1 else 30
def runB(t,M):
    k=t+':'+','.join(map(str,M))
    if k not in LOG:
        try: out=qB(t,list(M),timeout=TO)
        except subprocess.TimeoutExpired: out='TIMEOUT'
        LOG[k]=out.split(' nodes')[0][:6]; json.dump(LOG,open('Blog.json','w'))
    return LOG[k]
used=set()
def q(kind,M):
    M=tuple(sorted(M,reverse=True)); cap=sum(grrc.g[w] for w in M)
    if cap<grrc.MINOFF[kind]: return False
    if kind=='root':
        if cap>75: return True
        r=runB('E7',M)
        if r=='NONE': used.add('E7:'+','.join(map(str,M))); return False
        return True
    if cap>96: return True
    for t,o in TYPES:
        if o<=cap:
            r=runB(t,M)
            if r!='NONE': return True
    for t,o in TYPES:
        if o<=cap: used.add(t+':'+','.join(map(str,M)))
    return False
grrc.q=q
res={}
for r,(d,ws,s) in sorted(grrc.ROWS.items()):
    out=[(t,grrc.kill(w2,dd,ex)) for t,w2,dd,ex in grrc.scen(ws,d,s)]
    res[r]=out
    print(r,'KILLED' if all(k for _,k in out) else 'open', [(t,k) for t,k in out], flush=True)
json.dump({'res':res,'used':sorted(used)},open('fill_res.json','w'),indent=0)
