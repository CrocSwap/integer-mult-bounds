#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound whole-role path replay, complete geometry and exact moment.

The predecessor's independent owner checker and directed moment engine are
retained verbatim. Full native/controller/outer admission is a separate run.
"""
import argparse,copy,gzip,hashlib,importlib.util,json
from pathlib import Path
from collections import defaultdict,Counter
from fractions import Fraction as Q
P=Path(__file__).resolve().parent

def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def require(ok,msg):
 if not ok:raise ValueError(msg)
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def authenticate():
 for pin in read(P/'PREDECESSORS.json')['vendored_inputs']:
  b=(P/pin['local']).read_bytes();require(hashlib.sha256(b).hexdigest()==pin['local_sha256'],'changed input '+pin['local'])
  if pin['gzip_envelope']:b=gzip.decompress(b)
  require(hashlib.sha256(b).hexdigest()==pin['source_sha256'],'changed original bytes')
  require(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==pin['git_blob'],'changed Git blob')

def key(z):return z['owner_replica'],z['child'],z['port']
def family(plan,k):return k[0]*896+(2*plan['pairs'][str(k[1])]+plan['sides'][str(k[1])])*112+k[2]

def construct(original,plan,moves):
 rows=copy.deepcopy(original);occupied=defaultdict(set);bins=defaultdict(set)
 for i,z in enumerate(rows):occupied[z['time']].add(z['family']);bins[key(z)].add(i)
 def slack(k):return plan['windows'][f'{k[0]},{k[1]}'][0]-sum(rows[i]['width']for i in bins[k])
 def path_replay(path,width,start,end):
  require(bool(path) and width>0,'empty or nonpositive-width path')
  current=start;seen={start}
  for i,d in path:
   require(0<=i<len(rows),'unknown role');z=rows[i];d=tuple(d);old=key(z)
   require(d==current and old not in seen,'disconnected or cyclic path')
   require(d!=old and z['width']==width,'wrong path width or identity')
   require(width<=slack(d),'no whole-role capacity');f=family(plan,d)
   require(f not in occupied[z['time']],'duplicate physical family')
   require(z['time']in plan['windows'][f'{d[0]},{d[1]}'][1],'deadline crossed')
   occupied[z['time']].remove(z['family']);occupied[z['time']].add(f)
   bins[old].remove(i);bins[d].add(i)
   z.update(owner_replica=d[0],child=d[1],port=d[2],family=f,copy=d[0]*112+d[2])
   current=old;seen.add(old)
  require(current==end,'wrong path endpoint')
 require(len(moves['seven_nine'])==43 and len(moves['single_width'])==53,'wrong certificate size')
 for group in moves['seven_nine']:
  keys=[tuple(x)for x in group['gaps']]+[tuple(group['seven_bin']),tuple(group['nine_end'])]
  require(len(set(keys))==4 and [slack(k)for k in keys]==[7,7,0,5],'wrong composite entrance')
  for path,w,start,end in zip(group['paths'],(7,7,9),(keys[0],keys[1],keys[2]),(keys[2],keys[2],keys[3]),strict=True):path_replay(path,w,start,end)
  require([slack(k)for k in keys]==[0,0,5,14],'wrong composite exit')
 for step in moves['single_width']:
  target,end=tuple(step['target']),tuple(step['end']);old=[slack(target),slack(end)];w=step['width']
  require(old==step['old_slacks'] and old[0]>=w and old[1]>old[0]-w,'not a strict concavity gain')
  path_replay(step['path'],w,target,end)
  require([slack(target),slack(end)]==step['new_slacks']==[old[0]-w,old[1]+w],'wrong transfer bill')
 for ids in bins.values():
  offset=0
  for i in sorted(ids,key=lambda i:(rows[i]['time'],rows[i]['helper'])):rows[i]['offset']=offset;offset+=rows[i]['width']
 return rows

def verify(write=None):
 authenticate();plan=read(P/'inputs/PLAN.json.gz');contract=read(P/'inputs/CONTRACT.json.gz');original=read(P/'inputs/OWNERS.json.gz')
 oracle=module('predecessor_owner_reference',P/'vendor/owner_reference.py')
 old,_=oracle.owners_check(original,plan,contract);previous=read(P/'inputs/CLAIM.json')
 require(dict(old)=={int(k):v for k,v in previous['global_profile'].items()},'predecessor positive control')
 moves=read(P/'MOVES.json');rows=construct(original,plan,moves);H,idle=oracle.owners_check(rows,plan,contract)
 H=dict(sorted(H.items()));idle=dict(sorted(idle.items()));claim=read(P/'CLAIM.json')
 require(H=={int(k):v for k,v in claim['profile'].items()},'published complete profile')
 require(idle=={int(k):v for k,v in claim['idle'].items()},'published idle profile')
 engine=module('directed_moment',P/'vendor/fine_moment.py');engine.SH=256;engine.GRID=1<<256;engine.LOG_TERMS=100;engine.EXP_TERMS=96
 lo,hi=Q(claim['lo']),Q(claim['hi'])
 require(engine.moment(73,66304,sorted(H.items()),lo)[1]<1,'native lower endpoint')
 require(engine.moment(73,66304,sorted(H.items()),hi)[0]>1,'native upper rejection')
 require(Q(claim['comparison_kappa'])==Q(previous['kappa'])<Q(claim['kappa'])<=lo,'strict improvement')
 require(Q(read(P/'inputs/PR2349-OUTER-CLAIM.json')['kappa'])<Q(claim['kappa']),'not above the concurrent PR2349 point')
 full=read(P/'evidence/FULL-ADMISSION.json')
 require(full['status']=='PASS_T74_AUGMENTING_PATHS_FULL_CONDITIONAL_ADMISSION','missing full admission')
 require(full['global_profile']=={str(k):v for k,v in H.items()},'full admission profile binding')
 require(full['owners_content_sha256']==hashlib.sha256(canonical(rows)).hexdigest(),'full admission owner binding')
 require(full['published_kappa']==claim['kappa'] and full['admitted_kappa']==claim['admitted_outer_kappa'],'published outer point')
 require(Q(claim['kappa'])<Q(full['admitted_kappa'])<hi,'outer publication ordering')
 require(engine.moment(73,66304,sorted(H.items()),Q(full['admitted_kappa']))[1]<1,'admitted outer point exceeds native moment')
 for field,name in [('strict_assembly_sha256','STRICT-ASSEMBLY.json'),('outer_ledger_sha256','OUTER-LEDGER.json'),('inherited_replay_sha256','REPLAY.json'),('invoice_sha256','PHYSICAL-INVOICE.json')]:
  require(hashlib.sha256((P/'evidence'/name).read_bytes()).hexdigest()==full[field],'changed full receipt artifact '+name)
 invoice=read(P/'evidence/PHYSICAL-INVOICE.json')
 require(full['physical_stock']==invoice['physical']==66826 and full['private_zero_buffers']==invoice['private_zero_buffers']==78,'cleanup-buffer stock binding')
 for name,digest in full['driver_binding']['overlay_sha256'].items():
  require(hashlib.sha256((P/'vendor/private-stock'/name).read_bytes()).hexdigest()==digest,'changed conservative pricing file')
 cap=read(P/'inputs/PACKING-CAP.json');cp={int(k):v for k,v in cap['profile'].items()}
 # The local words, 666 calls, total idle mass and largest available rank stay fixed.
 expected=Counter()
 for call in plan['provider_calls']:expected.update({int(r):48*n for r,n in plan['provider_registry'][call['provider']]['actual_paid_profile'].items()})
 expected[48]+=sum(r*n for r,n in idle.items())
 require(dict(expected)==cp,'same fully charged favorable packing cap')
 require(engine.moment(73,48*66304,sorted(cp.items()),Q(cap['b_upper']))[0]>1,'packing cap upper endpoint')
 controls=[]
 def reject(label,fn):
  try:fn()
  except(ValueError,KeyError,IndexError):controls.append(label)
  else:raise ValueError('accepted mutation: '+label)
 for field,value in [('time',666),('family',-1),('copy',-1),('offset',100),('helper',434),('width',1)]:
  saved=rows[0][field];rows[0][field]=value;reject('wrong '+field,lambda:oracle.owners_check(rows,plan,contract));rows[0][field]=saved
 bad=copy.deepcopy(moves);bad['seven_nine'][0]['paths'][0]=bad['seven_nine'][0]['paths'][0][1:]
 reject('omitted path edge',lambda:construct(original,plan,bad))
 bad=copy.deepcopy(moves);bad['single_width'][0]['old_slacks'][1]=0
 reject('unpaid transfer endpoint',lambda:construct(original,plan,bad))
 bp=copy.deepcopy(plan);bp['windows']['43,0'][1]=[]
 reject('forged chronological window',lambda:oracle.owners_check(rows,bp,contract))
 receipt=dict(status='PASS_COMPLETE_OWNER_PATHS_AND_EXACT_NATIVE_MOMENT',roles=len(rows),composite_exchanges=43,single_width_paths=53,global_profile=H,idle_profile=idle,owners_content_sha256=hashlib.sha256(canonical(rows)).hexdigest(),native_lower=str(lo),native_upper=str(hi),packing_cap_upper=cap['b_upper'],fraction_of_cap=str(Q(claim['kappa'])/Q(cap['b_upper'])),rejected_controls=controls,scope='Finite complete owner construction and exact native moment; full supplier/outer admission is separate.')
 if write:
  write.mkdir(parents=True,exist_ok=False);(write/'OWNERS.json.gz').write_bytes(gzip.compress(canonical(rows),mtime=0));(write/'RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(receipt['status'],'roles',len(rows),'controls',len(controls),flush=True)
 return receipt,rows

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',type=Path);a=ap.parse_args();verify(a.write)
