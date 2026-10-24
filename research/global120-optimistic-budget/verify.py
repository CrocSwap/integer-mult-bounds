#!/usr/bin/env python3
"""Portable custody and exact scientific-projection replay for one optimistic point.
Chris R / Clear1nsight, substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import base64
import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent
BASE='1a3ced60b2f7a46bc70280a04f2eeb8ca027c700'
CHECKER_SHA='ba5b1a7d1e1c9de6a485e1e75947fa37c370d3a1f7d7dc0c5ccfa309e65e6b6e'
EXPECTED_SHA='406b81580297e81b13079c81afa28796f3f41c947586de164eaef8e721e1e659'
INTEGRITY_SHA256='513b5c6b4058ce614525a5b0bdeb0faf363c7517433855000e7ef774d0c03d72'
ENVIRONMENT_KEYS={'elapsed_seconds','maximum_resident_set_kib'}
EXCLUDED_FIELDS=['environment.elapsed_seconds','environment.maximum_resident_set_kib']

def require(ok,message):
    if not ok:raise ValueError(message)
def authenticate(data,digest):
    require(hashlib.sha256(data).hexdigest()==digest,'SHA256 authentication failed')
def load(name):return json.loads((ROOT/name).read_bytes())
def inventory():
    return {p.relative_to(ROOT).as_posix():dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),mode=oct(p.stat().st_mode&0o777),bytes=p.stat().st_size) for p in sorted(ROOT.rglob('*')) if p.is_file()}

def scientific_projection(value):
    require(isinstance(value,dict),'receipt object required')
    environment=value.get('environment')
    require(isinstance(environment,dict) and set(environment)==ENVIRONMENT_KEYS,'exact two recorded environment keys required')
    for number in environment.values():
        require(type(number) in (int,float) and math.isfinite(number) and number>=0,'finite nonnegative environment number required; bool forbidden')
    projected=copy.deepcopy(value)
    for key in ENVIRONMENT_KEYS:del projected['environment'][key]
    return projected

def canonical_scientific(value):
    return json.dumps(scientific_projection(value),sort_keys=True,separators=(',',':'),allow_nan=False)

def scope(value):
    scientific_projection(value)
    require(value['status']=='COMPLETE_SINGLE_POINT_OPTIMISTIC_GLOBAL120_SCREEN' and value['decision']=='POSITIVE_OPTIMISTIC_DECODER_ALLOWANCE','actual fixed-point result status')
    require(value['C']=='330007/100000000' and value['rho']=='1/1000000000','fixed point/reserve changed')
    require(value['binding']['old_baseline_paid_count']==64260 and value['binding']['assessor_check_count']==396,'actual baseline/assessment join')
    require(value['binding']['paid_count']==64668 and value['binding']['target_count']==10928,'fixed optimistic job counts')
    require(value['source_future_paid_and_losses_unknown'] is True and value['pricing_zero_future_repair_is_relaxation_only'] is True,'unknown future cost promoted to physical zero')
    require(value['all256_new_modes_unearned'] is True and value['old_main_preservation_optimistic'] is True,'optimistic targets promoted to admission')
    require(value['new_target_credit_admitted']==0 and value['complete_physical_caller'] is False and value['funded_kappa'] is None,'caller/target/kappa overclaim')
    require(value['compiler_geometry_or_old43_envelope_transferred'] is False and value['higher_moments_not_evaluated'] is True,'unrun compiler/higher-moment transfer')
    require(isinstance(value['remaining_gates'],dict) and value['remaining_gates'] and all(v is None for v in value['remaining_gates'].values()),'unknown remaining obligations changed')
    require(len(value['quotas'])==6 and all(q['quotas_not_additive'] is True and q['physical_cost_or_target_availability_proved'] is False for q in value['quotas']),'isolated quota scope changed')

def compare(actual,expected):
    scope(actual);scope(expected)
    require(canonical_scientific(actual)==canonical_scientific(expected),'typed complete scientific receipt differs; only two environment measurements excluded')

def must_reject(action,label):
    try:action()
    except ValueError:return label
    raise ValueError('negative control survived: '+label)

def object_id(kind, data):
    return hashlib.sha1(kind.encode()+b' '+str(len(data)).encode()+b'\0'+data).hexdigest()

def origin(proof, raw, expected_commit, expected_path):
    require(proof['commit'] == expected_commit and proof['path'] == expected_path, 'origin identity changed')
    commit = base64.b64decode(proof['commit_bytes_base64'], validate=True)
    require(object_id('commit',commit)==expected_commit, 'raw commit hash failed')
    require(commit.startswith(b'tree '), 'commit tree header missing')
    child = commit.splitlines()[0][5:].decode('ascii')
    parts = expected_path.split('/')
    require(len(parts)==len(proof['trees']), 'origin tree depth mismatch')
    for part, row in zip(parts,proof['trees']):
        tree=base64.b64decode(row['bytes_base64'],validate=True)
        require(row['oid']==child==object_id('tree',tree), 'raw tree hash failed')
        require(row['component']==part, 'path component mismatch')
        entries={}; cursor=0
        while cursor<len(tree):
            space=tree.index(b' ',cursor); zero=tree.index(b'\0',space)
            name=tree[space+1:zero].decode('utf-8'); mode=tree[cursor:space]
            require(name not in entries and zero+21<=len(tree),'malformed tree')
            entries[name]=(mode,tree[zero+1:zero+21].hex());cursor=zero+21
        require(part in entries,'path component absent')
        mode,child=entries[part]
        require(mode in ((b'100644',b'100755') if part==parts[-1] else (b'40000',)), 'unexpected object mode')
    require(child==proof['blob']==object_id('blob',raw),'original Git blob failed')
    require(len(raw)==proof['bytes'],'source byte count mismatch')
    authenticate(raw,proof['sha256'])

def verify(replay=True):
    before=inventory();raw=(ROOT/'INTEGRITY.json').read_bytes();authenticate(raw,INTEGRITY_SHA256);declaration=json.loads(raw)
    require(set(before)=={r['path'] for r in declaration['files']}|{'INTEGRITY.json','verify.py'},'package inventory differs')
    for row in declaration['files']:
        p=ROOT/row['path'];require(p.is_file() and not p.is_symlink(),'immutable file missing or aliased')
        data=p.read_bytes();require(len(data)==row['bytes'],'source length mismatch');authenticate(data,row['sha256'])
    for row in load('ORIGINS.json'):
        require(row['authority']=='canonical','unexpected origin authority')
        origin(row['proof'],(ROOT/row['retained']).read_bytes(),BASE,row['proof']['path'])
    for row in load('LOCAL-ORIGINS.json')['files']:
        data=(ROOT/row['path']).read_bytes();require(len(data)==row['bytes'],'LOCAL retained length changed');authenticate(data,row['sha256'])
    checker=ROOT/'science/price_global120.py';authenticate(checker.read_bytes(),CHECKER_SHA)
    expected_raw=(ROOT/'evidence/global120-Cstar-v1.json').read_bytes();authenticate(expected_raw,EXPECTED_SHA);expected=json.loads(expected_raw);scope(expected)
    guard=load('evidence/ACTUAL-GUARD-v1.json')
    require(guard['exit_code']==0 and guard['termination'] is None,'retained actual guard did not pass')
    authenticate((ROOT/'evidence/ACTUAL-stdout-v1.log').read_bytes(),guard['log_sha256'])
    audit=load('evidence/INDEPENDENT-AUDIT-RESULT.json')
    require(audit['status']=='PASS_STATIC_FIXED_POINT_NECESSARY_BUDGET_AUDIT' and audit['receipt_sha256']==EXPECTED_SHA,'retained independent audit binding')
    require(audit['scientific_engines_executed_by_auditor']==0 and audit['fresh_power_values_computed']==0 and audit['physical_or_kappa_admission'] is False,'static audit scope promoted')
    controls=[must_reject(lambda:authenticate(expected_raw+b'MUTANT',EXPECTED_SHA),'altered_raw_receipt_rejected')]
    bad=load('ORIGINS.json')[0];bad['proof']['trees'][0]['oid']='0'*40
    controls.append(must_reject(lambda:origin(bad['proof'],(ROOT/bad['retained']).read_bytes(),BASE,bad['proof']['path']),'forged_canonical_origin_rejected'))
    for label in ('earned_mode_claim','zero_unknown_cost','additive_quotas','extra_environment_field','boolean_environment_value','altered_numeric_interval','boolean_zero_target_credit','float_integer_paid_count'):
        value=copy.deepcopy(expected)
        if label=='earned_mode_claim':value['all256_new_modes_unearned']=False
        elif label=='zero_unknown_cost':value['remaining_gates'][next(iter(value['remaining_gates']))]=0
        elif label=='additive_quotas':value['quotas'][0]['quotas_not_additive']=False
        elif label=='extra_environment_field':value['environment']['scientific_data']=0
        elif label=='boolean_environment_value':value['environment']['elapsed_seconds']=True
        elif label=='boolean_zero_target_credit':value['new_target_credit_admitted']=False
        elif label=='float_integer_paid_count':value['binding']['paid_count']=64668.0
        else:value['optimistic_decoder_allowance_B_rho']['lower']='0'
        controls.append(must_reject(lambda:compare(value,expected),label+'_rejected'))
    fresh_environment=None
    if replay:
        with tempfile.TemporaryDirectory(prefix='global120-independent-price-') as folder:
            receipt=Path(folder)/'fresh.json'
            argv=[sys.executable,'-I','-Werror','-B','-X','pycache_prefix='+str(Path(folder)/'cache')]+(['-O'] if sys.flags.optimize else [])+[str(checker),'--receipt',str(receipt)]
            run=subprocess.run(argv,capture_output=True,text=True,timeout=30)
            print('FRESH_GLOBAL120_EVIDENCE '+json.dumps(dict(command=argv,exit_code=run.returncode,receipt_utf8=receipt.read_text() if receipt.exists() else None,stdout=run.stdout,stderr=run.stderr),sort_keys=True))
            require(run.returncode==0 and not run.stderr,'fresh optimistic one-point screen failed: '+run.stderr)
            fresh=json.loads(receipt.read_bytes());compare(fresh,expected);fresh_environment=fresh['environment']
    after=inventory();require(after==before,'source bytes or modes changed during replay')
    digest=lambda value:hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
    return dict(status='PASS_SOURCE_BOUND_SINGLE_POINT_OPTIMISTIC_GLOBAL120_PACKAGE',canonical_base=BASE,immutable_files=len(before),fresh_screen=replay,optimized=bool(sys.flags.optimize),excluded_receipt_fields=EXCLUDED_FIELDS,scientific_projection_sha256=hashlib.sha256(canonical_scientific(expected).encode()).hexdigest(),fresh_environment=fresh_environment,wrapper_negative_controls=controls,all256_modes_unearned=True,old_main_preservation_optimistic=True,future_costs_and_losses_unknown=True,complete_physical_caller=False,funded_kappa=None,pre_custody_sha256=digest(before),post_custody_sha256=digest(after),inputs_and_modes_unchanged=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--integrity-only',action='store_true');args=parser.parse_args()
    print(json.dumps(verify(not args.integrity_only),sort_keys=True))
