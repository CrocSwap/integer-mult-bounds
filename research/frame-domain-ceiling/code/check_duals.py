"""Verify every frame-domain LP dual using exact arithmetic only."""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import argparse,gzip,json,sys,copy,hashlib,importlib.util,time
ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--frozen-prefix',type=int,default=0);ap.add_argument('--mutant',choices=['drop_component','inflate_dual','alter_domain','accepted_endpoint']);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
root=Path(__file__).resolve().parent.parent;src=root/'vendor/static44';sys.path.insert(0,str(src/'gk'));import gk_word as G;import gk_common as C
G.V=C.V=112;G.DATA=C.DATA=7168
w=json.load(gzip.open(a.source));original=copy.deepcopy(w);raw=json.load(gzip.open(src/'inputs/RAW504.json.gz'));frozen_prefix=len(w['A'])-len(raw['A']) if a.frozen_prefix is None else a.frozen_prefix;V=112;N=224+w['report']['R']
engine=root/'engines/moment.py'
sp=importlib.util.spec_from_file_location('price',engine);M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
sp=importlib.util.spec_from_file_location('other',root/'engines/base_two_moment.py');Other=importlib.util.module_from_spec(sp);sp.loader.exec_module(Other)
assert a.frozen_prefix==0
assert hashlib.sha256(a.source.read_bytes()).hexdigest()=='dac4d6d6ad99208d3d50c640acb2f82e81ddaa1dc97a29da758353fd3bd49fa9'
P=root
certificates=json.load(gzip.open(P/'data/DUALS.json.gz'))
if a.mutant=='drop_component':certificates.pop()
if a.mutant=='inflate_dual':certificates[0]['dual'][0][0]=str(Q(certificates[0]['dual'][0][0])+1)
if a.mutant=='alter_domain':certificates[0]['domains'][str(certificates[0]['nodes'][0])].pop()
endpoint=Q('0.001594507308884431019638')
if a.mutant=='accepted_endpoint':endpoint-=Q(1,10**24)
exact={r:M.moment({r:1},73,7168,endpoint,True) for r in range(1,10)}
second={}
fl,fu=Other.moment(73,7168,[(1,32*73*73)],endpoint)
for r in range(1,10):
 l,u=Other.moment(73,7168,[(r,1)],endpoint);second[r]=(l+fl/Q(10**16),u+fu/Q(10**16))
@lru_cache(None)
def nonnegative(v):
 if not any(v):return True
 cs={r:v[r-2] for r in range(2,10)};cs[1]=-sum(r*v[r-2] for r in range(2,10))
 for engine in [exact,second]:
  lo=Q(0)
  for r,n in cs.items():
   l,u=engine[r];lo+=n*(l if n>=0 else u)
  if lo<0:return False
 return True
@lru_cache(None)
def span(F):return frozenset(G.span(F))
@lru_cache(None)
def basis(F):return G.basis(F)
FULL=G.FULL;nodes=[];chains=[[] for _ in range(N)];mutable=[]
def node(regs,F,sec,index=None):
 k=len(nodes);nodes.append(dict(regs=regs,F=basis(tuple(F)),section=sec,index=index))
 for r in regs:chains[r].append(k)
 if sec in ('A','B') and not(sec=='A' and index<frozen_prefix):mutable.append(k)
for r in range(N):
 F=[w['ports'][r]] if r<V else w.get('start_extra',{}).get(str(r),[]) if r>=2*V else w.get('target_levels',{}).get(str(r-V),[])
 node([r],F,'start')
for sec in ('A','B'):
 if sec=='B':
  for r,F in zip(w['centers'],w['center_frames']):node([r],F,'cut')
  for t in range(V):node([V+t],w.get('target_levels',{}).get(str(t),[]),'cut')
 for i,e in enumerate(w[sec]):node([e[1]]+([e[2]] if e[0]=='add' else []),e[-1],sec,i)
for r in range(N):node([r],FULL if r<V or r>=2*V else G.perp(w['ports'][r-V]),'end')
prev={};nxt={}
for r,ch in enumerate(chains):
 for p,q in zip(ch,ch[1:]):prev[q,r]=p;nxt[p,r]=q;assert span(nodes[p]['F'])<=span(nodes[q]['F'])

