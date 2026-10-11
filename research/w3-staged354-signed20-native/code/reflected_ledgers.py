#!/usr/bin/env python3
"""Replay both actual raw6 frame ledgers, including COPY lifetimes and paid ranks.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import sys
if not __debug__:raise SystemExit('Assertions must remain enabled; refusing optimization')
sys.dont_write_bytecode=True
import argparse,hashlib,json,struct
from pathlib import Path
from collections import Counter
from functools import lru_cache
ap=argparse.ArgumentParser();ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
c=a.candidate;read=lambda p:json.loads(p.read_text());st=read(c/'249-states.json');f=read(c/'frames.json')['frames'];fs={int(k):v for k,v in f.items()};raw=(c/'COHORT249-RECORDS.bin').read_bytes();ev=list(struct.iter_unpack('<6i',raw));n=st['n'];h=20
sparse=lambda rows:[[(i,x)for i,x in enumerate(r)if x]for r in rows]
B={k:sparse(v['B'])for k,v in fs.items()};A={k:sparse(v['A'])for k,v in fs.items()}
@lru_cache(None)
def sub(x,y,rev):
 basis=fs[x]['A']if rev else fs[x]['B'];ann=B[y]if rev else A[y]
 dx=h-fs[x]['dim']if rev else fs[x]['dim'];dy=h-fs[y]['dim']if rev else fs[y]['dim']
 assert dx<=dy and all(sum(row[i]*v for i,v in ar)==0 for row in basis for ar in ann),(x,y,rev)
 return True
results=[]
for rev in (False,True):
 begin=st['final'if rev else'initial'];end=st['initial'if rev else'final'];state={int(k):v for k,v in begin.items()};open_source=None;H=Counter();counts=Counter()
 for op,t,s,v,fid,z in reversed(ev)if rev else ev:
  counts[op]+=1
  if op==0:
   old,new=(v,s)if rev else(s,v)
   assert state[t]==old and sub(old,new,rev)
   difference=(fs[old]['dim']-fs[new]['dim'])if rev else(fs[new]['dim']-fs[old]['dim'])
   assert difference==fid and difference>=0
   if difference:H[difference]+=1
   state[t]=new
  elif op==1:
   assert state[t]==state[s]==fid and t!=s
   assert t!=n and (s!=n or open_source is not None)
   assert open_source is None or t!=open_source
  elif (op==3 if rev else op==2):
   assert open_source is None and s==n and state[t]==v and n not in state
   # Reflection swaps the rank difference's orientation; the paid extraction
   # rank remains dim(source)-dim(temporary), independently of basis choice.
   assert z==fs[v]['dim']-fs[fid]['dim'] and z>0
   open_source=t;state[n]=fid;H[z]+=1
  else:
   assert s==n and open_source==t and state[t]==v and state[n]==fid
   open_source=None;del state[n]
 assert open_source is None and state=={int(k):v for k,v in end.items()}
 assert counts[2]==counts[3]==h
 results.append(dict(reverse_complement=rev,records=len(ev),operations=dict(counts),paid_histogram=dict(H),rank_mass=sum(r*c for r,c in H.items()),copies=h,all_endpoints_exact=True,common_frame_adds=True,copy_original_source_immutable=True))
assert results[0]['paid_histogram']==results[1]['paid_histogram']
# Reject a rank-changing endpoint overcharge directly on the actual primitive.
try:sub(st['FULL'],st['ZERO'],False)
except AssertionError:negative=True
else:raise AssertionError('non-nested control accepted')
out=dict(status='PASS_BOTH_CHRONOLOGICAL_REFLECTED_FRAME_LEDGERS_AND_PAID_HISTOGRAMS',source_word_sha256=hashlib.sha256(raw).hexdigest(),frame_sha256=hashlib.sha256((c/'frames.json').read_bytes()).hexdigest(),state_sha256=hashlib.sha256((c/'249-states.json').read_bytes()).hexdigest(),containment_pairs=sub.cache_info().currsize,non_nested_control_rejected=negative,ledgers=results,scope='Exact original B/A dot products and both chronological frame/state ledgers; separate native frame-minor and projector receipts certify ranks/nondegeneracy. Complementary COPY uses the same paid rank difference with its orientation reversed.')
a.output.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print('PASS both reflected ledgers',len(ev),results[0]['rank_mass'],flush=True)
