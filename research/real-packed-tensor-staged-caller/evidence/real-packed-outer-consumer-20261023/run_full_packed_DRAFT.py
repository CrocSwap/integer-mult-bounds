"""STATIC DRAFT. Execute only after root approval of the complete-call budget.

One frozen candidate, one cached reduced p48 fixture, exactly two numerical
Tensor and three numerical Converter calls; no producer or original full replay.
"""
from pathlib import Path
import hashlib,importlib.util,json,signal,sys,threading,time,traceback
P=Path(__file__).resolve().parent;ROOT=P/'staged-source';PKG=ROOT/'research/physical-tensor-crt-sandwich-recovery';DRAFT=P/'packed_sandwich_DRAFT.py'
START=time.monotonic();R={'status':'RUNNING','scope':'One actual two-Tensor reduced staged caller; no production accuracy or cost-saving claim','source_head':'e65f47db55b9a3779fbf7fe23e93a8a4c5eb3ce1','source_shape':[5,7],'target_shape':[8,8],'p':48,'P':80,'b':8,'q':4,'require_recovery':False,'Tensor_calls':0,'Converter_calls':0,'injected_child_dispatches':0,'phase':'authentication','cap_seconds':600,'arrays':{}}
FIRST=[255,0,3,17];SECOND=[1,254,0,9]
R['independent_digit_streams']=[FIRST,SECOND]
def need(x,m):
 if not x:raise ValueError(m)
def hashes():return {str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest()for f in [DRAFT,*sorted(ROOT.rglob('*'))]if f.is_file()}
BEFORE=hashes();R['before_hashes']=BEFORE;R['harness_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
need(BEFORE['packed_sandwich_DRAFT.py']=='5dfcdfe63d9d03a89a00dd92e681ab0a0efc5bbc86aa7edae58f007baf752483','frozen candidate')
for row in json.loads((PKG/'SOURCES.json').read_text())['files']:
 if row['usage']=='input':need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source input '+row['path'])
for row in json.loads((P/'PUBLIC-TEXT-MANIFEST.json').read_text()):need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'public source '+row['path'])
raw=(PKG/'inputs/p48-5x7.bin').read_bytes();need(hashlib.sha256(raw).hexdigest()=='7dd7adbe9e8f6d5ffbecd425a72827b31d7222ee51bcd67a4148ebfd03420381','immutable published p48 cache')
def alarm(*_):raise TimeoutError('complete staged-caller budget reached')
signal.signal(signal.SIGALRM,alarm);signal.alarm(580)
finished=threading.Event()
def heartbeat():
 while not finished.wait(30):print(json.dumps({'progress_seconds':round(time.monotonic()-START,3),'phase':R['phase'],'Tensor_calls':R['Tensor_calls'],'Converter_calls':R['Converter_calls']}),flush=True)
