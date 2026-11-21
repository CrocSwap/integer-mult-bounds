import sys
sys.path.insert(0,'<word-rung-package>/tools')
import pricekit as pk
from collections import Counter
W=pk.load('<word-rung-package>/data/t7669.json.gz')
print([k for k in W.keys()])
n=W['public']; live=W['live']; H=W['hosted']
mains=set(live)|{r+112 for r in live}|set(H['X2'])|set(H['Y2'])
res=pk.verify(W) if hasattr(pk,'verify') else None
R=pk.replay(W); rows=R['rows']; print(R['ok'],R['problems'][:3])
hel=[r for r in range(n) if r not in mains]
c=Counter()
for r in hel:
    row=rows[r]; c['self1' if row.get(r)==1 else 'noself']+=1
    c['clean' if set(row)=={r} else 'junk']+=1
print('helpers',len(hel),dict(c))
# what symbols in helper junk
jk=Counter()
for r in hel:
    for k in rows[r]:
        if k!=r: jk['main' if k in mains else ('helper' if k<n else 'owned')]+=1
print('junk symbol kinds',dict(jk))
