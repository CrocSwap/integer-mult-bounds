"""Independent vectorized audit of the literal staged-pair owner journal.

No optimizer, producer, inherited owner checker or reconstructor is imported.
Uses the source execution template and the actual checked native frame tables.
"""
from pathlib import Path
from collections import Counter
import gzip,hashlib,json,os
import numpy as np
for key in ('OWNER_SOURCE_REPO','OWNER_LITERAL_DIR','OWNER_NATIVE_DIR','OWNER_PREDECESSOR_DIR','OWNER_AUDIT_OUTPUT'):
 if not os.environ.get(key):raise ValueError('missing '+key)
A=Path(os.environ['OWNER_LITERAL_DIR']).resolve()
NATIVE=Path(os.environ['OWNER_NATIVE_DIR']).resolve()
PARENT=Path(os.environ['OWNER_PREDECESSOR_DIR']).resolve()
S=Path(os.environ['OWNER_SOURCE_REPO']).resolve()/'research/rank7-joint-endframes/allocation/vendor'
def need(v,m):
 if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def rank(v):
 piv={}
 for q in v:
  while q:
   h=q.bit_length()
   if h in piv:q^=piv[h]
   else:piv[h]=q;break
 return len(piv)
paths=[A/n for n in ('COMPOSED-FILL.json.gz','ORDER.json','DISPATCH.json','PROFILE.json')]+[S/'PLAN.json.gz',S/'TEMPLATE.json.gz']
paths += [NATIVE/f'checked-{p}/CANONICAL-WORD.json.gz' for p in ('base','extra')]
pins={str(p):sha(p) for p in paths}
order=read(paths[1]);dispatch=read(paths[2]);profile={int(k):v for k,v in read(paths[3]).items()};plan=read(paths[4]);template=read(paths[5])
T=740;N=9*T
need(len(order)==N and len(set(map(tuple,order)))==N,'call coverage')
clock={tuple(call):t for t,call in enumerate(order)}
need(set(clock)=={(s,r) for s in range(9) for r in range(T)},'exact source calls')
need(all([clock[s,r] for s in range(9)]==sorted(clock[s,r] for s in range(9)) for r in range(T)),'per-replica order')
D={(s,r):p for s,r,p in dispatch};need(len(dispatch)==N and set(D)==set(clock),'dispatch coverage')
need(Counter(D.values())=={'gauge44':2500,'extra':4160},'provider count')
# Reconstruct source windows per replica from the actual source event sequence.
children={x['child']:x['rank'] for x in template['idle_children']};K=max(children)+1
cap=np.zeros((T,K),dtype=np.int64);lo=np.full((T,K),N,dtype=np.int64);hi=np.full((T,K),-2,dtype=np.int64)
local_pair={x['stage']:x['pair'] for x in template['recipe'] if x['kind']=='local'}
for r in range(T):
 touched={};t=None
 for ev in template['execution_schedule']:
  kind=ev['kind']
  if kind in ('bank_padding_cover_sweep','translate_every_live_family'):continue
  if kind=='local_cover_sweep':
   t=clock[ev['stage'],r];touched[local_pair[ev['stage']]]=t
  elif kind=='bridge':
   need(t is not None,'bridge source');touched[ev['src']]=t;touched[ev['dst']]=t
  elif kind=='idle_cover_sweep':
   need(t is not None,'idle source')
   for c in ev['child_indices']:
    if c in children:
     need(cap[r,c]==0,'unique source child');cap[r,c]=children[c];lo[r,c]=touched.get(ev['pair'],-1);hi[r,c]=t
  else:need(kind in ('terminal_Y_translations','terminal'),'known source event')
need(np.all(cap[:,list(children)]>0),'all source windows')
fam=np.full(K,-1,np.int64)
for c in children:fam[c]=2*plan['pairs'][str(c)]+plan['sides'][str(c)]
widths={};L=None
for tag,pid in [('base','gauge44'),('extra','extra')]:
 w=read(NATIVE/f'checked-{tag}/CANONICAL-WORD.json.gz')
 need(w['R']==408 and len(w['zero_buffers'])==91,'native helper stock')
 widths[pid]=np.array([rank(w['frames'][w['final'][224+h]])-rank(w['frames'][w['start'][224+h]]) for h in range(408)],dtype=np.int64)
 need(Counter(widths[pid])=={4:26,5:2,6:18,7:52,8:97,9:213},'actual native widths')
 loc={int(k):v for k,v in w['local_profile'].items()}
 need(L is None or L==loc,'common actual native bill');L=loc
