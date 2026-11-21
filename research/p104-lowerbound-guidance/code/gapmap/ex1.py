import sys; sys.path.insert(0,'<word-rung-package>/tools')
import pricekit as pk
from collections import Counter
W=pk.load('<word-rung-package>/data/t7669.json.gz')
print(W['schema'], list(W['hosted'].keys()), W['public'], W['owned_fields'])
n=W['public']; P=W['program']
print(Counter(e[0] for e in P))
print(P[:6])
dim=[len(f) for f in W['frames']]
own=[e for e in P if e[1]>=n]
print('owned ops',Counter(e[0] for e in own))
print(len(W['hosted']['Dports']), len(W['hosted']['X2']),len(W['hosted']['Y2']), len(W['live']))
print(sorted(Counter(dim).items()))
print(sorted(Counter(dim[f] for f in W['initial']).items()), sorted(Counter(dim[f] for f in W['final']).items()))
