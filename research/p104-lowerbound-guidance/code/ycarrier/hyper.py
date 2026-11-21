import sys; from collections import Counter
sys.path.insert(0,'<word-rung-package>/tools')
import pricekit as pk
P=pk.load('<word-rung-package>/data/t7669.json.gz')['ports']; PS=set(P)
dot=lambda a,b: bin(a&b).count('1')&1
c=Counter()
for v in range(1,512):
    k=sum(1 for p in P if not dot(v,p)); c[(('port' if v in PS else 'odd-nonport' if bin(v).count('1')%2 else 'even'),k)]+=1
for k,v in sorted(c.items()): print(k,v)
