"""Fresh PR259 replacement plus seven target intervals and25 retimings.
No saved execution receipt is consumed. Prepared with OpenAI assistance.
"""
from pathlib import Path
from array import array
from collections import Counter,defaultdict
from fractions import Fraction as Q
from copy import copy,deepcopy
from bisect import bisect_right
from math import gcd,lcm
import sys,json,gzip,hashlib,time,importlib.util
sys.dont_write_bytecode=True
BASE_RAW='2e0bc2a5c54cf8caf26fa30a1a2949702d842f620b28023ca2ba59140ecbed1a'
INTERVAL_RAW='6ab38175783163e729a77032e7e637299b2341aa9ab282134c22796b66699112'
FINAL_RAW='acf510b1377a6bd96eea50577de1aa049382499335fa7e5cac9b0300ecb377c7'
def sha(b):return hashlib.sha256(b).hexdigest()
def integral(row):
 row=list(map(Q,row));d=lcm(*(x.denominator for x in row));v=[int(x*d)for x in row];g=gcd(*v);return [x//g for x in v]if g else v
def run(p,raw,package,output):
 begun=time.monotonic();package=Path(package);W,C=p['W'],p['C'];old=p['records'];zero,full=p['ZERO'],p['FULL'];v=1760;n=20107
 assert sha(old.tobytes())==BASE_RAW
 spec=json.loads((package/'hybrid-selection.json').read_text())
 allc=json.loads(gzip.decompress((package/'kernel-candidates.json.gz').read_bytes()))
 assert len(allc)==518 and sum(z['dim']for z in allc)==1344
 drop=set(spec['removed_pivots']);assert drop=={17246,17222,17273,17255,17207}
 rows=[z for z in allc if z['pivot']not in drop];assert len(rows)==513
 intervals=spec['intervals'];assert len(intervals)==7
 chosen={q for z in intervals for q in z['streams']};targets={q for z in intervals for q in z['targets']}
 pivots={z['pivot']:z for z in rows};donors={q for z in rows for q in z['roles']if q!=z['pivot']}
 assert len(pivots)==513 and not(set(pivots)&donors)and not chosen.intersection(set(pivots)|donors)
 assert sum(z['dim']for z in rows)+133==1422 and 1422%3==0
 assert len(chosen)==14 and len(targets)==28
 meta=p['physical'];assert len(meta['category_names'])==28
 assert meta['category_names'][4]=='dirty_read'and meta['category_names'][25]=='terminal_pre'
 cuts=[k//6 for k in range(0,len(old),6)if tuple(old[k:k+6])==(1,3491,3488,-1,zero,25)]
 assert cuts==[727593];cut=cuts[0]
 final=dict(p['initial_state']);uses=defaultdict(list);badwrite={};badread={};cols={q:{q:1}for q in chosen};temporary=None
 at=defaultdict(list)
 for z in rows:at[z['cut']].append(z)
 for ci in at:at[ci].sort(key=lambda z:(z['dim'],z['pivot']))
 for k in range(0,len(old),6):
  i=k//6;op,a,b,c,f,z=old[k:k+6]
  if op==0:final[a]=c
  elif op==1:
   uses[a].append((i,f));uses[b].append((i,f));badwrite.setdefault(a,i)
   if not(z==4 and f==zero and v<=a<2*v):badread.setdefault(b,i)
   if i<=cut:
    assert a not in chosen
    if v<=b<2*v:assert v<=a<2*v
    if b in chosen:assert z==4 and f==zero and c==-1
    source=temporary if b==n else b
    for q,col in cols.items():
     value=col.get(a,0)+c*col.get(source,0)
     if value:col[a]=value
     else:col.pop(a,None)
  elif op==2:
   uses[a].append((i,c));badwrite.setdefault(a,i);badwrite.setdefault(b,i)
   if i<=cut:assert temporary is None and a not in chosen and not v<=a<2*v;temporary=a
  elif op==3 and i<=cut:assert temporary==a;temporary=None
  if i in at:
   assert temporary is None
   for z in at[i]:assert all(not any(col.get(q,0)for q in z['roles'])for col in cols.values())
 assert temporary is None
 def install(f,B):
  assert f not in C.B
  B=tuple(tuple(integral(b))for b in B);A,_=W.module.kernel(B,24)
  C.B[f],C.A[f],C.dimf[f]=B,A,len(B)
  assert C.nondeg(f)and len(A)==24-len(B)
  assert all(not sum(x*y for x,y in zip(b,a))for b in B for a in A)
  return f
 entries=[]
 for z in rows:
  f=install(z['new_frame_id'],z['basis']);assert C.dimf[f]==z['dim']
  for q in z['roles']:
   assert p['initial_state'][q]==zero and final[q]==full
   assert badwrite.get(q,10**9)>z['cut']and badread.get(q,10**9)>z['cut']
   j=bisect_right(uses[q],(z['cut'],10**9));assert j<len(uses[q])and C.sub(f,uses[q][j][1])
  role=p['context']['regs'][z['pivot']-2*v];assert role==z['role_a']and role not in W.gauge
  entries.append(dict(stream=z['pivot'],role=role,frame=f,rank=z['dim'],basis=C.B[f],targets=[]))
 blocks=[]
 for j,z in enumerate(intervals):
  high,low=z['streams'];ts=z['targets'];pivot=ts[0]
  assert cols[high]=={high:1,**{t:-1 for t in ts}}and cols[low]=={low:1,**{t:-1 for t in ts}}
  assert all(p['context']['regs'][q-2*v]==r for q,r in zip(z['streams'],z['roles']))
  L=install(300000+2*j,z['low_basis']);H=install(300001+2*j,z['high_basis']);K=z['inverse_frame']
  assert tuple(map(tuple,z['inverse_basis']))==tuple(map(tuple,C.B[K]))
  assert (C.dimf[L],C.dimf[H],C.dimf[K])==(5,14,20)and C.sub(L,H)and C.sub(H,K)
  for q in z['streams']+ts:
   index=bisect_right(uses[q],(cut,10**9));assert uses[q][index][1]==int(z['successor_frames'][str(q)])
  assert C.sub(L,int(z['successor_frames'][str(low)]))and C.sub(H,int(z['successor_frames'][str(high)]))
  assert all(C.sub(K,int(z['successor_frames'][str(t)]))for t in ts)
  local=[(1,t,pivot,-1,zero,30)for t in ts if t!=pivot]+[(1,pivot,low,-1,L,31),(1,pivot,high,-1,H,31)]+[(1,t,pivot,1,K,32)for t in reversed(ts)if t!=pivot]
  ids=ts+[low,high];slot={q:i for i,q in enumerate(ids)};M=[[int(i==j)for j in range(6)]for i in range(6)]
  for op,a,b,c,f,cat in local:M[slot[a]]=[x+c*y for x,y in zip(M[slot[a]],M[slot[b]])]
  assert M==[[int(i==j)-int(i<4 and j>=4)for j in range(6)]for i in range(6)]
  for op,a,b,c,f,cat in reversed(local):M[slot[a]]=[x-c*y for x,y in zip(M[slot[a]],M[slot[b]])]
  assert M==[[int(i==j)for j in range(6)]for i in range(6)]
  blocks.append(dict(z,L=L,H=H,K=K,word=local))
  for q,r,f in((high,z['roles'][0],H),(low,z['roles'][1],L)):
   assert p['initial_state'][q]==zero and r not in W.gauge
   entries.append(dict(stream=q,role=r,frame=f,rank=C.dimf[f],basis=C.B[f],targets=[t-v for t in ts]))
 initial=dict(p['initial_state'])
 for z in entries:initial[z['stream']]=z['frame']
 state=dict(initial);out=array('i');hist=Counter();temporary=None;removed=Counter();added=Counter()
 def move(q,f):
  before=state[q]
  if before==f:return
  if temporary is not None:assert q!=temporary[0]
  assert C.sub(before,f),(q,before,f)
  d=C.dimf[f]-C.dimf[before];assert d>=0
  out.extend((0,q,before,f,d,0));state[q]=f
  if d:hist[d]+=1
 def emit(e):
  nonlocal temporary
  op,a,b,c,f,z=e
  if op==1:
   if temporary is not None:assert a!=temporary[0]
   move(a,f);move(b,f);out.extend(e)
  elif op==2:
   assert temporary is None;move(a,c);state[b]=f;temporary=(a,b,c,f);out.extend(e);hist[z]+=1
  else:
   assert op==3 and temporary==(a,b,c,f)and state[a]==c and state[b]==f
   out.extend(e);del state[b];temporary=None
 for k in range(0,len(old),6):
  i=k//6;e=tuple(old[k:k+6]);op,a,b,c,f,z=e
  if op:
   if op==1 and b in pivots and z==4 and f==zero and i<=pivots[b]['cut']:removed['kernel_reads']+=1
   elif op==1 and b in chosen and i<=cut:assert z==4 and f==zero and c==-1;removed['interval_reads']+=1
   else:emit(e)
  for z in at.get(i,[]):
   assert temporary is None
   for q in z['roles']:
    if q!=z['pivot']:emit((1,q,z['pivot'],1,z['new_frame_id'],28));added['Q']+=1
  if i==cut:
   assert temporary is None
   for block in blocks:
    for e in block['word']:emit(e);added['interval']+=1
 for q in sorted(final):move(q,final[q])
 for pivot,z in sorted(pivots.items()):
  for q in z['roles']:
   if q!=pivot:emit((1,q,pivot,-1,full,29));added['Qinverse']+=1
 assert state==final and temporary is None and sha(out.tobytes())==INTERVAL_RAW
 assert removed=={'kernel_reads':27752,'interval_reads':56}and added=={'Q':756,'Qinverse':756,'interval':56}
 rt_spec=importlib.util.spec_from_file_location('hybrid_retiming25',package/'retiming25.py');rt=importlib.util.module_from_spec(rt_spec);rt_spec.loader.exec_module(rt)
 F={f:dict(basis=C.B[f],annihilator=C.A[f])for f in set(initial.values())|{out[k+j]for k in range(0,len(out),6)if out[k]==0 for j in(2,3)}}
 out,retiming=rt.transform(out,F,initial,final,json.loads((package/'retiming25-selection.json').read_text()),INTERVAL_RAW)
 assert sha(out.tobytes())==FINAL_RAW
 # Rebuild all required-use paths, not just the changed width histogram.
 needs={q:[]for q in initial};copies=Counter();centers=[];center=None;scalar=hashlib.sha256();tagged=hashlib.sha256();coeff=Counter();counts=Counter();count=0
 cats=list(meta['category_names'])+['multicut_basis','multicut_inverse','closed_interval_precondition','closed_interval_compensation','closed_interval_inverse']
 def event(h,x):h.update(json.dumps(x,separators=(',',':')).encode()+b'\n')
 for k in range(0,len(out),6):
  op,a,b,c,f,z=out[k:k+6]
  if op==1:
   needs[a].append(f)
   if b!=n:needs[b].append(f)
   else:assert center is not None
   source=center['source']if b==n else b;event(scalar,[a,source,c]);event(tagged,[a,b,c,f,cats[z]]);coeff[abs(c)]+=1;counts[cats[z]]+=1;count+=1
  elif op==2:
   assert center is None;needs[a].append(c);copies[z]+=1;center=dict(source=a,frame=c,rank=z,temporary=b,first_event=count,copy_output_frame=f)
  elif op==3:
   assert center is not None and center['source']==a;center.update(after_event=count,scatter_reads=count-center['first_event']);assert center['scatter_reads']==220;centers.append(center);center=None
 assert center is None and count==760383 and coeff=={1:759063,3:1320}
 per={};pairs=set();hist=Counter(copies);sourceH=Counter();targetH=Counter();internalH=Counter(copies)
 for q,before in initial.items():
  h=Counter()
  for f in needs[q]+[final[q]]:
   assert C.sub(before,f);d=C.dimf[f]-C.dimf[before];assert d==len(C.A[before])-len(C.A[f])>=0
   if d:h[d]+=1
   pairs.add((before,f));before=f
  per[q]=dict(h);hist.update(h);(sourceH if q<v else targetH if q<2*v else internalH).update(h)
 assert dict(hist)==retiming['local_histogram']and sum(hist.values())==96117 and sum(r*c for r,c in hist.items())==432755
 used=set(initial.values())|{f for pair in pairs for f in pair}
 for f in used:assert C.nondeg(f)
 execution=dict(p['context']);eW=copy(W);eW.gauge=dict(W.gauge);eW.w=dict(W.w);eW.w['gauges']=list(W.w['gauges'])
 for r in entries:
  assert r['role']not in eW.gauge
  z=dict(role=r['role'],frame=r['frame'],dim=r['rank'],targets=r['targets']);eW.gauge[r['role']]=z;eW.w['gauges'].append(z)
 execution['W']=eW
 entranceH=Counter(C.dimf[initial[q]]for q in range(2*v,n)if C.dimf[initial[q]])
 assert sum(entranceH.values())==2827
 receipt=dict(status='PASS_SOURCE_BOUND_PR259_REPLACEMENT_AND25_RETIMINGS',input_raw_sha256=BASE_RAW,replacement_raw_sha256=INTERVAL_RAW,raw_sha256=FINAL_RAW,
              retained_cohorts=513,removed_pivots=sorted(drop),intervals=blocks,new_entrance_rank=1422,selected_retimings=25,
              no_intermediate_rank1_drop=True,all14_signed_prefix_columns_exact=True,retained_kernel_operands_zero_on_chosen_columns=True,
              both_reflected_ledgers=True,all_external_observations_closed=True,producer_context_unchanged=True,
              removed=dict(removed),added=dict(added),retiming=retiming,seconds=time.monotonic()-begun)
 newmeta=dict(meta);newmeta.update(status=receipt['status'],scalar_projection_sha256=scalar.hexdigest(),tagged_scalar_sha256=tagged.hexdigest(),weighted_scalar_events=count,
  coefficient_histogram=dict(coeff),category_names=cats,categories=dict(counts),copied_center_blocks=centers,paid_histogram=dict(sorted(hist.items())),
  paid_rank_mass=sum(r*c for r,c in hist.items()),positive_rank_moves=sum(hist.values())-24,
  used_frames=[dict(frame_id=f,dimension=C.dimf[f],basis_sha256=sha(json.dumps(C.B[f],separators=(',',':')).encode()))for f in sorted(used)],
  initial_independent_entrances=dict(entranceH),hybrid_transform=receipt,physical_emitter_sha256=sha(Path(__file__).read_bytes()))
 result=dict(p);result.update(records=out,initial_state=initial,W=eW,context=execution,physical=newmeta,result=newmeta,hybrid_census=receipt,new_entrances=p['new_entrances']+entries)
 changed=deepcopy(raw);changed['hybrid_transform']=receipt;changed['physical_source_histogram']={str(r):c for r,c in sourceH.items()};changed['physical_target_histogram']={str(r):c for r,c in targetH.items()}
 internal=internalH.copy();internal.subtract(copies);changed['physical_internal_excluding_center_copies']={str(r):c for r,c in internal.items()if c}
 changed['one_stage_helper_histogram_including_copies']={str(r):c for r,c in hist.items()};changed['helper_rank_mass']=sum(r*c for r,c in hist.items())
 changed['auxiliary_entrance_rank_histogram']={str(r):c for r,c in entranceH.items()};changed['auxiliary_entrance_count']=sum(entranceH.values())
 five=Counter({r:5*c for r,c in hist.items()});five.update({int(r):c for r,c in raw['five_stage_profile']['idle_histogram'].items()})
 for r,c in entranceH.items():five[5*r]+=c
 changed['five_stage_profile'].update(histogram={str(r):c for r,c in five.items()},calls=sum(five.values()),rank_mass=sum(r*c for r,c in five.items()))
 assert changed['five_stage_profile']['rank_mass']==2830840
 d=Path(output);d.mkdir(parents=True,exist_ok=False);(d/'records.bin.gz').write_bytes(gzip.compress(out.tobytes(),mtime=0))
 for name,value in [('physical',newmeta),('hybrid',receipt),('raw',changed),('initial',initial),('per-role',per),('all-gauge-entrances',[dict(role=role,frame=z['frame'],rank=z['dim'],basis=C.B[z['frame']])for role,z in eW.gauge.items()if role in p['context']['regs']])]:
  (d/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
 (d/'used-bases.json').write_text(json.dumps({f:dict(basis=C.B[f],annihilator=C.A[f])for f in used},separators=(',',':'))+'\n')
 print('PASS fresh source hybrid',FINAL_RAW,'local children',sum(hist.values()),'entrances',sum(entranceH.values()),flush=True)
 return result,changed
