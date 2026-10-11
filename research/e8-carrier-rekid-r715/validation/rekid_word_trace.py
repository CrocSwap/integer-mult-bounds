"""word-level realisation of the rekid'd rules: replay D then A of the emitted word tracking x-support masks per register; for each rekid rule w find gates that produce content[w] from operand registers holding content[x], content[y] (or an equivalent decomposition); report frame at the gate."""
import sys,gzip,json
from loadh import loadh
hier,wordp,basep=sys.argv[1:4]
h=loadh(hier); base=loadh(basep)
word=json.load(gzip.open(wordp,'rt') if wordp.endswith('.gz') else open(wordp))
v=120; R=word['R']; nreg=2*v+R
sup=[1<<i if i<v else 0 for i in range(nreg)]
fr=word['frames']
def fmask(f): return sum(1<<s for s in f)
gates=[]
for ph in ('D','A'):
    for k,(f,d,srcs) in enumerate(word[ph]):
        before=[sup[d]]+[sup[s] for s in srcs]
        for s in srcs: sup[d]^=sup[s]
        gates.append((ph,k,f,d,srcs,before,sup[d]))
rk=[w for w in range(v,len(h.kids)) if base.kids[w]!=h.kids[w]]
bycont={}
for g in gates: bycont.setdefault(g[6],[]).append(g)
for w in rk:
    x,y=h.kids[w]; cw,cx,cy=h.content[w],h.content[x],h.content[y]
    prod=bycont.get(cw,[])
    exact=[g for g in prod if sorted(g[5][1:])==sorted([cx,cy]) and g[5][0]==0 or (set(g[5][1:])=={cx} and g[5][0]==cy) or (set(g[5][1:])=={cy} and g[5][0]==cx)]
    print('w=%d: %d gate(s) yield content[w]; %d of them compute exactly x(+)y with x,y at the new kids; x holds=%d y holds=%d'%(w,len(prod),len(exact),len(bycont.get(cx,[])),len(bycont.get(cy,[]))), end='')
    if exact:
        g=exact[0]; print('  e.g. %s#%d frame-dim %d dest %d srcs %s'%(g[0],g[1],len(fr[g[2]]) and __import__('builtins').len(fr[g[2]]),g[3],g[4]))
    else: print('  (no verbatim gate; reuse/elimination re-routed; contents seen at gates: %s)'%[(g[0],g[1],[bin(c).count('1') for c in g[5]]) for g in prod[:2]])
