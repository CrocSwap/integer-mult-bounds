#!/usr/bin/env python3
"""Two further signed generalized twins, replayed from the signed18 compact word.
Original twins: utcorvusvolat-dotcom (PR310), Louis Harrison/Anthropic Claude (PR346).
Generalized signed entrance transformation and this exact portable replay were prepared
with substantial OpenAI Codex assistance. Apache-2.0. Full admission is separate.
"""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
from pathlib import Path
from collections import defaultdict
import argparse,hashlib,json,struct,shutil
from generalized_twin_signed354 import kernel
SOURCE_WORD='8e9996b6819c1129b2507e3915842507d9dbe28077c7505bf57ebeaa6e53777e'
TARGET_WORD='6e0fcf5dd38d18a057a841b5dca56a4ab9c2d0489f37bc72a54a277d3f068330'
SOURCE_FILES={'COHORT249-FRAMES.json': 'c20b8a07afe23e4c30132c770984ea2c10d37834bae338196236046da8489d40', 'COHORT249-INITIAL.json': 'ce065ff1abc11517ee02eeda8e14aa22055df06eae5c431def7a245180c178be', '249-states.json': '077a3e16a361fe1cd650d04535624fb306f7bc5dc5718ef30996b6459bc8b0a6', 'frames.json': '3526c2d515706f0222393ce4a0949525dc7f44fd8802374f27eb012ce9f16beb', 'COHORT249-FINAL.json': '0ff88d85207a7c0c5fecbb2f093f853d512a88650e9f78a8ff29d0a39d500fd4', 'COHORT249-SELECTION.json': 'ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356', 'COHORT249-RECORDS.bin': '8e9996b6819c1129b2507e3915842507d9dbe28077c7505bf57ebeaa6e53777e'}
TARGET_FILES={'COHORT249-FRAMES.json': 'c20b8a07afe23e4c30132c770984ea2c10d37834bae338196236046da8489d40', 'COHORT249-INITIAL.json': '1854658f58bc9de5642fbdf9538e93c35ce7a14cef6b04d02708feb25d343232', '249-states.json': '7eb8e23b858a525754eea3075b3a149bf69a69bb6149872cbd872a2c2f3883f9', 'frames.json': '3526c2d515706f0222393ce4a0949525dc7f44fd8802374f27eb012ce9f16beb', 'COHORT249-FINAL.json': '0ff88d85207a7c0c5fecbb2f093f853d512a88650e9f78a8ff29d0a39d500fd4', 'COHORT249-SELECTION.json': 'ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356', 'COHORT249-RECORDS.bin': '6e0fcf5dd38d18a057a841b5dca56a4ab9c2d0489f37bc72a54a277d3f068330'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
write=lambda p,x:Path(p).write_text(json.dumps(x,sort_keys=True)+'\n')
def files(p):
 paths=list(p.rglob('*'));assert all(not z.is_symlink()for z in paths)
 return {z.relative_to(p).as_posix():sha(z)for z in paths if z.is_file()}
def regenerate(source,output):
 source,output=map(lambda p:Path(p).resolve(),(source,output));assert not output.exists()and not output.is_relative_to(source)
 assert files(source)==SOURCE_FILES
 st=read(source/'249-states.json');fr=read(source/'frames.json');fs={int(k):v for k,v in fr['frames'].items()};dim={k:v['dim']for k,v in fs.items()};ev=list(struct.iter_unpack('<6i',(source/'COHORT249-RECORDS.bin').read_bytes()));v,n,Z,F=st['v'],st['n'],st['ZERO'],st['FULL'];assert(v,n,st['h'])==(960,9530,20)
 moves=defaultdict(list)
 for k,(op,a,b,c,f,z)in enumerate(ev):
  if op==0:moves[a].append(k)
 chosen=[];insert=defaultdict(list);change={};pivots=set();append=[]
 for a,b in [(6233,7122),(6235,7120)]:
  assert 2*v<=a<n and 2*v<=b<n and a!=b
  assert st['initial'][str(a)]==st['initial'][str(b)]==Z and st['final'][str(a)]==st['final'][str(b)]==F
  ka,kb=moves[a][0],moves[b][0];u,w=ev[ka][3],ev[kb][3]
  assert ev[ka][:3]==(0,a,Z)and ev[kb][:3]==(0,b,Z)and dim[u]==dim[w]==3
  B=kernel(fs[u]['A']+fs[w]['A']);assert len(B)==1
  G=[[9*sum(x*y for x,y in zip(row,col))-sum(row)*sum(col)for col in B]for row in B]
  assert not kernel(G,len(G));A=kernel(B)
  available=[k for k,f in fs.items()if f==dict(B=B,A=A,dim=1)];assert len(available)==1;E=available[0]
  merges=[k for k,r in enumerate(ev)if r[0]==1 and r[1]==a and r[2]==b and 0<dim[r[4]]<20]
  assert len(merges)==1 and min(merges)>max(ka,kb);k=merges[0]
  chosen.append(dict(a=a,b=b,first_a=ka,first_b=kb,first_frame_a=u,first_frame_b=w,k=k,merge_frame=ev[k][4],B=B,A=A,dimension=1,entrance_frame=E))
  st['initial'][str(b)]=E;pivots.add(b);insert[min(ka,kb)].extend([(0,a,Z,E,1,0),(1,a,b,-1,E,46)])
  change[ka]=(0,a,E,u,2,0);change[kb]=(0,b,E,w,2,0);append.append((1,a,b,1,F,47))
 out=[];removed=[]
 for k,r in enumerate(ev):
  out.extend(insert.get(k,()))
  if r[0]==1 and dim[r[4]]==0 and (r[1]in pivots or r[2]in pivots):removed.append(k);continue
  out.append(change.get(k,r))
 out.extend(reversed(append));raw=b''.join(struct.pack('<6i',*r)for r in out)
 assert len(ev)==406294 and len(out)==406292 and len(removed)==8;digest=hashlib.sha256(raw).hexdigest();assert digest==TARGET_WORD
 shutil.copytree(source,output);(output/'COHORT249-RECORDS.bin').write_bytes(raw);st['record_sha256']=digest;write(output/'249-states.json',st);write(output/'COHORT249-INITIAL.json',st['initial']);assert files(output)==TARGET_FILES
 report=dict(status='PASS_EXACT_TWO_FURTHER_SIGNED_TWINS_REGENERATION_NOT_FULL_ADMISSION',source_word_sha256=SOURCE_WORD,candidate_word_sha256=digest,source_files=SOURCE_FILES,candidate_files=files(output),chosen=chosen,removed_zero_frame_additions=removed,records_before=len(ev),records_after=len(out),new_frames=0,entrance_rank_saved=2,scope='The additional earlier proper-frame reads invalidate the simple single-consumer template proof; the complete exact integer operator comparison is mandatory. Native frames, F2 columns, both ledgers, geometry, banks, moments and invoice are separate mandatory gates.')
 write(output.parent/(output.name+'-REGENERATION.json'),report);print('PASS exact two further signed twins',digest,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--output',required=True);a=p.parse_args();regenerate(a.source,a.output)
