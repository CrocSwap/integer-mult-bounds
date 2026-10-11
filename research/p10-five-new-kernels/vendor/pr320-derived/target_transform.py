N_STREAMS=None
"""Exact F2 target-prefix compression, with fresh literal word and both ledgers.
The retained signed producer is untouched. New signed-lift prefix bounds are
computed from the emitted odd payload word. OpenAI Codex assistance; Apache-2.0.
p = 10 port (Chafik Boukhalfa (chafreaky), Anthropic Claude assistance): h, v, centre copies and scatter reads come
from word_pins.shape and the stage counts are pinned in word-pins.json; the mechanism and checks are unchanged.
"""
from array import array
from collections import Counter,defaultdict
from copy import deepcopy
from pathlib import Path
import gzip,hashlib,json,time
if not __debug__:raise SystemExit('assertions required')
HERE=Path(__file__).resolve().parent
from word_pins import shape as _shape
_S=_shape();_H=_S['h'];_V=_S['v'];_CR=_S['center_rank'];_NC=_S['centers'];_SCAT=_S['scatter_reads']

def replay(records,reverse=False,omit=None):
 v=_V;n=N_STREAMS;columns=[1<<i for i in range(n)];wanted=columns[:];norms=[1]*n;largest=1;center=None;count=0;coeff=Counter();digest=hashlib.sha256()
 for t in range(v):wanted[v+t]^=1<<t
 for k in(range(len(records)-6,-1,-6)if reverse else range(0,len(records),6)):
  op,a,b,c,f,z=records[k:k+6]
  if op==1:
   if b==n:assert center is not None;b=center
   if k//6==omit:continue
   assert c%2 and a!=b;columns[a]^=columns[b];norms[a]+=abs(c)*norms[b];largest=max(largest,norms[a]);coeff[abs(c)]+=1;count+=1
   digest.update(json.dumps([a,b,-c if reverse else c],separators=(',',':')).encode());digest.update(b'\n')
  elif op==(3 if reverse else 2):assert center is None;center=a
  elif op==(2 if reverse else 3):assert center==a;center=None
 assert center is None and columns==wanted,'full all-column endpoint failure'
 return dict(reverse=reverse,all_formal_columns=n,all_source_and_dirty_restored=True,arbitrary_target_contents_preserved=True,weighted_additions=count,event_sha256=digest.hexdigest(),coefficient_counts=dict(coeff),literal_unit_additions=sum(c*cnt for c,cnt in coeff.items()),max_intermediate_row_l1=largest,final_source_row_l1=max(norms[:v]),final_target_row_l1=max(norms[v:2*v]),final_dirty_row_l1=max(norms[2*v:]))

