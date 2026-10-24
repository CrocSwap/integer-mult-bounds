"""Compute the exact rank of the additive correction to the disjointness map."""
import json
from pathlib import Path


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length()-1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


rows = []
for h in range(2,12):
    masks = list(range(1,2**h-1))
    matrix = [sum(1<<j for j,v in enumerate(masks)
                  if (u==v) ^ (u&v==0)) for u in masks]
    actual = rank(matrix)
    formula = (2**(h+1)-2*(-1)**h-3)//3
    assert actual == formula
    deficit = 2*len(masks)-3*actual
    assert deficit == 2*(-1)**h-1
    rows.append(dict(h=h,ports=len(masks),correction_rank=actual,
                     maximum_deficit_with_rank_one_centres=deficit))
result = dict(status='PASS_EXACT_F2_CORRECTOR_RANK',
              scope='PR172 literal disjointness endpoint, repaired by an additive sum of scalar rank-one copied centres.',
              general_formula='rank(I+A_h)=(2^(h+1)-2*(-1)^h-3)/3 for h>=2',
              proof='PROOF.txt',rows=rows)
Path(__file__).with_name('ZETA-CORRECTOR-CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
