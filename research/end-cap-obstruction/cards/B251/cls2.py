import sys,pickle,collections
sys.path.insert(0,__import__('os').environ['EO_ROOT']+'/cards/B251')
from feas import *
inc=pickle.load(open('inc.pkl','rb'));sel,ub=pickle.load(open('mis_h.pkl','rb'))
def members(b):
    s={0}
    for x in b:s|={y^x for y in s}
    m=0
    for y in s:m|=1<<y
    return m
def lay(h):
    return ('cold0' if len(start[h])==0 else 'enter%d'%len(start[h]))+('/endFULL' if end[h]==FULLB else '/endU')
H=[h for h in range(224,704) if h not in set(w['centers'])]
types=collections.Counter(lay(h) for h in H);print(types)
sm={h:members(start[h]) for h in H};em={h:members(end[h]) for h in H}
host=[]
for i,x in enumerate(inc):
    ts=set()
    for h in H:
        if not (sm[h]&~x['cap']) and not (x['Lm']&~em[h]):ts.add(lay(h))
    host.append(frozenset(ts))
pickle.dump(host,open('host.pkl','wb'))
print('hostable-type sets over clique members:',collections.Counter(tuple(sorted(host[i])) for i in sel))
print('actual types of carriers in clique:',collections.Counter(lay(c) for i in sel for c in inc[i]['car']))
allh=[i for i,x in enumerate(inc) if x['nh']==0]
print('hostable-type sets over all nh=0 incarnations:',collections.Counter(len(host[i]) for i in allh))
print('actual types of carriers of nh=0 incarnations:',collections.Counter(lay(c) for i in allh for c in inc[i]['car'] if c>=224))
