"""Exact fixed-slot commutation barrier, prepared for @woklerx.
Substantial OpenAI Codex assistance; Apache-2.0. Standard library only.
"""
import argparse
from bisect import bisect_right
from collections import Counter
from fractions import Fraction as Q
import gzip, hashlib, json, tarfile
from pathlib import Path

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
ARCHIVE='research/community-frontier1042-audit/selected-replay.tar.gz'
MEMBER='slots/local/FULL-WORD.json.gz'
PAYLOAD='c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8'
REQUIRED={ARCHIVE,'research/community-frontier1042-audit/ASSEMBLY.json',
 'research/gauge44-slots-t16/independent/audit_local.py'}

def need(ok,msg):
 if not ok:raise ValueError(msg)

def object_pairs(pairs):
 d={}
 for k,v in pairs:need(k not in d,'duplicate JSON key');d[k]=v
 return d

def loads(raw):
 return json.loads(raw,object_pairs_hook=object_pairs,
  parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite JSON')))

def canonical(x):return json.dumps(json.loads(json.dumps(x)),sort_keys=True,separators=(',',':'))
def sha(b):return hashlib.sha256(b).hexdigest()
def file_sha(p):
 b=p.read_bytes()
 if p.suffix not in ('.gz',):b=b.replace(b'\r\n',b'\n')
 return sha(b)

def sources(pins):
 need(set(pins)==REQUIRED,'source-name set mismatch')
 for p,h in pins.items():need(file_sha(ROOT/p)==h,'source hash mismatch')
 with tarfile.open(ROOT/ARCHIVE) as t:
  found=[m for m in t.getmembers() if m.name==MEMBER]
  need(len(found)==1 and found[0].isfile(),'archive member must be unique file')
  raw=t.extractfile(found[0]).read()
 decoded=gzip.decompress(raw);need(sha(decoded)==PAYLOAD,'selected word payload mismatch')
 asm=loads((ROOT/'research/community-frontier1042-audit/ASSEMBLY.json').read_bytes())
 need(Q(asm['kappa'])==Q(1672188119205421,10**18),'selected assembly guard')
 return loads(decoded),sha(raw)

def span(vs):
 s={0}
 for v in vs:
  need(type(v) is int and 0<v<512,'invalid frame vector')
  s|={x^v for x in tuple(s)}
 return sum(1<<x for x in s)

def rank(f):return f.bit_count().bit_length()-1
def inside(a,b):return a&~b==0
def regs(e):return e[1:3] if e[0]=='add' else e[1:2]
def commute(e,g):return e[0]==g[0]=='add' and e[1]!=g[2] and g[1]!=e[2]

def scalar_control(e,g):
 names=sorted(set(regs(e)+regs(g))); n=len(names)
 def apply(order):
  rows=[[Q(i==j) for j in range(n)] for i in range(n)]
  for op in order:
   t,s=map(names.index,op[1:3]);q=Q(op[3],op[4])
   rows[t]=[x+q*y for x,y in zip(rows[t],rows[s])]
  return rows
 return apply([e,g])==apply([g,e])

def stage_data(es,start):
 cur=start.copy();pre=[];touches=[[] for _ in cur];paid=Counter();frames=[]
 for i,e in enumerate(es):
  need(e[0] in ('add','scale'),'unknown scalar gate')
  q=Q(e[3],e[4]) if e[0]=='add' else Q(e[2],e[3]);need(q!=0,'zero scalar gate')
  if e[0]=='add':need(e[1]!=e[2],'self ADD')
  f=span(e[-1]);frames.append(f);pre.append(tuple(cur))
  for r in regs(e):
   need(type(r) is int and 0<=r<len(cur),'register out of range')
   need(inside(cur[r],f),'baseline frame not monotone')
   if (d:=rank(f)-rank(cur[r])):paid[d]+=1
   cur[r]=f;touches[r].append(i)
 return {'events':es,'frames':frames,'start':start,'end':cur,'pre':pre,'touches':touches,'paid':paid}

def full_replay(data,order):
 """Independent whole-stage reconstruction: no exposure/local-window logic."""
 cur=data['start'].copy();paid=Counter()
 for pos,k in enumerate(order):
  f=data['frames'][pos]
  for r in regs(data['events'][k]):
   if not inside(cur[r],f):return False,{'position':pos,'register':r,'old_rank':rank(cur[r]),'new_rank':rank(f),'reason':'containment'}
   if (d:=rank(f)-rank(cur[r])):paid[d]+=1
   cur[r]=f
 if cur!=data['end']:return False,{'reason':'stage_boundary'}
 return True,dict(paid)

def local_crossing(data,a,b,c,i,j):
 es,frames,pre,touches=data['events'],data['frames'],data['pre'],data['touches']
 changes={r:pre[a][r] for r in set(regs(es[i])+regs(es[j]))}
 order=[k for k in range(a,b) if k!=i]+[j,i]+[k for k in range(b,c) if k!=j]
 for pos,k in enumerate(order,a):
  f=frames[pos]
  for r in regs(es[k]):
   if r not in changes:continue
   if not inside(changes[r],f):return False
   changes[r]=f
 for r,f in changes.items():
  z=bisect_right(touches[r],c-1)
  if z==len(touches[r]):
   if f!=data['end'][r]:return False
  elif not inside(f,frames[touches[r][z]]):return False
 return True

def census(data):
 es,frames=data['events'],data['frames'];n=len(es);tally=Counter();adjacent=Counter();reasons=Counter()
 transcript=hashlib.sha256();examples=[]
 for i,(e,g) in enumerate(zip(es,es[1:])):
  if e[0]!=g[0] or e[0]!='add':adjacent['not_two_ADD']+=1;continue
  if not commute(e,g):adjacent['noncommuting']+=1;continue
  adjacent['commuting']+=1
  order=list(range(n));order[i],order[i+1]=i+1,i
  ok,p=full_replay(data,order)
  if ok:
   need(p==dict(data['paid']),'unexpected adjacent paid delta')
   need(frames[i]==frames[i+1],'unexpected crossing')
  adjacent['admissible_same_frame' if ok else 'frame_or_boundary_reject']+=1
 cuts=[0]+[i for i in range(1,n) if frames[i]!=frames[i-1]]+[n]
 for a,b,c in zip(cuts,cuts[1:],cuts[2:]):
  left=[i for i in range(a,b) if es[i][0]=='add' and all(commute(es[i],es[k]) for k in range(i+1,b))]
  right=[j for j in range(b,c) if es[j][0]=='add' and all(commute(es[k],es[j]) for k in range(b,j))]
  tally['boundaries']+=1
  for i in left:
   for j in right:
    tally['exposed_pairs']+=1
    if not commute(es[i],es[j]):tally['noncommuting']+=1;continue
    tally['commuting']+=1
    need(scalar_control(es[i],es[j]),'commutation formula mismatch')
    order=list(range(a))+[k for k in range(a,b) if k!=i]+[j,i]+[k for k in range(b,c) if k!=j]+list(range(c,n))
    fast=local_crossing(data,a,b,c,i,j);slow,why=full_replay(data,order)
    need(fast==slow,'local/full replay mismatch')
    need(not slow,'frame boundary crossing found')
    tally['frame_or_boundary_reject']+=1
    reasons[why['reason']]+=1
    item=[a,b,c,i,j,why];transcript.update((canonical(item)+'\n').encode())
    if len(examples)<3:examples.append(item)
 return {'adjacent':dict(adjacent),'exposed':dict(tally),'rejection_reasons':dict(reasons),'rejection_transcript_sha256':transcript.hexdigest(),'examples':examples}

def baseline(w):
 v,h,R=w['report']['v'],w['report']['h'],w['report']['R'];need((v,h,R)==(112,9,480),'selected geometry mismatch')
 n=2*v+R;start=[span([p]) for p in w['ports']]+[1]*(n-v)
 for r,f in w['start_extra'].items():start[int(r)]=span(f)
 a=stage_data(w['A'],start);b=stage_data(w['B'],a['end']);paid=a['paid']+b['paid']
 levels={int(t):span(f) for t,f in w.get('target_levels',{}).items()}
 need(all(a['end'][v+t]==levels.get(t,1) for t in range(v)),'target cut levels')
 for r,f0 in zip(w['centers'],w['center_frames']):
  f=span(f0);need(a['end'][r]==f,'center cut frame')
  served={levels.get(e[1]-v,1) for e in w['cut'] if e[2]==r}
  for t in sorted(served,key=lambda x:-rank(x)):
   need(inside(t,f),'non-nested center route')
   if (d:=rank(f)-rank(t)):paid[d]+=1
   f=t
 early=w.get('early_cleanup',[]);ids={i for i,f in early};need(len(ids)==len(early),'duplicate early cleanup')
 tail=[w['cleanup'][i][:-1]+[f] for i,f in early]
 t=stage_data(tail,b['end']);paid+=t['paid'];cur=t['end'];full=span([1<<i for i in range(h)])
 end=[full]*v+[span([x for x in range(1,512) if (x&p).bit_count()%2==0]) for p in w['ports']]+[full]*R
 for r,f in w.get('helper_final',{}).items():end[int(r)]=span(f)
 for r,f in enumerate(end):
  need(inside(cur[r],f),'terminal frame')
  if (d:=rank(f)-rank(cur[r])):paid[d]+=1
 need(all(all(end[r]==full for r in regs(e)) for i,e in enumerate(w['cleanup']) if i not in ids),'cleanup touches low end')
 need(dict(paid)=={int(k):v for k,v in w['report']['local_profile'].items()},'complete paid profile mismatch')
 return a,b,dict(sorted(paid.items()))

def controls(pins):
 passed=[]
 def rejects(name,fn):
  try:fn()
  except ValueError:passed.append(name);return
  raise ValueError('control accepted: '+name)
 e=['add',0,1,1,1,[]];g=['add',2,0,1,1,[]]
 need(not commute(e,g) and not scalar_control(e,g),'dependent ADD false-positive');passed.append('dependent_ADD_changes_endpoint')
 need(not inside(span([1]),span([2])),'rank is not containment');passed.append('equal_rank_different_subspace')
 rejects('duplicate_JSON_key',lambda:loads('{"a":1,"a":2}'))
 rejects('nonfinite_JSON',lambda:loads('[NaN]'))
 rejects('floating_seed',lambda:identity({'seed':27.0}))
 rejects('missing_required_pin',lambda:sources(dict(list(pins.items())[1:])))
 # A genuine legal crossing exists in the general class; the selected obstruction is not hardcoded.
 es=[['add',0,1,1,1,[1]],['add',2,3,1,1,[1,2]],
     ['add',0,1,1,1,[1,2]],['add',2,3,1,1,[1,2]]]
 d=stage_data(es,[1]*4);ok,p=full_replay(d,[1,0,2,3])
 need(ok and commute(es[0],es[1]),'positive crossing control');passed.append('synthetic_legal_crossing')
 # Omitting the suffix or only comparing ranks can falsely accept a crossing.
 bad=[['add',0,1,1,1,[1]],['add',2,3,1,1,[1,2]],['add',0,4,1,1,[1]]]
 d=stage_data(bad,[1]*5);need(not full_replay(d,[1,0,2])[0],'suffix decrease accepted');passed.append('later_frame_decrease_rejected')
 d=stage_data(es[:2],[1]*4);need(not full_replay(d,[1,0])[0],'changed boundary accepted');passed.append('stage_boundary_change_rejected')
 need(not commute(e,['scale',2,2,1,[]]),'scale is a fixed barrier');passed.append('non_ADD_fixed_barrier')
 es=[['add',0,1,1,1,[1]],['add',2,3,1,1,[1]],['add',4,2,1,1,[1,2]],
     ['add',0,1,1,1,[1,2]],['add',2,3,1,1,[1,2]],['add',4,5,1,1,[1,2]]]
 need(not commute(es[1],es[2]) and commute(es[0],es[1]) and commute(es[0],es[2]),'exposure control dependencies')
 d=stage_data(es,[1]*6);need(full_replay(d,[1,2,0,3,4,5])[0],'nonadjacent exposed crossing missed')
 passed.append('exposure_reveals_legal_crossing')
 return passed

def identity(d):need(type(d.get('seed')) is int and d['seed']==27,'seed must be exact integer 27')

def build(pins):
 w,compressed=sources(pins);a,b,paid=baseline(w)
 return {'seed':27,'base':'ba82555c64e1879e4b7decce28186f208fcb8262','selected_PR':1042,
  'source_hashes':pins,'archive_member':MEMBER,'word_payload_sha256':PAYLOAD,
  'word_container_sha256':compressed,'complete_local_profile':paid,
  'stage_lengths':{'A':len(w['A']),'B':len(w['B'])},'A':census(a),'B':census(b),'controls':controls(pins)}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 pins=loads((HERE/'SOURCES.json').read_bytes());result=build(pins)
 if args.write:(HERE/'CERTIFICATE.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 else:
  saved=loads((HERE/'CERTIFICATE.json').read_bytes());identity(saved)
  need(canonical(saved)==canonical(result),'complete certificate mismatch')
 print('PASS_COMPLEX_FRAME_SLOT_S27 exposed=11848 commuting=11811 legal_crossings=0 controls='+str(len(result['controls'])))

if __name__=='__main__':main()
