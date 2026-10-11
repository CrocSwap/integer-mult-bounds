"""Changed local E8 source in PR377 compressed B4; no unchanged public replay."""
import os,sys,json,gzip,hashlib,importlib.util,time,math
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
PUB=Path(os.environ.get('COMPLEX_PUBLIC',str(Path(__file__).resolve().parent/'public')))
BASE=PUB/'381/source/research/e8-nine-stage-kappa/complex377'
FAR=PUB/'378/source/research/e8-complex-far-retiming'
ROOT=BASE/'work/native358/vendor/complex-reserve/upstream/pr352/code/complex'
OUT=Path(os.environ.get('COMPLEX_OUTPUT',str(HERE/'complex-admission')));OUT.mkdir(exist_ok=True)
farcp=FAR/'data/gcert1-e8-r783-far.json.gz'
cp=Path(os.environ.get('COMPLEX_CERT',str(farcp)));orig=BASE/'work/pr361/complex/gcert1-e8-r783.json.gz'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source_hashes={str(p):sha(p) for p in [cp,orig,ROOT/'code/complex_labels.py',ROOT/'code/complex_scalars.py',ROOT/'code/complex_splice.py',BASE/'work/odd-stages/global_nine.py',BASE/'work/odd-stages/data_phases.py',BASE/'work/odd-stages/clifford_exact.py']}
c=json.load(gzip.open(cp));c0=json.load(gzip.open(orig));assert all(c[k]==c0[k] for k in ['format','h','v','R','cst','N','ports','start','final','ext','ret','scat'])
pp=OUT/'minimal-pins.json';pp.write_text(json.dumps({'H':9,'V':120,'R':783,'cst':72,'N':9039}))
os.environ['CX_PINS']=str(pp);sys.path.insert(0,str(ROOT/'code'))
import complex_labels as L,complex_scalars as C,complex_splice as S
if cp!=farcp:
 # Sufficient dirty-response extension: the new complete raw scalar operator
 # is exactly the old operator on EVERY live initial column, and the helper
 # subword is unchanged. Therefore the old explicit K and cleanup remain
 # the exact response/correction; only the main equal-frame word changes.
 old=json.load(gzip.open(farcp));source_hashes[str(farcp)]=sha(farcp)
 from fractions import Fraction
 def operator(z):
  rows=[{i:Q(1)} for i in range(1023)]
  def axpy(t,src,q):
   d=rows[t]
   for i,v in src.items():
    nv=d.get(i,Q(0))+q*v
    if nv:d[i]=nv
    else:d.pop(i,None)
  def run(gs):
   for g in gs:
    for r,a,b in g[3]:
     t,ss=(r,g[2]) if g[0]=='out' else (g[2],r)
     axpy(t,dict(rows[ss]),Q(a,b))
  run(z['A']);tot={k:dict(rows[r]) for k,r,f in z['ret']}
  for t,es in enumerate(z['scat']['table']):
   for k,a,b in es:axpy(120+t,tot[k],Q(a,b))
  run(z['B']);return rows,tot
 assert operator(c)==operator(old),'changed raw matrix or retained totals'
 def helper_word(z):
  ans=[]
  for g in z['A']+z['B']:
   for r,a,b in g[3]:
    t,ss=(r,g[2]) if g[0]=='out' else (g[2],r)
    if t<120 or t>=240:ans.append((t,ss,Q(a,b)))
  return ans
 assert helper_word(c)==helper_word(old),'changed helper/source cleanup subword'
 def main_flat(gs):
  out=[]
  for g in gs:
   assert g[0] in ('in','out')
   for r,a,b in g[3]:
    t,ss=(r,g[2]) if g[0]=='out' else (g[2],r)
    assert t!=ss and not(240<=ss and t<120)
    assert not(120<=ss<240) or 120<=t<240,'Y only feeds Y'
    out.append((t,ss,Q(a,b)))
  return out
 oldA=C.flat(old['A']);oldB=C.flat(old['B']);frozenK=list(C.old_positive(oldA,oldB,old))
 def frozen_schedule(ori,A,B,z):
  yield from ((p,e) for p,es in [('old_response',C.old_word(ori,frozenK)),('main',C.main_scalar(ori,A,B,z)),('cleanup',C.cleanup(ori,oldA+oldB))] for e in es)
 C.flat=main_flat;C.inv_schedule=frozen_schedule
 # Explicit old K, main-only Y->Y extension, original helper/source cleanup.
 # The emitted main walks the NEW certificate, not the old word.
 emit_text=(ROOT/'code/complex_splice.py').read_text()
 emit_text=emit_text[emit_text.index('def emit(c,ori):'):emit_text.index('def contains(U,V):')]
 emit_text=emit_text.replace("A=list(flat(c['A']));B=list(flat(c['B']));cur=c['start'].copy()","A=list(flat(OLD_CERT['A']));B=list(flat(OLD_CERT['B']));cur=c['start'].copy()")
 ns=dict(S.__dict__,OLD_CERT=old,flat=main_flat)
 exec(compile(emit_text,'explicit-frozen-K-main-Y-extension','exec'),ns)
 S.emit=ns['emit']
 (OUT/'FROZEN-K-EXTENSION.py').write_text(emit_text)
 print('new raw matrix all columns = old, old helper cleanup identical; explicit original K frozen PASS',flush=True)

