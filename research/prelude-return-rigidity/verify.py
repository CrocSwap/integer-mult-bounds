#!/usr/bin/env python3
"""Source-bound return-line certificate for twelve native preludes.

THU New Media Research Center (@thu-nmrc), with substantial OpenAI Codex
assistance. Apache-2.0. Source construction and prior first-image theorem
retain their attribution in PROOF.md.
"""
from collections import defaultdict,deque
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import gzip,json
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parents[1]/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
COMPRESSED='7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05'
PAYLOAD='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
def need(ok,why):
 if not ok:raise ValueError(why)
def span(b):
 s={0}
 for v in b:
  need(0<v<512 and v not in s,'independent 9-bit basis')
  s|={x^v for x in tuple(s)}
 return s
def roles(e):
 if e[0]!='scalar':return []
 g=e[1];return [r[1] for r in (g[1:3] if g[0] in ('add','copy') else g[1:2]) if r[0]=='L']
def skeleton(d,direction):
 p=[e for e in d['programs'][direction] if e[0]!='climb'];cur=[('entry',r) for r in range(632)];links=defaultdict(set)
 for i,e in enumerate(p):
  if e[0]=='scalar':
   for r in roles(e):links[cur[r],('scalar',i)].add(r);cur[r]=('scalar',i)
  elif e[0]=='warp':cur[e[1][1]]=('cut',i)
 for r in range(112,224):links[cur[r],('exit',r)].add(r)
 return p,links

def generate(d):
 c=d['canonical'];p,links=skeleton(d,'forward');adj=defaultdict(list)
 for a,b in links:adj[a].append(b)
 cases=[]
 for op in range(47,59):
  pre=next(i for i,e in enumerate(p) if e[0]=='warp' and e[2]==op and len(c['frames'][e[3]])==1);r=p[pre][1][1];inv=pre+5
  nex=next(i for i in range(inv+1,len(p)) if (p[i][0]=='warp' and p[i][1]==['L',r]) or r in roles(p[i]))
  need(p[nex][0]=='scalar','next persistent event scalar')
  start=('scalar',nex);q=deque([start]);paths={start:[start]};common=set(range(512));witnesses=[]
  while q and len(common)>2:
   n=q.popleft()
   if n[0]=='exit':
    out=n[1];B=c['frames'][c['final'][out]];new=common & span(B)
    if new!=common:
     normal=next(v for v in range(1,512) if all((v&x).bit_count()%2==0 for x in B));path=paths[n]
     witnesses.append({'nodes':path,'roles':[min(links[a,b]) for a,b in zip(path,path[1:])],'output_role':out,'normal':normal});common=new
   for n2 in adj[n]:
    if n2 not in paths:paths[n2]=paths[n]+[n2];q.append(n2)
  a=c['frames'][c['start'][r]][0]
  need(common=={0,a},'next contact forced input line')
  cases.append({'operator':op,'prelude':pre,'inverse':inv,'source_role':r,'next_scalar':nex,'input_vector':a,'witnesses':witnesses})
 return {'schema_version':1,'payload_sha256':PAYLOAD,'cases':cases}
