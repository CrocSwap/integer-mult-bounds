# which (h, t) have rank lab(Off(h)\{t}) <= 8 with |Off(h)| <= 65 (only f/root targets qualify)?  expect: h=f_i (any t), h=root t (t=r).
import sys
from base import *
T=[list(map(int,l.split())) for l in open('targets.txt') if l.strip()]
bad=0; fr=0; rt=0
for off in T:
    r=f2rank([LAB[t] for t in off])
    if r<=8: fr+=1; continue
    for t in off:
        if f2rank([LAB[u] for u in off if u!=t])<=8:
            # check t is the root of this target: Off(r)=N(r)∪{r} => target size 53 and t has max |<c_t,.>|? record
            if len(off)==53: rt+=1
            else: bad+=1
print('rank<=8 targets (frame):',fr,' root-coloop pairs:',rt,' other:',bad)
