import re,ast
g={1:1,2:2,3:4,4:8,5:12,6:20,7:36}
rows=[]
for l in open('/tmp/dom_out.txt'):
    if l.startswith('LEFT'):
        t=ast.literal_eval(l[5:].strip()); rows.append(t)
from collections import Counter
c=Counter()
small=[]
for d,s,ws,e in rows:
    big=sorted(ws,reverse=True); comp=big[d-1:]
    cap=sum(g[w] for w in comp)
    c[(d,cap<78)]+=1
    if cap<78 and d>=4: small.append((d,s,ws,cap,comp))
print(sorted(c.items()))
print(len(small))
for x in small[:40]: print(x)