def verify(d,cert):
 need(cert['payload_sha256']==PAYLOAD,'source payload')
 c=d['canonical'];need([r['operator'] for r in cert['cases']]==list(range(47,59)),'12 operator coverage');result={}
 for direction in ('forward','backward'):
  p,links=skeleton(d,direction);count=0;pathcount=0
  for case in cert['cases']:
   op,pre,inv,r,nex,a=[case[k] for k in ('operator','prelude','inverse','source_role','next_scalar','input_vector')]
   need(p[pre][:3]==['warp',['L',r],op] and p[inv][:3]==['warp',['L',r],-op] and inv==pre+5,'actual positive/inverse prelude')
   need(0<=r<112 and span(c['frames'][c['start'][r]])=={0,a},'fixed nonzero main X entrance')
   need(not any(e[0]=='warp' and e[1]==['L',r] for e in p[:pre]),'no earlier warp on main X owner')
   need(all(p[i][0]=='scalar' and r in roles(p[i]) for i in range(pre+1,inv)),'four scalar prelude contacts')
   need(nex>inv and p[nex][0]=='scalar' and r in roles(p[nex]),'following persistent scalar')
   need(not any((e[0]=='warp' and e[1]==['L',r]) or r in roles(e) for e in p[inv+1:nex]),'no intervening owner contact')
   normals=[];common=set(range(512));need(len(case['witnesses'])==8,'8 independent exits')
   for w in case['witnesses']:
    path=[tuple(n) for n in w['nodes']];owners=w['roles'];out=w['output_role'];normal=w['normal']
    need(112<=out<224 and path[0]==('scalar',nex) and path[-1]==('exit',out),'exact contact-to-main-Y path')
    need(len(path)==len(owners)+1,'one owner per literal edge')
    for u,v,owner in zip(path,path[1:],owners):need(owner in links.get((u,v),set()),'literal consecutive scalar contact path');count+=1
    B=c['frames'][c['final'][out]]
    need(len(B)==8 and 0<normal<512 and all((normal&v).bit_count()%2==0 for v in B),'exact independent main exit normal')
    normals.append(normal);common&=span(B);pathcount+=1
   need(len(span(normals))==256 and common=={0,a},'rank-8 normal matrix with forced kernel')
   direct={v for v in range(512) if all((v&n).bit_count()%2==0 for n in normals)}
   need(direct=={0,a},'independent 512-vector kernel')
  result[direction]={'operators':12,'paths':pathcount,'literal_links':count}
 return result

def load_source(raw=None):
 raw=SOURCE.read_bytes() if raw is None else raw
 need(sha256(raw).hexdigest()==COMPRESSED,'compressed source')
 data=gzip.decompress(raw)
 need(sha256(data).hexdigest()==PAYLOAD,'canonical source')
 return json.loads(data)

def run(write=False):
 d=load_source()
 cert=json.loads(json.dumps(generate(d)))
 if write:
  (HERE/'CERTIFICATE.json').write_text(json.dumps(cert,indent=2,sort_keys=True)+'\n')
 else:
  need(json.loads((HERE/'CERTIFICATE.json').read_text())==cert,'deterministic source certificate')
 result=verify(d,cert)
 controls=[]
 mutations=[
  ('wrong_input',lambda z:z['cases'][0].__setitem__('input_vector',1)),
  ('wrong_edge_owner',lambda z:z['cases'][0]['witnesses'][0]['roles'].__setitem__(0,999)),
  ('missing_normal',lambda z:z['cases'][0]['witnesses'].pop()),
  ('wrong_normal',lambda z:z['cases'][0]['witnesses'][0].__setitem__('normal',1)),
  ('wrong_inverse',lambda z:z['cases'][0].__setitem__('inverse',6327)),
  ('wrong_next_contact',lambda z:z['cases'][0].__setitem__('next_scalar',9068)),
 ]
 for name,mutate in mutations:
  bad=deepcopy(cert);mutate(bad)
  try:verify(d,bad)
  except ValueError:controls.append(name)
  else:raise ValueError('corruption accepted: '+name)
 try:load_source(SOURCE.read_bytes()+b'\0')
 except ValueError:controls.append('changed_source_bytes')
 else:raise ValueError('changed source accepted')
 rec={'status':'PASS_12_INVERSE_PRELUDE_OUTPUT_LINES_FORCED_BY_MAIN_EXITS',
      'source_compressed_sha256':COMPRESSED,'source_payload_sha256':PAYLOAD,
      'directions':result,'rejected_controls':controls,
      'scope':'Fixed scalar chronology and monotone persistent contacts; exact paired G/G^-1 preludes, fixed main endpoints. No improved kappa or supplier admission.'}
 if write:(HERE/'RESULT.json').write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
 else:need(rec==json.loads((HERE/'RESULT.json').read_text()),'deterministic result')
 return rec

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 print(json.dumps(run(args.write),sort_keys=True))