allowed=set(mutable);lower={};upper={}
for k,z in enumerate(nodes):
 F=basis(tuple(x for r in z['regs'] for x in lower[prev[k,r]])) if k in allowed else z['F']
 for r in z['regs']:
  if (k,r) in prev:assert span(lower[prev[k,r]])<=span(F)
 lower[k]=F
for k in reversed(range(len(nodes))):
 z=nodes[k]
 if k in allowed:
  U=set(span(FULL))
  for r in z['regs']:U.intersection_update(span(upper[nxt[k,r]]))
  F=basis(tuple(U))
 else:F=z['F']
 for r in z['regs']:
  if (k,r) in nxt:assert span(F)<=span(upper[nxt[k,r]])
 upper[k]=F
 assert span(lower[k])<=span(z['F'])<=span(F)

from collections import defaultdict,deque
var={k for k in mutable if lower[k]!=upper[k]};adj=defaultdict(set)
for (k,r),j in prev.items():
 if k in var and j in var:adj[k].add(j);adj[j].add(k)
components=[];remaining=set(var)
while remaining:
 root=min(remaining);q=[root];remaining.remove(root);component=[]
 while q:
  k=q.pop();component.append(k)
  for j in adj[k]&remaining:remaining.remove(j);q.append(j)
 components.append(component)

@lru_cache(None)
def domains(k):
 L,U=lower[k],upper[k];extras=[];current=L
 for v in U:
  if v not in span(current):extras.append(v);current=basis(tuple(current)+(v,))
 d=len(extras);assert d<=3
 spaces={()}
 for v in range(1,1<<d):spaces|={basis(S+(v,)) for S in list(spaces)}
 def lift(v):
  z=0
  for i,x in enumerate(extras):
   if v>>i&1:z^=x
  return z
 result=sorted({basis(tuple(L)+tuple(lift(v) for v in S)) for S in spaces})
 assert nodes[k]['F'] in result and all(span(L)<=span(F)<=span(U) for F in result)
 return result
edges=Counter((j,k) for (k,r),j in prev.items());history=[];initial=G.profile(w);began=time.monotonic()
assert len(components)==len(certificates)==71
for no,component in enumerate(sorted(components,key=lambda z:(-len(z),min(z)))):
 cert=certificates[no];assert cert['component']==no and set(cert['nodes'])==set(component) and len(cert['nodes'])==len(component);component=cert['nodes']
 cset=set(component);ds={k:domains(k) for k in component};coef=[];integrality=[];vectors=[];xids={};rows=[];cols=[];values=[];rhs=[]
 def variable(c,integer,profile=None):
  idx=len(coef);coef.append(c);integrality.append(integer);vectors.append({r:n for r,n in (profile or {}).items() if r>1});return idx
 def equality(xs,b):
  row=len(rhs);rhs.append(b)
  for j,v in xs:rows.append(row);cols.append(j);values.append(v)
 for k in component:
  xids[k]=[variable(0,1) for F in ds[k]];equality([(x,1) for x in xids[k]],1)
 for (p,q),mult in edges.items():
  if p not in cset and q not in cset:continue
  if p in cset and q in cset:
   outp=[[] for F in ds[p]];inq=[[] for F in ds[q]]
   for i,F in enumerate(ds[p]):
    for j,H in enumerate(ds[q]):
     if span(F)<=span(H):
      z=variable(0,0,{len(H)-len(F):mult});outp[i].append((z,1));inq[j].append((z,1))
   for i,x in enumerate(xids[p]):equality(outp[i]+[(x,-1)],0)
   for j,x in enumerate(xids[q]):equality(inq[j]+[(x,-1)],0)
  else:
   k=p if p in cset else q
   fixed=nodes[q if k==p else p]['F'];assert (q if k==p else p) not in var
   for j,F in enumerate(ds[k]):
    l,h=(F,fixed) if k==p else (fixed,F);assert span(l)<=span(h)
    rank=len(h)-len(l)
    if rank>1:vectors[xids[k][j]][rank]=vectors[xids[k][j]].get(rank,0)+mult
 assert cert['domains']=={str(k):[list(F) for F in ds[k]] for k in component}
 assert cert['constraints']==len(rhs) and cert['variables']==len(coef)
 dual=[[Q(x) for x in row] for row in cert['dual']];assert len(dual)==len(rhs) and all(len(row)==8 for row in dual)
 columns=[[] for _ in coef]
 for i,j,z in zip(rows,cols,values):assert z in (-1,1);columns[j].append((i,z))
 t=time.monotonic()
 # Exactly verify every reduced cost from the nominated rational linear forms.
 reduced=[]
 for j in range(len(coef)):
  v=[Q(vectors[j].get(r,0)) for r in range(2,10)]
  for i,z in columns[j]:
   v=[x-z*y for x,y in zip(v,dual[i])]
  reduced.append(tuple(v))
 objective=tuple(sum((Q(rhs[i])*dual[i][r] for i in range(len(rhs))),Q(0)) for r in range(8));baseline=Counter()
 for (p,q),mult in edges.items():
  if p in cset or q in cset:
   rank=len(nodes[q]['F'])-len(nodes[p]['F'])
   if rank>1:baseline[rank]+=mult
 assert objective==tuple(Q(baseline[r]) for r in range(2,10)),('objective polynomial differs',no,objective,baseline)
 assert all(nonnegative(v) for v in set(reduced)),('invalid reduced cost',no)
 history.append(dict(component=no,nodes=len(component),constraints=len(rhs),variables=len(coef),reduced_costs=len(set(reduced)),objective=[str(x) for x in objective]))
 print('PASS exact component',no,'nodes',len(component),flush=True)
