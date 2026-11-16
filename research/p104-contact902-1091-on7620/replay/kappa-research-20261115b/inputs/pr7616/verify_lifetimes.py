from pathlib import Path
import json,gzip,hashlib
R=Path(__file__).resolve().parent;O=Path(__import__('sys').argv[1])
W=json.loads(gzip.decompress((R/'data/word.json.gz').read_bytes()));B=json.loads(gzip.decompress((R/'data/base7605.json.gz').read_bytes()));n=W['public']
def tokens(w):return [(i,e) for i,e in enumerate(w['program']) if e[0] in ('INIT','CLEAR') or e[0]=='MOVE' and e[1]>=n]
bt=tokens(B);j=0;matched=set()
for i,e in tokens(W):
 if j<len(bt) and e==bt[j][1]:matched.add(i);j+=1
assert j==len(bt)
opened={};ls=[];peak=0
for i,e in enumerate(W['program']):
 op,r=e[:2]
 refs=e[1:3] if op in ('ADD','COPY') else [r]
 if op=='INIT':
  assert n<=r<n+W['owned_fields'] and r not in opened
  opened[r]=dict(field=r,start=i,start_chart=e[2],moves=[],matched_init=i in matched);peak=max(peak,len(opened))
 else:
  for rr in refs:
   if rr>=n:assert rr in opened,(i,rr)
  if op=='MOVE' and r>=n:opened[r]['moves'].append(i)
  if op=='CLEAR':
   life=opened.pop(r);life.update(end=i,end_chart=e[2],matched_clear=i in matched)
   assert life['matched_init']==life['matched_clear']
   if not life['matched_init']:assert not life['moves'] and life['start_chart']==life['end_chart']
   else:assert all(k in matched for k in life['moves'])
   ls.append(life)
assert not opened and len(ls)==113 and peak==50
extra=[x for x in ls if not x['matched_init']];assert len(extra)==39
stages=17;keys={(s,r) for s in range(stages) for r in range(n,n+W['owned_fields'])};assert len(keys)==1156
out=dict(status='PASS_LITERAL_LIFETIME_ALLOCATION',lifetimes=ls,extra_stationary=39,preserved_lifetimes=74,peak_live=50,reserved_distinct_banks=1156,allocation='Injective (native occurrence, declared owned field) bank; no peak-only compaction',scope='Literal sequential trace legality and allocation sufficiency. Atomic child return and exact erasure service retain framework premises; not an unconditional compiler proof.')
(O/'lifetime-allocation-w2.json').write_text(json.dumps(out,indent=2));print(out['status'],len(ls),len(extra),len(keys))