def run(producer,output_dir=None,selection_path=None):
 start=time.monotonic();path=Path(selection_path)if selection_path else HERE/'target-selection.json';selection=json.loads(path.read_text());old=producer['records'];oldmeta=producer['physical'];W,C=producer['W'],producer['C'];initial=dict(producer['initial_state']);ZERO=producer['ZERO'];v=W.v;n=len(initial);global N_STREAMS;N_STREAMS=n
 assert hashlib.sha256(old.tobytes()).hexdigest()==selection['input_raw_sha256']
 assert oldmeta['scalar_projection_sha256']==selection['input_scalar_sha256']
 groups=[];owner={};atclose=defaultdict(list);cut=selection['cut_record'];all_dep={}
 for j,row in enumerate(selection['groups']):
  r=dict(row);r['dependent']={int(t):ps for t,ps in r['dependent'].items()};r['frame']=W.register(r['close_basis']);F=r['frame'];assert C.dimf[F]==r['close_rank']and C.nondeg(F)
  assert r['cut_record']==cut and r['close_after_record']>cut
  assert not(set(r['dependent'])&{p for ps in r['dependent'].values()for p in ps})
  assert set(r['dependent'])|set(r['retained'])==set(r['targets'])
  for t in r['targets']:
   assert t not in owner;owner[t]=j
   assert all(W.module.dot(C.cov[t],b)==0 for b in C.B[F])
  for t,ps in r['dependent'].items():assert set(ps)<=set(r['retained']);all_dep[t]=j
  atclose[r['close_after_record']].append(j);groups.append(r)
 # Check the literal old prefix responses, rather than trusting selected dependencies.
 columns=[1<<i for i in range(n)];center=None;responses={t:0 for t in owner};final=dict(initial)
 for k in range(0,len(old),6):
  op,a,b,c,f,z=old[k:k+6];i=k//6
  if op==0:final[a]=c
  elif op==1:
   actual=center if b==n else b;assert actual is not None
   if i>cut:
    if actual-v in owner:assert i>groups[owner[actual-v]]['close_after_record'],'active target prefix used as a source'
    if a-v in owner and i<=groups[owner[a-v]]['close_after_record']:
     assert not(v<=actual<2*v);responses[a-v]^=columns[actual]
   assert c%2;columns[a]^=columns[actual]
  elif op==2:assert center is None;center=a
  elif op==3:assert center==a;center=None
  for j in atclose.get(i,[]):
   r=groups[j]
   for t,ps in r['dependent'].items():
    result=responses[t]
    for p in ps:result^=responses[p]
    assert result==0,('literal prefix dependency',j,t)
 assert center is None
 # Emit a concrete new word and regenerate every MOVE from actual needs.
 cats=list(oldmeta['category_names'])+['target_prefix_setup','target_prefix_restore'];out=array('i');state=dict(initial);center=None;deleted=[];inserted=[];first_setup=None
 def move(s,f):
  before=state[s]
  if before==f:return
  assert C.sub(before,f),('nonnested actual use',s,before,f);gap=C.dimf[f]-C.dimf[before];assert gap>=0;out.extend((0,s,before,f,gap,0));state[s]=f
 def add(a,b,c,f,z):move(a,f);move(b,f);out.extend((1,a,b,c,f,z))
 def batch(j,sign,f,z):
  nonlocal first_setup
  r=groups[j]
  for t in r['targets']:move(v+t,f)
  for t,ps in r['dependent'].items():
   for p in ps:
    if first_setup is None and sign<0:first_setup=len(out)//6
    add(v+t,v+p,sign,f,z);inserted.append((v+t,v+p,sign,f,z))
 for k in range(0,len(old),6):
  op,a,b,c,f,z=old[k:k+6];i=k//6
  if op==1:
   j=all_dep.get(a-v)
   if j is not None and cut<i<=groups[j]['close_after_record']:
    assert not(v<=b<2*v);deleted.append(i)
   else:add(a,b,c,f,z)
  elif op==2:
   assert center is None;move(a,c);out.extend((op,a,b,c,f,z));state[b]=f;center=(a,b,c)
  elif op==3:
   assert center==(a,b,c)and state[a]==c and state[b]==f;out.extend((op,a,b,c,f,z));del state[b];center=None
  if i==cut:
   assert center is None and all(state[v+t]==ZERO for t in owner)
   for j in range(len(groups)):batch(j,-1,ZERO,len(cats)-2)
  for j in atclose.get(i,[]):batch(j,1,groups[j]['frame'],len(cats)-1)
 for s in sorted(final):move(s,final[s])
 assert center is None and state==final
 # Independent required-frame census ignores all emitted MOVEs.
 needs={s:[]for s in initial};copies=Counter();center=None
 for k in range(0,len(out),6):
  op,a,b,c,f,z=out[k:k+6]
  if op==1:
   needs[a].append(f)
   if b!=n:needs[b].append(f)
   else:assert center is not None and f==ZERO
  elif op==2:assert center is None;center=(a,b,c);needs[a].append(c);copies[z]+=1
  elif op==3:assert center==(a,b,c);center=None
 assert center is None and copies=={_CR:_NC}
 census=Counter(copies);per_role={};pairs=set()
 for s,before in initial.items():
  H=Counter()
  for f in needs[s]+[final[s]]:
   assert C.sub(before,f);gap=C.dimf[f]-C.dimf[before]
   if gap:H[gap]+=1
   pairs.add((before,f));before=f
  per_role[s]=H;census.update(H)
 usedframes={f for pair in pairs for f in pair}
 for f in usedframes:assert C.nondeg(f)and len(C.B[f])==C.dimf[f]and len(C.A[f])+C.dimf[f]==_H
 for a,b in pairs:
  assert len(C.A[a])-len(C.A[b])==C.dimf[b]-C.dimf[a]
  assert all(W.module.dot(x,y)==0 for x in C.A[b]for y in C.B[a])
 # Independently validate literal frames and build fresh physical hashes.
 state=dict(initial);center=None;hist=Counter();cat=Counter();coeff=Counter();centers=[];count=0;scalar=hashlib.sha256();tagged=hashlib.sha256();used=set(initial.values())
 def event(d,row):d.update(json.dumps(row,separators=(',',':')).encode());d.update(b'\n')
 for k in range(0,len(out),6):
  op,a,b,c,f,z=out[k:k+6]
  if op==0:
   assert state[a]==b and C.sub(b,c)and C.dimf[c]-C.dimf[b]==f;state[a]=c;used.update((b,c))
   if f:hist[f]+=1
  elif op==1:
   assert c%2 and state[a]==state[b]==f and a!=b;kind=cats[z];source=center['source']if b==n else b
   event(scalar,[a,source,c]);event(tagged,[a,b,c,f,kind]);count+=1;cat[kind]+=1;coeff[abs(c)]+=1;used.add(f)
  elif op==2:
   assert center is None and b==n and state[a]==c and f==ZERO and z==_CR;state[b]=f;hist[z]+=1;center=dict(source=a,frame=c,rank=z,temporary=b,first_event=count,copy_output_frame=f)
  else:
   assert op==3 and center is not None and(a,b,c)==(center['source'],center['temporary'],center['frame'])and state[a]==c and state[b]==f==ZERO
   center.update(after_event=count,scatter_reads=count-center['first_event']);assert center['scatter_reads']==_SCAT;centers.append(center);center=None;del state[b]
 assert center is None and state==final and hist==census
 forward=replay(out);inverse=replay(out,True);assert forward['event_sha256']==scalar.hexdigest()
 try:replay(out,omit=first_setup)
 except AssertionError:negative='omitted target-prefix setup rejected'
 else:raise AssertionError('missing target prefix setup admitted')
 delta=Counter(hist);delta.subtract(Counter({int(k):v for k,v in oldmeta['paid_histogram'].items()}));delta={k:v for k,v in delta.items()if v}
 expected=Counter()
 for r in groups:expected.update({int(k):v for k,v in r['local_histogram_delta'].items()})
 assert delta=={k:v for k,v in expected.items()if v}
 assert sum(r*c for r,c in hist.items())==oldmeta['paid_rank_mass'];assert count==oldmeta['weighted_scalar_events']-len(deleted)+len(inserted)
 sourceH=Counter();targetH=Counter();internalH=Counter(copies)
 for s,H in per_role.items():(sourceH if s<v else targetH if s<2*v else internalH).update(H)
 receipt=dict(status='PASS_EXACT_F2_TARGET_PREFIX_COMPRESSION',selected_groups=len(groups),targets=len(owner),deleted_prefix_adds=len(deleted),inserted_setup_restore_adds=len(inserted),cut_record=cut,literal_prefix_dependencies_checked=True,remaining_payload_additions=count,local_histogram_delta=delta,both_reflected_ledgers=True,unchanged_all_input_output_frames=True,unchanged_copy_lifetimes=True,producer_context_unchanged=True,source_histogram=dict(sourceH),target_histogram=dict(targetH),internal_histogram_including_copies=dict(internalH),copied_center_histogram=dict(copies),unique_required_frame_pairs=len(pairs),explicit_reflected_annihilator_pairs=len(pairs),forward=forward,inverse=inverse,negative_control=negative,selection_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),transform_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),seconds=time.monotonic()-start)
 meta=dict(oldmeta);meta.update(status='PASS_PHYSICAL527_TARGET_PREFIX_FRAME_AND_SCALAR_PROJECTION',category_names=cats,scalar_projection_sha256=scalar.hexdigest(),tagged_scalar_sha256=tagged.hexdigest(),weighted_scalar_events=count,coefficient_histogram=dict(coeff),categories=dict(cat),copied_center_blocks=centers,paid_histogram=dict(sorted(hist.items())),paid_rank_mass=sum(r*c for r,c in hist.items()),positive_rank_moves=sum(hist.values())-_NC,used_frames=[dict(frame_id=f,dimension=C.dimf[f],basis_sha256=hashlib.sha256(json.dumps(C.B[f],separators=(',',':')).encode()).hexdigest())for f in sorted(used)],target_transform=receipt,physical_emitter_sha256=receipt['transform_sha256'])
 result=dict(producer);result.update(records=out,physical=meta,result=meta,target_census=receipt)
 if output_dir is not None:
  p=Path(output_dir);p.mkdir(parents=True,exist_ok=True);(p/'records.bin.gz').write_bytes(gzip.compress(out.tobytes(),mtime=0));(p/'physical.json').write_text(json.dumps(meta,indent=2)+'\n');(p/'target.json').write_text(json.dumps(receipt,indent=2)+'\n');(p/'target-used-bases.json').write_text(json.dumps({f:dict(basis=C.B[f],annihilator=C.A[f])for f in sorted(used)},separators=(',',':'))+'\n')
 print('PASS target prefix',len(groups),'groups',count,'ADDs',flush=True)
 return result