checks=L.replay_label_counts(c);A=C.flat(c['A']);B=C.flat(c['B']);bill={};locals={};local_check={};scalar_rows={}
for ori in ['forward','backward']:
 sch=list(C.inv_schedule(ori,A,B,c));bill[ori]=C.bill(iter(sch));life=C.lifecycle(iter(sch),c)
 events=list(S.emit(c,ori));local_check[ori]=S.validate(events,c,ori,{'checks':checks},bill);locals[ori]=events
 reg={('L',i):{i:Q(1)}for i in range(1023)}
 for ph,e in sch:
  if e[0]=='recursive_center':continue
  t=e[1]
  if e[0]=='clear':reg[t]={}
  elif e[0]=='copy':reg[t]=dict(reg.get(e[2],{}))
  elif e[0]=='add':
   src=dict(reg.get(e[2],{}));q=Q(e[3],e[4]);d=reg.setdefault(t,{})
   for j,z in src.items():
    nz=d.get(j,Q(0))+q*z
    if nz:d[j]=nz
    else:d.pop(j,None)
  else:raise AssertionError(e)
 expected={('L',i):{i:Q(1)} for i in range(1023)}
 for t in range(120):
  if ori=='forward':expected[('L',120+t)][t]=Q(1)
  else:expected[('L',t)][120+t]=Q(-1)
 assert all(reg[r]==e for r,e in expected.items()) and all(not z for r,z in reg.items() if r[0]!='L')
 scalar_rows[ori]={'independent_live_columns':1023,'dirty_helper_columns':783,'private_restored_zero':True,'scalar_macros':len(sch),'lifecycle':life}
 print('changed-source local dirty columns + frames + lifecycle PASS',ori,flush=True)
# Reconstruct paid histogram from literal invocation events, all 72 calls.
H=Counter();event_count=0;scalar_primitives=0
for ori,num in [('forward',40),('backward',32)]:
 for ev in locals[ori]:
  if ev[0]=='climb':H[ev[5]]+=num
  elif ev[0]=='center':H[ev[4]]+=num
 event_count+=num*len(locals[ori]);scalar_primitives+=num*local_check[ori]['real_component_primitives']
for r in [16,8,32,8,48,8,48,32,16]:H[r]+=1920
H[1]+=7047
assert all(H[r]-7047*(r==1)-1920*[16,8,32,8,48,8,48,32,16].count(r)==72*int(checks['invocation_histogram'].get(str(r),0)) for r in H)
m,live,physical=73,14727,15520;mass=sum(r*n for r,n in H.items());assert m*live-mass==2496
# Whole-bank stream assignment rebuilt; all 8 rank9 residuals + rank1 padding.
assign=[]
for rep in range(8):
 for helper in range(783):
  bank,slot=divmod(rep*783+helper,8);assign.append((rep,helper,bank,slot))
