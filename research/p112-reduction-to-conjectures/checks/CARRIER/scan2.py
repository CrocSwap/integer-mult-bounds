import ast
from collections import Counter
g={1:1,2:2,3:4,4:8,5:12,6:20,7:36}
rows=[ast.literal_eval(l[5:].strip()) for l in open('/tmp/dom_out.txt') if l.startswith('LEFT')]
c=Counter()
for d,s,ws,e in rows:
    if d<4: continue
    big=sorted(ws,reverse=True); cap=sum(g[w] for w in big[d-1:])
    if cap<53: c['univ cap<53']+=1
    elif s==7 and cap<57: c['ClassI s=7 cap<57']+=1
    elif s==7 and cap<78: c['ClassI s=7 root-only (57<=cap<78)']+=1
    elif s==7: c['s=7 cap>=78']+=1
    elif cap<78: c['s<=6 cap<78']+=1
    else: c['s<=6 cap>=78']+=1
print(c, sum(c.values()))
