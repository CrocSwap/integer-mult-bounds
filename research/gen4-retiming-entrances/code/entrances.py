"""Exact transport of 60 independent dirty entrances after center scatter.

Frozen source words and selected stream/role identities are checked before replay.
Each relocated elementary shear has a target destination and an unchanged helper
source. Targets are never read by ADD or COPY; selected helpers are neither
written nor copied before the transport cut. Consequently these240 shears commute
with all intervening scalar/COPY instructions over every coefficient ring. Their
original signed coefficients are retained. Literal projection and an independent
integer replay of all60 selected dirty columns check the resulting equality.

The physical frame change is checked separately: new entrance bases and their
annihilators have full rank, zero pairing, and nonzero Gram determinant. Every
changed movement is nested; each ADD has a common frame. The containment check
also gives the reversed annihilator inclusion for the reflected ledger. Source
and target endpoints are unchanged. The60 selected helper endpoints remainFULL24.

The new residuals are12 of rank5 and48 of rank6, replacing60 of rank24. Sixty
replicas tile120-coordinate banks exactly:30+144 banks per stage replace720.
The full integrated finite invoice and chart audit are separate verifier steps.

Substantial OpenAI Codex assistance. Apache-2.0; see repository notices.
"""
import argparse,json,hashlib,struct,functools,math
from pathlib import Path
from collections import Counter
import sympy as sp
if not __debug__:raise SystemExit('Assertions required')
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--source-dir',required=True,type=Path)
ap.add_argument('--export-dir',required=True,type=Path)
ap.add_argument('--output',required=True,type=Path)
args=ap.parse_args();X=args.export_dir;D=args.output;D.mkdir(exist_ok=True,parents=True);base=args.source_dir
st=json.loads((X/'gen4-states.json').read_text());n=st['n'];v=st['v'];zero=st['ZERO'];fs={int(k):x for k,x in json.loads((X/'frames.json').read_text())['frames'].items()};fs.update({int(k):x for k,x in json.loads((base/'COHORT249-FRAMES.json').read_text()).items()});extra={}
selection_path=Path(__file__).resolve().parent.parent/'data'/'entrances60.json'
selection=json.loads(selection_path.read_text());assert (n,v)==(19930,1760)
assert hashlib.sha256((base/'COHORT249-RECORDS.bin').read_bytes()).hexdigest()==selection['source_word_sha256']
assert st['record_sha256']==selection['export_word_sha256']
selected={e['stream']:dict(e) for e in selection['entries']};assert len(selected)==len(selection['entries'])==60 and sum(e['rank']for e in selected.values())==1092
raw=list(struct.iter_unpack('<6i',(base/'COHORT249-RECORDS.bin').read_bytes()));initial={int(k):x for k,x in json.loads((base/'COHORT249-INITIAL.json').read_text()).items()};final={int(k):x for k,x in json.loads((base/'COHORT249-FINAL.json').read_text()).items()};cut=max(j for j,e in enumerate(raw)if e[0]==3);read=st['physical']['category_names'].index('dirty_read');oldH=Counter();pairs=set();basepairs={(e[2],e[3])for e in raw if e[0]==0}
def introw(row):
 den=sp.ilcm(*[a.q for a in row]);z=[int(a*den)for a in row];g=math.gcd(*z);return [a//g for a in z]
for h,e in selected.items():
 assert 2*v<=h<n and st['regs'][h-2*v]==e['role'] and initial[h]==zero
 B=sp.Matrix(e['basis']);rank=e['rank'];assert B.rank()==rank and (B*(9*sp.eye(24)-sp.ones(24))*B.T).det()!=0
 A=[introw(row.T.tolist()[0])for row in B.nullspace()];assert len(A)+rank==24;assert sp.Matrix(A).rank()==24-rank and B*sp.Matrix(A).T==sp.zeros(rank,24-rank)
 f=max(fs)+1;fs[f]=dict(B=e['basis'],A=A,dim=rank);extra[f]=fs[f];e['frame']=f;initial[h]=f
@functools.lru_cache(None)
def sub(a,b):return fs[a]['dim']<=fs[b]['dim'] and all(sum(x*y for x,y in zip(u,w))==0 for u in fs[a]['B']for w in fs[b]['A'])
# Exact commutation contract: no target is ever read, each chosen helper is
# untouched up to cut, and all its initial target reads are before that cut.
reads=[];counter=Counter();helper_touches=Counter()
for j,(op,a,b,c,f,z)in enumerate(raw):
 if op==0:
  if f:oldH[f]+=1
 elif op==1:
  assert not(v<=b<2*v),'Target read invalidates simple commutation proof'
  if a in selected and j<=cut:raise AssertionError(('selected helper written before cut',a,j))
  if b in selected and j<=cut:
   assert v<=a<2*v and z==read and f==zero and abs(c)==1
   reads.append((j,a,b,c,z));counter[b]+=1
  if b in selected and f==zero:assert j<=cut
 elif op==2:
  assert not(v<=a<2*v),'Target COPY source invalidates simple commutation proof'
  oldH[z]+=1
  if j<=cut:assert a not in selected
assert len(reads)==240 and set(counter)==set(selected) and set(counter.values())=={4}
assert {a-v for _,a,b,c,z in reads}=={t for e in selected.values()for t in e['targets']}
for h,e in selected.items():assert {a-v for _,a,b,c,z in reads if b==h}==set(e['targets'])
state=dict(initial);out=[];temporary=None;H=Counter();changedpairs=set();skip={j for j,a,b,c,z in reads}
def move(a,f):
 old=state[a]
 if old==f:return
 if (old,f)not in basepairs:assert sub(old,f),('nonnested',a,old,f);changedpairs.add((old,f))
 pairs.add((old,f));rank=fs[f]['dim']-fs[old]['dim'];assert rank>=0;out.append((0,a,old,f,rank,0));state[a]=f
 if rank:H[rank]+=1
for j,(op,a,b,c,f,z)in enumerate(raw):
 if op==0:continue
 if j in skip:continue
 if op==1:move(a,f);move(b,f);out.append((op,a,b,c,f,z))
 elif op==2:
  assert temporary is None and b==n;move(a,c);state[b]=f;temporary=(a,b,c,f);H[z]+=1;out.append((op,a,b,c,f,z))
 else:
  assert op==3 and temporary==(a,b,c,f)and state[a]==c and state[b]==f;out.append((op,a,b,c,f,z));del state[b];temporary=None
 if j==cut:
  assert temporary is None
  for oldj,a,b,c,z in reads:
   f=selected[b]['frame'];assert state[b]==f;move(a,f);out.append((1,a,b,c,f,z))
assert temporary is None
for a in range(n):move(a,final[a])
assert state==final
# Full chronological projection with exactly the documented read relocation.
expect=[]
for j,(op,a,b,c,f,z) in enumerate(raw):
 if op and j not in skip:expect.append((op,a,b,c,z))
 if j==cut:expect.extend((1,a,b,c,z)for _,a,b,c,z in reads)
assert [(op,a,b,c,z)for op,a,b,c,f,z in out if op]==expect
# Selected 60 columns replay both source words over exact integers. This is
# stronger than a parity test for the relocated arbitrary dirty payload.
def columns(word):
 cols=[{}for _ in range(n)];tmp=None
 for h in selected:cols[h][h]=1
 for op,a,b,c,f,z in word:
  if op==1:
   q=tmp if b==n else b
   for h,x in list(cols[q].items()):
    value=cols[a].get(h,0)+c*x
    if value:cols[a][h]=value
    elif h in cols[a]:del cols[a][h]
  elif op==2:assert tmp is None;tmp=a
  elif op==3:assert tmp==a;tmp=None
 assert tmp is None
 return cols
assert columns(raw)==columns(out)
delta=Counter(H);delta.subtract(oldH);delta={r:x for r,x in delta.items()if x};assert sum(r*x for r,x in delta.items())==-1092
residual_before=Counter(fs[final[h]]['dim']-fs[zero]['dim']for h in selected);residual_after=Counter(fs[final[h]]['dim']-selected[h]['rank']for h in selected);assert residual_before=={24:60}and residual_after=={5:12,6:48}
data=b''.join(struct.pack('<6i',*e)for e in out)
assert hashlib.sha256(data).hexdigest()==selection['expected_output_sha256']
(D/'COHORT249-RECORDS.bin').write_bytes(data)
for name,value in [('INITIAL',initial),('FINAL',final),('FRAMES',{**json.loads((base/'COHORT249-FRAMES.json').read_text()),**extra})]:(D/f'COHORT249-{name}.json').write_text(json.dumps(value)+'\n')
receipt=dict(selection_sha256=hashlib.sha256(selection_path.read_bytes()).hexdigest(),emitter_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),status='PASS_60_EXACT_INTEGER_DIRTY_COMPENSATION_TRANSPORT',source=str(base),source_sha256=hashlib.sha256((base/'COHORT249-RECORDS.bin').read_bytes()).hexdigest(),output_sha256=hashlib.sha256(data).hexdigest(),new_entrance_count=60,new_entrance_rank=1092,cut_record=cut,relocated_reads=reads,entries=list(selected.values()),all_selected_integer_columns_equal=True,only_documented_scalar_reordering=True,all_new_frames_exact_nondegenerate=True,changed_connector_pairs=sorted(changedpairs),paid_histogram=dict(H),histogram=dict(H),delta=delta,rank_mass=sum(r*x for r,x in H.items()),record_count=len(out),new_residual_histogram=dict(residual_after),local_entropy_delta=sum(x*r*math.log(120/r)for r,x in delta.items()))
(D/'ENTRANCE-TRANSPORT.json').write_text(json.dumps(receipt,indent=2)+'\n');(D/'ENTRANCE-SELECTION.json').write_text(json.dumps(selection,indent=2)+'\n');print({k:v for k,v in receipt.items()if k not in ['entries','relocated_reads','changed_connector_pairs','paid_histogram','histogram']},flush=True)
