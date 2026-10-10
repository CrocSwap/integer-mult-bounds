#!/usr/bin/env python3
"""Fresh gen5 prerequisites, source retiming, target compression and exact price."""
import sys
if not __debug__:raise SystemExit('Assertions must be enabled')
sys.dont_write_bytecode=True
import argparse,concurrent.futures,gzip,hashlib,json,os,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE_MANIFEST='2bf16d814b629cfb314db663532c55eba5f12d63f732793e825d1ec3eb07df17'
BASE_WORD='6613c804f11ee9e96d96f1a34f8a7afa7a4a5380d998a72a1ac29012aeca029f'
RETIME_WORD='729b7dd88da3d5da4ec2ba77325312e6730c7c4b93abbffc0f2fa9eca533a48a'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def integrity(root):
    manifest=root/'MANIFEST.json';actual={}
    for p in root.rglob('*'):
        assert not p.is_symlink(),'Symlink in source package'
        if p.is_file()and p!=manifest:actual[p.relative_to(root).as_posix()]=sha(p)
    assert actual==load(manifest)['files'],'Changed, missing or unpinned source file'
    return sha(manifest)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--base',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--cxx',default='g++');ap.add_argument('--boost-include',type=Path);a=ap.parse_args()
    base,out=a.base.resolve(),a.output.resolve();assert sys.version_info>=(3,11) and sys.byteorder=='little'
    assert not out.exists() and not out.is_relative_to(ROOT) and not out.is_relative_to(base)
    own=integrity(ROOT);assert integrity(base)==BASE_MANIFEST
    out.mkdir(parents=True)
    for name in ['logs','bin','base','retimed','candidate']:(out/name).mkdir()
    started=time.monotonic();stages=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');py=[sys.executable,'-B']
    def run(label,cmd):
        print(label,flush=True);t=time.monotonic()
        with (out/'logs'/(label+'.log')).open('w')as log:subprocess.run(list(map(str,cmd)),stdout=log,stderr=subprocess.STDOUT,env=env,check=True)
        stages.append(dict(stage=label,seconds=time.monotonic()-t))
    def exe(n):return out/'bin'/(n+('.exe'if os.name=='nt'else''))
    def compile_one(p):
        cmd=[a.cxx,'-O2','-std=c++17','-I',ROOT/'vendor']
        if a.boost_include:cmd+=['-I',a.boost_include.resolve()]
        run('compile-'+p.stem,cmd+[p,'-o',exe(p.stem)])
    def compile_all():
        with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:list(pool.map(compile_one,sorted((ROOT/'code').glob('*.cpp'))))
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
            jobs=[pool.submit(compile_all),pool.submit(run,'01-pr285',py+[base/'verify.py','--output',out/'pr285'])]
            for j in jobs:j.result()
        cert=load(out/'pr285/verification.json')
        assert cert['status']=='PASS_IMMUTABLE_PARITY_FUSED_GEN5_FIVE_STAGE_BANKED_CONSTRUCTION'
        assert cert['inputs_unchanged'] and cert['manifest_sha256']==BASE_MANIFEST
        assert set(cert['fresh_stages'])=={'virtual','raw','bit','scalar','primes','banks','complex','math','finite'}
        run('02-export',py+[ROOT/'export.py',base,out/'base'])
        B=out/'base';R=out/'retimed';D=out/'candidate'
        assert sha(B/'249-records.bin')==BASE_WORD
        for name in ['retiming','targets']:
            (out/(name+'.json')).write_bytes(gzip.decompress((ROOT/(name+'.json.gz')).read_bytes()))
        sel=load(out/'retiming.json');assert sel['input_word_sha256']==BASE_WORD and len(sel['entries'])==880
        run('03-retiming',[exe('retime279'),B,B,out/'retiming.json',R])
        assert sha(R/'COHORT249-RECORDS.bin')==RETIME_WORD
        run('04-targets',[exe('target'),B,R,out/'targets.json',D,B/'249-records.bin',B/'IDENTITY.json'])
        jobs=[('05-grams',[exe('target-gram'),B,D,D/'TARGET279-GRAM.json']),('06-legality',[exe('legality'),B,D,D/'LEGALITY.json']),
              ('07-banks',[exe('banks'),B,D/'COHORT249-INITIAL.json',D/'COHORT249-FRAMES.json',D,'gen5-retiming-targets']),
              ('08-global',[exe('global'),D/'COHORT249-RECORDS.bin',B/'249-states.json',D/'GLOBAL.json'])]
        with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:list(pool.map(lambda j:run(*j),jobs))
        run('09-price',[exe('price'),D/'COHORT249-REPLAY.json',D/'BANK-REVIEW.json',D/'PRICE.json'])
        run('10-finite',[exe('finite'),D/'COHORT249-RECORDS.bin',D/'PRICE.json',D/'BANK-REVIEW.json',D/'GLOBAL.json',D/'FINITE.json'])
        run('11-fixed',[exe('fixed'),D/'PRICE.json',D/'FINITE.json',D/'FIXED-PRICE.json'])
        run('12-independent',py+[ROOT/'check.py','--replay',out])
        proof=load(D/'INDEPENDENT.json');assert integrity(ROOT)==own and integrity(base)==BASE_MANIFEST
        result=dict(status='PASS_FRESH_GEN5_RETIMING_TARGET_COMPOSITION',manifest_sha256=own,base_manifest_sha256=BASE_MANIFEST,
                    inputs_unchanged=True,fresh_stages=sorted(stages,key=lambda x:x['stage']),seconds=time.monotonic()-started,
                    word_sha256=proof['word_sha256'],kappa=proof['kappa'],kappa_decimal=proof['kappa_decimal'],scope=proof['scope'])
        (out/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS kappa = '+result['kappa_decimal'],flush=True)
    except BaseException as e:
        (out/'FAILURE.json').write_text(json.dumps(dict(error=str(e),completed_stages=stages),indent=2)+'\n');raise

if __name__=='__main__':main()
