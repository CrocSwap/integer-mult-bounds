"""Fresh exact17-stage application of the changed485/1455 producer.

Retained source checks and attribution come from the authenticated #7480
closure. All adaptations are counted and recorded. No selected frontier is
modified. Apache-2.0, following the retained source notices.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util,json,gzip,shutil,subprocess,sys,time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'inputs/pr7480'
CANDIDATE=ROOT/'producer54/reroute'
NATIVE=ROOT/'producer54/validation_native/NATIVE-RESULT.json'
OUT=HERE/'RESULT.json'
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);obj=importlib.util.module_from_spec(spec);sys.modules[name]=obj;spec.loader.exec_module(obj);return obj
def read(path):
 raw=Path(path).read_bytes();return json.loads(gzip.decompress(raw)if raw[:2]==b'\x1f\x8b'else raw)
def normal(x):return json.loads(json.dumps(x,default=str))
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
assert __debug__
src=load('producer_source',SOURCE/'source.py')
adapter=load('producer_adapter',SOURCE/'adapt.py')
old_word=read(SOURCE/'WORD.json.gz');new_word=read(CANDIDATE/'WORD.json.gz')
old_result=read(SOURCE/'NATIVE-RESULT.json');new_result=read(NATIVE)
assert sha256(canonical(new_word)).hexdigest()==new_result['word_canonical_sha256']
commands=('emit_odd_type_b.py','emit_odd_type_ab.py','check_odd_caller_exact_grid.py',
          'check_odd_physical_binding.py','check_odd_precision.py','check_odd_partial_admission.py',
          'check_odd_fixed_tape_counts.py')
log=[];started=time.time()
with src.sources()as(vendor,archive,rank9,bundle,parent,unused_old):
 with src.bundles()as(parts,unused_previous,temp):
  working=temp/'producer54-signed-working';shutil.copytree(parts[7113]/'replay',working)
  folder=working/'supplier7112/short-caller'
  (folder.parent/'WORD.json.gz').write_bytes((CANDIDATE/'WORD.json.gz').read_bytes())
  (folder.parent/'RESULT.json').write_bytes(NATIVE.read_bytes())
  for path in folder.glob('SHORT-CATALOGUE-*-*.log'):path.unlink()
  sys.path.insert(0,str(folder))
  model=load('producer_signed_model',folder/'signed_model.py');ind=model.signed_model()
  code=(folder/'independent.py').read_text();part=code[code.index('def invoices('):code.index('def ordinary(')]
  assert part.count('assert calls==18')==1
  part=part.replace('assert calls==18',"assert calls==C['stages']")
  old="elif e[1]=='IDLE_ONE':P[8*len(e[3])]+=ports";assert part.count(old)==1
  part=part.replace(old,"elif e[1] in ('IDLE_ONE','IDLE_ODD'):P[8*len(e[3])+(e[1]=='IDLE_ODD')]+=ports")
  exec(compile(part,str(folder/'independent.py'),'exec'),ind.__dict__)
  C=read(parts[7113]/'expected/ODD-TYPE-AB-CALLER.json')
  assert sha256((parts[7113]/'expected/ODD-TYPE-AB-CALLER.json').read_bytes()).hexdigest()=='255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'
  inventories=[ind.native(w)for w in(old_word,new_word)]
  for n,r,w in zip(inventories,(old_result,new_result),(old_word,new_word)):
   assert normal(n)==r['native']and not n['bad_inputs']
   assert sha256(canonical(w)).hexdigest()==r['word_canonical_sha256']
  before,after=[ind.invoices(w,C,n)for w,n in zip((old_word,new_word),inventories)]
  previous=read(SOURCE/'RESULT.json')['price']
  assert normal(before)==previous['after'],'Whole reconstructed #7480 invoice'
  G=load('producer_signed_price_engine',bundle/'gate.py')
  gate,price=G.exact_price(vendor,archive,before,after,{'gate':previous['gate']})
  assert Q(gate['claim'])>Q('0.003646777872835')
  assert Q(gate['claim'])>Q(new_result['gate']['claim'])
  native_invoice={k:({int(r):v for r,v in value.items()}if k in('T','P')else value)for k,value in new_result['invoice'].items()}
  directed=G.module('producer_native_comparator',vendor/'interval_gate.py')
  assert directed.moment(G.signed(native_invoice),Q(gate['claim']))[1]<0
  price_record=normal(dict(before=before,after=after,gate=gate,price=price,
    native_baseline_rejects_new_claim=True,old_native=old_result['word_canonical_sha256'],new_native=new_result['word_canonical_sha256']))
  (folder/'CURRENT-PRICE.json').write_text(json.dumps(price_record,indent=2)+'\n')
  (folder/'COHORT-PRICE.json').write_text(json.dumps(normal(dict(target=after['T'],paid=after['P'],bracket=gate['raw_bracket'])),indent=2)+'\n')
  (HERE/'PRICE.json').write_text(json.dumps(price_record,indent=2)+'\n')
  print('PASS two complete literal invoices and both directed prices',price['claim_decimal'],flush=True)
  changes=adapter.adapt(folder,price['claim_decimal'],new_result['derived_grid']['fractional_bits'])
  for name in commands:
   print('RUN',name,flush=True);tick=time.time()
   with (HERE/(name+'.log')).open('w')as stream:
    subprocess.run([sys.executable,'-B',str(folder/name)],cwd=folder,stdout=stream,stderr=subprocess.STDOUT,check=True)
   log.append({'check':name,'seconds':time.time()-tick})
   print((HERE/(name+'.log')).read_text(),end='',flush=True)
  assert(folder/'ODD-TYPE-AB-CALLER.json').read_bytes()==(parts[7113]/'expected/ODD-TYPE-AB-CALLER.json').read_bytes()
  fresh_price=read(folder/'CURRENT-PRICE.json');partial=read(folder/'ODD-ADMISSION-PARTIAL.json')
  assert fresh_price['after']==partial['invoice']
  assert fresh_price['gate']==partial['compiler_outer']
  catalogue=[]
  size=int(subprocess.check_output([sys.executable,'-B',str(folder/'short_native_catalogue.py'),'--size'],cwd=folder,text=True))
  for start in range(0,size,1000):
   stop=min(start+1000,size);print('RUN complete catalogue',start,stop,flush=True)
   path=folder/f'SHORT-CATALOGUE-{start}-{stop}.log'
   with path.open('x')as stream:subprocess.run([sys.executable,'-B',str(folder/'short_native_catalogue.py'),'--start',str(start),'--stop',str(stop)],cwd=folder,stdout=stream,check=True)
   text=path.read_text();catalogue.append(json.loads(text[text.index('\n{'):]))
   shutil.copy2(path,HERE/path.name)
  with(HERE/'assemble_odd_application.py.log').open('w')as stream:
   subprocess.run([sys.executable,'-B',str(folder/'assemble_odd_application.py')],cwd=folder,stdout=stream,stderr=subprocess.STDOUT,check=True)
  print((HERE/'assemble_odd_application.py.log').read_text(),end='',flush=True)
  files=('ODD-TYPE-AB-REPLAY.json','ODD-CALLER-EXACT-GRID.json','ODD-PHYSICAL-BINDING.json',
         'ODD-PRECISION.json','ODD-ADMISSION-PARTIAL.json','ODD-FIXED-TAPE-COUNTS.json','ODD-8X9-APPLICATION-CHECKS.json')
  result=normal(dict(status='PASS_CHANGED_485_1455_PRODUCER_COMPLETE_SIGNED_APPLICATION',
    claim=fresh_price['gate']['claim'],price=fresh_price,caller_sha256=sha256((folder/'ODD-TYPE-AB-CALLER.json').read_bytes()).hexdigest(),
    adapter=changes,catalogue=catalogue,checks={name:read(folder/name)for name in files},
    source_head='58a9d052143f5d85295ed2d0163591c47f89a331',timings=log,elapsed_seconds=time.time()-started,
    assumptions=['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery']))
  OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
  # Retain the precisely adapted checker text and its generated essential inputs.
  keep=HERE/'adapted';keep.mkdir(exist_ok=True)
  for name in set(commands)|{'short_native_catalogue.py','assemble_odd_application.py','CURRENT-PRICE.json','COHORT-PRICE.json'}:
   shutil.copy2(folder/name,keep/name)
  print(result['status'],price['claim_decimal'],flush=True)
