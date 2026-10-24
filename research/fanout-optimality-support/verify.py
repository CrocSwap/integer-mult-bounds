#!/usr/bin/env python3
"""Unchanged-source fanout replay and scoped-proof custody; no extra engine.
Chris R / Clear1nsight, substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path,PurePosixPath
import subprocess
import sys
import tempfile
import zlib

ROOT=Path(__file__).resolve().parent
BASE='1a3ced60b2f7a46bc70280a04f2eeb8ca027c700'
RESULT_SHA='bf29a13f9e7ef9feb87befcc71b6919ed75726e6fef87b139e0c9c6ad244cdb7'
PROGRAM_SHA='5575fc71eb94f1b75b3421d787d3313716ece5e72d3498ce348500f3628291f7'
CHECKER_SHA='b824bf066999887b96fc386678ce44fb2269dc30406b06d65a9aac43a0437ae3'
LOWER_SHA='cfa9f3df855f96a3e73bcb8042a750a3aa41d18ec098d6a34268370f3e84d782'
LOWER_PATH='retained/race-kappa0033-sol-high-20261024/consultants/astra-query-sharing/EXACT-FANOUT-MODULE-LOWER-v1.md'
INTEGRITY_SHA256='1f94365b800cf480c49904f7056ddc6fb788b4b915ea8ea8353c5b15aed65f92'

def require(ok,message):
    if not ok:raise ValueError(message)
def authenticate(data,digest):
    require(hashlib.sha256(data).hexdigest()==digest,'SHA256 authentication failed')
def load(name):return json.loads((ROOT/name).read_bytes())
def inventory():
    return {p.relative_to(ROOT).as_posix():dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size,mode=oct(p.stat().st_mode&0o777)) for p in sorted(ROOT.rglob('*')) if p.is_file()}
def typed(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
def compare_json(actual,expected):
    require(typed(actual)==typed(expected),'typed complete JSON differs; zero exclusions')
def must_reject(action,label):
    try:action()
    except ValueError:return label
    raise ValueError('negative control survived: '+label)

def scoped_claims(claims):
    upper=claims['upper'];lower=claims['lower']
    require(upper['full_137_field_physical_endpoint_replay'] is False,'selfalias checks promoted to137field endpoint replay')
    require(upper['endpoint_basis']=='COMPOSITIONAL_SOURCE_FACTORIZATION_LITERAL_COEFFICIENTS_AND_LIFETIMES','endpoint evidence changed')
    require(type(upper['paid_H1']) is int and upper['paid_H1']==112 and type(upper['query_savings']) is int and upper['query_savings']==0,'upper call count/reduction claim changed')
    require(type(lower['minimum_total_gaussian_field_calls']) is int and lower['minimum_total_gaussian_field_calls']==112,'scoped lower count changed')
    require(lower['bound_interpretation']=='TOTAL_STANDALONE_NOT_INCREMENTAL','total bound promoted to incremental/global charge')
    require(lower['width_quantifier']=='ALL_POSITIVE_WIDTHS_OR_ONE_CONSECUTIVE_TAIL','unsupported restricted width family')
    for key in ('fixed_finite_program','fixed_exterior_coefficients','finite_columnwise_ordinary_group','ordinary_initial_span_only','fixed_common_field_capacity','central_scalar_M_shared_right_Km','arbitrary_independent_originals','exact_per_column_phases'):
        require(lower[key] is True,'required lower proof premise changed: '+key)
    require(type(lower['paid_output_rows_per_call']) is int and lower['paid_output_rows_per_call']==1,'paid output capacity changed')
    require(lower['weighted_recursive_invoice_claimed'] is False,'call count promoted to weighted invoice')
    require(claims['full_physical_raw_dual'] is False and claims['complete_caller'] is False and claims['compiler_precision_stock_admitted'] is False and claims['new_kappa'] is None,'component/proof promoted to admission')

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
        path=ROOT/row['path'];require(path.is_file() and not path.is_symlink(),'input missing or symlinked')
        data=path.read_bytes();require(len(data)==row['bytes'],'input byte length changed');authenticate(data,row['sha256'])
    for row in load('ORIGINS.json'):
        require(row['authority']=='canonical','unexpected origin authority')
        origin(row['proof'],(ROOT/row['retained']).read_bytes(),BASE,row['proof']['path'])
    for row in load('LOCAL-ORIGINS.json')['files']:
        data=(ROOT/row['path']).read_bytes();require(len(data)==row['bytes'],'LOCAL source length changed');authenticate(data,row['sha256'])
    authenticate((ROOT/LOWER_PATH).read_bytes(),LOWER_SHA)
    runtime=load('RUNTIME-INPUTS.json');expected_result=(ROOT/runtime['expected_result']).read_bytes();expected_program=(ROOT/runtime['expected_program']).read_bytes()
    authenticate(expected_result,RESULT_SHA);authenticate(expected_program,PROGRAM_SHA)
    result=json.loads(expected_result);program=json.loads(expected_program);claims=load('CLAIMS.json');scoped_claims(claims)
    require(result['status']=='PASS_EXACT_COMPONENT_NO_QUERY_REDUCTION' and result['program_sha256']==PROGRAM_SHA and result['checker_sha256']==CHECKER_SHA,'original result/checker/program binding')
    require(result['group_sizes']==[1]*112 and result['group_ranks']==[1]*112 and result['rationalrank_sum_Qqueries']==112,'retained singleton class/rank outcome changed')
    require(result['all512_alias_columns_checked']==57344 and len(result['controls'])==13 and all(c['rejected'] is True for c in result['controls']),'original coverage/controls changed')
    require(program['queries']==112 and program['positiveQpaid_profile']=={'1':112} and program['runtime_odd_divisions']==0,'retained program tariff changed')
    compare_json(program['ordinary_counts'],claims['upper']['ordinary_counts'])
    guard=load('evidence/RECEIPT.json');require(guard['exit_code']==0 and guard['termination'] is None,'original guard did not pass')
    authenticate((ROOT/'evidence/stdout.log').read_bytes(),guard['log_sha256'])
    controls=[must_reject(lambda:authenticate((ROOT/LOWER_PATH).read_bytes()+b'MUTANT',LOWER_SHA),'changed_lower_proof_bytes_rejected')]
    bad=load('ORIGINS.json')[0];bad['proof']['trees'][0]['oid']='0'*40
    controls.append(must_reject(lambda:origin(bad['proof'],(ROOT/bad['retained']).read_bytes(),BASE,bad['proof']['path']),'forged_canonical_origin_rejected'))
    for label in ('cached_initial_observation','width_subsequence','changed_field_capacity','incremental_bound','physical137_replay_claim','width_dependent_coefficients'):
        bad=copy.deepcopy(claims)
        if label=='cached_initial_observation':bad['lower']['ordinary_initial_span_only']=False
        elif label=='width_subsequence':bad['lower']['width_quantifier']='WIDTHS_DIVISIBLE_BY_FOUR'
        elif label=='changed_field_capacity':bad['lower']['fixed_common_field_capacity']=False
        elif label=='incremental_bound':bad['lower']['bound_interpretation']='ADDITIONAL_AT_GLOBAL_CUT'
        elif label=='physical137_replay_claim':bad['upper']['full_137_field_physical_endpoint_replay']=True
        else:bad['lower']['fixed_exterior_coefficients']=False
        controls.append(must_reject(lambda:scoped_claims(bad),label+'_rejected'))
    bad_result=copy.deepcopy(result);bad_result['query_savings_vs112']=False
    controls.append(must_reject(lambda:compare_json(bad_result,result),'bool_for_zero_result_rejected'))
    bad_program=copy.deepcopy(program);bad_program['queries']=112.0
    controls.append(must_reject(lambda:compare_json(bad_program,program),'float_for_integer_program_rejected'))
    if replay:
        with tempfile.TemporaryDirectory(prefix='fanout-unchanged-source-') as folder:
            temp=Path(folder);work=temp/'work';work.mkdir()
            for row in runtime['files']:
                rel=PurePosixPath(row['source_path']);require(not rel.is_absolute() and '..' not in rel.parts,'runtime path escapes mirror')
                data=(ROOT/row['path']).read_bytes();authenticate(data,row['sha256']);dest=work/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);dest.chmod(0o444)
            checker=work/runtime['checker'];authenticate(checker.read_bytes(),CHECKER_SHA)
            fresh_program=temp/'FANOUT-PROGRAM-v1.json';fresh_result=temp/'FANOUT-RESULT-v1.json'
            argv=[sys.executable,'-I','-Werror','-B','-X','pycache_prefix='+str(temp/'cache')]+(['-O'] if sys.flags.optimize else [])+[str(checker),'--input',str(work/runtime['input']),'--program',str(fresh_program),'--result',str(fresh_result)]
            run=subprocess.run(argv,cwd=work,capture_output=True,text=True,timeout=30)
            new_program=fresh_program.read_bytes() if fresh_program.exists() else None;new_result=fresh_result.read_bytes() if fresh_result.exists() else None
            # Lossless compression is transport only; scientific equality uses original uncompressed bytes.
            evidence=dict(command=argv,exit_code=run.returncode,result_utf8=new_result.decode() if new_result is not None else None,program_zlib_base64=base64.b64encode(zlib.compress(new_program,9)).decode() if new_program is not None else None,program_raw_sha256=hashlib.sha256(new_program).hexdigest() if new_program is not None else None,program_raw_bytes=len(new_program) if new_program is not None else None,stdout=run.stdout,stderr=run.stderr)
            print('FRESH_FANOUT_EVIDENCE '+json.dumps(evidence,sort_keys=True))
            require(run.returncode==0 and not run.stderr,'unchanged upper checker failed: '+run.stderr)
            require(new_program==expected_program and new_result==expected_result,'full raw program/result differs; zero excluded fields')
            compare_json(json.loads(new_program),program);compare_json(json.loads(new_result),result)
    after=inventory();require(after==before,'source bytes or modes changed during replay')
    digest=lambda value:hashlib.sha256(typed(value).encode()).hexdigest()
    return dict(status='PASS_SCOPED_FANOUT_OPTIMALITY_SUPPORT_PACKAGE',canonical_base=BASE,immutable_files=len(before),fresh_upper_checker=replay,optimized=bool(sys.flags.optimize),result_sha256=RESULT_SHA,program_sha256=PROGRAM_SHA,comparison_exclusions=[],fresh_program_transport='losslesszlibbase64; compare uncompressedrawbytes, notcontaineridentity',original_upper_controls=13,wrapper_controls=controls,minimum_total_calls_in_fixed_grammar=112,upper_H1_calls=112,query_savings=0,full_137_field_physical_endpoint_replay=False,lower_proof_execution='hash/scope authentication only; retained independent static review, no formal kernel',incremental_global_bound=False,full_rawdual_or_compiler_admission=False,new_kappa=None,pre_custody_sha256=digest(before),post_custody_sha256=digest(after),inputs_and_modes_unchanged=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--integrity-only',action='store_true');args=parser.parse_args()
    print(json.dumps(verify(not args.integrity_only),sort_keys=True))
