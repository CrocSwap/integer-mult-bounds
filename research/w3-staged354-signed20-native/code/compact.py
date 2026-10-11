#!/usr/bin/env python3
"""Compact PR354 no-event dormant roles and compose PR329's sorted sink relabeling.
Prepared with substantial OpenAI Codex assistance; Apache-2.0. Native admission is separate.
"""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,json,hashlib,struct,shutil
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,x:p.write_text(json.dumps(x,sort_keys=True)+'\n')
def run(base,final,sinks,output):
 base,final,sinks,output=map(lambda p:Path(p).resolve(),(base,final,sinks,output));assert not output.exists();output.mkdir(parents=True)
 b,c,sk=read(base/'249-states.json'),read(final/'249-states.json'),read(sinks);v=b['v'];assert(v,b['n'],c['n'])==(960,10020,10010)and c['v']==v
 raw=(final/'249-records.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()=='f5fca11b5855a5a575a9408b1cde69d152d03432ce3e8e375d6b20b39baf3434'
 deleted_sinks=sorted(x['stream']for x in sk['sinks']);assert len(deleted_sinks)==len(set(deleted_sinks))==10 and all(x['stream']==2*v+x['role']for x in sk['sinks'])
 original_survivors=[i for i in range(b['n'])if i not in deleted_sinks];assert len(original_survivors)==c['n']
 staged_to_original=dict(enumerate(original_survivors));original_to_staged={v:k for k,v in staged_to_original.items()};original_to_staged[b['n']]=c['n'];staged_to_original[c['n']]=b['n']
 events=list(struct.iter_unpack('<6i',raw));used=set()
 for op,a,bb,cc,f,z in events:
  assert op in range(4);used.add(a)
  if op!=0:used.add(bb)
 dead=[i for i in range(2*v,c['n'])if c['initial'][str(i)]==c['final'][str(i)]==c['FULL']and i not in used];assert len(dead)==480
 survivors=[i for i in range(c['n'])if i not in dead];mp={r:j for j,r in enumerate(survivors)};mp[c['n']]=len(survivors);inv={j:i for i,j in mp.items()};assert len(survivors)==9530 and all(r in mp for r in used)
 compact=[(op,mp[a],bb if op==0 else mp[bb],cc,f,z)for op,a,bb,cc,f,z in events];craw=b''.join(struct.pack('<6i',*r)for r in compact)
 assert raw==b''.join(struct.pack('<6i',op,inv[a],bb if op==0 else inv[bb],cc,f,z)for op,a,bb,cc,f,z in compact)
 original_to_compact={staged_to_original[k]:j for k,j in mp.items()};assert original_to_compact[b['n']]==9530
 assert set(original_to_compact)==set(range(b['n']+1))-set(deleted_sinks)-{staged_to_original[k]for k in dead}
 for tag,path,st,records in [('base',base,b,(base/'249-records.bin').read_bytes()),('final',final,c,craw)]:
  out=output/tag;out.mkdir();isfinal=tag=='final';regs=[staged_to_original[i]-2*v for i in survivors if i>=2*v]if isfinal else list(range(b['n']-2*v))
  meta=dict(n=len(survivors)if isfinal else b['n'],v=v,ZERO=st['ZERO'],FULL=st['FULL'],raw_sha256=hashlib.sha256(records).hexdigest())
  write(out/'meta.json',meta);write(out/'regs.json',regs)
  for end in ('initial','final'):write(out/(end+'.json'),{str(mp[int(i)]):f for i,f in st[end].items()if int(i)in mp and int(i)<c['n']}if isfinal else st[end])
  shutil.copyfile(path/'frames.json',out/'frames.json');(out/'records.bin').write_bytes(records)
 sourcefiles=[p/f for p in (base,final)for f in ('249-states.json','249-records.bin','frames.json')]+[sinks]
 report=dict(status='PASS_PR354_COMPOSED_SINK_DORMANT_PHYSICAL_ROLE_MAP',sink_roles_original=deleted_sinks,deleted_dormant_staged=dead,deleted_dormant_original=[staged_to_original[k]for k in dead],original_to_staged=original_to_staged,staged_to_compact=mp,original_to_compact=original_to_compact,inverse_event_relabeling_byte_exact=True,base_registers=10020,staged_registers=10010,final_registers=9530,original_helpers=8100,staged_helpers=8090,active_helpers=7610,copy_slots=[10020,10010,9530],records=len(events),source_word_sha256=hashlib.sha256(raw).hexdigest(),compacted_word_sha256=hashlib.sha256(craw).hexdigest(),inherited_stale_metadata_record_hash=c['record_sha256'],source_hashes={str(p):sha(p)for p in sourcefiles})
 write(output/'COMPACTION.json',report);print('PASS PR354 compaction',report['compacted_word_sha256'],flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--final',required=True);p.add_argument('--sinks',required=True);p.add_argument('--output',required=True);a=p.parse_args();run(a.base,a.final,a.sinks,a.output)
