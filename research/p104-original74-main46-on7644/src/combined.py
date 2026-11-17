# SPDX-License-Identifier: Apache-2.0
"""Bind the candidate to #7605 with the #7611 peer edit and retained credit."""
import json,gzip,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;S=D/'source7644';load=lambda p:json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
source=load(S/'retained/pr7605/data/word.json.gz'); peer=load(S/'data/peer7611.json');candidate=load(D/'candidate.json.gz');p=source['program']; assert len(p)==peer['base_events']+5
removed=[[i+5,e] for i,e in peer['delete']]
assert all(p[i]==e for i,e in removed)
insert=[]
for i,ops in peer['insert_before']:
 if i==0:
  ops=[e for e in ops if e[1] not in (185,196)]+[e for e in ops if e[1] in (185,196)]
  insert.append([0,ops])
 else:insert.append([i+5,ops])
manifest={'base_events':len(p),'delete':removed,'insert_before':insert,'append':[]}
rm=dict(removed);add=dict(insert);reconstructed=[]
for i,e in enumerate(p):
 reconstructed.extend(add.get(i,[]))
 if i not in rm:reconstructed.append(e)
assert reconstructed==candidate['program'] and dict(source,program=reconstructed)==candidate
(D/'combined-edits.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Exact tariff is recomputed from literal native MOVE ranks, each counted 17 times.
def paid(w):
 from collections import Counter
 hist=Counter();dim=list(map(len,w['frames']))
 for e in w['program']:
  if e[0]=='MOVE':hist[str(abs(dim[e[3]]-dim[e[2]]))]+=1
 return hist
old=load(S/'data/word.json.gz'); x,y=paid(old),paid(candidate); invoice=load(S/'data/invoice.json');delta={k:17*(y[k]-x[k]) for k in set(x)|set(y) if x[k]!=y[k]}
assert delta=={'1':-34,'4':-17,'6':17},delta
for k,v in delta.items():invoice['paid'][k]+=v
(D/'candidate-invoice.json').write_text(json.dumps(invoice,indent=2)+'\n')
print(json.dumps({'candidate_sha256':hashlib.sha256(gzip.decompress((D/'candidate.json.gz').read_bytes())).hexdigest(),'old_7605_events':len(p),'candidate_events':len(reconstructed),'signed_paid_delta':delta,'paid_total':sum(invoice['paid'].values()),'combined_edits_sha256':hashlib.sha256((D/'combined-edits.json').read_bytes()).hexdigest(),'invoice_sha256':hashlib.sha256((D/'candidate-invoice.json').read_bytes()).hexdigest()},indent=2))
