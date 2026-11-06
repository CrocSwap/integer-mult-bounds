"""Separate exact forward-SSA reconstruction; imports no primary generator.

Algorithmic lineage: forward SSA review in #6765/#6767. Reimplemented here over
Q, with direct old-input row ratios for combined targets and certificate-only
dot tests. Jerry Chen / @CubeJerry, substantial OpenAI Codex assistance.
Apache-2.0. Same-session implementation independence, not external acceptance.
"""
from collections import Counter,defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import gzip,json,sys
HERE=Path(__file__).resolve().parent
PIN='e8c7a9d54d98a4cfa27e15593016b3908afed303e0f480076ed3f596192e5a4d'
def require(condition,message):
 if not condition:raise ValueError(message)
def accumulate(a,b,factor=1):
 for k,value in b.items():
  z=a.get(k,Q(0))+factor*value
  if z:a[k]=z
  elif k in a:del a[k]
def serial(vector):return[[k,str(v)]for k,v in sorted(vector.items())]
def digest(value):return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def decode(vector):return{k:Q(v)for k,v in vector}
def witness_ok(witness,columns,target):
 return sum(witness.get(k,0)*v for k,v in target.items())==1 and all(sum(witness.get(k,0)*v for k,v in col.items())==0 for col in columns)

def exact_rows(word):
 program,n=word['program'],word['public'];N=n+word['owned_fields']
 writes=defaultdict(list);reads=defaultdict(list)
 for position,operation in enumerate(program):
  writes[operation[1]].append(position)
  if operation[0]in('ADD','COPY'):reads[operation[2]].append(position)
 excluded=set(word['live'])|{r+112 for r in word['live']};intervals=[]
 for role in range(n):
  if role in excluded:continue
  history=writes[role]
  for at,first in enumerate(history):
   if program[first][0]!='MOVE':continue
   following=at+1
   while following<len(history)and program[history[following]][0]=='SCALE':following+=1
   if following==len(history)or program[history[following]][0]!='MOVE':continue
   last=history[following];exports=[z for z in reads[role]if first<z<last]
   if not exports:continue
   require(all(program[z][0]=='ADD'for z in exports),'Independent ADD-export domain')
   before=at-1
   while before>=0 and program[history[before]][0]=='SCALE':before-=1
   after=following+1
   while after<len(history)and program[history[after]][0]=='SCALE':after+=1
   intervals.append(dict(role=role,first=first,last=last,lo=history[before]+1 if before>=0 else 0,
                         hi=history[after]if after<len(history)else len(program),exports=exports))
 at_first=defaultdict(list)
 for interval in intervals:at_first[interval['first']].append(interval)
 export_positions={z for interval in intervals for z in interval['exports']}
 state=[{r:Q(1)}if r<n else{}for r in range(N)];source_rows={};export_rows={};copies=0
 for position,instruction in enumerate(program):
  for interval in at_first[position]:
   row=state[interval['role']];require(row,'Independent nonzero held row');factor=row[min(row)]
   interval['normalization']=str(factor);interval['rowkey']=tuple((k,str(v/factor))for k,v in sorted(row.items()))
   source_rows[position]=row.copy()
  if position in export_positions:export_rows[position]=state[instruction[2]].copy()
  op,dst=instruction[:2]
  if op in('INIT','CLEAR'):state[dst]={}
  elif op=='SCALE':
   factor=Q(instruction[2]);require(factor!=0,'Independent nonzero SCALE')
   state[dst]={k:v*factor for k,v in state[dst].items()}
  elif op in('ADD','COPY'):
   require(dst!=instruction[2],'Independent no self update')
   if op=='COPY':require(not state[dst],'Independent exact COPY-zero');copies+=1
   accumulate(state[dst],state[instruction[2]],Q(instruction[3]))
 expected=[{r:Q(1)}if r<n else{}for r in range(N)]
 for r in word['live']:expected[r+112][r]=Q(1)
 require(state==expected,'Independent exact full source endpoint')
 groups=defaultdict(list)
 for interval in intervals:groups[interval['rowkey']].append(interval)
 return intervals,groups,writes,reads,source_rows,export_rows,copies

