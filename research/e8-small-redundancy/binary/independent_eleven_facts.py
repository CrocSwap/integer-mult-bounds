"""Check the extra finite facts for the eleven-centre proof."""
from standard_e8 import *
from collections import Counter
assert all(dot(q,q)==8 for q in roots)
assert {dot(q,r) for i,q in enumerate(roots) for r in roots[i+1:]} <= {-4,0,4}
n=nullvec(a[:7]);H=[j for j,r in enumerate(roots) if not dot(r,n)]
O=[j for j in range(120) if j not in H]
nr=next(j for j in O if all(not dot(roots[j],roots[k]) for k in H))
outside_hist=Counter(sum(c>>j&1 for j in O) for c in C)
assert outside_hist=={0:1,1:1,24:63,25:63,28:128,29:128,32:63,33:63,56:1,57:1}
assert {c for c in C if sum(c>>j&1 for j in O)<=13}=={0,K[nr]}
e7=[]
for d in range(7):
 rows=[a[j] for j in range(7) if j!=d]
 J=[j for j in H if rank_mod(rows+[roots[j]])==6]
 assert rank_mod([roots[j] for j in H if j not in J])==7
 e7.append({'deleted':d,'inside_count':len(J),'complement_rank':7})
assert max(x['inside_count'] for x in e7)==36
out={'verified':True,'root_squared_norm':8,'distinct_root_products':[-4,0,4],'outside_weight_histogram':dict(sorted(outside_hist.items())),'e7_rank_six_flats':e7}
Path(__file__).with_name('independent-eleven-facts.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
