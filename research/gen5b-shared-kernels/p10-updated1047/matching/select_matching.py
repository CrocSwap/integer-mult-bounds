"""Original weighted-cardinality890 matching with minimum changed pairs.
Reads inert finite graph and canonical JSON. No upstream program executed.
Rank-greedy transversal selection fixes an optimal strictly rank-increasing
weight profile at cardinality890. Min-cost integral flow then maximizes old
exact pairs among matchings with that profile. Final residual potentials certify
cost optimality; sorted construction and heap ordering make ties deterministic.
"""
if not __debug__:raise RuntimeError('Assertions required')
from pathlib import Path
from collections import Counter,defaultdict
import json,hashlib,heapq,gzip
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import support
support.require_assertions()
P=support.out('matching','placeholder').parent;Q=P
w=support.read('bitword/selected/bit/word_p10.json.gz')
f=support.read('bitword/selected/bit/frames_p10.json.gz')['frames']
graph={int(d):sorted(rs)for d,rs in json.loads((Q/'postdescent_graph.json').read_text()).items()}
old=dict(w['pairs']);phase=set(w['phase1']);order=w['phase1']+[i for i in range(len(w['ops']))if i not in phase];last={};first={}
for t,i in enumerate(order):
 for r in w['ops'][i][:2]:last[r]=(t,w['op_frame'][i]);first.setdefault(r,t)
rank={d:f[str(last[d][1])]['dim']for d in graph}
assert len(graph)==4300 and sum(map(len,graph.values()))==18648
assert all(r in graph[d]for d,r in old.items())
assigned={}
def augment(d,seen):
 for r in graph[d]:
  if r in seen:continue
  seen.add(r)
  if r not in assigned or augment(assigned[r],seen):assigned[r]=d;return True
 return False
chosen=[]
for d in sorted(graph,key=lambda d:(-rank[d],d not in old,d)):
 if augment(d,set()):chosen.append(d)
assert len(chosen)==892
quotas=Counter(rank[d]for d in chosen[:890])
# Residual graph edge: [target, residual capacity, cost, reverse index].
N=2+len(quotas)+len(graph)+len({r for rs in graph.values()for r in rs});E=[[]for _ in range(N)];s=0;t=N-1
rn={r:1+i for i,r in enumerate(sorted(quotas))};dn={d:1+len(rn)+i for i,d in enumerate(sorted(graph))};recips=sorted({r for rs in graph.values()for r in rs});tn={r:1+len(rn)+len(dn)+i for i,r in enumerate(recips)}
def edge(a,b,cap,cost):
 i=len(E[a]);j=len(E[b]);E[a].append([b,cap,cost,j]);E[b].append([a,0,-cost,i]);return i
for r,c in quotas.items():edge(s,rn[r],c,0)
for d in sorted(graph):
 if rank[d]in rn:edge(rn[rank[d]],dn[d],1,0)
refs={}
for d in sorted(graph):
 for r in graph[d]:refs[d,r]=(dn[d],edge(dn[d],tn[r],1,int(old.get(d)!=r)))
for r in recips:edge(tn[r],t,1,0)
pot=[0]*N;cost=0
for flow in range(890):
 dist=[10**9]*N;dist[s]=0;previous={};queue=[(0,s)]
 while queue:
  dd,a=heapq.heappop(queue)
  if dd!=dist[a]:continue
  for i,(b,cap,c,rev)in enumerate(E[a]):
   if not cap:continue
   z=dd+c+pot[a]-pot[b]
   assert z>=dd
   if z<dist[b]:dist[b]=z;previous[b]=(a,i);heapq.heappush(queue,(z,b))
 assert dist[t]<10**9
 # Extend unreachable potentials by largest reached distance to retain a
 # globally feasible reduced-cost certificate over all residual edges.
 largest=max(x for x in dist if x<10**9)
 pot=[p+(d if d<10**9 else largest)for p,d in zip(pot,dist)]
 b=t
 while b!=s:
  a,i=previous[b];e=E[a][i];cost+=e[2];e[1]-=1;E[b][e[3]][1]+=1;b=a
selected=sorted([d,r]for(d,r),(a,i)in refs.items()if E[a][i][1]==0)
assert len(selected)==890 and len({d for d,r in selected})==len({r for d,r in selected})==890
assert Counter(rank[d]for d,r in selected)==quotas
reduced=[c+pot[a]-pot[b]for a,edges in enumerate(E)for b,cap,c,rev in edges if cap]
assert min(reduced)>=0 and cost==sum(old.get(d)!=r for d,r in selected)
new=dict(w);new['pairs']=selected;new['reads']=dict(w['reads'])
# Retain existing explicit reads, set newly paired recipient reads at first use.
for d,r in selected:
 if str(r)not in new['reads']:new['reads'][str(r)]=first[r]
raw=json.dumps(new,sort_keys=True,separators=(',',':')).encode()+b'\n';assert hashlib.sha256(raw).hexdigest()==support.WORD_SHA;assert raw==support.materialize_word().read_bytes();(P/'word_weighted890.json').write_bytes(raw)
report=dict(status='PASS_RANK_PROFILE_AND_EXACT_PAIR_MINCOST',head='1b37957d1520c80b6ea796bf418e52be5109c2d4',candidate_sha256=hashlib.sha256(raw).hexdigest(),graph_sha256=hashlib.sha256((Q/'postdescent_graph.json').read_bytes()).hexdigest(),graph_edges=18648,maximum_cardinality=892,selected_cardinality=890,donor_rank_histogram=dict(sorted(quotas.items())),retained_old_pairs=890-cost,changed_pairs=cost,minimum_residual_reduced_cost=min(reduced),old_recipients_removed=sorted(set(old.values())-{r for d,r in selected}),new_recipients_added=sorted({r for d,r in selected}-set(old.values())),checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),objective='Maximum sum(phi(20-d)-phi(17-d)) among cardinality890 matchings on cached exact graph via strictly rank-descending matroid greedy; then maximum original exact pairs for that optimal rank profile. Deterministic sorted-node/edge Dijkstra tie handling. No broader optimality claim.')
(P/'matching-result.json').write_text(json.dumps(report,indent=2)+'\n');(P/'matching-optimality-certificate.json').write_text(json.dumps(dict(rank_quotas=dict(quotas),potentials=pot,source=s,target=t,rank_nodes=rn,donor_nodes=dn,recipient_nodes=tn,pairs=selected))+'\n');print(json.dumps(report,indent=2))