def forward_graph(word):
 program,n=word['program'],word['public'];N=n+word['owned_fields'];edges=[]
 def node(parents=()):edges.append(tuple(parents));return len(edges)-1
 state=[node()for _ in range(n)]+[None]*(N-n);frames=word['initial'][:]+[None]*(N-n);start=[0]*N
 residence=[];post={};monitors=[];copies=sum(e[0]=='COPY'for e in program)
 for position,instruction in enumerate(program):
  op,dst=instruction[:2];affected=[dst]
  if op in('ADD','COPY'):affected.append(instruction[2])
  for role in affected:
   if frames[role]is not None:residence.append((role,start[role],position,frames[role],state[role]))
   start[role]=position+1
  if op=='INIT':
   require(state[dst]is None and frames[dst]is None,'Independent fresh owned INIT')
   frames[dst]=instruction[2];state[dst]=node()
  elif op=='CLEAR':
   require(frames[dst]==instruction[2],'Independent CLEAR residence');frames[dst]=None;state[dst]=None
  elif op=='MOVE':
   require(frames[dst]==instruction[2],'Independent MOVE source frame')
   frames[dst]=instruction[3];state[dst]=node(((state[dst],Q(1)),))
  elif op=='SCALE':
   require(frames[dst]==instruction[3],'Independent SCALE residence')
   state[dst]=node(((state[dst],Q(instruction[2])),))
  elif op in('ADD','COPY'):
   src=instruction[2];require(frames[dst]==frames[src]==instruction[4],'Independent ADD/COPY residence')
   olddst,oldsrc=state[dst],state[src]
   if op=='COPY':monitors.append((olddst,n+copies-1-len(monitors)))
   state[dst]=node(((olddst,Q(1)),(oldsrc,Q(instruction[3]))));state[src]=node(((oldsrc,Q(1)),))
  else:raise ValueError(op)
  post[position]=state[dst]
 for role in range(N):
  if frames[role]is not None:residence.append((role,start[role],len(program),frames[role],state[role]))
 require(frames==word['final']+[None]*(N-n),'Independent final residence and owned release')
 responses=[{}for _ in edges]
 for role in range(n):
  if word['final'][role]!=127:responses[state[role]][role]=Q(1)
 for oldnode,label in monitors:responses[oldnode][label]=Q(1)
 for current in range(len(edges)-1,-1,-1):
  for parent,factor in edges[current]:accumulate(responses[parent],responses[current],factor)
 residence=[(r,l,h,f,responses[v])for r,l,h,f,v in residence]
 return residence,responses,post,len(edges),len(monitors)

