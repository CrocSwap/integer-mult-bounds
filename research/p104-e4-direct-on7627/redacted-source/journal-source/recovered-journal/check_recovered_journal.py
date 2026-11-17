#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""E4 post-run resource/price consumer; no calculation occurs at import.

Requires an independently frozen binding and finalized supervised signed stage.
No source row replay, native execution, process launch, or supplier claim.
"""
import argparse,copy,gzip,hashlib,importlib.util,json,runpy,sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
SOURCE='b80b6e74bff87c8d8160c5e121dac7c68df0827a7061847b896075417a346238'
CAND='1ea66c263faa51da704d7aae944f3371400afaf5df8a56904ab96319f6554e0e'
SRCGZ='3b0947df9d291308279a00e009f9c1f845151b5b40f81960a53a2949cb44c9a9'
CANDGZ='736d475843e2ca53cad8a193ed582926e2659abaec40895a41d55efd4fca532f'
CALLER='255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'
COMMON='734403f0278609a6dfbeb962556fbf0f3bb66e95e7553302b5ddb10f7b579947'
UPPER=Q('0.0036657312773679346788340108614613'); CLAIM=Q('.003666272802'); TEST=CLAIM+Q(7,10**15)
FIXED={'signed_terminal':'720b20a1b1f33e322b01736cefd4e9dc01d07ce7e53cad56ee5c357def3ffbd7','signed_execution':'fd5c10e102f712d853ff5eff118b7f594398ec97b886b6f408341b93f772b641','signed_journal':'897a42bee0afa89b8ea45af12f5ac8393702a74c4c57d1216ed1431c244ca718','signed_retirement':'5ec1ca0045497270715f1fab371cf63758e36ea0bf4b25343f293b730408dd83','signed_audit':'c487e86b053cd7b168bee107ec1b7722b7f87f3e1830c80a9e878aa77f40d62c','native_supervisor':'c225ea5df75ded89db7857d808b950a5ece49d2f3b7b97c7402f97b5cb5db134','recovery_host':'4bb1de52405b3a465461767b4b79599faa935f1ffa46092670ce56229e38a269','source_manifest':'064e11ecfedce9937ea1782e5baee37e89b3c9eebabed5b4a9ba84f412bbe078','producer':'e6327f23c5b15cf26ea049c2444e9f6cd5be62c680bd8ad8a5347df2b8910485','origins':'7fe3af176684321d4776d50b8fe2209db37889f128e65c940e9fb2770ba16ed2','predecessor_resource':'b619cb3e97034edf66419fcf05bf607989434d95f31cc4d45f9322fcd752511d','independent':'21f46a8340331abb1486b50bd4e04453f1968b0a5950d86ff7780dd368590874','census':'169a4f0b1944b62821d26724e81730bc0b139fefc24fb9182d337512e0f5d135','power':'52b20f41fd0bb55fa88dccd6015af2ce358917817b9506720f3e60ce681cc3ad','compare':'3930c22c11da7bc6042cfeb6e459ecb06e4478430037bee3469d034353855fc6','interval':'60a743d13f668ef86db4b8215b4d5d04430a671ba6f1fe06d9c1c4c3dfe86da5','source_word':SRCGZ,'candidate_word':CANDGZ,'caller':CALLER,'common_u':COMMON,'exact':'0fc0ba9b143e956e41c30e89550b104b0c451b074aa4d35d5a384ecf957ff337','provisional':'a5cf1dd107e2cd1ded105aee741d72f2ce3ded433c9faf52cba25107f0adaa0f','firstgate':'11016b0db3aa46b16e36e6cfe9b4914d4d49bb4c77c1f4e6d2403f9e2d3783c7','certificates':'e6faf6fe56172f31c76cb3300055ba27f786f7e67a1f8e8e64ba446511b2b41e','certificate_terminal':'c67b225097edf653c3880ed0ef3a55cd0959bb112c0646cac2be812a6faba49f'}
NAMES=('ODD-TYPE-B-REPLAY.json','ODD-TYPE-AB-REPLAY.json','ODD-CALLER-EXACT-GRID.json','ODD-PHYSICAL-BINDING.json','ODD-PRECISION.json','ODD-ADMISSION-PARTIAL.json','ODD-FIXED-TAPE-COUNTS.json')
def need(b,msg):
 if not b:raise ValueError(msg)
def safe_path(p, *, output=False):
 p=Path(p);need(p.is_absolute() and '..' not in p.parts,'absolute, non-traversing path required')
 cur=Path(p.anchor)
 need(not cur.is_symlink() and cur.is_dir(),'unsafe filesystem root')
 for part in p.parts[1:-1]:
  cur=cur/part;need(not cur.is_symlink() and cur.is_dir(),'unsafe or missing ancestor '+str(cur))
 need(not p.is_symlink(),'symlink leaf '+str(p))
 if output:need(not p.exists(),'exclusive output')
 else:need(p.is_file(),'regular input '+str(p))
 return p
def sha(p):return hashlib.sha256(safe_path(p).read_bytes()).hexdigest()
def read(p):return json.loads(safe_path(p).read_bytes())
def norm(x):return json.loads(json.dumps(x,default=str))
def canon(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def load(name,path):
 path=safe_path(path);spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def patched_independent(path):
 raw=safe_path(path).read_text();part=raw[raw.index('def ordinary('):raw.index('def main(')]
 edits=(('calls=18;',"calls=C['stages'];"),
 ("queryroute=sum(p*1000*(2+(e[4]==-1)) for e in qr)","queryroute=sum(p*1000*(2+(e[4]==-1)) for e in qr)\n  fusedroute=sum(36500*p for e in C['events'] if e[:2]==[ty,'IDLE_ODD'])"),
 ('idle_routes=idleroute,query_routes=queryroute)','idle_routes=idleroute,query_routes=queryroute,fused_routes=fusedroute)'))
 for a,b in edits:need(part.count(a)==1,'ordinary adaptation anchor');part=part.replace(a,b,1)
 m=load('e4_resource_independent',path);exec(compile(part,str(path),'exec'),m.__dict__)
 return m,hashlib.sha256(part.encode()).hexdigest()
def invoice(caller,n):
 T=Counter();P=Counter();calls=0
 for e in caller['events']:
  if e[0]=='J':calls+=1;T.update({int(k):v for k,v in n['helpers'].items()});P.update({int(k):v for k,v in n['paid'].items()})
  else:
   ports=len(caller['types'][e[0]]['ports'])
   if e[1]=='QUERY':P[1]+=ports
   elif e[1] in ('IDLE_ONE','IDLE_ODD'):P[8*len(e[3])+(e[1]=='IDLE_ODD')]+=ports
 for d in caller['types'].values():
  for dg in d['diagonal']:T[dg[0]%2+8*sum(dg[2:])]+=len(d['ports'])
 need(calls==caller['stages']==17,'actual 17 caller occurrences')
 S=sum(k*(T[k]-P[k]) for k in T.keys()|P.keys())
 return {'T':{str(k):v for k,v in sorted(T.items()) if v},'P':{str(k):v for k,v in sorted(P.items()) if v},'S':S}
def run_ids(stage,binding=None):
 need(type(stage['run_id']) is str and bool(stage['run_id']) and type(stage['native_run_id']) is str and bool(stage['native_run_id']) and stage['run_id']!=stage['native_run_id'],'distinct signed and native run IDs')
 if binding is not None:need(binding['run_id']==stage['run_id'] and binding['native_run_id']==stage['native_run_id'],'execution binding run IDs')
def signed_recovery(r, paths, hashes):
 for k in ('signed_terminal','signed_execution','signed_journal','signed_retirement','signed_audit'):
  need(r[k+'_sha256']==hashes[k],'recovery evidence binding '+k)
 need(r['original_error']=={'stage':'supervisor','error':"ValueError('final cgroup absent')"},'original failure preserved')
 need(r['journal_invocation_id']=='668d934ed2d440c89a4f038823b0cabf','journal invocation')
 need(r['initial_limits_pass'] is True and r['original_readback_limits_pass'] is False and 'readback_limits_pass' not in r,'unavailable original post-limit readback')
 need(not any(k in r for k in ('original_supervisor_status','original_supervisor_pass','wall_killed','cpu_killed')),'no ordinary supervisor pass or invented kill flags')
 t=read(paths['signed_terminal']);e=read(paths['signed_execution']);h=read(paths['signed_retirement'])
 need(t['status']=='INCOMPLETE_OR_FAILED' and t['error']==r['original_error'] and t['readback_limits_pass'] is False and t['exit_code'] is None and t['post_authentication_pass'] is True and t['process_group_empty'] is True and t['audit_capture_status']=='ARCHIVED','original supervisor terminal')
 need(t['verified_before_release'] is True and t['source_released'] is True and t['kernel_limits']=={'cpu.max':'10000 10000','cpu.max.burst':'0','memory.max':'2147483648','memory.oom.group':'1','memory.swap.max':'0','pids.max':'16'},'initial kernel controls')
 audit=[json.loads(x) for x in safe_path(paths['signed_audit']).read_text().splitlines()]
 need(len(audit)==3 and all(x=={'source_sha256':'35a3a38c6fe57cfb703a57a0382ef6f6b738131753b5fb5b97a68185b82994e1','before':'str(arc.relative_to(HERE))','after':'arc.relative_to(HERE).as_posix()','adapted_sha256':'57d9c83ecbcb3e9d7697dfa0d78bce6ff98958a1ee53267bffb710e362844caf','path_name':'source.py'} for x in audit),'exact archived audit inventory')
 need(e['status']=='SIGNED_CHILD_RETURNED' and type(e['exit_code']) is int and e['exit_code']==r['exit_code']==0 and e['run_id']==t['run_id']==r['run_id'] and e['native_run_id']==t['native_run_id']==r['native_run_id'] and e['binding_sha256']==t['binding_sha256']==hashes['signed_binding'] and e['result_sha256']==hashes['signed_result'],'actual child identity and exit')
 unit=t['unit'];need(h['unit']==unit and h['boot_id']=='c3e37344b22642659171a0fd082541b1' and h['show_exit_code']==0 and h['cgroup_lstat_errno']==2 and all(x in h['show_stdout'].splitlines() for x in ('MainPID=0','LoadState=not-found','ActiveState=inactive','SubState=dead','ControlGroup=')),'retired unit and absent group')
 j=[json.loads(x) for x in safe_path(paths['signed_journal']).read_text().splitlines()];need(len(j)==4,'journal event count')
 need(all(x['USER_UNIT']==unit and x['USER_INVOCATION_ID']==r['journal_invocation_id'] and x['_BOOT_ID']==h['boot_id'] and x['_PID']=='3194' and x['_EXE']=='/usr/lib/systemd/systemd' for x in j),'same journal invocation and manager')
 need([x['MESSAGE_ID'] for x in j]==['7d4958e842da4a758f6c1cdc7b36dcc5','39f53479d3a045ac8e11786248231fbf','9d1aaa27d60140bd96365438aad20286','ae8f7b866b0347b9af31fe1c80b127c0'],'journal lifecycle order')
 need(j[1]['MESSAGE'].removeprefix('Started ')==j[2]['MESSAGE'].removeprefix('Stopped ') and e['freeze_sha256'] in j[1]['MESSAGE'] and unit in j[1]['MESSAGE'],'journal executable and frozen identity')
 wall=(int(j[2]['__MONOTONIC_TIMESTAMP'])-int(j[0]['__MONOTONIC_TIMESTAMP']))/1000000
 need(abs(r['execution_wall_seconds']-wall)<0.000001 and r['aggregate_cpu_usec']==int(j[3]['CPU_USAGE_NSEC'])//1000==562277967 and int(j[3]['CPU_USAGE_NSEC'])%1000==0 and r['peak_memory_bytes']==int(j[3]['MEMORY_PEAK'])==591405056 and r['peak_swap_bytes']==int(j[3]['MEMORY_SWAP_PEAK'])==0,'journal elapsed and exact accounting')
 need(r['run_id']=='f6c24629d235470b86c46703ad59fb22' and r['native_run_id']=='c2e263c03ed18855afd4125d42981d71a27151b81d00ed05b133966629394cf4','original distinct invocation ids')

def validate_stage(r, paths, hashes, budget):
 need(r['schema']=='e4-signed-stage-recovery/v1' and r['status']=='PASS_RECOVERED_SIGNED_STAGE','recovered signed status')
 signed_recovery(r,paths,hashes)
 need(r['candidate_canonical_sha256']==CAND and r['exit_code']==0 and type(r['exit_code']) is int,'signed termination')
 for k in ('post_authentication_pass','process_group_empty','audit_capture_valid'):need(r[k] is True,'recovered custody '+k)
 for k,n in [('signed_result_sha256','signed_result'),('signed_binding_sha256','signed_binding'),('producer_sha256','producer'),('native_result_sha256','native'),('native_supervisor_sha256','native_supervisor'),('certificate_result_sha256','certificates'),('certificate_terminal_sha256','certificate_terminal'),('common_u_sha256','common_u')]:need(r[k]==hashes[n],'supervisor binding '+k)
 run_ids(r)
 for k,cap in [('execution_wall_seconds','wall_seconds'),('aggregate_cpu_usec','cpu_usec'),('peak_memory_bytes','memory_bytes')]:
  need(type(r[k]) in (int,float) and 0<r[k]<=budget[cap],'supervisor budget '+k)
 need(budget['wall_seconds']>0 and budget['cpu_usec']>0 and budget['memory_bytes']<=2*1024**3,'approved caps')
 root=paths['signed_result'].parent;need(type(r['raw_hashes']) is dict and r['raw_hashes'],'signed raw inventory')
 required={'RESULT.json','PRICE.json','MATCHED-ORDINARY.json','SOURCE-RESOURCE.json','GENERATOR-PREPARED.json','adapted/short_native_catalogue.py'} | {side+'-checks/'+name for side in ('source','candidate') for name in NAMES} | {'candidate-checks/ODD-8X9-APPLICATION-CHECKS.json'}
 need(required<=r['raw_hashes'].keys(),'complete signed stage artifact custody')
 for name,h in r['raw_hashes'].items():
  need(type(name) is str and not Path(name).is_absolute() and '..' not in Path(name).parts,'raw artifact relative path');p=safe_path(root/name);need(p.resolve().is_relative_to(root.resolve()) and sha(p)==h,'raw artifact '+name)
 return r['run_id']
def recovery_receipt(ns,nr,n,host,hashes,stage,sb):
 need(ns['schema']=='e4-native-recovery/v1' and ns['status']=='PASS_RECOVERED_INGREDIENT_NATIVE' and ns['original_finalizer_core_status']=='PASS_SUPERVISED_INGREDIENT_NATIVE' and ns['result_status']=='PASS_E4_INGREDIENT_NATIVE_ONLY','recovered native status and separate core status')
 need(ns['run_id']==nr['run_id']==n['run_id']==stage['native_run_id'] and ns['result_sha256']==hashes['native'] and ns['driver_terminal_sha256']==hashes['native_terminal'],'recovered native run and artifact binding')
 need(nr['status']=='SCOPED_GATE_RETURNED' and nr['result_status']=='PASS_E4_INGREDIENT_NATIVE_ONLY' and nr['result_sha256']==hashes['native'] and nr['freeze_sha256']==ns['freeze_sha256'] and n['schema']=='e4-native-paired/v1','original driver terminal and native result')
 need(ns['freeze_sha256']=='3328d0b08145bf8a6fa08e0a075d0dc77a24b3c7d6ae31d5eb298fe91db0be0f' and ns['freeze_sha256']==n['freeze_sha256'],'recovered native freeze')
 need(type(ns['exit_code']) is int and ns['exit_code']==0 and ns['measured_within_limits'] is True and not ns['secondary_errors'] and not ns.get('error'),'recovered native measured completion')
 need(type(ns['execution_wall_seconds']) in (int,float) and 0<=ns['execution_wall_seconds']<=4200 and type(ns['aggregate_cpu_usec']) is int and 0<ns['aggregate_cpu_usec']<=3600*1000000 and type(ns['peak_memory_bytes']) is int and 0<ns['peak_memory_bytes']<=2*1024**3,'recovered measured resource limits')
 need(ns['post_authentication_pass'] is True and ns['readback_limits_pass'] is True and ns['process_group_empty'] is True and ns['original_cleanup_observed'] is False,'recovered custody and original cleanup distinction')
 need(not any(k in ns for k in ('wall_killed','cpu_killed','original_supervisor_terminal')),'do not invent original supervisor facts')
 host_path=safe_path(sb['recovery_host_path'])
 need(sb['native_supervisor_provenance']=='RECOVERED_ORIGINAL_UNIT_NOT_ORIGINAL_TERMINAL' and sb['recovery_receipt_sha256']==hashes['native_supervisor'] and sb['recovery_host_sha256']==hashes['recovery_host'] and sb['closure'].get(str(host_path.resolve()))==hashes['recovery_host'],'recovery binding and host closure')
 need(sha(host_path)==hashes['recovery_host'],'recovery host actual bytes')
 expected={'origin':'retained original unit','observer_exit_code':143,'host_readback_sha256':hashes['recovery_host'],'original_supervisor_terminal_present':False,'original_unit':'<REDACTED-UNIT-IDENTIFIER>'}
 need(ns['recovery_provenance']==expected,'exact recovery provenance')
 need(host['observer_exit_code']==143 and host['original_supervisor_terminal_present'] is False and host['original_unit']==expected['original_unit'] and host['systemctl_show']['exit_code']==0 and host['original_cgroup_stat']['exit_code']==1,'host readback identity')
 need(ns['original_artifact_sha256']['SCOPED-RESULT.json']==hashes['native'] and ns['original_artifact_sha256']['SCOPED-TERMINAL.json']==hashes['native_terminal'],'original artifacts identity')

def run(binding):
 need(__debug__,'assertions enabled')
 cfg=read(binding);need(cfg['schema']=='e4-resource-check-binding/v1','binding schema')
 need(cfg['checker_sha256']==sha(__file__),'checker identity')
 rows=cfg['files'];need(type(rows) is dict and set(FIXED)<=rows.keys(),'fixed source inventory')
 paths={};hashes={}; seen=set()
 for k,r in rows.items():
  p=safe_path(r['path']);need(str(p.resolve()) not in seen,'unique regular input '+k)
  seen.add(str(p.resolve()));h=sha(p);need(h==r['sha256'] and (k not in FIXED or h==FIXED[k]),'input hash '+k);paths[k]=p;hashes[k]=h
 for k in ('signed_result','signed_binding','producer','native','native_supervisor','native_terminal','signed_stage','origins'):need(k in paths,'missing required input '+k)
 source_manifest=read(paths['source_manifest']);need(source_manifest['replay/supplier7112/short-caller/independent.py']==hashes['independent'],'7113 manifest binds independent engine')
 stage=read(paths['signed_stage']);run_id=validate_stage(stage,paths,hashes,cfg['budget'])
 sb=read(paths['signed_binding']);run_ids(stage,sb);need(sb['schema']=='e4-signed-binding/v1' and sb['source_canonical_sha256']==SOURCE and sb['candidate_canonical_sha256']==CAND and sb['native_run_id']==stage['native_run_id'],'signed execution binding')
 for key,file in [('native_sha256','native'),('native_receipt_sha256','native_terminal'),('native_supervisor_sha256','native_supervisor'),('certificates_sha256','certificates'),('certificate_receipt_sha256','certificate_terminal'),('common_u_sha256','common_u'),('exact_sha256','exact'),('provisional_sha256','provisional'),('firstgate_sha256','firstgate')]:need(sb[key]==hashes[file],'signed binding '+key)
 n=read(paths['native']);ns=read(paths['native_supervisor']);nr=read(paths['native_terminal']);s=read(paths['signed_result']);cert=read(paths['certificates']);ct=read(paths['certificate_terminal']);u=read(paths['common_u'])
 recovery_receipt(ns,nr,n,read(paths['recovery_host']),hashes,stage,sb)
 need(n['status']=='PASS_E4_INGREDIENT_NATIVE_ONLY' and n['source_word']['canonical_sha256']==SOURCE and n['candidate_word']['canonical_sha256']==CAND,'fresh native pair')
 need(cert['status']=='PASS_INDEPENDENT_CERTIFICATE_AND_REMAINING_LIVE_RANK_204' and cert['source_records']==cert['candidate_records']==204 and ct['exit_code']==0 and ct['result_sha256']==hashes['certificates'] and ct['post_authentication_pass'] is True and ct['readback_limits_pass'] is True and ct['process_group_empty'] is True,'certification custody')
 need(u['status']=='EXPLICIT_UNIMPLEMENTED_SUPPLIER_PREMISE' and u['source_candidate_bindings']['source_canonical_sha256']==SOURCE and u['source_candidate_bindings']['candidate_canonical_sha256']==CAND,'common U actual pair')
 tariff=u['finite_same_tariff_assumptions'];need((tariff['ordinary_source_units_per_lifetime_pair'],tariff['scalar_services_per_INIT_or_CLEAR'],tariff['scalar_elementary_coefficient_per_service'],tariff['precision_context_cap'],tariff['fixed_banks_signed'])==(4000,32,2**20,4096,1156),'U tariff')
 need(s['status']=='PASS_E4_COMPLETE_SIGNED_APPLICATION' and s['caller_sha256']==CALLER,'signed stage result')
 source=json.loads(gzip.decompress(safe_path(paths['source_word']).read_bytes()));cand=json.loads(gzip.decompress(safe_path(paths['candidate_word']).read_bytes()))
 need(canon(source)==SOURCE and canon(cand)==CAND,'canonical words')
 census=runpy.run_path(str(safe_path(paths['census'])));base=census['census'](source);new=census['census'](cand)
 for k in ('lifetimes','peak','owned_labels_used','owned_fields','owned_moves','owned_rises'):need(base[k]==new[k],'actual owned census '+k)
 need((base['lifetimes'],base['peak'],base['owned_labels_used'],base['owned_moves'])==(204,50,68,47),'actual ownership')
 need(census['diff'](base['native_paid'],new['native_paid'])=={'2':-1,'3':-1,'5':1} and census['diff'](base['native_targets'],new['native_targets'])=={},'native profile')
 for d,nn in ((base,n['native']['source']),(new,n['native']['candidate'])):
  need(d['native_paid']=={str(k):v for k,v in nn['paid'].items()} and d['native_targets']=={str(k):v for k,v in nn['helpers'].items()} and not nn['bad_inputs'],'independent census vs native')
 origin=read(paths['origins']);need(len(origin)==len(cand['program']) and origin.count(None)==21,'twenty one added ADDs')
 need([i for i in origin if i is not None]==[i for i in range(len(source['program'])) if i!=43041],'literal source origin coverage')
 changes={41629:['MOVE',490,594,883,False],41631:['ADD',1427,296,'-1',725]}
 for i,e in zip(origin,cand['program']):
  if i is not None:need(e==changes.get(i,source['program'][i]),'literal source projection')
 added=[e for i,e in zip(origin,cand['program']) if i is None];need(all(e[0]=='ADD' and e[-1]==127 for e in added),'literal added operations')
 def scalar(e):
  q=Q(e[3]);a=abs(q.numerator);return 4*(a.bit_length()+q.denominator.bit_length()+1+a.bit_count())
 addcharges=[{'coefficient':str(Q(e[3])),'numerator_bits':abs(Q(e[3]).numerator).bit_length(),'denominator_bits':Q(e[3]).denominator.bit_length(),'numerator_popcount':abs(Q(e[3]).numerator).bit_count(),'charge':scalar(e)} for e in added]
 caller=read(paths['caller']);srcinvoice=invoice(caller,n['native']['source']);newinvoice=invoice(caller,n['native']['candidate']);price=s['price'];expected=read(paths['provisional'])
 for i,key in ((srcinvoice,'source_invoice'),(newinvoice,'candidate_invoice')):need(i['P']==expected[key]['paid'] and i['T']==expected[key]['targets'] and i['S']==1424,'fresh actual caller invoice '+key)
 for i,key in ((srcinvoice,'baseline_7627'),(newinvoice,'after')):need(i['P']==price[key]['P'] and i['T']==price[key]['T'] and i['S']==price[key]['S'] and price[key]['empty_root_credits']==0,'signed price invoice '+key)
 need(sum(srcinvoice['P'].values())==110043 and sum(newinvoice['P'].values())==110026 and sum(newinvoice['T'].values())==22461,'signed complete denominator')
 pred=load('e4_prior_resource',paths['predecessor_resource']);sr=s['source_resource'];need(sr['status']=='DERIVED_FRESH_SOURCE_RESOURCE_ONLY' and sr['source_catalogue_rerun'] is False and sr['candidate_native_receipt_sha256']==hashes['native'],'source resource provenance')
 root=paths['signed_result'].parent;need(read(root/'PRICE.json')==price and read(root/'SOURCE-RESOURCE.json')==sr and read(root/'MATCHED-ORDINARY.json')==s['matched_ordinary'],'signed resource output copies');checks={}
 for side in ('source','candidate'):
  expected_checks=sr['checks'] if side=='source' else s['checks'];checks[side]={}
  for name in NAMES:
   p=root/(side+'-checks')/name;need(not p.is_symlink() and p.is_file() and read(p)==expected_checks[name],'retained raw check '+side+'/'+name)
   want=(sr['check_sha256'] if side=='source' else s['candidate_check_sha256'])[name];need(sha(p)==want,'raw check hash')
   checks[side][name]=read(p)
  np=n['economics'][side+'_precision'];pr=checks[side]['ODD-PRECISION.json']
  need(pr['native_grid']==np['word'] and pr['rounded_native']==np['rounded_native'],'fresh native precision '+side)
 results={side:pred.signed_resources(checks[side],w,h,side) for side,w,h in [('source',source,SOURCE),('candidate',cand,CAND)]}
 for key in ('context_height','context_mass_bits','context_c'):need(checks['source']['ODD-PRECISION.json'][key]==checks['candidate']['ODD-PRECISION.json'][key],'charged common precision '+key)
 need(results['candidate']['scalar_services']==results['source']['scalar_services']+17*21*32,'scalar service addition')
 I,patched_hash=patched_independent(paths['independent']);bills={}
 for side,w,inv,native in [('source',source,srcinvoice,n['native']['source']),('candidate',cand,newinvoice,n['native']['candidate'])]:
  nd=dict(native);nd['paid']={int(k):v for k,v in native['paid'].items()};nd['helpers']={int(k):v for k,v in native['helpers'].items()};nd['rises']={int(k):v for k,v in native['rises'].items()}
  fresh=norm(I.ordinary(w,caller,nd));charge=checks[side]['ODD-ADMISSION-PARTIAL.json']['ordinary']
  for k in ('scalar_upper','init_clear_allowance','route_items','routing','caller_items','caller_total','raw_upper','per_input_conversion','lambda_second_charge','odd_divisions','lambda_paid_rank1_would_reduce_S_by'):need(fresh[k]==charge[k],'independent actual ordinary '+side+' '+k)
  need(fresh['conservative_total']+charge['all_caller_scalar_surcharge']+charge['charged_caller_odd_conversions']==charge['conservative_total'],'complete actual ordinary '+side);bills[side]=charge['conservative_total']
 need(bills['source']==s['matched_ordinary']['source_total'] and bills['candidate']==s['matched_ordinary']['candidate_total'],'matched signed bill')
 need(checks['candidate']['ODD-ADMISSION-PARTIAL.json']['ordinary']['scalar_upper']-checks['source']['ODD-ADMISSION-PARTIAL.json']['ordinary']['scalar_upper']==sum(x['charge'] for x in addcharges),'all 21 exact scalar charges')
 interval=runpy.run_path(str(safe_path(paths['interval'])));need('compare_recursive_invoices' not in sys.modules,'preloaded comparator');power=runpy.run_path(str(safe_path(paths['power'])));need(Path(sys.modules['compare_recursive_invoices'].__file__).resolve()==paths['compare'].resolve(),'comparator binding')
 contract=expected['source_invoice']['contract'];schema='integer-mult-recursive-invoice/v1';zero={'schema':schema,'contract':contract,'paid':{},'targets':{}}
 def two(inv,k):
  hist={int(r):inv['T'].get(r,0)-inv['P'].get(r,0) for r in inv['T'].keys()|inv['P'].keys()};lo,hi=interval['moment'](hist,k)
  v={'schema':schema,'contract':contract,'paid':inv['P'],'targets':inv['T']};p=power['evaluate'](zero,v,1-k,bits=256)
  sign='positive' if lo>0 else 'negative' if hi<0 else 'unresolved';need(p['classification']=={'positive':'new_cost_lower','negative':'new_cost_higher'}.get(sign),'two price engines agreement')
  return {'sign':sign,'interval':[str(Q(lo,interval['B'])),str(Q(hi,interval['B']))],'integer':p['new_minus_old']}
 actual_lo,actual_hi=map(Q,price['gate']['raw_bracket']);actual_claim=Q(price['gate']['claim']);need(UPPER<CLAIM<TEST<actual_lo<actual_hi and UPPER<actual_claim<actual_lo,'signed gate ordering')
 pts={'old_upper':UPPER,'claim':CLAIM,'tested':TEST,'actual_claim':actual_claim,'actual_lower':actual_lo,'actual_upper':actual_hi,'goal':Q('.00368')};prices={side:{k:two(inv,v) for k,v in pts.items()} for side,inv in [('source',srcinvoice),('candidate',newinvoice)]}
 need(prices['source']['old_upper']['sign']==prices['source']['claim']['sign']=='negative' and all(prices['candidate'][k]['sign']=='positive' for k in ('old_upper','claim','tested')) and prices['candidate']['goal']['sign']=='negative' and prices['candidate']['actual_lower']['sign']=='positive' and prices['candidate']['actual_upper']['sign']=='negative' and prices['source']['actual_claim']['sign']=='negative' and prices['source']['actual_upper']['sign']=='negative','actual price screen')
 for g in (price['public_claim_gate'],price['gate'],sr['source_17_gate'],n['economics']['source_gate'],n['economics']['candidate_gate']):pred.gate(g,'fresh signed or native ingredient gate')
 need(Q(price['public_claim_gate']['claim'])==CLAIM and Q(price['first_gate_old_upper'])==UPPER and Q(price['first_gate_probe'])==TEST,'price source comparison')
 size=s['catalogue_size'];rows=s['catalogue'];cursor=0;need(type(size) is int and size>0 and rows,'catalogue nonempty')
 for r in rows:
  need(r['catalogue_size']==size and r['slice_start']==cursor and 0<r['checked_maps']==r['slice_stop']-cursor<=1000 and r['word_sha256']==CANDGZ and r['phase_control_rejected'] is True,'catalogue slice');cursor=r['slice_stop']
 need(cursor==size and sum(r['main_boundary_pairs'] for r in rows)==104,'catalogue closure')
 g=root/'GENERATOR-PREPARED.json';gen=root/'adapted/short_native_catalogue.py';gp=read(g);need(gp['run_id']==stage['native_run_id'] and gp['native_result_sha256']==hashes['native'] and gp['candidate_canonical_sha256']==CAND and gp['generator_sha256']==sha(gen)==s['catalogue_generator_sha256'],'generator provenance')
 app=root/'candidate-checks/ODD-8X9-APPLICATION-CHECKS.json';need(read(app)==s['checks']['ODD-8X9-APPLICATION-CHECKS.json'] and sha(app)==s['candidate_check_sha256']['ODD-8X9-APPLICATION-CHECKS.json'] and read(app)['native_canonical_sha256']==CAND,'assembled candidate application')
 return {'schema':'e4-resource-price-consumer/v1','status':'PASS_RESOURCE_PRICE_CONDITIONAL_ON_UNIMPLEMENTED_U','run_id':run_id,'native_run_id':stage['native_run_id'],'checker_sha256':sha(__file__),'binding_sha256':sha(binding),'input_sha256':hashes,'source_signed':results['source'],'candidate_signed':results['candidate'],'signed_ordinary':bills,'caller_sha256':CALLER,'source_invoice':srcinvoice,'candidate_invoice':newinvoice,'two_directed_prices':prices,'added_scalar_charges':addcharges,'ordinary_adapter_sha256':patched_hash,'catalogue_size':size,'boundaries':104,'u_status':u['status'],'source_scope':'Derived from fresh candidate-bound paired source native calculation; source catalogue not rerun.','signed_custody_scope':'Recovered same original signed invocation from saved journal and records; original supervisor failed and original post-limit readback unavailable.','native_custody_scope':'Externally recovered original native unit; original supervisor terminal missing, wrapper exit 143, interruption cause unknown.','limitations':['No implementation of U or implication from original erasure premise.','Five inherited framework assumptions remain.','This consumer does not independently rerun physical/native/certificate proofs or prove an unconditional multiplier theorem.']}
def main():
 p=argparse.ArgumentParser();p.add_argument('--binding',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();safe_path(a.binding);safe_path(a.out,output=True);r=run(a.binding);safe_path(a.out,output=True)
 with a.out.open('x') as f:json.dump(r,f,sort_keys=True,indent=2);f.write('\n')
 print(json.dumps({'status':r['status'],'run_id':r['run_id']}))
if __name__=='__main__':main()
