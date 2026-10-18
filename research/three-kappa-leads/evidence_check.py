# SPDX-License-Identifier: Apache-2.0
# Adapted from retained PR3624 verify_evidence.py; original bytes/credits in source archive.
"""Authenticate stored T360 execution evidence; never claims a fresh replay."""
if not __debug__: raise RuntimeError('optimized execution is unsupported')
from pathlib import Path
from fractions import Fraction as Q
import argparse,hashlib,json
PROFILE={'1':7986600,'2':2352240,'3':749250,'4':330480,'5':69930,'8':25920,'48':137790}
PINS_SHA='bbf5db27ce41a97f0918f47a3b6156bf67060ad7e77af406a409fe120d46231e'  # Freeze only after independent terminal receipt audit.
SOURCE='318ede57c79d10323fb1918f7be4d451d1fcdac01c6456fe9851d51d05d59453'
WORDS={'base':'735c540b1fe29d0ceeb4d2f304ec941e5f2bd3bc92bafc8cce2b4f9a67a3b653','extra':'886338fc32da14f3389a82c8120a1bcf9c5e2f0ec3e9b2d377fdae809e1d977f'}
EXPECTED=Q('.001730096363528623534230')-Q(1,10**46)-Q(1,10**70)
FRONTIER=Q('.001730071864705779882540')-Q(1,10**46)-Q(1,10**70)
def need(x,m):
 if not x:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def owner_check(o):
 need(o['status']=='PASS_INDEPENDENT_LITERAL_OWNER_WINDOWS_FAMILIES_PREFIXES_AND_INVOICE','independent owner status')
 need((o['replicas'],o['calls'],o['roles'],o['physical'])==(360,3240,1321920,323069),'owner counts/stock')
 need(o['profile']==PROFILE and sum(int(k)*v for k,v in o['profile'].items())==65088*360,'owner full profile')
 need(o['idle']=={'1':84240,'3':23490,'5':5130,'48':137790},'owner idle')
STRICT_CHECKS={'local_primitive_bound','logical','router','literal','mass','precision','tape','row','halving'}
def strict_check(i):
 c=i.get('strict_checks');need(type(c) is dict and set(c)==STRICT_CHECKS and all(c[k] is True for k in STRICT_CHECKS),'strict finite invoice complete inventory')