def check():
 raw=(HERE/'inputs/PR6702-WORD.json.gz').read_bytes();require(sha256(raw).hexdigest()==PIN,'Independent native source pin')
 word=json.loads(gzip.decompress(raw));receipt=json.loads((HERE/'CERTIFICATE.json').read_text())
 require(receipt['source_sha256']==PIN,'Receipt native binding')
 intervals,groups,writes,reads,source_rows,export_rows,copies=exact_rows(word)
 require((len(intervals),len(groups),dict(Counter(map(len,groups.values()))),copies)==(631,523,{1:429,2:80,3:14},1),'Independent complete projective census')
 require(digest(sorted(intervals,key=lambda c:(c['role'],c['first'],c['last'])))==receipt['census_sha256'],'Every exact rational held row and interval')
 residences,responses,post,ssa_nodes,monitors=forward_graph(word)
 require(digest(sorted((r,l,h,f,serial(v))for r,l,h,f,v in residences))==receipt['residence_sha256'],'All exact forward SSA residence responses')
 triples=[sorted(group,key=lambda c:c['first'])for group in groups.values()if len(group)==3]
 by_role={triple['role']:triple for triple in receipt['triples']}
 require(len(by_role)==len(triples)==14,'Complete independent triple set')
 dots=0;controls=0;positive=0;target_checks=0;topologies=0
 for members in triples:
  role=members[0]['role'];first=members[0]['first'];last=members[-1]['last'];record=by_role[role]
  require(all(c['role']==role for c in members)and all(a['last']==b['first']for a,b in zip(members,members[1:])),'Independent four-MOVE triple chain')
  lo,hi=members[0]['lo'],members[-1]['hi'];moves=[c['first']for c in members]+[last]
  frames=[word['program'][first][2]]+[word['program'][z][3]for z in moves]
  require(all(word['program'][z][0]in('MOVE','SCALE')for z in writes[role]if lo<=z<hi),'Independent no-feedback window')
  exports=sorted(z for c in members for z in c['exports'])
  require(exports==[z for z in reads[role]if first<z<last],'Independent complete deleted-export set')
  ranks=[len(word['frames'][word['program'][z][3]])-len(word['frames'][word['program'][z][2]])for z in moves]
  meta=dict(role=role,first=first,last=last,lo=lo,hi=hi,moves=moves,frames=frames,exports=exports,ranks_before=ranks,
            lower=max([lo]+[z+1 for z in reads[role]if lo<=z<first]),upper=min([hi]+[z for z in reads[role]if last<z<hi]))
  for key,value in meta.items():require(record[key]==value,'Independent triple metadata '+key)
  target={};source=source_rows[first];pivot=min(source)
  for z in exports:
   factor=export_rows[z][pivot]/source[pivot]
   require(export_rows[z]=={k:v*factor for k,v in source.items()},'Exact old-input row proportionality at every export')
   instruction=word['program'][z];response=responses[post[z]]
   accumulate(target,response,Q(instruction[3])*factor)
   # Reinsert at this exact old residence, in the original full-frame path.
   candidates=[v for r,l,h,f,v in residences if r==instruction[1]and l<=z<=h and f==instruction[4]]
   require(response in candidates,'Independent full-frame chronological reinsertion control')
   frame_index=frames.index(instruction[4])
   require(moves[frame_index-1]<z<moves[frame_index],'Export lies between its true source MOVEs')
  require(serial(target)==record['target'],'Independent exact combined target from row ratios');target_checks+=1;positive+=1
  witness_by_omission={w['omitted_frame_index']:w for w in record['witnesses']}
  require(set(witness_by_omission)=={1,2,3},'All three maximal omissions')
  inventories={}
  for omitted in(1,2,3):
   witness_record=witness_by_omission[omitted];allowed={f for k,f in enumerate(frames)if k!=omitted}
   columns={tuple(sorted(v.items()))for r,l,h,f,v in residences if r!=role and v and f in allowed and l<=hi and h>=lo}
   inventories[omitted]=columns;columns=[dict(v)for v in sorted(columns)]
   require(len(columns)==witness_record['column_count'],'Independent column count')
   require(digest([serial(v)for v in columns])==witness_record['columns_sha256'],'Every independent maximal-inventory response')
   witness=decode(witness_record['dual']);require(witness_ok(witness,columns,target),'Independent rational separating dot products')
   dots+=len(columns)+1
   k=next(iter(witness));bad=target.copy();accumulate(bad,{k:Q(1)/witness[k]})
   require(not witness_ok({},columns,target),'Independent zero-witness negative control')
   require(not witness_ok(witness,columns+[{k:Q(1)}],target),'Independent changed-inventory control')
   require(not witness_ok(witness,columns,bad),'Independent changed-target control');controls+=3
  topology_records={tuple(t['retained_frame_indices']):t for t in record['covered_topologies']}
  expected_keeps={(0,*inside,4)for count in range(3)for inside in combinations((1,2,3),count)}
  require(set(topology_records)==expected_keeps,'All seven proper retained-frame topologies')
  for keep,topology in topology_records.items():
   omitted=topology['separator_omits'];require(omitted not in keep and omitted in(1,2,3),'Applicable maximal omission')
   allowed={frames[k]for k in keep};columns={tuple(sorted(v.items()))for r,l,h,f,v in residences if r!=role and v and f in allowed and l<=hi and h>=lo}
   require(columns<=inventories[omitted],'Independent universal column-subset reduction')
   expected=[len(word['frames'][frames[b]])-len(word['frames'][frames[a]])for a,b in zip(keep,keep[1:])]
   require(topology['ranks_after']==expected and sum(expected)==sum(ranks),'Independent unique-MOVE transport invoice');topologies+=1
 require((dots,controls,positive,target_checks,topologies)==(receipt['rational_dot_products'],receipt['mutation_controls'],14,14,98),'Complete independently checked totals')
 return dict(source_sha256=PIN,arithmetic='exact rational',primary_imports=0,eligible_intervals=len(intervals),projective_classes=len(groups),
             triples=len(triples),ssa_nodes=ssa_nodes,residences=len(residences),copy_monitors=monitors,rational_dot_products=dots,
             mutation_controls=controls,exact_combined_targets=target_checks,chronological_reinsertion_controls=positive,covered_topologies=topologies)

if __name__=='__main__':
 result=check()
 if len(sys.argv)>1:Path(sys.argv[1]).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print('PASS_FORWARD_SSA_RATIONAL_TRIPLE_REVIEW',json.dumps(result,sort_keys=True))