need(L=={1:2439,2:726,3:224,4:102,5:20,8:8},'new local bill')
bycall=np.stack([widths[D[tuple(call)]] for call in order])
j=read(A/'COMPOSED-FILL.json.gz');need(j['columns']==['time','helper','owner_replica','child','port','offset'] and j['dispatch_overrides']==[],'journal schema')
need(all(len(row)==6 and all(type(v) is int for v in row) for row in j['rows']),'literal integer roles')
rows=np.array(j['rows'],dtype=np.int64);del j
need(rows.shape==(N*408,6),'literal role shape')
need(np.array_equal(rows[:,0],np.repeat(np.arange(N),408)) and np.array_equal(rows[:,1],np.tile(np.arange(408),N)),'complete literal ordered helper identities')
t,h,o,c,p,z=rows.T
need(np.all((o>=0)&(o<T)&(c>=0)&(c<K)&(p>=0)&(p<112)),'owner bounds')
need(np.all(cap[o,c]>0),'declared source child')
need(np.all((lo[o,c]<t)&(t<=hi[o,c])),'strict/closed actual source windows')
family=o*896+fam[c]*112+p
call_stage=np.array([s for s,r in order],dtype=np.int64)
call_replica=np.array([r for s,r in order],dtype=np.int64)
call_pair=np.array([local_pair[int(s)] for s in call_stage],dtype=np.int64)
need(np.all((o!=call_replica[t]) | ((fam[c]//2)!=call_pair[t])), 'active local pair excluded from helper owners')
key=t*(896*T)+family
sort=np.sort(key);need(np.all(sort[1:]!=sort[:-1]),'same-call physical family uniqueness')
w=bycall[t,h];need(np.all((z>=0)&(z+w<=cap[o,c])),'actual widths and capacity')
binid=(o*K+c)*112+p
idx=np.lexsort((t,binid));bins=binid[idx];ws=w[idx];starts=np.r_[True,bins[1:]!=bins[:-1]]
cs=np.cumsum(ws,dtype=np.int64)-ws;baseline=np.maximum.accumulate(np.where(starts,cs,0));expected=cs-baseline
need(np.array_equal(z[idx],expected),'every chronological pending mask is a compact prefix')
used=np.zeros(T*K*112,np.int64);np.add.at(used,binid,w)
allcap=np.repeat(cap.reshape(-1),112);valid=allcap>0
need(np.all(used[~valid]==0) and np.all(used<=allcap),'full used-bin mass')
idle=Counter(map(int,(allcap-used)[valid]));idle.pop(0,None)
H=Counter({r:n*N for r,n in L.items()});H.update(idle)
need(dict(H)==profile and sum(r*n for r,n in H.items())==65088*T,'independent complete histogram')
# Small semantic predicates test each independent gate on actual changed inputs.
controls=[]
def reject(name,test):
 need(not test(), 'control accepted '+name);controls.append(name)
reject('duplicate helper',lambda: np.array_equal(np.r_[rows[0,1],rows[:-1,1]],np.tile(np.arange(408),N)))
reject('strict lower endpoint used as available',lambda: bool(lo[o[0],c[0]]<lo[o[0],c[0]]<=hi[o[0],c[0]]))
reject('same-call family reused',lambda: len({int(family[0]),int(family[0])})==2)
reject('unpaid chronological hole',lambda: int(z[idx[0]])+1==int(expected[0]))
bad=dict(profile);bad[1]+=1;reject('one unpaid rank1 child',lambda:dict(H)==bad)
# Independently restrict the entire change to the five announced role destinations.
parent_dir=PARENT
parent_path=parent_dir/'COMPOSED-FILL.json.gz'
need(hashlib.sha256(gzip.decompress(parent_path.read_bytes())).hexdigest()=='653085641ff2e9470e25aedfc92861ec34e5cf594d52123e8b28b6f0ec20b9f8','complete predecessor literal payload')
parent=np.array(read(parent_path)['rows'],dtype=np.int64)
need(np.array_equal(parent[:,:2],rows[:,:2]),'all call/helper identities unchanged')
changed=np.flatnonzero(np.any(parent[:,2:5]!=rows[:,2:5],axis=1))
expected_moves={16544:[22,6,111],16545:[25,6,111],16546:[135,6,26],130613:[703,12,0],1355192:[18,15,111]}
need(set(map(int,changed))==set(expected_moves),'exact five changed owners')
for index,dest in expected_moves.items():need(rows[index,2:5].tolist()==dest,'literal destination binding')
for n in ('ORDER.json','DISPATCH.json','PROVIDERS.json'):
 need((A/n).read_bytes()==(parent_dir/n).read_bytes(),'unchanged '+n)
all_changed=np.flatnonzero(np.any(parent!=rows,axis=1))
need(len(all_changed)==24,'24 total changed literal rows')
oldH={1:16417896,2:4835160,3:1540174,4:679321,5:143992,6:3,8:53280,48:283185}
actual_delta={k:H.get(k,0)-oldH.get(k,0) for k in set(H)|set(oldH) if H.get(k,0)!=oldH.get(k,0)}
need(actual_delta=={1:-4,4:-1,5:1,6:-3,7:3},'independently derived whole histogram delta')
need(all(sha(Path(p))==v for p,v in pins.items()),'input drift')
result={'status':'PASS_INDEPENDENT_LITERAL_OWNER_WINDOWS_FAMILIES_PREFIXES_AND_INVOICE','replicas':T,'calls':N,'roles':len(rows),'physical':896*T+509,'idle':dict(sorted(idle.items())),'profile':dict(sorted(H.items())),'input_sha256':pins,'script_sha256':sha(Path(__file__)),'controls':controls,'scope':'Independent finite vectorized audit; no producer, solver, retained owner checker or reconstructor imports. Actual native frames are authenticated input data; their separate full operator proofs are required.'}
Path(os.environ['OWNER_AUDIT_OUTPUT']).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:result[k] for k in ('status','roles','idle','profile')},indent=2))
