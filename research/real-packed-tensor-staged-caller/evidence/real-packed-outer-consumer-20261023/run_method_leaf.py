"""One bounded, Git/network-free source-cohort leaf execution. No numerical Tensor."""
from pathlib import Path
import builtins,hashlib,importlib,importlib.util,json,runpy,signal,sys,time,traceback
P=Path(__file__).resolve().parent;ROOT=P/'staged-source';PKG=ROOT/'research/physical-tensor-crt-sandwich-recovery';DRAFT=P/'packed_sandwich_DRAFT.py'
START=time.monotonic();R={'status':'RUNNING','source_head':'e65f47db55b9a3779fbf7fe23e93a8a4c5eb3ce1','hard_budget_seconds':60,'numerical_Tensor_calls':0,'numerical_Converter_calls':0,'owner_constructors':{'Tensor':0,'Converter':0},'scope':'Actual source leaves plus local real Tape/J/word methods; not changed whole caller'}
def need(x,m):
 if not x:raise ValueError(m)
def hashes():return {str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest()for f in [DRAFT,*sorted(ROOT.rglob('*'))]if f.is_file()}
BEFORE=hashes();R['before_hashes']=BEFORE
need(BEFORE['packed_sandwich_DRAFT.py']=='5dfcdfe63d9d03a89a00dd92e681ab0a0efc5bbc86aa7edae58f007baf752483','frozen draft hash')
for row in json.loads((PKG/'SOURCES.json').read_text())['files']:
 if row['usage']=='input':need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source input '+row['path'])
for row in json.loads((P/'PUBLIC-TEXT-MANIFEST.json').read_text()):need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'public source '+row['path'])
need(hashlib.sha256((PKG/'inputs/p48-5x7.bin').read_bytes()).hexdigest()=='7dd7adbe9e8f6d5ffbecd425a72827b31d7222ee51bcd67a4148ebfd03420381','published fixture')
def alarm(*_):raise TimeoutError('bounded leaf computational budget reached')
signal.signal(signal.SIGALRM,alarm);signal.alarm(58)
original_import=builtins.__import__;patched=set()
def watched(name,*args,**kwargs):
 module=original_import(name,*args,**kwargs)
 for key,klass,method in [('tensor_engine','Tensor','run'),('crt_converter','Converter','run_plan')]:
  if key in sys.modules and key not in patched and hasattr(sys.modules[key],klass):
   cls=getattr(sys.modules[key],klass);init=cls.__init__
   def init_guard(self,*a,_init=init,_klass=klass,**kw):
    need(all(getattr(getattr(sys.modules[k],c),m).__dict__.get('_bounded_numerical_guard',False) for k,c,m in [('tensor_engine','Tensor','run'),('crt_converter','Converter','run_plan')]),'both numerical guards installed before owner controls')
    R['guards_before_owner_controls']=True
    R['owner_constructors'][_klass]+=1;return _init(self,*a,**kw)
   def forbidden(self,*a,_klass=klass,**kw):
    R['numerical_'+('Tensor'if _klass=='Tensor'else'Converter')+'_calls']+=1
    raise RuntimeError('PROHIBITED numerical child '+_klass)
   forbidden._bounded_numerical_guard=True
   cls.__init__=init_guard;setattr(cls,method,forbidden);patched.add(key)
   R.setdefault('installed_numerical_guards',[]).append(key+'.'+klass+'.'+method)
 return module
