"""Check the complete retained F-star witness data without the search code."""
import json
from pathlib import Path
p=Path(__file__).with_name('combined-2335-witnesses.json')
d=json.loads(p.read_text())
assert len(d['witnesses'])==196
for w in d['witnesses']:
 P,Q,labels,subset,order=(w[k] for k in ('P','Q','labels','subset','order'))
 v=len(labels)
 assert 4<=v<=12 and len(P)==len(Q)==3 and all(len(a)==v for a in P+Q)
 assert len(subset)==len(set(subset))==len(order)==len(set(order)) and set(subset)==set(order)
 assert len(subset)>=2*v//3 and all(0<=x<v for x in subset)
 for i,(a,b) in enumerate(labels):
  assert 0<=a<8 and 0<=b<8 and sum(P[j][i]*Q[j][i] for j in range(3))!=0
  assert all(not(a>>j&1)or P[j][i]!=0 for j in range(3))
  assert all(not(b>>j&1)or Q[j][i]!=0 for j in range(3))
 for i,x in enumerate(order):
  assert (labels[x][0]&labels[x][1]).bit_count()%2==1
  for y in order[i+1:]:
   if sum(P[j][x]*Q[j][y] for j in range(3))==0:assert (labels[x][0]&labels[y][1]).bit_count()%2==0
print('PASS_ALL_196_FSTAR_WITNESSES')
