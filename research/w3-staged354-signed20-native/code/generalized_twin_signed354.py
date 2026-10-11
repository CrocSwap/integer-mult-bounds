#!/usr/bin/env python3
"""Regenerate generalized dirty twin entrances from the actual compacted Design T word.
Original twin template: utcorvusvolat-dotcom (PR310), Louis Harrison/Anthropic Claude (PR346).
Generalization to two rank-three first frames sharing a nondegenerate line, signed -entry/+exit compensation, exact discovery,
and this portable replay use substantial OpenAI Codex assistance. Apache-2.0.
The independent native scalar/dirty, both-frame-ledger, prime, bank and invoice checks are mandatory.
"""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
from pathlib import Path
from collections import defaultdict,Counter
from fractions import Fraction as Q
from functools import lru_cache
import argparse,json,struct,math,hashlib,shutil
SOURCE_WORD='2aa5b4af88e4295588079cf951a5655bdff861588d39ba8af43c185ee93d14b6'
TARGET_WORD='8e9996b6819c1129b2507e3915842507d9dbe28077c7505bf57ebeaa6e53777e'
SOURCE_FILES={'COHORT249-FRAMES.json': '1550d26e4569e400817d1c1de4dc30fd0a6458bb8d41597c5f80a7aa7d1e9109', 'COHORT249-INITIAL.json': '3c90f37c23a092855baf4def0ca489c09b11ecbfed366888d096ea326badae14', '249-states.json': '79de66272d4092010cf7cd342fcb4b6c50268f92c3e3cb844194758f9fc433f9', 'frames.json': '583303099bceb6468167f71adf74fd86ee56b3646bd6af3700f160b2fdef9691', 'COHORT249-FINAL.json': '0ff88d85207a7c0c5fecbb2f093f853d512a88650e9f78a8ff29d0a39d500fd4', 'COHORT249-SELECTION.json': 'ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356', 'COHORT249-RECORDS.bin': '2aa5b4af88e4295588079cf951a5655bdff861588d39ba8af43c185ee93d14b6'}
TARGET_FILES={'COHORT249-FRAMES.json': 'c20b8a07afe23e4c30132c770984ea2c10d37834bae338196236046da8489d40', 'COHORT249-INITIAL.json': 'ce065ff1abc11517ee02eeda8e14aa22055df06eae5c431def7a245180c178be', '249-states.json': '077a3e16a361fe1cd650d04535624fb306f7bc5dc5718ef30996b6459bc8b0a6', 'frames.json': '3526c2d515706f0222393ce4a0949525dc7f44fd8802374f27eb012ce9f16beb', 'COHORT249-FINAL.json': '0ff88d85207a7c0c5fecbb2f093f853d512a88650e9f78a8ff29d0a39d500fd4', 'COHORT249-SELECTION.json': 'ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356', 'COHORT249-RECORDS.bin': '8e9996b6819c1129b2507e3915842507d9dbe28077c7505bf57ebeaa6e53777e'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
write=lambda p,x:Path(p).write_text(json.dumps(x,sort_keys=True)+'\n')
def kernel(M,width=20):
 a=[[Q(x)for x in row]for row in M];r=0;piv=[]
 for col in range(width):
  pivot=next((i for i in range(r,len(a))if a[i][col]),None)
  if pivot is None:continue
  a[r],a[pivot]=a[pivot],a[r];q=a[r][col];a[r]=[x/q for x in a[r]]
  for i in range(len(a)):
   if i!=r and a[i][col]:q=a[i][col];a[i]=[x-q*y for x,y in zip(a[i],a[r])]
  piv.append(col);r+=1
  if r==len(a):break
 out=[]
 for col in range(width):
  if col in piv:continue
  row=[Q(0)]*width;row[col]=Q(1)
  for i,p in enumerate(piv):row[p]=-a[i][col]
  den=math.lcm(*(x.denominator for x in row));integers=[int(x*den)for x in row];g=math.gcd(*integers);out.append([x//g for x in integers])
 return out

def regenerate(base,source,output):
 base,source,output=map(lambda p:Path(p).resolve(),(base,source,output));assert not output.exists()and not output.is_relative_to(source)and not output.is_relative_to(base)
 assert sha(source/'COHORT249-RECORDS.bin')==SOURCE_WORD
 assert all(not p.is_symlink()for p in source.rglob('*'));assert {p.name:sha(p)for p in source.iterdir()if p.is_file()}==SOURCE_FILES
 st=read(source/'249-states.json');fr=read(source/'frames.json');frames=fr['frames'];fs={int(k):v for k,v in frames.items()};dim={k:v['dim']for k,v in fs.items()};ev=list(struct.iter_unpack('<6i',(source/'COHORT249-RECORDS.bin').read_bytes()));v,n,Z,F=st['v'],st['n'],st['ZERO'],st['FULL'];assert(v,n,st['h'])==(960,9530,20)
 initial={int(k):x for k,x in st['initial'].items()};final={int(k):x for k,x in st['final'].items()};moves=defaultdict(list);src=defaultdict(list)
 for k,(op,a,b,c,f,z)in enumerate(ev):
  if op==0:moves[a].append(k)
  elif op==1:src[b].append(k)
 @lru_cache(None)
 def intersection(u,w):return kernel(fs[u]['A']+fs[w]['A'])
 chosen=[];used=set()
 for k,(op,a,b,c,f,z)in enumerate(ev):
  if op!=1 or not(2*v<=a<n and 2*v<=b<n)or not(0<dim[f]<20):continue
  if initial[a]!=Z or initial[b]!=Z or final[a]!=F or final[b]!=F:continue
  if [j for j in src[b]if 0<dim[ev[j][4]]<20]!=[k]:continue
  if any(j<k and 0<dim[ev[j][4]]<20 for j in src[a]):continue
  ka,kb=moves[a][0],moves[b][0];u,w=ev[ka][3],ev[kb][3]
  if not(ka<k and kb<k and ev[ka][2]==ev[kb][2]==Z):continue
  B=intersection(u,w)
  # This finite construction selects only the exact rank-three / rank-one pattern.
  if (dim[u],dim[w],len(B))!=(3,3,1):continue
  G=[[9*sum(x*y for x,y in zip(row,col))-sum(row)*sum(col)for col in B]for row in B]
  if kernel(G,len(G))or{a,b}&used:continue
  used.update((a,b));chosen.append(dict(k=k,a=a,b=b,merge_frame=f,first_a=ka,first_b=kb,first_frame_a=u,first_frame_b=w,dimension=1,B=B,A=kernel(B),category=z))
 assert len(chosen)==18
 extra=read(source/'COHORT249-FRAMES.json');nextid=max(map(int,set(frames)|set(read(base/'frames.json')['frames'])))+1;insert=defaultdict(list);change={};append=[];pivots=set();lineframes={}
 for row in chosen:
  a,b,ka,kb,u,w=row['a'],row['b'],row['first_a'],row['first_b'],row['first_frame_a'],row['first_frame_b'];key=tuple(map(tuple,row['B']))
  if key not in lineframes:
   fid=nextid;nextid+=1;frame=dict(B=row['B'],A=row['A'],dim=1);frames[str(fid)]=frame;extra[str(fid)]=frame;lineframes[key]=fid
  E=lineframes[key];row['entrance_frame']=E;st['initial'][str(b)]=E;pivots.add(b);insert[min(ka,kb)].extend([(0,a,Z,E,1,0),(1,a,b,-1,E,44)])
  for k,target,frame in((ka,a,u),(kb,b,w)):
   assert ev[k][:4]==(0,target,Z,frame);change[k]=(0,target,E,frame,2,0)
  append.append((1,a,b,1,F,45))
 out=[];removed=[]
 for k,r in enumerate(ev):
  out.extend(insert.get(k,()))
  if r[0]==1 and frames[str(r[4])]['dim']==0 and(r[1]in pivots or r[2]in pivots):removed.append(k);continue
  out.append(change.get(k,r))
 out.extend(reversed(append));raw=b''.join(struct.pack('<6i',*r)for r in out);digest=hashlib.sha256(raw).hexdigest();assert digest==TARGET_WORD and len(removed)==72 and len(lineframes)==2
 shutil.copytree(source,output);(output/'COHORT249-RECORDS.bin').write_bytes(raw);st['record_sha256']=digest
 for name,value in [('249-states',st),('frames',fr),('COHORT249-INITIAL',st['initial']),('COHORT249-FRAMES',extra)]:write(output/(name+'.json'),value)
 assert {p.name:sha(p)for p in output.iterdir()if p.is_file()}==TARGET_FILES
 report=dict(status='PASS_EXACT_GENERALIZED_TWIN_REGENERATION_NOT_FULL_ADMISSION',source_word_sha256=SOURCE_WORD,candidate_word_sha256=digest,source_state_sha256=sha(source/'249-states.json'),source_frames_sha256=sha(source/'frames.json'),source_base_frames_sha256=sha(base/'frames.json'),chosen=chosen,removed_zero_frame_additions=removed,records_before=len(ev),records_after=len(out),new_frames=2,entrance_rank_saved=18,source_correction_scope='Literal source/frame recurrence reproduced; independent native columns, reflected ledgers, geometry, all prime minors, banks, complete paid profile and finite invoice remain mandatory.')
 write(output.parent/(output.name+'-REGENERATION.json'),report);print('PASS exact generalized twin regeneration',digest,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--source',required=True);p.add_argument('--output',required=True);a=p.parse_args();regenerate(a.base,a.source,a.output)
