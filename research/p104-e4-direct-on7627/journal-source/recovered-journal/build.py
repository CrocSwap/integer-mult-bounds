#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Build a counted, custody-only adaptation; no scientific execution."""
import hashlib, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'recovered-native/check_recovered.py'
OUT=HERE/'check_recovered_journal.py'; LEDGER=HERE/'ADAPTER.json'
def digest(b): return hashlib.sha256(b).hexdigest()
raw=BASE.read_bytes()
if digest(raw)!='4cab2bee594f7448cc8df639d4d5def98eb8f1d9e6621666a7016e7795cff582': raise ValueError('approved consumer pin')
s=raw.decode(); changes=[]
extra="'signed_terminal':'720b20a1b1f33e322b01736cefd4e9dc01d07ce7e53cad56ee5c357def3ffbd7','signed_execution':'fd5c10e102f712d853ff5eff118b7f594398ec97b886b6f408341b93f772b641','signed_journal':'897a42bee0afa89b8ea45af12f5ac8393702a74c4c57d1216ed1431c244ca718','signed_retirement':'5ec1ca0045497270715f1fab371cf63758e36ea0bf4b25343f293b730408dd83','signed_audit':'c487e86b053cd7b168bee107ec1b7722b7f87f3e1830c80a9e878aa77f40d62c',"
helper='''def signed_recovery(r, paths, hashes):
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

def validate_stage(r, paths, hashes, budget):'''
edits=[
 ("FIXED={'native_supervisor':", "FIXED={"+extra+"'native_supervisor':"),
 ('def validate_stage(r, paths, hashes, budget):',helper),
 (" need(r['schema']=='e4-signed-stage-receipt/v1' and r['status']=='PASS_SUPERVISED_SIGNED_STAGE','signed supervisor status')", " need(r['schema']=='e4-signed-stage-recovery/v1' and r['status']=='PASS_RECOVERED_SIGNED_STAGE','recovered signed status')\n signed_recovery(r,paths,hashes)"),
 (" for k in ('post_authentication_pass','readback_limits_pass','process_group_empty','audit_capture_valid'):need(r[k] is True,'supervisor '+k)"," for k in ('post_authentication_pass','process_group_empty','audit_capture_valid'):need(r[k] is True,'recovered custody '+k)"),
 ("'native_custody_scope':'Externally recovered original native unit;", "'signed_custody_scope':'Recovered same original signed invocation from saved journal and records; original supervisor failed and original post-limit readback unavailable.','native_custody_scope':'Externally recovered original native unit;"),
]
for before,after in edits:
 count=s.count(before)
 if count!=1: raise ValueError('unique edit anchor '+repr(before[:100])+' count '+str(count))
 s=s.replace(before,after,1);changes.append({'anchor_sha256':digest(before.encode()),'replacement_sha256':digest(after.encode()),'count':count,'description':before[:100]})
if OUT.exists() or LEDGER.exists(): raise ValueError('exclusive outputs')
OUT.write_text(s)
ledger={'schema':'e4-signed-journal-resource-counted-adapter/v1','status':'PREPARED_NOT_EXECUTED','source_sha256':digest(raw),'output_sha256':digest(s.encode()),'edits':changes}
LEDGER.write_text(json.dumps(ledger,sort_keys=True,indent=2)+'\n')
print(json.dumps({'checker_sha256':ledger['output_sha256'],'edit_count':len(changes),'ledger_sha256':digest(LEDGER.read_bytes())}))
