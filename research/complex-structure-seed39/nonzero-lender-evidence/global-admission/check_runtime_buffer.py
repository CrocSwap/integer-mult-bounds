#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Focused runtime buffer validator test; full controller admission is separate.

Build only the metadata consumed by the concrete buffer layer, check all666
maps against the artifact, inverse-lower allfour programs, execute allfour
physical dispatch templates and reject six concrete mutations.
"""
from pathlib import Path
import sys,json,gzip,hashlib
p=Path(__file__).resolve().parent.parent
g=p/'global-admission';sys.path.insert(0,str(g/'runtime-overlay/code'))
import buffer_runtime as b
read=lambda q:json.loads(gzip.decompress(q.read_bytes()) if q.suffix=='.gz' else q.read_bytes())
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
bind=read(g/'GLOBAL-BUFFER-BINDING.json.gz');reg={}
for pid,tag in [('gauge44','base'),('extra','extra')]:
 d=p/'native-evidence'/tag
 reg[pid]={'local_programs':read(d/'LOCAL-PROGRAMS.json.gz'),'canonical_word_sha256':sha(d/'CANONICAL-WORD.json.gz'),'local_programs_sha256':sha(d/'LOCAL-PROGRAMS.json.gz')}
calls=[{k:v for k,v in c.items() if k not in ('provider','lowered_program_sha256')}|{'provider_id':c['provider']} for c in bind['calls']]
t={'buffer_binding':bind,'private_namespace':bind['private_namespace'],'live':bind['live'],'physical':bind['physical'],'provider_dispatch':b.DISPATCH,'hosting':{'owner_map_sha256':bind['source_sha256']['owners']},'exact_data_phase_recipe_sha256':bind['source_sha256']['data_phases'],'local_providers':reg,'calls':calls}
r=b.validate(t);controls=b.mutation_controls(t);seen=set();events={}
for c in calls:
 k=(c['provider_id'],c['orientation'])
 if k in seen:continue
 seen.add(k);stream=list(b.iter_call_events(t,c));events[':'.join(k)]=len(stream)
 for e in stream:
  if e[0]=='scalar':refs=e[1][1:3] if e[1][0] in ('add','copy') else e[1][1:2]
  elif e[0] in ('center','warp'):refs=[e[1]]
  elif e[0] in ('adapter','residual_adapter','climb'):refs=[e[2]]
  else:refs=[]
  assert all(x[0]=='F' and 0<=x[1]<66818 for x in refs)
assert len(seen)==4 and len(controls)==6
out={'status':'PASS_RUNTIME_BUFFER_ADMISSION_AND_ALL_FOUR_DISPATCH_TEMPLATES','admission':r,'controls':controls,'physical_dispatch_events':events,'source_sha256':{f.name:sha(f) for f in (g/'runtime-overlay/code').glob('*.py') if f.name in ('buffer_runtime.py','emit_allcold.py','audit_allcold.py','invoice_allcold.py')}}
(g/'RUNTIME-BUFFER-CHECK.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status']);print(events)
