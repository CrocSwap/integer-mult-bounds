"""Fixed-sixths rejection and fresh literal-primitive replay; no gxcore certificate.

The two gx modules are unchanged upstream PR402 leaves. This additive diagnostic
preserves their rejection, distinguishes clean-X E5 from dirty E7, and independently
replays the separately admitted literal compiler's exact HALF/divide3 expansion.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
from collections import Counter
from math import lcm
import copy,gzip,importlib.util,json,os,sys
if not __debug__:raise RuntimeError('Assertions are required')
sys.dont_write_bytecode=True
sha=lambda p:sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
def rational_replay(c,inputs):
 n=2*c['v']+c['R'];v=c['v'];rows=[{r:Q(1)} if r in inputs else {} for r in range(n)]
 stats={k:dict(denominator_lcm=1,max_absolute=Q(0),max_numerator=0) for k in 'xys'}
 for r in inputs:
  k='x' if r<v else 'y' if r<2*v else 's';stats[k]['max_absolute']=Q(1);stats[k]['max_numerator']=1
 term_lcm=1;first=None;writes=0
 def ax(t,src,q,where,source):
  nonlocal term_lcm,first,writes
  kind='x' if t<v else 'y' if t<2*v else 's'
  for key,u in list(src.items()):
   contribution=q*u;before=rows[t].get(key,Q(0));after=before+contribution
   term_lcm=lcm(term_lcm,contribution.denominator)
   if first is None and (6*contribution).denominator!=1:
    first=dict(where=where,target=t,source=source,input_column=key,source_value=str(u),literal_coefficient=str(q),contribution=str(contribution),target_before=str(before),target_after=str(after))
   if after:rows[t][key]=after
   else:rows[t].pop(key,None)
   a=stats[kind];a['denominator_lcm']=lcm(a['denominator_lcm'],after.denominator);a['max_absolute']=max(a['max_absolute'],abs(after));a['max_numerator']=max(a['max_numerator'],abs(after.numerator));writes+=1
 for phase in ['A','B']:
  if phase=='B':
   totals={k:dict(rows[r]) for k,r,f in c['ret']}
   for t,terms in enumerate(c['scat']['table']):
    for k,a,b in terms:ax(v+t,totals[k],Q(a,b),['scatter',t,k],['retained',k])
  for i,g in enumerate(c[phase]):
   for j,(r,a,b) in enumerate(g[3]):
    t,s=(r,g[2]) if g[0]=='out' else (g[2],r)
    ax(t,dict(rows[s]),Q(a,b),[phase,i,j],s)
 for a in stats.values():a['max_absolute']=str(a['max_absolute'])
 return rows,dict(stats_by_role=stats,contribution_denominator_lcm=term_lcm,first_outside_sixths=first,sparse_entry_updates=writes,input_columns=len(inputs))
def run(source404,gx_source,shared_long,candidate,fresh_full,output):
 SOURCE,G,SHARED_LONG,CANDIDATE,FULL,OUT=map(lambda p:Path(p).resolve(),[source404,gx_source,shared_long,candidate,fresh_full,output])
 assert not OUT.exists(), 'Use a fresh diagnostic output directory'
 fixed={'gx.py':'6f3dc8bb639933227a8dae181ec4a542e85c7276be9c9e330f49518e7b630b95','gxcore.py':'eb972c06fe8c322db2d9a8d9a7d05596e8f40c4ca8e5f42eb6df3c7361b5d517'}
 assert all(sha(G/n)==h for n,h in fixed.items())
 native={'local/local_admit.py':'55e56591261f5bb23e0badc78376ff55ca427a658859fe4bd661f46855c6cba3','local/deps/complex_labels.py':'e000ee131389fec427388b85f632879cbaaf10e5e5d979a47d6307d64ce58982','local/deps/complex_scalars.py':'39b44fff410747d7ba96d6527bd38294cf78e62dd2d8d4055849b6dd72358af6','local/deps/complex_splice.py':'4fd7e0c9aa825a6bd40c5053c715a6efad0653c0947287fc9b90a56e52b5f8fd','local/coefficient_words.py':'5c6cdaf446ad217068fee6dbe9e5b21fabff504c64e408d5dd7a61159808904a'}
 assert all(sha(SOURCE/n)==h for n,h in native.items())
 bound_inputs={**{'source402/'+n:G/n for n in fixed},**{'derived411/'+n:SOURCE/n for n in native},'shared-long.json':SHARED_LONG,'candidate.json':CANDIDATE,'fresh/local/RESULT.json':FULL/'local/RESULT.json','fresh/local/LOCAL-PROGRAMS.json.gz':FULL/'local/LOCAL-PROGRAMS.json.gz','fresh/local/MINIMAL-PINS.json':FULL/'local/MINIMAL-PINS.json','fresh/banks/ADMISSION.json':FULL/'banks/ADMISSION.json','fresh/local/RECOMPUTED-K.json':FULL/'local/RECOMPUTED-K.json','fresh/local/COEFFICIENT-WORDS.json':FULL/'local/COEFFICIENT-WORDS.json','gx_domain.py':Path(__file__)}
 pins={name:sha(path) for name,path in bound_inputs.items()}
 sys.path.insert(0,str(G))
 import gx,gxcore
 assert Path(gx.__file__).resolve()==G/'gx.py' and Path(gxcore.__file__).resolve()==G/'gxcore.py'
 OUT.mkdir()
 def write(name,z):(OUT/name).write_text(json.dumps(z,sort_keys=True,indent=2)+'\n')
 results={}
 for name,path,pin in [
  ('shared_long',SHARED_LONG,'7ff1782ab6fa0b846d7b00f57a034c05cd64b286eb9c3215efb184d5e9511408'),
  ('shared_long_resynth',CANDIDATE,'eedfb5796c8b2b5b202a1e7fee2785b6b23cd1f017794d3f8ddb19c87bd0a384')]:
  assert sha(path)==pin;c=read(path);D=gxcore.normal(copy.deepcopy(c));v=c['v'];n=2*v+c['R']
  gx.check1(copy.deepcopy(c),scalar=True)
  try:gxcore.mirror(D)
  except gxcore.Reject as exc:rejection=str(exc)
  else:raise AssertionError('The unchanged fixed-sixths mirror must reject')
  assert rejection==('E5: an entry needs a denominator beyond sixths (register 275)' if name=='shared_long' else 'E5: an entry needs a denominator beyond sixths (register 208)')
  x_rejection=None
  try:
   xr,_=gxcore.replay(D,{r:{r:gxcore.SC} for r in range(v)})
  except gxcore.Reject as exc:
   x_rejection=str(exc)
  if name=='shared_long':
   assert x_rejection is None and all(xr[r]=={r:6} and xr[v+r]=={r:6} for r in range(v))
  else:assert x_rejection=='E5: an entry needs a denominator beyond sixths (register 208)'
  try:gxcore.replay(D,{r:{r:6} for r,f in D['ext']})
  except gxcore.Reject as exc:
   gauged_rejection=str(exc);assert gauged_rejection=='E5: an entry needs a denominator beyond sixths (register 275)'
  else:raise AssertionError('Expected gauged-only rejection')
  modes={}
  for mode,inputs in [('x_content',set(range(v))),('gauged_dirt',set(dict(c['ext']))),('all_raw_columns',set(range(n)))]:
   rows,detail=rational_replay(c,inputs)
   if mode=='x_content':assert all(rows[r]=={r:Q(1)} and rows[v+r]=={r:Q(1)} for r in range(v))
   elif mode=='gauged_dirt':assert all(not rows[v+r] for r in range(v))
   else:assert all(rows[v+t].get(r,Q(0))==0 for t in range(v) for r,f in c['ext'])
   modes[mode]=detail
  results[name]=dict(candidate_sha256=pin,gx_fraction_check='PASS',gxcore='REJECTED',gxcore_exact_rejection=rejection,unchanged_gxcore_x_content_replay='REJECTED' if x_rejection else 'PASS',unchanged_gxcore_x_content_rejection=x_rejection,unchanged_gxcore_gauged_dirt_replay='REJECTED',unchanged_gxcore_gauged_dirt_rejection=gauged_rejection,fraction_replays=modes)
  print(name,[(k,x['stats_by_role']) for k,x in modes.items()],flush=True)
 
 # Decode the actual fresh checked physical event list, independently execute its
 # emitted primitive expansion, and compare its exact bill and projection hashes.
 os.environ['CX_PINS']=str(FULL/'local/MINIMAL-PINS.json');sys.path.insert(0,str(SOURCE/'local/deps'))
 import complex_splice as S
 assert Path(S.__file__).resolve()==SOURCE/'local/deps/complex_splice.py', 'Run in a fresh process with the pinned compiler'
 local=read(FULL/'local/RESULT.json');payload=gzip.decompress((FULL/'local/LOCAL-PROGRAMS.json.gz').read_bytes());programs=json.loads(payload)
 assert sha256(payload).hexdigest()==local['local_programs_uncompressed_sha256']
 assert programs['candidate_sha256']==results['shared_long_resynth']['candidate_sha256']
 assert local['actual_nongauged_dirty_response_recomputed'] and local['raw_operator_matches_protected_blocks'] and local['helper_cleanup_subword_equal']
 assert not local['raw_operator_equals_same_entrance_nonY_baseline'] and sha(FULL/'local/RECOMPUTED-K.json')==local['recomputed_response_sha256']
 actual_K=read(FULL/'local/RECOMPUTED-K.json');assert len(actual_K)==local['recomputed_response_entries']==7057
 coefficient=read(FULL/'local/COEFFICIENT-WORDS.json');assert coefficient['status']=='PASS_LITERAL_COEFFICIENT_WORDS'
 for source,digest in local['source_hashes'].items():assert sha(Path(source))==digest
 lowered={}
 for ori,events in programs['local_programs'].items():
  rows={('L',r):{r:Q(1)} for r in range(1021)};count=Counter();coefs=Counter();den=1;maxnum=1;mx=Q(1);term_den=1;trace=sha256();projection=sha256()
  def observe(row):
   nonlocal den,maxnum,mx
   for value in row.values():den=lcm(den,value.denominator);maxnum=max(maxnum,abs(value.numerator));mx=max(mx,abs(value))
  for event in events:
   if event[0]=='center':
    projection.update((json.dumps(('main',('recursive_center',event[1],event[4])),separators=(',',':'))+'\n').encode());continue
   if event[0]!='scalar':continue
   _,phase,e,f=event;projection.update((json.dumps((phase,e),separators=(',',':'))+'\n').encode())
   if e[0]=='add':
    q=Q(e[3],e[4]);assert abs(q.numerator) in (1,2) and q.denominator in (1,2,3,4,6,8);coefs[str(q)]+=1
   for op in S.lower_scalar(e):
    trace.update((json.dumps((phase,op),separators=(',',':'))+'\n').encode());name=op[0];t=tuple(op[1]);count[name]+=1
    if name=='clear':rows[t]={}
    elif name=='copy':rows[t]=dict(rows.get(tuple(op[2]),{}))
    elif name in ('double','halve','divide3'):
     scale={'double':Q(2),'halve':Q(1,2),'divide3':Q(1,3)}[name];rows[t]={k:a*scale for k,a in rows[t].items()}
    elif name=='accumulate':
     for k,a in list(rows[tuple(op[2])].items()):
      z=rows.setdefault(t,{}).get(k,Q(0))+op[3]*a
      if z:rows[t][k]=z
      else:rows[t].pop(k,None)
    else:raise AssertionError(name)
    observe(rows[t])
   if e[0]=='add':assert not rows[('W',0)]
  want={('L',r):{r:Q(1)} for r in range(1021)}
  for t in range(120):want[('L',120+t if ori=='forward' else t)][t if ori=='forward' else 120+t]=Q(1 if ori=='forward' else -1)
  assert all(rows[k]==z for k,z in want.items()) and all(not row for k,row in rows.items() if k[0]!='L')
  check=local['local_checks'][ori];bill=local['bills'][ori]['totals']
  assert trace.hexdigest()==check['scalar_primitive_sha256'] and projection.hexdigest()==check['scalar_projection_sha256']
  assert sum(count.values())==check['Gaussian_primitives']==bill['Gaussian_primitive_steps']
  assert count['halve']==bill['halving_exposure'] and count['divide3']==bill['divisor3_exposure']
  lowered[ori]=dict(raw_independent_columns=1021,dirty_helpers=781,endpoint_restored=True,private_streams_zero=True,literal_coefficients=dict(coefs),primitive_counts=dict(count),primitive_sha256=trace.hexdigest(),scalar_projection_sha256=projection.hexdigest(),actual_primitive_prefix_denominator_lcm=den,actual_primitive_prefix_max_absolute=str(mx),actual_primitive_prefix_max_numerator=maxnum,paid_real_primitive_count=2*sum(count.values()),halves_exactly_paid=count['halve'],divides3_exactly_paid=count['divide3'])
  print(ori,lowered[ori],flush=True)
 controls=[]
 for ori,events in programs['local_programs'].items():
  state={('L',r):{r:Q(1)}for r in range(1021)};omitted=False
  for event in events:
   if event[0]!='scalar':continue
   macro=event[2];halves=0
   for op in S.lower_scalar(macro):
    if op[0]=='halve':halves+=1
    if not omitted and macro[0]=='add'and Q(macro[3],macro[4]).denominator==8 and op[0]=='halve'and halves==3:
     omitted=True;continue
    name=op[0];t=tuple(op[1])
    if name=='clear':state[t]={}
    elif name=='copy':state[t]=dict(state.get(tuple(op[2]),{}))
    elif name in('double','halve','divide3'):
     q={'double':Q(2),'halve':Q(1,2),'divide3':Q(1,3)}[name];state[t]={k:a*q for k,a in state[t].items()}
    elif name=='accumulate':
     for k,a in list(state[tuple(op[2])].items()):
      z=state.setdefault(t,{}).get(k,Q(0))+op[3]*a
      if z:state[t][k]=z
      else:state[t].pop(k,None)
    else:raise AssertionError(name)
  want={('L',r):{r:Q(1)}for r in range(1021)}
  for t in range(120):want['L',120+t if ori=='forward'else t][t if ori=='forward'else 120+t]=Q(1 if ori=='forward'else-1)
  assert omitted and any(state[k]!=z for k,z in want.items())
  controls.append(dict(orientation=ori,mutation='omit_actual_third_halve_of_eighth',rejected=True))
 result=dict(status='PASS_RATIONAL_AND_LITERAL_COMPILER_DIAGNOSTIC_WITH_UNCHANGED_GXCORE_REJECTION',candidates=results,emitted_primitive_replays=lowered,controls_rejected=controls,
  source_hashes={name:sha(path) for name,path in bound_inputs.items()},actual_recomputed_response_sha256=sha(FULL/'local/RECOMPUTED-K.json'),actual_recomputed_response_entries=len(actual_K),coefficient_words_sha256=sha(FULL/'local/COEFFICIENT-WORDS.json'),
  scope='The fixed-sixths integer mirror rejects the new eighth clean-X prefix at208 and independently the gauged dirty prefix at275; parent7ff clean-X still passes. The exact fractional and paid quarter/eighth compiler domain is wider than those old sixth-grid guards. It is not relaxed and no gxcore/Lean certificate is claimed. Exact rational checks and explicitly emitted paid HALF/divide3 scalar primitives cover this finite candidate. The all-size chart/compiler, common-grid/precision, correlated-bank, ordinary-wrapper and analytic interfaces remain conditional; this is not a physical global stream implementation or an integer-decoder theorem.')
 assert all(sha(path)==pins[name] for name,path in bound_inputs.items())
 write('RECEIPT.json',result)
 return result

if __name__=="__main__":
 assert len(sys.argv)==7, "DERIVED416 GX_SOURCE_DIR PARENT7FF_JSON CANDIDATE208_JSON FRESH_FULL OUTPUT"
 run(*sys.argv[1:])
