#!/usr/bin/env python3
"""Fixed completed112 COMPLEX ceiling custody/replay; no new scientific case.
Chris R / Clear1nsight; substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import base64
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path,PurePosixPath
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent
BASE='1a3ced60b2f7a46bc70280a04f2eeb8ca027c700'
INTEGRITY_SHA256='05e3242b2c6068711e66803137c61c08ea8d7d1b96cfc746eb71bec09b1924f2'
CHECKER_SHA='ca0e4f5830f9130666a57fc5f858e0a54f2204b27daa01ea33d7d0f0f4c4f179'
RESULT_SHA='4895186a36fe9c38e37da61ca752a2d07f4a57dd3160917c25e91aec334b1074'
PEER='retained/outputs/controller4666-sixquery-complex-screen-source-20261024/'
CASE='retained/race-kappa0033-sol-high-20261024/lanes/invoice/fivefull-sixcall-price-v1/'
GUARD='retained/swarm-price-plane-20261023T112711Z/runs/fivefull-onethin-conditional-shortfraction-v1/'

def require(ok,message):
    if not ok:raise ValueError(message)
def authenticate(data,digest):require(hashlib.sha256(data).hexdigest()==digest,'SHA256 authentication failed')
def load(name):return json.loads((ROOT/name).read_bytes())
def inventory():
    return {p.relative_to(ROOT).as_posix():dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size,mode=oct(p.stat().st_mode&0o777)) for p in sorted(ROOT.rglob('*')) if p.is_file()}
def typed(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
def compare_json(actual,expected):require(typed(actual)==typed(expected),'complete typedJSON differs; zero exclusions')
def must_reject(action,label):
    try:action()
    except ValueError:return label
    raise ValueError('negative control survived: '+label)

def scoped_claims(c):
    require(c['scope_tag']=='conditional-complex-completed112-current-kernel-fiveFULL-oneThin' and c['range']=='33/10000<=C<1','different fixed model/range')
    h=c['hypotheses']
    for key in ('fixed_actual_neutral_completed112_profile','independent_formal_D_stages','stage_degree_zero_unimodular_boundaries','canonical_odd_Q_monomial_outputs','nonnegative_integer_degrees','all_helpers_distinct_positive_optimistic_grant'):
        require(h[key] is True,'required fixed-model premise missing: '+key)
    for key,val in [('FULL_occurrences',5),('THIN_H1_jobs',112),('total_main_degree',10),('main_banks',4),('fields_per_bank',112)]:
        require(type(h[key]) is int and h[key]==val,'integer model inventory changed: '+key)
    require(h['rank_rule']=='1+8*d','shared central direction rank rule changed')
    compare_json(h['main_concavity_cap'],{'17':224,'25':224})
    require(c['inherited_source_applicability_review'] is True,'inherited review omitted')
    for key in ('fresh_native_or_source_semantic_validation','actual8H8_completion_is_universal_minimum','actual_author_BIT1920_case_closed','BC120_or_global120_closed','arbitrary_sixquery_controller_class_closed','other_completion_or_coded_output_class_closed','complete_caller','new_target_credit_admitted','funding_admitted'):
        require(c[key] is False,'unsupported scope extension: '+key)
    require(c['new_kappa'] is None,'new kappa claimed')

def fraction_certificate(r,c):
    require(r['C0']=='33/10000','wrong point')
    require(Fraction(r['target_upper'])-Fraction(r['paid_lower'])==Fraction(r['upper_signed_moment_gate']),'reported fraction identity differs')
    require(r['upper_signed_moment_gate']==c['point_upper_gate'] and r['strict_simple_upper']==c['strict_simple_upper'],'claim/result gate differs')
    require(Fraction(r['upper_signed_moment_gate'])<Fraction(r['strict_simple_upper'])<0,'strict negative gate absent')
    require(r['main_balanced_degrees']==[2,2,3,3],'degree cap differs')
    for key in ('fractional_power_log_exp_engine_calls','candidate_or_partition_enumerations'):
        require(type(r[key]) is int and r[key]==0,'forbidden engine/case count')
    for key in ('source_applicability_review_performed_here','author_BIT_n4_case_closed','BC120_case_closed','complete_caller','new_target_credit_admitted','funding_admitted'):
        require(r[key] is False,'unsupported result coverage')
    require(r['new_kappa'] is None,'result newkappa')

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
    before=inventory();raw=(ROOT/'INTEGRITY.json').read_bytes();authenticate(raw,INTEGRITY_SHA256);index=json.loads(raw)
    require(set(before)=={r['path'] for r in index['files']}|{'INTEGRITY.json','verify.py'},'package inventory differs')
    for row in index['files']:
        path=ROOT/row['path'];require(path.is_file() and not path.is_symlink(),'input missing/symlinked')
        data=path.read_bytes();require(len(data)==row['bytes'],'input length changed');authenticate(data,row['sha256'])
    for row in load('ORIGINS.json'):
        require(row['authority']=='canonical','unexpected origin authority');origin(row['proof'],(ROOT/row['retained']).read_bytes(),BASE,row['proof']['path'])
    for row in load('LOCAL-ORIGINS.json')['files']:
        data=(ROOT/row['path']).read_bytes();require(len(data)==row['bytes'],'LOCAL source length changed');authenticate(data,row['sha256'])
    runtime=load('RUNTIME-INPUTS.json');expected=(ROOT/runtime['expected_result']).read_bytes();authenticate(expected,RESULT_SHA)
    result=json.loads(expected);claims=load('CLAIMS.json');scoped_claims(claims);fraction_certificate(result,claims)
    model=load(CASE+'MODEL.json');gate=load(CASE+'SOURCE-GATE-ACCEPTED.json');modelgate=load(PEER+'MODEL-GATE.json')
    # The unchanged witness hashes REPORT, but does not consume MODEL-GATE. Bind it separately here.
    authenticate((ROOT/(PEER+'MODEL-GATE.json')).read_bytes(),gate['peer_model_gate_sha256'])
    require(modelgate['status']=='CONDITIONAL_MODEL_VALID_WITH_FIXED_NEUTRAL_PROFILE','different source model review')
    compare_json(modelgate['fixed_aggregate']['paid'],result['paid']);compare_json(modelgate['signed_upper_profile'],result['signed_coefficients'])
    compare_json(modelgate['fixed_aggregate']['optimistic_main_upper'],claims['hypotheses']['main_concavity_cap'])
    require(modelgate['completion_scope']['universal_physical_minimum_established'] is False and modelgate['active_BC_KSWAP_global120_profile_transfer'] is False,'inherited source gate overextended')
    require(result['status']=='PASS_CONDITIONAL_COMPLEX_CURRENT_KERNEL_NEGATIVE_GATE_FROM_0033' and result['checker_sha256']==CHECKER_SHA,'original result identity differs')
    guard=load(GUARD+'RECEIPT.json');require(guard['exit_code']==0 and guard['termination'] is None,'original guard did not pass')
    stdout=(ROOT/(GUARD+'stdout.log')).read_bytes();authenticate(stdout,guard['log_sha256']);require(stdout.decode().strip()==result['status'],'original stdout label differs; full RESULT authenticated separately')
    controls=[must_reject(lambda:authenticate((ROOT/(CASE+'PROOF.md')).read_bytes()+b'MUTANT',model['source_bindings'][0]['sha256']),'changed_proof_bytes_rejected')]
    bad=load('ORIGINS.json')[0];bad['proof']['trees'][0]['oid']='0'*40
    controls.append(must_reject(lambda:origin(bad['proof'],(ROOT/bad['retained']).read_bytes(),BASE,bad['proof']['path']),'forged_canonical_origin_rejected'))
    mutations=[('universal_completion_minimum','actual8H8_completion_is_universal_minimum',True),('BIT1920_closure','actual_author_BIT1920_case_closed',True),('BC_global_closure','BC120_or_global120_closed',True),('all_sixquery_closure','arbitrary_sixquery_controller_class_closed',True),('coded_outputs_closure','other_completion_or_coded_output_class_closed',True)]
    for label,key,value in mutations:
        bad=copy.deepcopy(claims);bad[key]=value;controls.append(must_reject(lambda:scoped_claims(bad),label+'_rejected'))
    for label,key,value in [('rank9d','rank_rule','9*d'),('dependent_stages','independent_formal_D_stages',False),('nonunimodular_boundary','stage_degree_zero_unimodular_boundaries',False),('uncanonical_phase_outputs','canonical_odd_Q_monomial_outputs',False)]:
        bad=copy.deepcopy(claims);bad['hypotheses'][key]=value;controls.append(must_reject(lambda:scoped_claims(bad),label+'_rejected'))
    bad=copy.deepcopy(result);bad['fractional_power_log_exp_engine_calls']=False
    controls.append(must_reject(lambda:compare_json(bad,result),'bool_for_zero_result_rejected'))
    bad=copy.deepcopy(result);bad['paid']['1']=11077.0
    controls.append(must_reject(lambda:compare_json(bad,result),'float_for_integer_inventory_rejected'))
    bad=copy.deepcopy(result);bad['upper_signed_moment_gate']='0'
    controls.append(must_reject(lambda:fraction_certificate(bad,claims),'nonnegative_fraction_gate_rejected'))
    if replay:
        with tempfile.TemporaryDirectory(prefix='fivefull-unchanged-fraction-') as folder:
            temp=Path(folder);work=temp/'work';work.mkdir()
            for row in runtime['runtime_files']:
                rel=PurePosixPath(row['source_path']);require(not rel.is_absolute() and '..' not in rel.parts,'runtime path escapes mirror')
                data=(ROOT/row['path']).read_bytes();authenticate(data,row['sha256']);dest=work/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);dest.chmod(0o444)
            checker=work/runtime['checker'];authenticate(checker.read_bytes(),CHECKER_SHA)
            fresh=temp/'RESULT.json';require(not fresh.exists(),'fresh output already exists')
            argv=[sys.executable,'-I','-Werror','-B','-X','pycache_prefix='+str(temp/'cache')]+(['-O'] if sys.flags.optimize else [])+[str(checker),'--root',str(work),'--model',runtime['model'],'--source-gate',runtime['source_gate'],'--output',str(fresh)]
            run=subprocess.run(argv,cwd=work,capture_output=True,timeout=25)
            new=fresh.read_bytes() if fresh.exists() else None
            print('FRESH_FIVEFULL_EVIDENCE '+json.dumps(dict(command=argv,exit_code=run.returncode,result_utf8=new.decode() if new is not None else None,result_raw_sha256=hashlib.sha256(new).hexdigest() if new is not None else None,result_raw_bytes=len(new) if new is not None else None,stdout_utf8=run.stdout.decode('utf-8'),stdout_raw_sha256=hashlib.sha256(run.stdout).hexdigest(),stdout_raw_bytes=len(run.stdout),stderr_utf8=run.stderr.decode('utf-8'),stderr_raw_sha256=hashlib.sha256(run.stderr).hexdigest(),stderr_raw_bytes=len(run.stderr)),sort_keys=True))
            require(run.returncode==0 and run.stderr==b'','unchanged Fraction witness failed: '+run.stderr.decode('utf-8'))
            require(run.stdout==stdout,'complete raw stdout differs from authenticated historical64bytes')
            require(new==expected,'complete raw RESULT differs; zero exclusions');compare_json(json.loads(new),result)
    after=inventory();require(after==before,'source bytes/modes changed during replay')
    digest=lambda value:hashlib.sha256(typed(value).encode()).hexdigest()
    return dict(status='PASS_FIXED_COMPLETED112_COMPLEX_FIVEFULL_CEILING_PACKAGE',canonical_base=BASE,immutable_files=len(before),fresh_fraction_witness=replay,optimized=bool(sys.flags.optimize),result_sha256=RESULT_SHA,comparison_exclusions=[],wrapper_controls=controls,scope_tag=claims['scope_tag'],point_upper_gate=claims['point_upper_gate'],range=claims['range'],fresh_source_semantic_validation=False,BIT1920_case_closed=False,BC120_or_global_case_closed=False,new_kappa=None,pre_custody_sha256=digest(before),post_custody_sha256=digest(after),inputs_and_modes_unchanged=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--integrity-only',action='store_true');args=parser.parse_args()
    print(json.dumps(verify(not args.integrity_only),sort_keys=True))
