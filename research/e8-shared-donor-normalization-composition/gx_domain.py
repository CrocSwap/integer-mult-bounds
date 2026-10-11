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
 native={'local/local_admit.py':'4154b8e6d5fd8fa8649a86900d91282670f73460e3af0ff7f8bc5eaae73991c4','local/deps/complex_labels.py':'e000ee131389fec427388b85f632879cbaaf10e5e5d979a47d6307d64ce58982','local/deps/complex_scalars.py':'38e985ebe8c8e7f8c83c03828abde0c80be418caf95e97afdf2d0c357c0ed919','local/deps/complex_splice.py':'aaf46c8e5c68875b8315892e924e082b2f219f8d042dd14937e7cd2f72456dce'}
 assert all(sha(SOURCE/n)==h for n,h in native.items())
 bound_inputs={**{'source402/'+n:G/n for n in fixed},**{'source404/'+n:SOURCE/n for n in native},'shared-long.json':SHARED_LONG,'candidate.json':CANDIDATE,'fresh/local/RESULT.json':FULL/'local/RESULT.json','fresh/local/LOCAL-PROGRAMS.json.gz':FULL/'local/LOCAL-PROGRAMS.json.gz','fresh/local/MINIMAL-PINS.json':FULL/'local/MINIMAL-PINS.json','fresh/banks/ADMISSION.json':FULL/'banks/ADMISSION.json','gx_domain.py':Path(__file__)}
 pins={name:sha(path) for name,path in bound_inputs.items()}
 sys.path.insert(0,str(G))
 import gx,gxcore
 assert Path(gx.__file__).resolve()==G/'gx.py' and Path(gxcore.__file__).resolve()==G/'gxcore.py'
 OUT.mkdir()
 def write(name,z):(OUT/name).write_text(json.dumps(z,sort_keys=True,indent=2)+'\n')
 results={}
 for name,path,pin in [
  ('shared_long',SHARED_LONG,'feb95ec8f4068337b066b6208a60752199015fddedd2992bd7f76ba35ea3f0c5'),
  ('shared_long_resynth',CANDIDATE,'3ced59a749d2e61e6a540e423af7bcd1abfef602606f883de99fb83faa61022c')]:
  assert sha(path)==pin;c=read(path);D=gxcore.normal(copy.deepcopy(c));v=c['v'];n=2*v+c['R']
  gx.check1(copy.deepcopy(c),scalar=True)
  try:gxcore.mirror(D)
  except gxcore.Reject as exc:rejection=str(exc)
  else:raise AssertionError('The unchanged fixed-sixths mirror must reject')
  assert rejection=='E5: an entry needs a denominator beyond sixths (register 947)'
  xr,_=gxcore.replay(D,{r:{r:gxcore.SC} for r in range(v)})
  assert all(xr[r]=={r:6} and xr[v+r]=={r:6} for r in range(v))
  try:gxcore.replay(D,{r:{r:6} for r,f in D['ext']})
  except gxcore.Reject as exc:assert str(exc)==rejection
  else:raise AssertionError('Expected gauged-only rejection')
  modes={}
  for mode,inputs in [('x_content',set(range(v))),('gauged_dirt',set(dict(c['ext']))),('all_raw_columns',set(range(n)))]:
   rows,detail=rational_replay(c,inputs)
   if mode=='x_content':assert all(rows[r]=={r:Q(1)} and rows[v+r]=={r:Q(1)} for r in range(v))
   elif mode=='gauged_dirt':assert all(not rows[v+r] for r in range(v))
   else:assert all(rows[v+t].get(r,Q(0))==0 for t in range(v) for r,f in c['ext'])
   modes[mode]=detail
  results[name]=dict(candidate_sha256=pin,gx_fraction_check='PASS',gxcore='REJECTED',gxcore_exact_rejection=rejection,unchanged_gxcore_x_content_replay='PASS',unchanged_gxcore_gauged_dirt_replay='REJECTED',fraction_replays=modes)
  print(name,[(k,x['stats_by_role']) for k,x in modes.items()],flush=True)
 
 # Decode the actual fresh checked physical event list, independently execute its
 # emitted primitive expansion, and compare its exact bill and projection hashes.
 os.environ['CX_PINS']=str(FULL/'local/MINIMAL-PINS.json');sys.path.insert(0,str(SOURCE/'local/deps'))
 import complex_splice as S
 assert Path(S.__file__).resolve()==SOURCE/'local/deps/complex_splice.py', 'Run in a fresh process with the pinned compiler'
 local=read(FULL/'local/RESULT.json');payload=gzip.decompress((FULL/'local/LOCAL-PROGRAMS.json.gz').read_bytes());programs=json.loads(payload)
 assert sha256(payload).hexdigest()==local['local_programs_uncompressed_sha256']
 assert programs['candidate_sha256']==results['shared_long_resynth']['candidate_sha256']
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
    q=Q(e[3],e[4]);assert abs(q.numerator) in (1,2) and q.denominator in (1,2,3,6);coefs[str(q)]+=1
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
 result=dict(status='PASS_RATIONAL_AND_LITERAL_COMPILER_DIAGNOSTIC_WITH_UNCHANGED_GXCORE_REJECTION',candidates=results,emitted_primitive_replays=lowered,
  source_hashes={name:sha(path) for name,path in bound_inputs.items()},
  scope='The fixed-sixths integer mirror rejects gauged dirty intermediates. It is not relaxed and no gxcore/Lean certificate is claimed. Exact rational checks and explicitly emitted paid HALF/divide3 scalar primitives cover this finite candidate. The all-size chart/compiler, common-grid/precision, correlated-bank, ordinary-wrapper and analytic interfaces remain conditional; this is not a physical global stream implementation or an integer-decoder theorem.')
 assert all(sha(path)==pins[name] for name,path in bound_inputs.items())
 write('RECEIPT.json',result)
 return result

if __name__=="__main__":
 assert len(sys.argv)==7, "SOURCE404 GX_SOURCE_DIR SHARED_LONG_JSON CANDIDATE_JSON FRESH_FULL OUTPUT"
 run(*sys.argv[1:])
