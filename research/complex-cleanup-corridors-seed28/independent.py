"""Backward read epochs and literal rational columns; no verifier imports."""
from fractions import Fraction
def barriers(ops):
 # Moving backwards, an explicit source read changes that register's epoch.
 # Two same-operand additions can be target-unread only in the same epoch.
 epoch={};seen={};all_pairs={};barriers={};opportunities=[]
 for i in range(len(ops)-1,-1,-1):
  e=ops[i]
  if e[0]!='add':continue
  t,s=e[1:3];key=(t,s);state=(t,s,epoch.get(t,0))
  if state in seen:opportunities.append([i,seen[state]])
  seen[state]=i
  if key in all_pairs:
   j=all_pairs[key]
   # Last explicit read before that endpoint, already remembered by the scan.
   if t in barriers:barriers_for_pair=barriers[t]
   else:barriers_for_pair=None
   yield (i,j,barriers_for_pair)
  all_pairs[key]=i
  epoch[s]=epoch.get(s,0)+1;barriers[s]=i
 if opportunities:raise ValueError('target-unread corridor '+str(opportunities[:4]))
def replay(ops,n):
 columns=[]
 for j in range(n):
  x=[Fraction(int(i==j)) for i in range(n)]
  for e in ops:
   if e[0]=='add':x[e[1]]+=Fraction(e[3],e[4])*x[e[2]]
   elif e[0]=='scale':x[e[1]]*=Fraction(e[2],e[3])
   else:raise ValueError('bad primitive')
  columns.append(x)
 return columns
