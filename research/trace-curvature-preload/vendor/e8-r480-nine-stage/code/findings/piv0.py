# pivot-class structure of a bitE8 word: first frames, resp vectors, per-line classes
import json,gzip,sys
from collections import Counter
W=json.load(gzip.open(sys.argv[1],'rt')); V=W['v']; R=W['R']; n=2*V+R
fr=[set(x) for x in W['frames']]
first={}
occ={h:[] for h in range(2*V,n)}
for ph in ('D','A','B','C'):
    for f,d,ss in W[ph]:
        for r in [d]+ss:
            if r>=2*V and fr[f]: occ[r].append(f)
for h in range(2*V,n): first[h]=occ[h][0]
resp={h:0 for h in range(2*V,n)}
for f,t,ss in W['D']:
    assert not fr[f]
    for s in ss: resp[s]^=1<<(t-V)
ret=set(W['ret'])
def rank(vs):
    b=[]
    for v in vs:
        for x in b: v=min(v,v^x)
        if v: b.append(v)
    return len(b)
print('first-frame dims',Counter(len(fr[first[h]]) for h in range(2*V,n)),'resp==0:',sum(1 for h in resp if resp[h]==0 and h not in ret))
cls={l:[h for h in range(2*V,n) if h not in ret and l in fr[first[h]]] for l in range(V)}
nul={l:len(c)-rank([resp[h] for h in c]) for l,c in cls.items()}
print('class sizes',Counter(len(c) for c in cls.values()),'class nullity',Counter(nul.values()))
print('coord lines 0-7 sizes',[len(cls[l]) for l in range(8)],'nullity',[nul[l] for l in range(8)])
print('sum nullity all',sum(nul.values()),'coord',sum(nul[l] for l in range(8)))
C=[h for h in range(2*V,n) if h not in ret]; print('|C|',len(C),'rank resp(C)',rank([resp[h] for h in C]),'ceiling',len(C)-rank([resp[h] for h in C]))
json.dump(dict(first={h:sorted(fr[first[h]]) for h in first},resp={h:resp[h] for h in resp},ret=sorted(ret)),open(sys.argv[2],'w'))
