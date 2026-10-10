#!/usr/bin/env python3
"""Recompute the compact record stream and the candidate's binding receipts after a transcript stage (same freed-role map as prepare_candidate.py)."""
import hashlib,json,struct,sys
from pathlib import Path
if not __debug__:raise SystemExit('Assertions required')
out=Path(sys.argv[1]);read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
st=read(out/'249-states.json');ini=read(out/'COHORT249-INITIAL.json');FULL=st['FULL'];n=st['n'];assert n==20107
freed={r for r in range(3520,n) if ini[str(r)]==FULL};assert len(freed)==1455
ev=list(struct.iter_unpack('<6i',(out/'COHORT249-RECORDS.bin').read_bytes()))
for op,a,b,c,f,z in ev:assert a not in freed and (op==0 or b not in freed),'Freed role used after the stage'
live=[r for r in range(n) if r not in freed];mapping={r:i for i,r in enumerate(live)};mapping[n]=len(live);assert len(live)==18652
compact=[(op,mapping[a],b if op==0 else mapping[b],c,f,z) for op,a,b,c,f,z in ev]
(out/'COMPACT-RECORDS.bin').write_bytes(b''.join(struct.pack('<6i',*r) for r in compact))
wordsha=sha(out/'COHORT249-RECORDS.bin');st['record_sha256']=wordsha;st['record_count']=len(ev)
final=dict(st['final'])
for op,a,b,c,f,z in ev:
 if op==0:final[str(a)]=c
assert final==st['final'],'data and helper endpoints unchanged'
(out/'249-states.json').write_text(json.dumps(st,sort_keys=True,separators=(',',':'))+'\n');(out/'249-records.bin').write_bytes((out/'COHORT249-RECORDS.bin').read_bytes())
b=read(out/'SOURCE-BINDING.json');b.update(word_sha256=wordsha,compact_word_sha256=sha(out/'COMPACT-RECORDS.bin'),record_count=len(ev),stage_after_binding='target-prefix (209 exact F2 squares, inputs/target-selection.json)');(out/'SOURCE-BINDING.json').write_text(json.dumps(b,sort_keys=True,indent=1)+'\n')
print('PASS recompaction after target prefix:',wordsha,len(ev),'records',flush=True)