threading.Thread(target=heartbeat,daemon=True).start()
try:
 sys.path.insert(0,str(PKG));from sandwich_sources import opened
 with opened():
  from cardinal_counts import Count
  from records import Tape
  from router_metadata import owned
  from session import initialize_marker,erase_marker
  from tensor_engine import Tensor
  from tensor_fixture import finite_chirp,literal_native,p48_setup
  from tensor_router import FullRouter
  from crt_converter import Converter
  from tensor_records import bounded_record_io
  from check_support import no_decode
  from ring_check_words import tape,word_bits
  from check_composed import encode
  from expansion_check_block import packet_bytes
  from words import BLANK,LEFT
  from sandwich_reference import full,crt,inverse_crt
  spec=importlib.util.spec_from_file_location('frozen_packed',DRAFT);draft=importlib.util.module_from_spec(spec);spec.loader.exec_module(draft)
  # The inherited oracle is a separate natural-coordinate staged algorithm.
  # Run it on the actual packed input/product, never on separately rounded
  # forwards combined after their returns.
  R['phase']='staged oracle preflight'
  ingress=[[(d<<(48-8-2),0)for d in digits]+[(0,0)]*(35-4)for digits in (FIRST,SECOND)]
  naturals=[crt(v)for v in ingress];packed=[(a[0],b[0])for a,b in zip(*naturals)]
  forward=full(packed,raw)
  J=lambda values:[values[((-i)%5)*7+((-j)%7)]for i in range(5)for j in range(7)]
  reflected=J(forward);tz=lambda v,bits:(abs(v)>>bits)*(-1 if v<0 else 1)
  product=[(tz(2*a*b+2*c*d,50),tz(-a*a+b*b+c*c-d*d,50))for(a,b),(c,d)in zip(forward,reflected)]
  need(any(a or b for a,b in forward),'nonzero staged packed forward required')
  need(any(a or b for a,b in product),'nonzero staged nonlinear product required')
  need(all(a*a+b*b<=(1<<94)for a,b in product),'staged opposite half-disk input')
  opposite=full(product,raw,True)
  nearest=lambda n:(abs(n)+(1<<47))//(1<<48)*(-1 if n<0 else 1)
  natural_coefficients=[nearest(a*35*35*(1<<20))for a,_ in opposite]
  ordinary_coefficients=inverse_crt(natural_coefficients)
  need(all(c>=0 for c in ordinary_coefficients),'diagnostic carry domain')
  integer=sum(c*256**i for i,c in enumerate(ordinary_coefficients))
  need(integer<(1<<64),'diagnostic output fits prescribed 2q radix digits')
  expected_output=bytes((integer>>i)&1 for i in reversed(range(64)))
  R['arrays'].update(expected_natural_inputs=naturals,expected_packed=packed,expected_forward=forward,expected_J=reflected,expected_product=product,expected_opposite=opposite,expected_coefficients=ordinary_coefficients)
  R['staged_integer']=integer;R['true_integer']=sum(v*256**i for i,v in enumerate(FIRST))*sum(v*256**i for i,v in enumerate(SECOND));R['production_recovery_claim']=False
  R['diagnostic_difference']=integer-R['true_integer'];R['diagnostic_equals_true_product']=integer==R['true_integer']
  R['unrun_full_stage_mutation_controls']=['wrong opposite sign','same-R replaced by inverse-R','missing one S','double gamma restoration']
  R['mutation_boundary']='Earlier method leaf discriminated J/conjugation/i-sign/raw-product shift on supplied physical method data. This whole-run harness asserts correct call signs and exact full staged returns but does not execute the four listed mutated numerical callers.'
  R['staged_nonzero_records']={'forward':sum(bool(a or b)for a,b in forward),'product':sum(bool(a or b)for a,b in product),'opposite':sum(bool(a or b)for a,b in opposite)}
  R['phase']='owner construction and candidate preflight controls'
  tensor=Tensor(finite_chirp(),FullRouter(literal_native()));converter=Converter(FullRouter(literal_native()))
  original_tensor=tensor.run;original_converter=converter.run_plan
  observations=[];conversions=[]
  def capture(value):
   head=value.head;data=packet_bytes(value);need(value.head==head,'inspection preserves canonical child head');return data
  def observe_tensor(*args,**options):
   need(R['phase']=='actual candidate','no numerical Tensor outside the one declared caller')
   index=R['Tensor_calls'];need(index<2,'at most two numerical Tensor calls')
   opposite_flag=options.get('opposite',False);need(opposite_flag==(index==1),'actual forward/opposite order')
   expected_in=packed if index==0 else product;need(capture(args[0])==encode(expected_in,50),'exact numerical Tensor input')
   R['Tensor_calls']+=1;print('NUMERICAL_TENSOR_START',index,opposite_flag,flush=True)
   returned=original_tensor(*args,**options)
   try:
    data=capture(returned)
    need(data==encode(forward if index==0 else opposite,50),'all35 actual Tensor returned complex records')
    observations.append({'opposite':opposite_flag,'input_sha256':hashlib.sha256(encode(expected_in,50)).hexdigest(),'return_sha256':hashlib.sha256(data).hexdigest(),'raw_bits':list(data),'complete_child_counts':dict(tensor.last_counts),'seconds':round(time.monotonic()-START,3)})
   except BaseException:
    returned.clear();erase_marker(returned);raise
   print('NUMERICAL_TENSOR_FINISH',index,flush=True);return returned
  def observe_converter(*args,**options):
   if R['phase']=='injected first converter dispatch failure':
    R['injected_child_dispatches']+=1;raise ValueError('declared injected first converter failure before numerical child')
   need(R['phase']=='actual candidate','no numerical Converter outside the one declared caller')
   index=R['Converter_calls'];need(index<3,'at most three numerical Converter calls')
   inverse=options.get('inverse',False);need(inverse==(index==2),'two forward CRT then one inverse')
   input_data=capture(args[0]);expected_input=encode(ingress[index],50)if index<2 else b''.join(word_bits(v,86)for v in natural_coefficients)
   need(input_data==expected_input,'all actual CRT input records before numerical child')
   R['Converter_calls']+=1;returned=original_converter(*args,**options)
   try:
    data=capture(returned)
    expected=encode(naturals[index],50)if index<2 else b''.join(word_bits(v,86)for v in ordinary_coefficients)
    need(data==expected,'all actual CRT returned records')
    conversions.append({'inverse':inverse,'input_sha256':hashlib.sha256(input_data).hexdigest(),'input_raw_bits':list(input_data),'return_sha256':hashlib.sha256(data).hexdigest(),'raw_bits':list(data),'complete_child_counts':dict(converter.last_counts)})
   except BaseException:
    returned.clear();erase_marker(returned);raise
   return returned
  tensor.run=observe_tensor;converter.run_plan=observe_converter
  from entry_controls import construction,check
  construction(draft.RealPackedSandwich,tensor,converter,initialize_marker,erase_marker,need)
  machine=draft.RealPackedSandwich(tensor,converter)
  R['candidate_preflight_controls']=check(machine,tape,raw,Count,owned,initialize_marker,erase_marker,need)
  need(R['Tensor_calls']==R['Converter_calls']==0,'all preflight controls rejected before numerical children')
  first=tape(b''.join(word_bits(x,8)for x in FIRST));second=tape(b''.join(word_bits(x,8)for x in SECOND));catalogue=tape(raw)
  borrowed=(first,second,catalogue);before=[(tuple(t.cells),t.head)for t in borrowed]
  original_pointwise=machine.pointwise
  def observe_pointwise(*args):
   need(capture(args[0])==encode(forward,50)and capture(args[1])==encode(reflected,50),'actual H and paid JH banks')
   returned=original_pointwise(*args);need(capture(returned)==encode(product,50),'all35 actual fused pointwise products')
   R['arrays']['actual_pointwise_bits']=list(capture(returned));return returned
  machine.pointwise=observe_pointwise
  with owned(Count.literal(8),Count.literal(4))as(b,q):
   metadata_before=[(tuple(t.tape.cells),t.tape.head)for t in (b,q)]
   R['phase']='actual candidate'
   with p48_setup()as setup,no_decode():returned=machine.run(first,second,catalogue,b,q,require_recovery=False)
   actual_output=capture(returned);need(actual_output==expected_output,'diagnostic nearest/inverse-CRT/carry return')
   need((R['Tensor_calls'],R['Converter_calls'])==(2,3),'exact completed numerical call census')
   need(tensor.calls==2,'two underlying complete Tensor executions')
   actual_counts=machine.last_counts.copy();need(actual_counts==dict(conversions=3,transforms=2,pointwise_products=1,packed_records=35,J_axis_passes=2,split_records=35,split_exact_adds=140,pointwise_real_products=140),'actual frozen candidate counters')
   need(machine.closed and not machine.pool.live and machine.pending,'closed full caller with one pending return')
   need([(tuple(t.cells),t.head)for t in borrowed]==before,'full caller borrowed values and heads restored')
   need([(tuple(t.tape.cells),t.tape.head)for t in (b,q)]==metadata_before,'full caller metadata values and heads restored')
   tensor.idle();converter.idle()
   # Read-only output movement to the end must not bypass the pending token.
   while returned.read()!=BLANK:returned.step(1)
   R['phase']='pending output rejection'
   try:machine.run(first,second,catalogue,b,q,require_recovery=False)
   except ValueError as error:need('consume prior sandwich'in str(error),'pending end-head guard')
   else:raise ValueError('occupied full return reused')
   need((R['Tensor_calls'],R['Converter_calls'])==(2,3),'no numerical calls on pending rejection')
   machine.consume();need(not machine.pending and not machine.pool.live and machine.output.read()==BLANK,'paid consume clears return')
   R['phase']='post-consume production policy rejection'
   try:machine.run(first,second,catalogue,b,q)
   except ValueError as error:need('production coefficient'in str(error),'default production entry still rejects cached reduced pages')
   else:raise ValueError('reduced catalogue admitted as production')
   need(not machine.pending and machine.closed and not machine.pool.live,'policy rejection cleanup')
   # Test one declared live-parent failure cut without another original child
   # operation: the first Converter dispatch throws before delegation.
   R['phase']='injected first converter dispatch failure'
   try:machine.run(first,second,catalogue,b,q,require_recovery=False)
   except ValueError as error:need('declared injected first converter failure'in str(error),'injected child failure reaches parent finally')
   else:raise ValueError('missing injected dispatch failure')
   need(R['injected_child_dispatches']==1 and(R['Tensor_calls'],R['Converter_calls'])==(2,3),'failure probe adds zero numerical calls')
   need(machine.closed and not machine.pending and not machine.pool.live and machine.output.read()==BLANK,'injected first-dispatch parent cleanup')
   need([(tuple(t.cells),t.head)for t in borrowed]==before,'failure borrowed data and heads restored')
   need([(tuple(t.tape.cells),t.tape.head)for t in (b,q)]==metadata_before,'failure metadata data and heads restored')
   tensor.idle();converter.idle()
   for private in machine.private:
    need(private.read()==BLANK,'empty resident current cursor after consume/failures')
    private.step(-1)
    try:need(private.read()in(BLANK,LEFT),'canonical empty resident origin')
    finally:private.step(1)
   R.update(actual_counts=actual_counts,p48_setup_metadata_counts=dict(setup),output_sha256=hashlib.sha256(actual_output).hexdigest(),output_bits=list(actual_output),pending_end_head_rejected=True,consume_and_reuse_policy_checked=True,borrowed_values_heads_restored=True,metadata_values_heads_restored=True,injected_failure_cut='first Converter dispatch before original child operation',failure_cleanup_scope='parent owns first ingress bank; no arbitrary post-numerical-child exception claim',resident_empty_origin_checks=True)
  R['actual_Tensor_observations']=observations;R['actual_Converter_observations']=conversions
 R['phase']='complete';R['status']='PASS_ACTUAL_TWO_TENSOR_STAGED_PACKED_CALLER'
except BaseException as error:
 R['status']='TIMEOUT'if isinstance(error,TimeoutError)else'FAIL';R['error']=repr(error);R['traceback']=traceback.format_exc();print(R['traceback'],flush=True)
finally:
 finished.set();signal.alarm(0);R['seconds']=round(time.monotonic()-START,6);R['after_hashes']=hashes();R['source_and_candidate_unchanged']=R['after_hashes']==BEFORE
 R['harness_after_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();R['harness_unchanged']=R['harness_after_sha256']==R['harness_sha256']
 if not(R['source_and_candidate_unchanged']and R['harness_unchanged']):
  R['status_before_integrity_failure']=R['status'];R['status']='FAIL_SOURCE_OR_HARNESS_DRIFT'
 (P/'FULL-PACKED-RESULT.json').write_text(json.dumps(R,indent=2)+'\n')
 print(json.dumps({k:v for k,v in R.items()if k not in('arrays','before_hashes','after_hashes','traceback','actual_Tensor_observations','actual_Converter_observations')},sort_keys=True),flush=True)
 if R['status']!='PASS_ACTUAL_TWO_TENSOR_STAGED_PACKED_CALLER':sys.exit(1)