assert len(set(assign))==6264 and max(z[2] for z in assign)==782
for b in range(783):assert [z[3] for z in assign if z[2]==b]==list(range(8))
# New source-counted finite work, same explicit owner and endpoint factors.
compiler=64*74**3;macros=max(bill[o]['totals']['scalar_macros'] for o in locals);lc=checks['invocation_calls']
adapters=16*(macros+lc+1023+9)+64*73
local_primitive=max(local_check[o]['real_component_primitives'] for o in locals);local_bound=local_primitive+adapters*compiler
bridge_adds=18*120*8;terminal_shifts=4*120*8;terminal_movements=2*4*120*8;cover_corrections=live
idle_count=120*18
nonlocal_items=4*120*8*9+2*120*8*9+2*9*8*783+idle_count*8+9*783+bridge_adds+terminal_shifts+terminal_movements+cover_corrections+physical
outside=8*nonlocal_items+64*73
pervertex=scalar_primitives+bridge_adds+terminal_shifts+terminal_movements+cover_corrections+(72*adapters+outside)*compiler+64*physical
r=36;group=2**(r*r)*math.prod(2**(2*i)-1 for i in range(1,r+1));s=group*mass;stock=group*physical;logical=group*pervertex+64;router=compiler*(logical+1)*(stock+1)**2
G,E,C0=1<<30000,1<<100000,1<<210000;bb=s+E;literal=2*G*stock**2+8*s+4*stock+4+32*73
assert local_bound<1<<48 and logical<1<<6050 and router<G and literal<E and bb<1<<100001 and 32*73*bb*bb<C0
assert 73**2>2*48**2 and 2*bb*(73-48)-s-E==49*bb
row=2*stock.bit_length()+9909+252;assert row==15445<20161
invoice=dict(local_primitive_bound=local_bound,local_adapters=adapters,compiler=compiler,scalar_primitives_all_invocations=scalar_primitives,outside_adapter_bound=outside,pervertex=pervertex,group_bits=group.bit_length(),physical_stock_bits=stock.bit_length(),logical_groups_bits=logical.bit_length(),router_bits=router.bit_length(),literal_bits=literal.bit_length(),required_C0_bits=(32*73*bb*bb).bit_length(),halving_degree=2,induction_gap_multiple_B=49,physical_row_coefficient=row,retained_row_coefficient=20161)
def load(name):
 path=BASE/'work/pr361/code/engines'/(name+'.py');spec=importlib.util.spec_from_file_location('changed_'+name,path);x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x);return x
M=load('moment');BM=load('base_two_moment');root=M.certify(H,73,14727,True);b=Q(int(Q(root['lower'])*10**18),10**18);step=Q(1,10**18)
assert M.moment(H,73,14727,b,True)[1]<1<M.moment(H,73,14727,b+step,True)[0]
fb=32*73*73*sum(H.values());_,hi=BM.moment(73,14727,list(H.items()),b);_,bhi=BM.moment(73,14727,[(1,fb)],b);lo,_=BM.moment(73,14727,list(H.items()),b+step);blo,_=BM.moment(73,14727,[(1,fb)],b+step)
assert hi+Q(1,10**16)*bhi<1<lo+Q(1,10**16)*blo
assert source_hashes=={p:sha(p) for p in source_hashes}
def enc(x):
 if isinstance(x,Q):return str(x)
 raise TypeError(type(x))
# Portable literal local data forms the changed portion of the global template.
raw=json.dumps({'certificate_gzip_sha256':sha(cp),'local_programs':locals,'invocation_counts':{'forward':40,'backward':32},'whole_bank_assignments':assign,'idle_ranks':[16,8,32,8,48,8,48,32,16],'all_live_cover_corrections':14727,'bank_padding':{'rank':1,'calls':7047},'source_owner_and_phase_recipe':source_hashes[str(BASE/'work/odd-stages/global_nine.py')]},sort_keys=True,separators=(',',':'),default=enc).encode();(OUT/'CHANGED-TEMPLATE.json.gz').write_bytes(gzip.compress(raw,mtime=0))
result=dict(status='PASS_CHANGED_LOCAL_FRAMES_DIRTY_WORDS_BANKS_TWO_MOMENTS_AND_FINITE_INVOICE',coarse=str(b),coarse_float=float(b),profile=dict(sorted(H.items())),live=live,physical=physical,m=73,rank_mass=mass,deficit=2496,paid_calls=sum(H.values()),local_events=event_count,local_frames=len(c['frames']),scalar_rows=scalar_rows,local_splice=local_check,invoice=invoice,template_sha256=hashlib.sha256(raw).hexdigest(),source_hashes=source_hashes,clifford_revalidation='separate changed-certificate exact Clifford audit required',dirty_response_extension=('original literal K and unchanged helper cleanup, complete raw matrix equality' if cp!=farcp else 'unchanged permitted source directions'),scope='Finite conditional compressed B4 composition. Exact local changed Clifford adapters and template assembly remain required; inherited all-size theorem interfaces remain conditional.')
(OUT/'RESULT.json').write_text(json.dumps(result,indent=2,default=enc));print('PASS changed compressed source',b,float(b),flush=True)