def rebind(raw,receipt):
 assert receipt['status']=='PASS_EXACT_F2_TARGET_PREFIX_COMPRESSION'and receipt['both_reflected_ledgers']and receipt['producer_context_unchanged']
 hist=lambda x:Counter({int(k):v for k,v in x.items()if v});compact=lambda h:{str(k):v for k,v in sorted(h.items())if v}
 source=hist(receipt['source_histogram']);target=hist(receipt['target_histogram']);internal=hist(receipt['internal_histogram_including_copies']);copies=hist(receipt['copied_center_histogram']);helper=source+target+internal
 assert source==hist(raw['physical_source_histogram'])and internal==hist(raw['physical_internal_excluding_center_copies'])+copies
 delta=helper.copy();delta.subtract(hist(raw['one_stage_helper_histogram_including_copies']));assert compact(delta)==compact(hist(receipt['local_histogram_delta']))
 old=deepcopy(raw);five=Counter({r:5*n for r,n in helper.items()});five.update(hist(raw['five_stage_profile']['idle_histogram']))
 for r,n in hist(raw['auxiliary_entrance_rank_histogram']).items():five[5*r]+=n
 assert sum(r*n for r,n in five.items())==raw['five_stage_profile']['rank_mass']
 raw['before_target_prefix_ledger']=old;raw['schema']='source527-target-prefix-fresh-raw-ledger/1';raw['physical_target_histogram']=compact(target);raw['one_stage_helper_histogram_including_copies']=compact(helper);raw['five_stage_profile'].update(histogram=compact(five),calls=sum(five.values()));raw['target_transform']=receipt
 return raw
