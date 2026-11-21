# independent check of cover completeness for cx4: ALL rectangles Dset x Sset (subsets of readers x gathers), no flag theory
import itertools
from common import *
exec(open('cx4.py').read().split("print('labels'")[0])
odd=[(t,p) for t in range(n) for p in range(n) if Qm[t][p]]
nz=[(t,p) for (t,p) in odd if T[t][p]]
rd=sorted({t for t,p in nz}); gt=sorted({p for t,p in nz})
rects=[]
for r1 in range(1,len(rd)+1):
  for Ds in itertools.combinations(rd,r1):
    for r2 in range(1,len(gt)+1):
      for Ss in itertools.combinations(gt,r2):
        pr=price([labs[t] for t in Ds],[labs[p] for p in Ss])
        if 1<=pr<=3: rects.append((frozenset(Ds),frozenset(Ss),pr))
print('rects price<=3:',len(rects))
cells=frozenset(nz)
cv=[frozenset(c for c in cells if c[0] in R[0] and c[1] in R[1]) for R in rects]
found=[]
def rec(chosen,covered,budget):
    if covered==cells: found.append(chosen); return
    c=min(cells-covered)
    for i in range(len(rects)):
        if rects[i][2]<=budget and c in cv[i] and (not chosen or i>=0):
            rec(chosen+[i],covered|cv[i],budget-rects[i][2])
rec([],frozenset(),3)
shapes=set(tuple(sorted(rects[i][2] for i in f)) for f in found)
print('covers found',len(found),'price shapes',shapes)
# every cover contains a rectangle containing the fully-odd 2x2 block {2,4}x{7,14}?
blk={(labs.index(a),labs.index(b)) for a in (2,4) for b in (7,14)}
print('block T',[[T[labs.index(a)][labs.index(b)] for b in (7,14)] for a in (2,4)], 'all odd',all(Qm[t][p] for t,p in blk))
print('covers where some single rect covers the whole block and is the ONLY rect meeting it:',
      sum(1 for f in found if sum(1 for i in f if cv[i]&blk)==1))
print('all covers have exactly one rect meeting block?', all(sum(1 for i in f if cv[i]&blk)==1 for f in found))
