#!/usr/bin/env python3
"""Compare integer recurrence to a separate literal Fraction implementation."""
from fractions import Fraction as Q
from pathlib import Path
from random import Random
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from height_exact import CASES,GRID,BOOKED,ordinary

samples=[1,2,3,1000,10**6,10**9,10**12,2*10**12]
for _,_,h in CASES:
    samples += [h-2,h-1,h,h+1,h+2]
rng=Random(461)
samples += [rng.randrange(1,2*10**12+1) for _ in range(150)]
count=0
for depth,C,_ in CASES:
    c=Q(C,2**depth)
    for h in samples:
        rows=ordinary(depth,C,h)
        previous=Q()
        for i,row in enumerate(rows):
            limit=min(Q(39,10000),(249*(c-Q(11,8*h*16**i))+previous)/250)
            rate=Q(BOOKED,GRID) if i==6 else Q(int(limit*GRID)-1,GRID)
            assert row['rate_tick']==rate*GRID
            assert Q(row['margin'])==limit-rate
            assert row['strict']==(previous<rate<limit)
            previous=rate
            count+=1
print('PASS_INTEGER_RECURRENCE_VS_FRACTION',count,'stage comparisons')
