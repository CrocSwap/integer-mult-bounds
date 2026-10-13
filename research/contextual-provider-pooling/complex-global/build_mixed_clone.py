"""Five finite controller copies, interleaved at each source invocation; m stays73."""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,copy,gzip,hashlib,json,shutil
ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--owners',type=Path,required=True);ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
assert not a.out.exists();a.out.mkdir(parents=True)
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def dump(p,x):
 raw=json.dumps(x,sort_keys=True,separators=(',',':')).encode();p.write_bytes(gzip.compress(raw,mtime=0)if p.suffix=='.gz'else raw+b'\n');return hashlib.sha256(raw).hexdigest()
C=5;T0=8;T=40;V=112;D0=7168;DATA=D0*C
old=read(a.base/'split-centres/GLOBAL-TEMPLATE.json.gz');roles=read(a.owners);plan=read(a.plan)
assert len(old['calls'])==72 and plan['T']==8 and plan['M']==73 and len(roles)==36288
B=a.out/'base';shutil.copytree(a.base,B)
t=copy.deepcopy(old);oldlive=old['live'];newlive=oldlive*C;reserve=old['physical']-oldlive;assert reserve==514
# Dedicated bank controls remain five independent 8-replica banks, never one 40-replica bank.
def fam(f,c):
 if f<D0:return f+c*D0
 if f<oldlive:return DATA+(f-D0)+c*(oldlive-D0)
 return newlive+(f-oldlive)
t['calls']=[]
for oc in old['calls']:
 for cl in range(C):
  q=copy.deepcopy(oc);q['replica']+=8*cl;q['owners']=[[fam(f,cl),rt]for f,rt in q['owners']];t['calls'].append(q)
t['live']=newlive;t['physical']=newlive+reserve
for k,(l,u)in t['private_namespace'].items():t['private_namespace'][k]=[newlive+l-oldlive,newlive+u-oldlive]
for q in t['idle_children']:assert q['replicas']==8;q['replicas']=40
oldbank=old['bank_padding'];t['bank_padding']['families']=[fam(f,c)for c in range(C)for f in oldbank['families']]
t['bank_padding']['children']=[]
for c in range(C):
 for q in oldbank['children']:
  z=copy.deepcopy(q);z['family']=fam(q['family'],c);t['bank_padding']['children'].append(z)
t['cover_final_correction'].update(families=[0,newlive],charged_calls_per_cover=newlive)
for e in t['execution_schedule']:
 if 'replicas'in e:e['replicas']=list(range(T))
 if e['kind']=='bank_padding_cover_sweep':e['families']=[DATA,newlive]
 elif e['kind']=='translate_every_live_family':e.update(t['cover_final_correction'])
parent_hash=dump(B/'split-centres/GLOBAL-TEMPLATE.json.gz',t)
p=copy.deepcopy(plan)
for stale in ('patterns','stage_assignments','numeric_saving','solver_status','gap','numeric_saving_scope'):p.pop(stale,None)
p.update(T=40,live=DATA,deficit=12800,mode='five finite interleaved clones with one pooled remainder packet')
p['order']=[[s,r+8*c]for s,r in plan['order']for c in range(C)]
p['provider_for_call']={f'{s},{r+8*c}':plan['provider_for_call'][f'{s},{r}']for s,r in plan['order']for c in range(C)}
p['windows']={}
for k,(rank,times)in plan['windows'].items():
 r,i=map(int,k.split(','))
 for cl in range(C):p['windows'][f'{r+8*cl},{i}']=[rank,[5*t+c for t in times for c in range(C)]]
h=Counter({int(r):5*n for r,n in plan['profile'].items()});h[39]-=5;h[48]+=4;h[3]+=1;p['profile']={r:n for r,n in sorted(h.items())if n};assert 73*DATA-sum(r*n for r,n in h.items())==12800
out=[];witness=[]
for q in roles:
 for cl in range(C):
  z=copy.deepcopy(q);z['replica']+=8*cl;z['owner_replica']+=8*cl;z['family']+=D0*cl;z['copy']+=8*V*cl;z['time']=5*q['time']+cl
  if(q['owner_replica'],q['child'],q['port'])==(6,8,6):
   assert(q['time'],q['stage'],q['replica'],q['helper'],q['width'],q['offset'],q['family'])==(52,4,6,141,9,0,6054)
   z.update(owner_replica=6,family=6054,copy=678,offset=9*cl);witness.append(z)
  out.append(z)
out.sort(key=lambda z:(z['time'],z['helper']));assert len(witness)==5
# Literal independent width/time/whole-family check before the geometric auditor.
bycall=defaultdict(set);used=defaultdict(set)
for z in out:
 key=(z['stage'],z['replica']);assert z['family']not in bycall[key];bycall[key].add(z['family']);rank,times=p['windows'][f"{z['owner_replica']},{z['child']}"];assert z['time']in times
 k=(z['owner_replica'],z['child'],z['port']);cells=set(range(z['offset'],z['offset']+z['width']));assert max(cells)<rank and not used[k]&cells;used[k]|=cells
assert all(len(s)==504 for s in bycall.values()) and len(bycall)==360
for cells in used.values():assert cells==set(range(len(cells)))
ph=dump(a.out/'PLAN.json',p);oh=dump(a.out/'OWNERS.json.gz',out)
receipt={'status':'FIVE_FINITE_CLONES_LITERAL_RESOURCE_WITNESS','ambient_m':73,'replicas_per_clone':8,'clones':5,'calls':360,'helper_roles':len(out),'profile':p['profile'],'live':DATA,'deficit':12800,'pooled_roles':witness,'parent_semantic_sha256':parent_hash,'plan_semantic_sha256':ph,'owners_semantic_sha256':oh,'sources':{str(x.name):hashlib.sha256(x.read_bytes()).hexdigest()for x in [a.owners,a.plan,a.base/'split-centres/GLOBAL-TEMPLATE.json.gz']},'scope':'Literal resource construction; fresh full physical audit and finite scalar invoice required.'}
dump(a.out/'CLONE-CONSTRUCTION.json',receipt);print(json.dumps(receipt,indent=2))
