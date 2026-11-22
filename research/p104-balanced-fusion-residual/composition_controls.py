#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent low-pivot diagonal and dependent-residual mutation control."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent

def low_rank(rows):
    pivots={}
    for row in rows:
        while row:
            bit=row & -row
            if bit not in pivots:
                pivots[bit]=row
                break
            row ^= pivots[bit]
    return len(pivots)

def main():
    rows=json.loads((HERE/'caller_dual_check.json').read_text())['placement_records']
    assert len(rows)==36
    matrices=[]; diagonals=[]
    for r in rows:
        b,s=r['lane_base'],r['stage']; assert b in (0,19) and 1<=s<=18
        assert r['source_roles']==r['affected_output_roles']==[b,b+s]
        assert r['unique_diagonal']==b+s
        diagonals.append(r['unique_diagonal'])
        matrices.append(sum(1<<(38*i+j) for i in (b,b+s) for j in (b,b+s)))
    assert len(set(diagonals))==36 and low_rank(matrices)==36
    # Replacing an error matrix by a duplicate manufactures a real dependence.
    damaged=matrices.copy();damaged[-1]=damaged[0]
    assert damaged[0]^damaged[-1]==0 and low_rank(damaged)==35
    try:assert low_rank(damaged)==36
    except AssertionError:pass
    else:raise AssertionError('a dependent residual set was accepted')
    print(json.dumps({'verified_distinct_diagonals':36,'independent_matrix_rank':36,
       'duplicate_error_matrix_rank':35,'dependent_residual_mutation_rejected':True},indent=2,sort_keys=True))

if __name__=='__main__':main()
