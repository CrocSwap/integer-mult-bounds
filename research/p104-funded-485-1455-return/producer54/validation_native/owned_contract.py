# SPDX-License-Identifier: Apache-2.0
"""Exact independent local check of every original owned operation and boundary.

All coordinates at source cut33163 are treated as independent formal values.
The native full forward checker separately validates the actual COPY guard.
"""
from pathlib import Path
from fractions import Fraction as F
import gzip,json,hashlib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
old=json.load(gzip.open(ROOT/'inputs/pr7480/WORD.json.gz','rt'))
new=json.load(gzip.open(ROOT/'producer54/reroute/WORD.json.gz','rt'))
assert hashlib.sha256(json.dumps(new,sort_keys=True,separators=(',',':')).encode()).hexdigest()=='64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
n=old['public'];size=n+old['owned_fields'];start,end=33163,33219
mapping=json.load(open(ROOT/'producer54/reroute/OLD-TO-NEW.json'))
changed_end=mapping[str(end)]
assert old['program'][:start]==new['program'][:start]
assert old['program'][end:]==new['program'][changed_end:]
def replay(program):
 rows=[{r:F(1)}for r in range(size)];trace=[]
 for e in program:
  op,r=e[:2];touched=e[1:3]if op in('ADD','COPY')else e[1:2]
  if any(q>=n for q in touched):trace.append((e,{q:rows[q].copy()for q in touched}))
  if op in('INIT','CLEAR'):rows[r]={}
  elif op=='SCALE':rows[r]={q:F(e[2])*v for q,v in rows[r].items()}
  elif op in('ADD','COPY'):
   if op=='COPY':assert not rows[r]
   c=F(e[3]);dst=rows[r].copy()
   for q,v in rows[e[2]].items():
    z=dst.get(q,F(0))+c*v
    if z:dst[q]=z
    else:dst.pop(q,None)
   rows[r]=dst
 return rows,trace
before,traces_before=replay(old['program'][start:end])
after,traces_after=replay(new['program'][start:changed_end])
assert before==after
assert traces_before==traces_after
result={'status':'PASS_EXACT_ORIGINAL_OWNED_CONTRACTS_AND_LOCAL_BOUNDARY',
 'source_interval':[start,end],'candidate_interval':[start,changed_end],
 'formal_independent_cut_coordinates':size,'boundary_rows_compared':len(before),
 'owned_contact_count':len(traces_before),'owned_contacts':[e for e,_ in traces_before],
 'every_owned_operand_row_identical':True,'literal_unchanged_prefix_and_suffix':True,
 'interpretation':'Exact identity in independent formal cut coordinates, plus actual full forward COPY guard checked separately.'}
(HERE/'LOCAL-OWNED-CONTRACT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