try:
 prior=json.loads((P/'ATTEMPT2-BOUNDED-LEAF-RESULT.json').read_text())
 need(prior.get('source_leaves_completed') and prior.get('all_consumed_source_and_draft_hashes_unchanged'),'previous source-leaves PASS')
 R['previous_source_leaves_receipt_sha256']=hashlib.sha256((P/'ATTEMPT2-BOUNDED-LEAF-RESULT.json').read_bytes()).hexdigest()
 R['source_leaves_repeated']=False;R['source_leaves_prior_seconds']=prior['source_leaves_seconds']
 builtins.__import__=watched
 print('START actual Tape/Count/Arithmetic/DigitWordProduct/J+split leaf',flush=True)
 sys.path.insert(0,str(PKG));from sandwich_sources import opened
 with opened():
  import tensor_engine,crt_converter
  need(patched=={'tensor_engine','crt_converter'},'both numerical guards installed in method-only cohort')
  R['guards_before_leaf']=True
  from cardinal_counts import Count
  from records import Tape
  from router_metadata import owned
  from scratch_pool import ScratchPool
  from session import OuterScope,initialize_marker,erase_marker,sealed_constructors
  from tensor_records import bounded_record_io
  from tensor_word import DigitWordProduct
  from fft_arithmetic import Arithmetic
  from ring_words import read_signed
  from ring_check_words import tape
  from check_composed import encode
  from expansion_check_block import packet_bytes
  from words import BLANK
  spec=importlib.util.spec_from_file_location('packed_draft',DRAFT);draft=importlib.util.module_from_spec(spec);spec.loader.exec_module(draft)
  class LeafOwner:
   pack_real=draft.RealPackedSandwich.pack_real
   move_bits=staticmethod(draft.RealPackedSandwich.move_bits)
   negate_frequencies=draft.RealPackedSandwich.negate_frequencies
   pointwise=draft.RealPackedSandwich.pointwise
   def __init__(self):
    self.pool=ScratchPool(128);self.word=DigitWordProduct();self.scope=OuterScope(self.pool);self.arithmetic=Arithmetic(self.word,self.scope)
    self.last_counts=dict(packed_records=0,J_axis_passes=0,split_records=0,split_exact_adds=0,pointwise_real_products=0)
    for t in self.pool.tapes:erase_marker(t)
  class Axis:
   def __init__(self,s):self.s=Count.literal(s)
   def close(self):self.s.close()
  class Plan:
   def __init__(self):
    self.p=Count.literal(48);self.component_bits=Count.literal(50);self.record_bits=Count.literal(100);self.dimensions=Count.literal(2);self.source_product=Count.literal(35)
   def axis(self,index):
    # Both metadata coordinates are read using the authenticated encoded
    # comparator, never by decoding an input-dependent Count.
    from encoded import compare
    with owned(Count.literal(0))as(zero,):return Axis(5 if compare(index,zero)==0 else 7)
   def close(self):
    for value in vars(self).values():value.close()
  owner=LeafOwner();plan=Plan();p=48;N=35
  h=[((((17*j+11)%63-31)<<(p-8))+(j==1),(((29*j+7)%57-28)<<(p-8))+(j==3))for j in range(N)]
  raw=encode(h,50);bank=tape(raw);snapshot=(tuple(bank.cells),bank.head)
  zero=[(0,0)]*N;u=[(j<<(p-8),0)for j in range(N)];v=[((34-j)<<(p-8),0)for j in range(N)]
  first,second=tape(encode(u,50)),tape(encode(v,50));borrowed=[bank,first,second];snapshots=[(tuple(t.cells),t.head)for t in borrowed]
  for t in owner.pool.tapes:initialize_marker(t)
  counters={k:0 for k in ('read','step','append','rewind','clear')};primitive={};enabled=[False];peak=[0];word_calls=[0]
  for name in counters:
   original=getattr(Tape,name);primitive[name]=original
   def counted(self,*a,_name=name,_original=original,**kw):
    if enabled[0]:counters[_name]+=1;peak[0]=max(peak[0],len(owner.pool.live))
    return _original(self,*a,**kw)
   setattr(Tape,name,counted)
  word_original=owner.word.run
  def word_count(*a,**kw):word_calls[0]+=1;return word_original(*a,**kw)
  owner.word.run=word_count
  def observe(value):
   enabled[0]=False
   try:return packet_bytes(value)
   finally:enabled[0]=True
  reflected=product=packed=None
  try:
   with bounded_record_io(),sealed_constructors(),owner.scope.installed():
    enabled[0]=True
    packed=owner.pack_real(first,second,plan);packed_bits=observe(packed);packed.clear();packed=None
    reflected=owner.negate_frequencies(bank,plan);reflected_bits=observe(reflected)
    product=owner.pointwise(bank,reflected,plan);product_bits=observe(product)
    product.clear();product=None;reflected.clear();reflected=None;owner.pool.empty()
    enabled[0]=False
   success_counters=counters.copy()
   expectedJ=[h[((-i)%5)*7+((-j)%7)]for i in range(5)for j in range(7)]
   need(reflected_bits==encode(expectedJ,50),'all35 actual J records')
   need(packed_bits==encode([(a[0],b[0])for a,b in zip(u,v)],50),'both independent real streams packed once')
   tz=lambda x,bits:(abs(x)>>bits)*(-1 if x<0 else 1)
   def square_oracle(values,reflected,conjugate=True,sign=1,shift=50):
    out=[]
    for(a,b),(c,d)in zip(values,reflected):
     if not conjugate:d=-d
     # Independent squared-difference /4i formula, rather than four split products.
     rr=2*a*b+2*c*d;ii=-a*a+b*b+c*c-d*d
     out.append((sign*tz(rr,shift),sign*tz(ii,shift)))
    return out
   expected=square_oracle(h,expectedJ)
   need(product_bits==encode(expected,50),'all35 physical once-truncated products')
   mutants={'wrong_J_identity':square_oracle(h,h),'omitted_conjugation':square_oracle(h,expectedJ,False),'wrong_i_sign':square_oracle(h,expectedJ,True,-1),'wrong_raw_shift_p':square_oracle(h,expectedJ,True,1,48)}
   rejected={k:any(x!=y for x,y in zip(expected,v))for k,v in mutants.items()};need(all(rejected.values()),'all four mutants distinguished')
   odd=any((a+c)%2 or(b-d)%2 or(b+d)%2 or(c-a)%2 for(a,b),(c,d)in zip(h,expectedJ));need(odd,'actual odd half-sum probe')
   need(word_calls[0]==140,'four actual real word products per coordinate')
   need(all((tuple(t.cells),t.head)==s for t,s in zip(borrowed,snapshots)),'success borrowed values/cursors restored')
   # Harness finally, rather than local-method guarantees, restores borrowed
   # cursors and releases leases on exceptions. Do not claim full run coverage.
   failure=tape(encode([(1,1)]+u[1:],50));failure_snapshot=tuple(failure.cells)
   try:
    enabled[0]=True
    with bounded_record_io(),sealed_constructors(),owner.scope.installed():owner.pack_real(failure,second,plan)
   except ValueError as error:need('two real'in str(error),'real-input rejection')
   else:raise ValueError('complex operand accepted')
   finally:
    failure.rewind();second.rewind()
    for lease in tuple(owner.pool.live.values()):lease.clear()
    owner.pool.empty();enabled[0]=False
   need(tuple(failure.cells)==failure_snapshot,'failure borrowed data preserved')
   R['leaf']={'source_shape':[5,7],'p':48,'component_bits':50,'split_operand_bits':51,'product_shift':50,'records':35,'numerators_h':h,'numerators_Jh':expectedJ,'numerators_product':expected,'method_counts':owner.last_counts,'actual_real_word_products':word_calls[0],'primitive_counts_success_including_cleanup_and_encoded_metadata':success_counters,'primitive_counts_failure_probe_and_harness_cleanup':{k:counters[k]-success_counters[k]for k in counters},'inspection_capture_excluded_from_primitive_counter':True,'peak_parent_leases_observed':peak[0],'route_direct_source_moves_algebra':30200,'route_output_writes_algebra':7000,'bank_bits':3500,'mutants_rejected_by_independent_oracle_on_actual_stage_data':rejected,'odd_raw_split_exact':odd,'borrowed_success_restored':True,'failure_harness_cleanup':True,'source_Tensor_returns_supplied':False,'data_class':'supplied bounded p-grid bank; no produced Tensor approximation claim'}
  finally:
   enabled[0]=False
   for name,original in primitive.items():setattr(Tape,name,original)
   for t in borrowed:t.rewind()
   for lease in tuple(owner.pool.live.values()):lease.clear()
   owner.pool.empty()
   for t in owner.pool.tapes:erase_marker(t)
   plan.close()
 R['status']='PASS_BOUNDED_PHYSICAL_METHOD_LEAF'
except BaseException as error:
 R['status']='TIMEOUT'if isinstance(error,TimeoutError)else'FAIL';R['error']=repr(error);R['traceback']=traceback.format_exc();print(R['traceback'],flush=True)
finally:
 signal.alarm(0);builtins.__import__=original_import;R['seconds']=round(time.monotonic()-START,6);R['after_hashes']=hashes();R['all_consumed_source_and_draft_hashes_unchanged']=R['after_hashes']==BEFORE
 (P/'METHOD-LEAF-RESULT.json').write_text(json.dumps(R,indent=2)+'\n')
 print(json.dumps({k:v for k,v in R.items()if k not in ('before_hashes','after_hashes','leaf','traceback')},sort_keys=True),flush=True)
 if R['status']!='PASS_BOUNDED_PHYSICAL_METHOD_LEAF':sys.exit(1)
