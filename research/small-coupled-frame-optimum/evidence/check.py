"""Independent verification of fixed-C and cut1..3 DP certificates.
No author domain/factor/Price/solver implementation is imported. No emitter.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from functools import lru_cache
from hashlib import sha256
import importlib.util,itertools,json,sys
HERE=Path(__file__).resolve().parent
ZERO=(0,)*10;PENALTY=(0,5328)+(0,)*8;C=Q(15108879,5000000000)
def need(x,m):
 if not x:raise ValueError(m)
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def delta(a,b):return tuple(x-y for x,y in zip(a,b))
def sem(x):
 if isinstance(x,dict):return {k:sem(v)for k,v in x.items()if k not in('runtime_seconds','total_runtime_seconds')}
 if isinstance(x,list):return [sem(v)for v in x]
 return x
@lru_cache(None)
def image(cols,S):
 out=0
 while S:
  bit=S&-S;x=bit.bit_length()-1;S-=bit;y=0
  for j,c in enumerate(cols):
   if x>>j&1:y^=c
  out|=1<<y
 return out
def dim(S):return S.bit_count().bit_length()-1
def span(basis):
 points={0}
 for v in basis:points|={x^v for x in tuple(points)}
 return sum(1<<x for x in points)
def valid_space(S):
 need(S&1 and S.bit_length()<=512,'subspace range/zero')
 basis=[];generated=1
 for v in range(1,512):
  if S>>v&1 and not generated>>v&1:basis.append(v);generated=span(basis)
 need(generated==S,'subspace closure');return len(basis)
def domain_check(vals,L,H,source):
 d=valid_space(H)-valid_space(L);want=0
 for k in range(d+1):
  n=Q(1)
  for i in range(k):n*=Q((1<<(d-i))-1,(1<<(k-i))-1)
  need(n.denominator==1,'Gaussian cardinality');want+=int(n)
 need(len(vals)==len(set(vals))==want,'complete unique quotient domain')
 for S in vals:valid_space(S);need(S&L==L and S&H==S,'domain containment')
 need(source in vals,'source domain fallback')
def inventory(actual,record):
 need(len(actual)==record['factor_multiedges'] and sha256(json.dumps(actual,separators=(',',':')).encode()).hexdigest()==record['edge_sha256'],'factor inventory mismatch')
def expect_bad(fn,text):
 try:fn()
 except ValueError as e:need(text in str(e),'intended independent rejection');return True
 raise ValueError('Independent mutation accepted')

def main():
 f=HERE/'frozen'
 for n in ('FIXED-C-FILES.json','CUT-FILES.json'):
  for name,h in json.loads((f/n).read_text()).items():need(sha256((f/name).read_bytes()).hexdigest()==h,'author freeze '+name)
 pin=json.loads((HERE/'EXTRA-SOURCE.json').read_text());need(sha256((HERE/'interval_source.py').read_bytes()).hexdigest()==pin['sha256'],'independent interval source')
 probe=load('independent_dp_source',HERE/'source/inspect_graph.py');data,construct,frame=probe.load()
 E=load('independent_dp_intervals',HERE/'interval_source.py')
 weights={0:(Q(0),Q(0)),1:(Q(1),Q(1))}
 weights.update({r:E.power(r,1-C)for r in range(2,10)})
 def interval(h):
  lo=hi=Q(0)
  for r,n in enumerate(h):
   a,b=weights[r];lo+=n*(a if n>=0 else b);hi+=n*(b if n>=0 else a)
  need(lo<=hi,'signed enclosure order');return lo,hi
 @lru_cache(None)
 def fixedsign(h):
  if h==ZERO:return 0
  a,b=interval(h);need(b<0 or a>0,'independent unresolved fixed-C comparison');return -1 if b<0 else 1
 fixed=json.loads((f/'RESULT.json').read_text());need(sem(fixed)==sem(json.loads((f/'OPTIMIZED.json').read_text())),'fixed normal/O semantics')
 need(fixed['C']==str(C),'exact fixed C')
 for r,ends in fixed['comparison']['final_weight_bounds_rational'].items():
  a,b=map(Q,ends);l,u=weights[int(r)];need(a<=l<=u<=b,'independent finer power enclosure containment')
 need(len(fixed['comparison']['certificates'])==119,'119 stored strict comparisons')
 for record in fixed['comparison']['certificates']:
  need(fixedsign(tuple(record['difference_histogram']))==record['sign'],'independent comparison certificate')
 summary=json.loads((f/'cuts-normal/SUMMARY.json').read_text());need(summary['status']=='STOP_LOWER_CUT_FOUND_NO_ALL_CONCAVE_CEILING'and set(summary['objectives'])=={'1','2','3'},'authorized stop exactly k3')
 need(sem(summary)==sem(json.loads((f/'cuts-optimized/SUMMARY.json').read_text())) or
      {k:v['directions']for k,v in summary['objectives'].items()}=={k:v['directions']for k,v in json.loads((f/'cuts-optimized/SUMMARY.json').read_text())['objectives'].items()},'cut summary normal/O')
 cases=[('fixed',None,fixed)]+[(f'cut{k}',k,json.loads((f/f'cuts-normal/CUT-{k}.json').read_text()))for k in (1,2,3)]
 controls={};output={};message_states=0;proof_checks=0;badarg_done=False;unary_done=False
 for direction,sourceword in data['programs'].items():
  program,_,_=construct(sourceword);schedule=frame.NativeSchedule(data['canonical'],program);g=schedule.graph;L,H=g.bounds();original=schedule.original_values
  edges=[(a,b,i,tuple(cols))for b,ps in enumerate(g.parents)for i,(a,cols)in enumerate(ps)]
  need(len(edges)==29790 and all(a!=b for a,b,_,_ in edges),'all mapped edge inventory/no self factors')
  variable={v for v in range(len(L))if L[v]!=H[v]};adj={v:set()for v in variable}
  for a,b,_,_ in edges:
   if a in variable and b in variable:adj[a].add(b);adj[b].add(a)
  unseen=set(variable);derived=[]
  while unseen:
   todo=[unseen.pop()];component=set(todo)
   while todo:
    for w in adj[todo.pop()]&unseen:unseen.remove(w);component.add(w);todo.append(w)
   derived.append(frozenset(component))
  need(len(derived)==19 and sorted(map(len,derived))==[1]*8+[2]*3+[3]*3+[9,10,11,15,1271],'independent components')
  expected_components={x for x in derived if len(x)<1271};expected_small=set().union(*expected_components)
  need(len(expected_small)==68,'independent small component scope')
  def full_hist(values):
   h=list(ZERO);h[8]=8
   for v,pinned in enumerate(g.fixed):need(pinned is None or values[v]==pinned,'prescribed boundary')
   for a,b,ei,cols in edges:
    need(image(cols,values[a])&values[b]==image(cols,values[a]),'full mapped containment')
    r=dim(values[b])-dim(values[a]);need(r>=0,'full nonnegative rank')
    if r:h[r]+=1
   return tuple(h)
  old=full_hist(original);need(sum(r*n for r,n in enumerate(old))==5327,'source rankmass')
  for label,k,result in cases:
   if k:
    need(sem(result)==sem(json.loads((f/f'cuts-optimized/CUT-{k}.json').read_text())),'cut normal/O semantics')
    need(result['objective']['k']==k,'actual integer objective')
    compare=lambda x,y: (sum(n*min(r,k)for r,n in enumerate(delta(x,y)))>0)-(sum(n*min(r,k)for r,n in enumerate(delta(x,y)))<0)
   else:compare=lambda x,y:fixedsign(delta(x,y))
   rec=result['directions'][direction];D={int(v):list(map(int,vals))for v,vals in rec['all_domains'].items()};small=set(D)
   need(small==expected_small and {frozenset(x['nodes'])for x in rec['components']}==expected_components and len(rec['components'])==18,'exact independent small scope/partition')
   for v,vals in D.items():domain_check(vals,L[v],H[v],original[v])
   values=list(original);totalstates=0
   for component in rec['components']:
    comp=set(component['nodes']);order=component['order'];need(set(order)==comp and len(order)==len(comp),'complete order')
    factors=[];ids=[]
    for a,b,ei,cols in edges:
     if a not in comp and b not in comp:continue
     scope=tuple(sorted(v for v in(a,b)if v in comp));table={}
     for ix in itertools.product(*(range(len(D[v]))for v in scope)):
      env={v:D[v][j]for v,j in zip(scope,ix)};av=env.get(a,original[a]);bv=env.get(b,original[b]);moved=image(cols,av)
      if moved&bv==moved:
       r=dim(bv)-dim(av);need(r>=0,'feasible edge rank');table[ix]=tuple(int(i==r and r>0)for i in range(10))
      else:table[ix]=PENALTY
     factors.append((scope,table));ids.append([a,b,ei,list(cols)])
    inventory(ids,component)
    if not unary_done:
     unary=next(i for i,(scope,table)in enumerate(factors)if len(scope)==1)
     controls['missing_unary_inventory_rejected']=expect_bad(lambda:inventory(ids[:unary]+ids[unary+1:],component),'factor inventory');unary_done=True
    controls['missing_edge_inventory_rejected']=expect_bad(lambda:inventory(ids[1:],component),'factor inventory')
    trace=component['traceback'];need(len(trace)==len(order),'trace length');active=list(factors);records=[];states=0
    for v,t in zip(order,trace,strict=True):
     need(v==t[0],'trace order');bucket=[x for x in active if v in x[0]];active=[x for x in active if v not in x[0]]
     sep=tuple(sorted({w for scope,tab in bucket for w in scope}-{v}));need(list(sep)==t[1],'actual separator')
     choices={tuple(ix):j for ix,j in t[2]};keys=list(itertools.product(*(range(len(D[w]))for w in sep)))
     need(set(choices)==set(keys),'complete separator choices');table={}
     for ix in keys:
      env=dict(zip(sep,ix));costs=[]
      for j in range(len(D[v])):
       env[v]=j;h=ZERO
       for scope,tab in bucket:h=add(h,tab[tuple(env[w]for w in scope)])
       costs.append(h);states+=1
      arg=choices[ix];need(0<=arg<len(costs),'trace choice domain');chosen=costs[arg]
      def validate_choice(j):
       for other in costs:need(compare(costs[j],other)<=0,'nonoptimal argmin')
      validate_choice(arg);proof_checks+=len(costs)
      if not badarg_done:
       bad=next((j for j,x in enumerate(costs)if compare(x,chosen)>0),None)
       if bad is not None:controls['nonoptimal_trace_choice_rejected']=expect_bad(lambda:validate_choice(bad),'nonoptimal argmin');badarg_done=True
      table[ix]=chosen
     active.append((sep,table));records.append((v,sep,choices))
    need(all(not scope for scope,tab in active),'all variables eliminated');opt=ZERO
    for scope,tab in active:opt=add(opt,tab[()])
    need(list(opt)==component['histogram'],'independent message optimum histogram')
    indices={}
    for v,sep,ch in reversed(records):indices[v]=ch[tuple(indices[w]for w in sep)]
    need(indices=={int(v):j for v,j in component['assignment_indices'].items()},'independent reverse traceback')
    direct=ZERO;source_h=ZERO
    for scope,tab in factors:
     direct=add(direct,tab[tuple(indices[v]for v in scope)])
     source_h=add(source_h,tab[tuple(D[v].index(original[v])for v in scope)])
    need(direct==opt and list(source_h)==component['source_histogram'],'direct factors versus messages/source')
    for v,j in indices.items():values[v]=D[v][j]
    need(states==component['bucket_states'],'exact bucket states');totalstates+=states
   need(totalstates==1095,'all small bucket states');message_states+=totalstates
   need(all(values[v]==original[v]for v in range(len(values))if v not in small),'big/determined frozen source')
   need({str(v):str(values[v])for v in small}==rec['assignment'],'complete chosen assignment')
   need([v for v in sorted(small)if values[v]!=original[v]]==rec['changed_nodes'],'exact changed-node census')
   full=full_hist(values);need(list(full)==rec['optimal_full_histogram']and list(old)==rec['original_histogram'],'full histogram equality')
   need(sum(r*n for r,n in enumerate(full))==5327,'candidate rankmass')
   if not k:need(full==old,'fixed-C source histogram optimum')
   output[label+'_'+direction]={'full_histogram':list(full),'prefix_differences':[sum(n*min(r,j)for r,n in enumerate(delta(full,old)))for j in range(1,10)],'changed_nodes':len(rec['changed_nodes']),'states_verified':totalstates,'all_containments':29790}
  # This tests the actual containment predicate with an incorrect retained map,
  # not a claim that the author reran a mutated optimization.
  a,b,ei,cols=next(e for e in edges if image(e[3],original[e[0]])&original[e[1]]==image(e[3],original[e[0]])and original[e[0]]&original[e[1]]!=original[e[0]])
  controls['map_identity_wrong_containment_witness']=[a,b]
  tampered=list(old);r=next(i for i,n in enumerate(old)if i and n);tampered[r]-=1
  controls['wrong_full_histogram_rejected']=expect_bad(lambda:need(tuple(tampered)==old,'full histogram mismatch'),'full histogram')
 need(badarg_done and unary_done,'meaningful mutation controls reached')
 expected=(0,2223,421,490,132,40,0,0,8,0)
 need(all(tuple(output['cut3_'+d]['full_histogram'])==expected for d in data['programs']),'exact k3 witness')
 h=delta(expected,tuple(fixed['directions']['forward']['original_histogram']));need(h==(0,22,9,-20,5,0,0,0,0,0),'k3 delta')
 lo,hi=interval(h);need(lo>0,'k3 witness is worse at fixed C')
 result={'status':'PASS_FIXED_C_AND_K3_DISTINCT_RESULTS','C':str(C),'independent_message_states_verified':message_states,'argmin_alternatives_checked':proof_checks,'author_solver_imported':False,'author_price_imported':False,'domain_completeness':'All actual domains unique/contained/closed and Gaussian cardinality/source inclusion verified','independent_interval_source':pin,'strict_author_comparisons_validated':119,'results':output,'meaningful_independent_controls':controls,'k3_fixed_C_paid_cost_increase':E.display((lo,hi)),'all_concave_ceiling':False,'cuts4_to8_executed':False,'physical_emitter':False,'new_kappa':None}
 print(json.dumps(result,indent=2,sort_keys=True))
 if '--emit'in sys.argv:(HERE/'REVIEW-RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