# Variable frame differences telescope on each complete register chain. The
# central served-level charges, boundaries and owner remainders are fixed.
graph=Counter()
for (p,q),mult in edges.items():
 rank=len(nodes[q]['F'])-len(nodes[p]['F'])
 if rank:graph[rank]+=mult
constant={r:initial[r]-graph[r] for r in set(initial)|set(graph)};assert all(n>=0 for n in constant.values())
assert sum(r*n for r,n in graph.items())==sum(len(nodes[ch[-1]]['F'])-len(nodes[ch[0]]['F']) for ch in chains)
source=json.loads((P/'data/PR551-EXPECTED.json').read_text());assert {str(r):n for r,n in initial.items()}==source['complex_local_profile']
profile={int(r):n for r,n in source['complex_global_profile'].items()};remainder={r:profile.get(r,0)-72*initial.get(r,0) for r in set(profile)|set(initial)};assert all(n>=0 for n in remainder.values())
lo,hi=M.moment(profile,73,7168,endpoint,True);ll,uu=Other.moment(73,7168,list(profile.items()),endpoint);fl,fu=Other.moment(73,7168,[(1,32*73*73*sum(profile.values()))],endpoint);ll+=fl/Q(10**16);uu+=fu/Q(10**16)
assert lo>1 and ll>1,'the proposed ceiling does not exclude the admitted baseline'
balanced_upper=endpoint/(1+endpoint);published_k=Q('0.001591968902833346');next_k=published_k+Q(1,10**18)
assert published_k<balanced_upper<next_k
r=dict(retained_outer_kappa_upper=str(balanced_upper),excluded_next_kappa=str(next_k),status='PASS_COMPLETE_FIXED_WORD_FRAME_CEILING',excluded_b=str(endpoint),excluded_b_decimal='0.001594507308884431019638',source_word_sha256=hashlib.sha256(a.source.read_bytes()).hexdigest(),source_pr551_commit='e7faafc4fec401d24080e5b2df12f964f1cfe123',mutable_events=len(mutable),variable_events=len(var),components=len(components),graph_rank_mass=sum(r*n for r,n in graph.items()),fixed_center_profile={r:n for r,n in constant.items() if n},local_profile=dict(initial),global_profile=profile,owner_remainder={r:n for r,n in remainder.items() if n},strict_excess_intervals={'mercator':[str(lo-1),str(hi-1)],'base_two':[str(ll-1),str(uu-1)]},duals=history,scope='Every legal simultaneous frame reassignment over this fixed scalar word, starts, central cut, endpoints, width signatures and owner schedule. No scalar rewrites, new helpers, new cuts, owner repacking, alternative bad-class charges or outer theorem changes are covered. No improved kappa or universal bound is claimed.')
(a.out/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['excluded_b_decimal'],flush=True)
