#!/usr/bin/env python3
"""Explicit no-event dormant-role compaction, prepared with OpenAI Codex assistance."""
import sys
if not __debug__:raise SystemExit('Assertions must remain enabled; refusing optimization')
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,hashlib,json,struct,shutil
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--base',type=Path,required=True);ap.add_argument('--final',type=Path,required=True);ap.add_argument('--expected-word',required=True);a=ap.parse_args()
ROOT=a.output.resolve();BASE=a.base.resolve();FINAL=a.final.resolve()
assert ROOT.exists() and not (ROOT/'materialized').exists()
assert not ROOT.is_relative_to(BASE) and not ROOT.is_relative_to(FINAL)
read=lambda p:json.loads(p.read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def write(p,x):p.write_text(json.dumps(x,sort_keys=True)+'\n')
b=read(BASE/'249-states.json');c=read(FINAL/'249-states.json');raw=(FINAL/'249-records.bin').read_bytes();fr=read(FINAL/'frames.json')
n=c['n'];v=c['v'];assert n==10020 and v==960 and len(raw)%24==0
assert sha(raw)==a.expected_word
events=list(struct.iter_unpack('<6i',raw));used=set()
for op,a,bb,cc,f,z in events:
 assert op in range(4);used.add(a)
 if op!=0:used.add(bb)
full=c['FULL'];dead=[i for i in range(2*v,n) if c['initial'][str(i)]==full==c['final'][str(i)] and i not in used]
assert len(dead)==480
survivors=[i for i in range(n) if i not in dead];mapping={r:j for j,r in enumerate(survivors)};mapping[n]=len(survivors)
assert all(r in mapping for r in used)
compact=[]
for op,a,bb,cc,f,z in events:
 compact.append((op,mapping[a],bb if op==0 else mapping[bb],cc,f,z))
craw=b''.join(struct.pack('<6i',*r) for r in compact)
# An inverse relabeling returns every original event byte.
inv={j:i for i,j in mapping.items()}
assert raw==b''.join(struct.pack('<6i',op,inv[a],bb if op==0 else inv[bb],cc,f,z)for op,a,bb,cc,f,z in compact)
mat=ROOT/'materialized';mat.mkdir()
for tag,path,st,records in [('base',BASE,b,(BASE/'249-records.bin').read_bytes()),('final',FINAL,c,craw)]:
 out=mat/tag;out.mkdir();isfinal=tag=='final';regs=[i-2*v for i in survivors if i>=2*v]if isfinal else list(range(n-2*v))
 meta=dict(n=len(survivors)if isfinal else n,v=v,ZERO=st['ZERO'],FULL=st['FULL'],raw_sha256=sha(records))
 write(out/'meta.json',meta);write(out/'regs.json',regs)
 for end in ('initial','final'):
  write(out/(end+'.json'),{str(mapping[int(i)]):f for i,f in st[end].items()if int(i)in mapping and int(i)<n}if isfinal else st[end])
 shutil.copyfile(path/'frames.json',out/'frames.json');(out/'records.bin').write_bytes(records)
sourcefiles=[p/f for p in (BASE,FINAL)for f in ('249-states.json','249-records.bin','frames.json')]
receipt=dict(status='PASS_BIJECTIVE_EVENT_RELABELING_AND_NO_EVENT_FULL_DORMANT_DELETION',deleted_roles=dead,deleted_count=len(dead),declared_helpers=8100,active_helpers=len(survivors)-2*v,copy_slot_before=n,copy_slot_after=len(survivors),original_final_word_sha256=sha(raw),compacted_word_sha256=sha(craw),original_inherited_metadata_hash=c['record_sha256'],source_hashes={str(p):sha(p.read_bytes())for p in sourcefiles},records=len(events),role_mapping=mapping,inverse_event_relabeling_byte_exact=True,scope='Deleted only unchanged FULL/FULL helpers appearing in no literal event; all remaining roles and the COPY slot relabeled bijectively. Native scalar/formal/frame audits must replay separately.')
write(ROOT/'COMPACTION.json',receipt)
print('PASS compaction',len(dead),len(survivors)-2*v,sha(craw),flush=True)