def semantic_check(r,s,n,i,o):
 owner_check(o)
 need(r['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE' and s['status']=='PASS_RELEASE','terminal full release')
 need(Q(r['kappa'])==Q(r['kappa_decimal'])==Q(s['kappa_decimal'])==EXPECTED>FRONTIER,'exact endpoint and latest frontier')
 need(r['profile']==PROFILE and r['replicas']==360 and r['actual_expected_helpers']==408,'release actual profile')
 need(r['source_manifest_sha256']==n['manifest_sha256']==SOURCE and r['source_file_count']==648,'frozen source')
 need(r['source_upstream_head']=='ac92a027c78b0c9bb0ada739b26959afda489d0e','actual supplier head')
 need(s['manifest_sha256']==r['package_manifest_sha256'],'release package manifest')
 need(r['order_sha256']=='e14d3c8b183f82ea1f8b1cbdf70d2fb07e450340ebb51815756b1248aa0609d6' and r['dispatch_sha256']=='8064e69e9be904bd81219fdde3b895adbad8d5c43c3a97de46a3aebbdb4424da','literal source clock/dispatch')
 for suffix,key in [('ORDER.json','order_sha256'),('DISPATCH.json','dispatch_sha256')]:
  hs=[h for path,h in o['input_sha256'].items() if path.endswith('/'+suffix)]
  need(hs==[r[key]],'independent owner binding '+suffix)
 need('6e6b8683cc87a84e5410c399b1128eb68694f852a3927cb124067f503ed7d7c7' in r['external_input_sha256'].values(),'original stock checker')
 need(i['status']=='PASS_INDEPENDENT_MIXED_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE','finite invoice status')

 need(n['status']=='PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE' and {t:n['providers'][t]['word_sha256'] for t in WORDS}==WORDS,'both source-bound native providers')
 need([t['name'] for t in r['stages']]==['owners','parent-lift','rebind','discovery','outer-check_ledger.py','outer-independent_check.py','release'] and all(t['exit_code']==0 for t in r['stages']),'complete release stages')
 need(i['physical']==323069==896*360+408+8+91+2 and i['live']==896*360,'physical all stock')
 need(i['helpers']==408 and i['centres']==8 and i['private_zero_buffers']==91,'private stock')
 need(i['provider_counts']=={'gauge44':1568,'extra':1672},'provider dispatch')
 need(i['selected_local_paid_profile']=={k:v*3240 for k,v in {'1':2439,'2':726,'3':224,'4':102,'5':20,'8':8}.items()},'all paid local calls')
 strict_check(i)
 b=i['blocknorm'];need(b['replicas']==360 and b['physical_families']==323069,'block stock')
 need(b['local_actual_prefix_bits']==95 and b['stock_l2_bits']==1323 and b['actual_prefix_bits']==1478 and b['required_reserve_bits']==1511 and b['retained_payload_bits']==2048,'prefix precision')
 need(i['global_prefix_bits']==1478 and i['charged_prefix_bits']==2048,'charged precision')
 for pid in ('gauge44','extra'):
  for direction in ('forward','backward'):
   z=b['endpoint_replay'][pid][direction];need(z['all_arbitrary_columns']==632 and z['helper_to_data_response_zero'] and z['centres_first_clear_and_terminal_zero']==8 and z['zero_buffers_allocated_and_cleared']==91,'arbitrary-dirty endpoint/cleanup')
def check(directory):
 need(PINS_SHA is not None and sha(directory/'EVIDENCE-PINS.json')==PINS_SHA,'terminal evidence not yet frozen or changed')
 pins=read(directory/'EVIDENCE-PINS.json')
 need(pins['scope']=='Authenticated stored completed execution; not a fresh replay','stored scope')
 need({'RESULT.json','RELEASE-RECEIPT.json','NATIVE-RECEIPT.json','PREFIX-AND-INVOICE.json','INDEPENDENT-OWNERS.json','FILL-BINDING.json','NATIVE-RESULT-base.json','NATIVE-RESULT-extra.json'}<=set(pins['files']),'complete receipt inventory')
 for name,h in pins['files'].items():
  p=directory/name;need(Path(name).name==name and p.is_file() and not p.is_symlink() and sha(p)==h,'receipt bytes '+name)
 r=read(directory/'RESULT.json');s=read(directory/'RELEASE-RECEIPT.json');n=read(directory/'NATIVE-RECEIPT.json');i=read(directory/'PREFIX-AND-INVOICE.json');o=read(directory/'INDEPENDENT-OWNERS.json')
 need(r['release_receipt_sha256']==sha(directory/'RELEASE-RECEIPT.json') and r['native_receipt_sha256']==sha(directory/'NATIVE-RECEIPT.json'),'receipt chain')
 semantic_check(r,s,n,i,o)
 binding=read(directory/'FILL-BINDING.json')
 need(r['fill_sha256']==binding['admission_sha256'] and [h for p,h in o['input_sha256'].items()if p.endswith('/FILL.json.gz')]==[binding['literal_sha256']],'literal/admission container bindings')
 need(binding['literal_payload_sha256']=='9c7288f6b65ea8b4509b658c7df881963410c144e112b6c8accf03283ddf2828' and binding['semantic_equality'] is True and binding['rows']==1321920,'semantic fill conversion')
 need(n['fresh_current_provider_count']==2 and n['reused_retained_parent'] is True,'fresh changed native and explicit retained parent scope')
 for tag in WORDS:
  native=read(directory/('NATIVE-RESULT-'+tag+'.json'))
  need(native['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY' and native['word_sha256']==WORDS[tag],'fresh native result '+tag)
  need([z['step']for z in native['steps']]==['native','ledgers','local-replay','wrappers','phases']and all(z['exit_code']==0 for z in native['steps']),'all five native stages '+tag)

 return 'PASS_STORED_T360_COMPLETE_RELEASE_NOT_FRESH_REPLAY'
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,default=Path(__file__).with_name('evidence'));print(check(p.parse_args().evidence))
