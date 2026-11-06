#!/usr/bin/env python3
"""Review only the frozen proportional-pair census, via earlier independent SSA.
Jerry Chen / @CubeJerry, substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter,defaultdict
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
import gzip,inspect,importlib.util,json,itertools,sys
B=Path(sys.argv[1]).resolve()
OWN=Path(sys.argv[2]).resolve()if len(sys.argv)>2 else Path(__file__).resolve().parents[1]/'native-span-review'/'review.py'
CENSUS=Path(sys.argv[3]).resolve()if len(sys.argv)>3 else B/'tmp/b2/CENSUS.json'
SOURCE=Path(sys.argv[4]).resolve()if len(sys.argv)>4 else B/'research/p104-distributed-carrier-recoding/inputs/PR6702-WORD.json.gz'
OUTPUT=Path(sys.argv[5]).resolve()if len(sys.argv)>5 else Path(__file__).with_name('REVIEW.json')
if sha256(OWN.read_bytes()).hexdigest()!='b6004f9b0a14e952f6bee15214682585a180e5961e12231ac96e36e743f177f0':raise ValueError('Pinned independent SSA source')
spec=importlib.util.spec_from_file_location('independent_A_forward',OWN);A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
# Expose already computed SSA responses, without changing any algorithm.
ns=dict(A.__dict__);src=inspect.getsource(A.build).replace('return cs,residences,len(edges),len(monitors)','return cs,residences,adj,after,writes,reads')
exec(compile(src,str(OWN),'exec'),ns)
source=SOURCE
A.need(sha256(source.read_bytes()).hexdigest()=='e8c7a9d54d98a4cfa27e15593016b3908afed303e0f480076ed3f596192e5a4d','Native source pin')
w=json.loads(gzip.decompress(source.read_bytes()));program=w['program'];n=w['public'];N=n+w['owned_fields'];P=A.P
intervals,residences,adj,after,writes,reads=ns['build'](w)
lookup={(x['role'],x['first'],x['second']):x for x in intervals}
# Independent exact old-input replay: compare every retained normalized row,
# not merely a modular hash of that row.
rows=[{r:Q(1)}if r<n else{}for r in range(N)];at=defaultdict(list)
for x in intervals:at[x['first']].append(x)
groups=defaultdict(list)
for i,e in enumerate(program):
 for c in at[i]:
  v=rows[c['role']];A.need(v,'Nonzero rational held row');unit=v[min(v)]
  c['normalization']=str(unit);c['rowkey']=tuple((r,z/unit)for r,z in sorted(v.items()));groups[c['rowkey']].append(c)
 op,r=e[:2]
 if op in ('INIT','CLEAR'):rows[r]={}
 elif op=='SCALE':rows[r]={j:z*Q(e[2])for j,z in rows[r].items()}
 elif op in ('ADD','COPY'):
  if op=='COPY':A.need(not rows[r],'Exact COPY-zero premise')
  for j,z in rows[e[2]].items():
   z=rows[r].get(j,Q(0))+Q(e[3])*z
   if z:rows[r][j]=z
   else:rows[r].pop(j,None)
census=json.loads(CENSUS.read_text())
expected={}
for cl in census['classes']:
 key=tuple((r,Q(z))for r,z in cl['normalized_held_row'])
 for c in cl['members']:expected[c['role'],c['first'],c['second']]=(key,c['normalization'])
A.need(set(expected)==set(lookup),'Entire eligible interval census')
for k,c in lookup.items():A.need((c['rowkey'],c['normalization'])==expected[k],'Every exact held old-input row')
pairs=[]
for cl in groups.values():
 for a,b in itertools.combinations(sorted(cl,key=lambda x:x['first']),2):
  A.need(a['role']==b['role'],'Every proportional pair uses one held helper')
  A.need(a['second']<=b['first'],'Shared or disjoint MOVE windows')
  r=a['role'];i=a['first'];j=b['second']
  A.need(all(program[z][0]in('MOVE','SCALE')for z in writes[r]if i<z<j),'No held-source feedback')
  pairs.append((a,b))
cp={(x['role'],x['first'],x['middle_left'],x['middle_right'],x['last']):x for x in census['pairs']}
A.need(len(cp)==len(pairs)==122,'Complete proportional pair count')
receipts=[];counts=Counter();dots=0;controls=0
for a,b in pairs:
 r=a['role'];i=a['first'];j=b['second'];shared=a['second']==b['first'];lo=a['lo'];hi=b['hi']
 ck=(r,i,a['second'],b['first'],j);c=cp[ck]
 oldmoves=sorted({a['first'],a['second'],b['first'],b['second']})
 ranks=[len(w['frames'][program[z][3]])-len(w['frames'][program[z][2]])for z in oldmoves]
 A.need(all(x>0 for x in ranks),'Positive paid body transports')
 A.need(ranks==c['paid_ranks_before'],'Shared MOVE billed exactly once')
 newranks=[len(w['frames'][b['G']])-len(w['frames'][a['E']])]if shared else[len(w['frames'][a['G']])-len(w['frames'][a['E']]),len(w['frames'][b['G']])-len(w['frames'][b['E']])]
 A.need(newranks==c['paid_ranks_after'],'New full paid ranks match actual endpoints')
 exports=[z for z in reads[r]if i<z<j]if shared else a['exports']+b['exports']
 A.need(all(program[z][0]=='ADD'for z in exports),'ADD-only removed exports')
 target={}
 for z in exports:
  coefficient=A.q(program[z][3])
  for zz in writes[r]:
   if i<zz<z and program[zz][0]=='SCALE':coefficient=coefficient*A.q(program[zz][2])%P
  A.add(target,adj[after[z]],coefficient)
 # Forward-generated full residence columns; no B generator or solver imported.
 if shared:
  low=max([lo]+[z+1 for z in reads[r]if lo<=z<i]);high=min([hi]+[z for z in reads[r]if j<z<hi]);bounds=[(low,high)]
  windows=[('A',a['E'],lo,high),('E',b['G'],low,hi)]
 else:
  middle=[z for z in reads[r]if a['second']<z<b['first']]
  A.need(middle and a['G']==b['E'],'Retained middle-frame contract')
  low=max([lo]+[z+1 for z in reads[r]if lo<=z<i]);high=min(middle)
  low2=max(middle)+1;high2=min([hi]+[z for z in reads[r]if j<z<hi]);bounds=[(low,high),(low2,high2)]
  A.need(high<low2,'Cut order forced by retained reads')
  windows=[('A',a['E'],lo,high),('C',a['G'],low,high2),('E',b['G'],low2,hi)]
 nodes=[]
 for rr,left,right,frame,node in residences:
  if rr==r or not adj[node]:continue
  for kind,f,l,h in windows:
   u,v=max(left,l),min(right,h)
   if frame==f and u<=v:nodes.append((u,v,kind,A.key(adj[node])))
 axes=[{l,h}for l,h in bounds]
 for l,h,kind,v in nodes:
  if shared:axes[0].add(l if kind=='A'else h)
  elif kind=='A':axes[0].add(l)
  elif kind=='E':axes[1].add(h)
  else:axes[0].add(h);axes[1].add(l)
 axes=[sorted(z for z in axis if lo<=z<=hi)for axis,(lo,hi)in zip(axes,bounds)]
 for cuts in itertools.product(*axes):
  t1=cuts[0];t2=cuts[-1]
  columns=[dict(v)for v in sorted({v for l,h,kind,v in nodes if (kind=='A'and l<=t1)or(kind=='E'and h>=t2)or(kind=='C'and l<=t2 and h>=t1)})]
  lam=A.dual(columns,target);A.need(lam is not None,'Every frozen pair system separated')
  A.need(A.dual_ok(lam,columns,target),'Direct separating-functional dot products')
  if not controls:
   pivot=next(iter(lam));bad=target.copy();A.add(bad,{pivot:1},pow(lam[pivot],-1,P))
   A.need(not A.dual_ok({},columns,target),'Reject zero dual')
   A.need(not A.dual_ok(lam,columns+[{pivot:1}],target),'Reject enlarged carrier inventory')
   A.need(not A.dual_ok(lam,columns,bad),'Reject changed response target')
   controls=3
  dots+=len(columns)+1;counts['shared_systems'if shared else'disjoint_systems']+=1
  receipts.append({'role':r,'first':i,'last':j,'cuts':cuts,'dual':lam,'columns':len(columns)})
 counts['shared_pairs'if shared else'disjoint_pairs']+=1
A.need(dict(counts)=={'shared_systems':439,'shared_pairs':108,'disjoint_systems':248,'disjoint_pairs':14},'Frozen source census and system counts')
result={'source_sha256':sha256(source.read_bytes()).hexdigest(),'reviewed_census_sha256':sha256(CENSUS.read_bytes()).hexdigest(),'independent_ssa_source_sha256':sha256(OWN.read_bytes()).hexdigest(),'eligible_intervals':len(intervals),'projective_classes':len(groups),'class_size_counts':dict(Counter(len(x)for x in groups.values())),'counts':counts,'direct_dot_products':dots,'mutation_controls':controls,'dual_certificates':receipts,'scope':'Exact fixed-source proportional-pair resident span; paid-stop pilots excluded'}
out=OUTPUT;out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in result.items()if k!='dual_certificates'},indent=2,sort_keys=True));print('PASS_INDEPENDENT_PROPORTIONAL_PAIR_CENSUS_AND_DUALS')
