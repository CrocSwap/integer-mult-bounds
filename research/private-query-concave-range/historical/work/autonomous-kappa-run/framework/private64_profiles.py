#!/usr/bin/env python3
"""Enumerate scalar-query rank multiplicities with a separate recursion."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
import json
from pathlib import Path
import sys
import time

if not __debug__:
    raise SystemExit('Run with assertions enabled.')
root,out=map(lambda s:Path(s).resolve(),sys.argv[1:3]);started=time.monotonic()
geometry_path=root/'framework/PRIVATE64-GEOMETRY.json';geometry=json.loads(geometry_path.read_text())
capacity=geometry['analytic_source_capacities'];weights=[0]+geometry['generalized_support_bounds']
counts=Counter();survivors=[];multiplicity=[0]*10
def choose(n,k):return comb(n,k)if n>=k>=0 else 0
concavity_checks=0
for m in range(1,64):
    for k in range(1,m+1):
        coverage=[choose(m,k)-choose(m-x,k)for x in range(m+1)]
        increments=[b-a for a,b in zip(coverage,coverage[1:])]
        assert all(x>=y>=0 for x,y in zip(increments,increments[1:]));concavity_checks+=1
assert Q(2)*(1-Q(comb(2,2),comb(4,2)))>1
def screen():
    counts['all']+=1;n=sum(multiplicity)
    if n<8:counts['row_rank']+=1;return
    incidence=sum(capacity[r]*multiplicity[r]for r in range(1,10))
    if incidence<224-n:counts['column_incidence']+=1;return
    parts=tuple(r for r in range(1,10)for _ in range(multiplicity[r]))
    prefix=[0]
    for r in parts:prefix.append(prefix[-1]+capacity[r])
    for d in range(1,9):
        k=n-8+d
        if prefix[k]<weights[d]:counts['generalized_support']+=1;return
    for d in range(1,9):
        k=n-8+d
        for m in range(k+1,n+1):
            t,remainder=divmod(prefix[m],112);den=choose(m,k)
            covered=(112-remainder)*(den-choose(m-t,k))+remainder*(den-choose(m-t-1,k))
            if covered<weights[d]*den:counts['average_union']+=1;return
    if n==9 and parts[0]<=6 and parts[1]<=7:
        assert capacity[parts[0]]+capacity[parts[1]]<=56
        assert 20+32<53;counts['short_root_pair']+=1;return
    survivors.append(parts)
def visit(rank,remaining):
    if rank==0:screen();return
    for number in range(remaining//rank+1):
        multiplicity[rank]=number;visit(rank-1,remaining-number*rank)
    multiplicity[rank]=0
visit(9,63)
assert counts['all']==1735600
assert set(survivors)=={(7,)*9,(1,6)+(7,)*8}
assert counts['all']==sum(v for k,v in counts.items()if k!='all')+len(survivors)
reference_path=root/'framework/GENERALIZED-QUERY-PROFILES.json';reference=json.loads(reference_path.read_text())
assert dict(counts)==reference['profile_counts']
report=dict(status='PASS_INDEPENDENT_PRIVATE64_MULTIPLICITY_RECURSION',budget=63,profile_counts=dict(counts),
    survivors=survivors,discrete_concavity_cases=concavity_checks,seconds=time.monotonic()-started,
    source_sha256={str(p):sha256(p.read_bytes()).hexdigest()for p in(geometry_path,reference_path)},
    scope='Separate rank-multiplicity recursion. The generalized support and balanced-incidence average bounds leave two profiles. Their separate geometric closures and the current scalar-private contract are required before claiming optimum64.')
out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],report['seconds'])
