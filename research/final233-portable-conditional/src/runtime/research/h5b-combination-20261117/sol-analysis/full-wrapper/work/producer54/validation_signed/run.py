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
adapter=load('producer_adapter',HERE/'w2_adapt.py')
FROZEN=ROOT/'frozen-composition'
old_word=read(FROZEN/'7546-WORD.json.gz');new_word=read(CANDIDATE/'WORD.json.gz')
assert new_word==read(FROZEN/'CANDIDATE-WORD.json.gz'),'Pinned literal helper757 word'
assert sha256(canonical(new_word)).hexdigest()=='8ab3d9dbe2e2e24202ac96c6122b010b3e7980912f935cc0cc2db2e9d85f83aa'
adjusted=read(FROZEN/'7546-WORD.json.gz');assert adjusted['initial'][457]==3;adjusted['initial'][457]=281
assert {k:v for k,v in adjusted.items()if k!='program'}=={k:v for k,v in new_word.items()if k!='program'},'Only declared initial457 delta; exact other metadata'
old_result=read(FROZEN/'7546-NATIVE.json');new_result=read(NATIVE)
assert new_result['status']=='PASS_COMBINED_CANDIDATE_ADAPTED_NATIVE'
assert old_result['word_canonical_sha256']=='bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745'
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
  previous=read(FROZEN/'7546-SIGNED.json')['price']
  assert Q(previous['gate']['claim'])==Q('0.003648411294790')
  ranks=set(before['P'])|set(after['P'])
  delta={r:after['P'].get(r,0)-before['P'].get(r,0)for r in ranks if after['P'].get(r,0)!=before['P'].get(r,0)}
  assert delta=={1:-561,2:918,3:-3689,4:697,5:255,6:901,8:34} and {r:after['T'].get(r,0)-before['T'].get(r,0) for r in set(after['T'])|set(before['T']) if after['T'].get(r,0)!=before['T'].get(r,0)}=={6:17,9:-17}
  assert before['S']==after['S']==1424 and not before['empty_root_credits'] and not after['empty_root_credits']
  assert sum(after['P'].values())==109023 and sum(after['T'].values())==22461
  assert normal(before)==previous['after'],'Whole reconstructed #7546 invoice'
  peer_word=read(FROZEN/'7604-WORD.json.gz')
  peer_native=ind.native(peer_word);assert not peer_native['bad_inputs']
  peer_invoice=ind.invoices(peer_word,C,peer_native)
  frozen_peer=read(FROZEN/'7604-INVOICE.json')
  assert normal(peer_invoice['P'])==frozen_peer['paid'] and normal(peer_invoice['T'])==frozen_peer['targets']
  assert peer_invoice['S']==1424 and not peer_invoice['empty_root_credits']
  ranks=set(peer_invoice['P'])|set(after['P'])
  assert {r:after['P'].get(r,0)-peer_invoice['P'].get(r,0)for r in ranks if after['P'].get(r,0)!=peer_invoice['P'].get(r,0)}=={1:-493,2:986,3:-3706,4:680,5:238,6:901,8:34}
  candidate_invoice=read(FROZEN/'CANDIDATE-INVOICE.json')
  assert normal(after['P'])==candidate_invoice['paid'] and normal(after['T'])==candidate_invoice['targets']
  G=load('producer_signed_price_engine',bundle/'gate.py')
  gate,price=G.exact_price(vendor,archive,before,after,{'gate':previous['gate']})
  assert Q(gate['claim'])>Q(previous['gate']['raw_bracket'][1]),'Strictly higher than #7546 raw crossing'
  assert Q(gate['claim'])>Q('0.0036475398278'),'Strictly higher than upper endpoint of #7542 price enclosure'
  assert Q(gate['claim'])>Q(new_result['gate']['claim'])
  native_invoice={k:({int(r):v for r,v in value.items()}if k in('T','P')else value)for k,value in new_result['invoice'].items()}
  directed=G.module('producer_native_comparator',vendor/'interval_gate.py')
  assert directed.moment(G.signed(before),Q(gate['claim']))[1]<0,'Exact #7546 invoice rejects the new signed claim'
  assert directed.moment(G.signed(native_invoice),Q(gate['claim']))[1]<0
  assert directed.moment(G.signed(peer_invoice),Q(gate['claim']))[1]<0,'Exact open #7604 invoice rejects the new signed claim'
  assert Q(gate['claim'])>Q('0.0036502223358273'),'Strict improvement over latest #7604 crossing'
  assert Q(gate['claim'])>=Q('0.0037'),'Conservative public claim is within the proved application'
  public_claim=Q('0.0037')
  public_gate=directed.gate(after,public_claim,public_claim+Q(7,10**17),*map(Q,gate['raw_bracket']),Q(gate['BIT_pin']))
  price_record=normal(dict(public_claim_gate=public_gate,before=before,after=after,gate=gate,price=price,
    native_baseline_rejects_new_claim=True,signed_incumbent_rejects_new_claim=True,
    old_native=old_result['word_canonical_sha256'],new_native=new_result['word_canonical_sha256']))
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
   cached=HERE/f'CACHED-SHORT-CATALOGUE-{start}-{stop}.log'
   if cached.exists():
    raw_cached=cached.read_text();cached_rec=json.loads(raw_cached[raw_cached.index('\n{'):])
    assert cached_rec['word_sha256']=='d7eb204bb24b2e1b5a3e4ebc282d346a4706ddd738004929d1e9ac345085a79a'
    assert cached_rec['slice_start']==start and cached_rec['slice_stop']==stop
    shutil.copy2(cached,path)
   else:
    with path.open('x')as stream:subprocess.run([sys.executable,'-B',str(folder/'short_native_catalogue.py'),'--start',str(start),'--stop',str(stop)],cwd=folder,stdout=stream,check=True)
   text=path.read_text();catalogue.append(json.loads(text[text.index('\n{'):]))
   shutil.copy2(path,HERE/path.name)
  with(HERE/'assemble_odd_application.py.log').open('w')as stream:
   subprocess.run([sys.executable,'-B',str(folder/'assemble_odd_application.py')],cwd=folder,stdout=stream,stderr=subprocess.STDOUT,check=True)
  print((HERE/'assemble_odd_application.py.log').read_text(),end='',flush=True)
  files=('ODD-TYPE-AB-REPLAY.json','ODD-CALLER-EXACT-GRID.json','ODD-PHYSICAL-BINDING.json',
         'ODD-PRECISION.json','ODD-ADMISSION-PARTIAL.json','ODD-FIXED-TAPE-COUNTS.json','ODD-8X9-APPLICATION-CHECKS.json')
  result=normal(dict(status='PASS_COMBINED_CANDIDATE_ADAPTED_SIGNED_APPLICATION',
    claim=fresh_price['gate']['claim'],price=fresh_price,caller_sha256=sha256((folder/'ODD-TYPE-AB-CALLER.json').read_bytes()).hexdigest(),
    adapter=changes,catalogue=catalogue,checks={name:read(folder/name)for name in files},
    source_head='99438c43df7aac1e5dbcc43c1578fcd886c119ec',peer_head='ba2638c5a6e2b9a1c0c559a41811e5d41a591f41',
    component_head='71f5acb0409daf208a865482f3349049dbd3251c',timings=log,elapsed_seconds=time.time()-started,
    assumptions=['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery']))
  OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
  # Retain the precisely adapted checker text and its generated essential inputs.
  keep=HERE/'adapted';keep.mkdir(exist_ok=True)
  for name in set(commands)|{'short_native_catalogue.py','assemble_odd_application.py','CURRENT-PRICE.json','COHORT-PRICE.json'}:
   shutil.copy2(folder/name,keep/name)
  print(result['status'],price['claim_decimal'],flush=True)
