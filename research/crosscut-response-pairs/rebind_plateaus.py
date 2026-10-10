#!/usr/bin/env python3
"""Bind a frozen plateau witness to a changed cohort word by full core alignment."""
import argparse,hashlib,json,struct
from pathlib import Path
if not __debug__:raise SystemExit('assertions are required')
ap=argparse.ArgumentParser();ap.add_argument('baseline',type=Path);ap.add_argument('witness',type=Path);ap.add_argument('candidate',type=Path);ap.add_argument('output',type=Path);args=ap.parse_args()
b=args.baseline.read_bytes();n=args.candidate.read_bytes();w=json.loads(args.witness.read_text());assert hashlib.sha256(b).hexdigest()==w['input_sha256'];E=struct.Struct('<6i');be=[e for e in E.iter_unpack(b) if e[0]];ne=[e for e in E.iter_unpack(n) if e[0]]
def core(events):return [(i,e) for i,e in enumerate(events) if not(e[0]==1 and e[5] in {4,28,29})]
bc,nc=core(be),core(ne);assert [e for i,e in bc]==[e for i,e in nc],'complete core event sequence changed'
mapping={i:j for (i,e),(j,f) in zip(bc,nc)};bindings=[]
for c in w['candidates']:
 gg=[]
 for i in c['gates']:
  j=mapping[i];assert be[i]==ne[j] and ne[j][4]==c['old_frame'];gg.append(j);bindings.append(dict(baseline_gate=i,candidate_gate=j,event=be[i]))
 c['gates']=gg
w['baseline_input_sha256']=w['input_sha256'];w['input_sha256']=hashlib.sha256(n).hexdigest();w['core_binding']=dict(status='PASS_FULL_UNCHANGED_CORE_EVENT_ALIGNMENT',events_compared=len(bc),bindings=bindings)
args.output.write_text(json.dumps(w,indent=2)+'\n');print('bound',len(bindings),'gates across',len(bc),'identical core events',flush=True)
