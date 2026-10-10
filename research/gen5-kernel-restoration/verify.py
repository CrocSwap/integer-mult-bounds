#!/usr/bin/env python3
"""Fresh pinned PR290, exact early restorations, complete banks and finite price."""
import sys
if not __debug__:raise SystemExit('Assertions must be enabled')
sys.dont_write_bytecode=True
import argparse,concurrent.futures,hashlib,json,os,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PIN='3fa7b6814eaebe2d61147b9b59db2d7b713aca481d909ae1de4916b582ae2647'
WORD='e7daa5545698288da62cb775114bda64227d2068b14f1add1b09008cbc460542'
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
    base,out=a.base.resolve(),a.output.resolve()
    assert sys.version_info>=(3,11) and sys.byteorder=='little'
    assert not out.exists() and not out.is_relative_to(ROOT) and not out.is_relative_to(base)
    own=integrity(ROOT);assert integrity(base)==PIN
    out.mkdir(parents=True)
    for name in ['logs','bin','candidate']:(out/name).mkdir()
    started=time.monotonic();stages=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');py=[sys.executable,'-B']
    def run(label,cmd,timeout=600):
        print(label,flush=True);t=time.monotonic()
        with (out/'logs'/(label+'.log')).open('w')as log:
            subprocess.run(list(map(str,cmd)),stdout=log,stderr=subprocess.STDOUT,env=env,check=True,timeout=timeout)
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
            jobs=[pool.submit(compile_all),pool.submit(run,'01-pr290',py+[base/'verify.py','--output',out/'pr290'])]
            for j in jobs:j.result()
        cert=load(out/'pr290/verification.json')
        assert cert['status']=='PASS_IMMUTABLE_GEN5_KERNEL_ENTRIES_FIVE_STAGE_BANKED_CONSTRUCTION'
        assert cert['inputs_unchanged'] and cert['manifest_sha256']==PIN
        assert set(cert['fresh_stages'])=={'virtual','raw','bit','kernel','scalar','primes','banks','complex','math','finite'}
        run('02-coordinates',py+[ROOT/'export.py',base,out/'coordinates'])
        coords=out/'coordinates';B=out/'base';D=out/'candidate'
        for name,digest in {'frames.json':'c2af2f8ae7ae2e3d9d5569799aca7b79a9ccc396d215e73af8b38f07191d85d8','249-states.json':'894b6cdcbc93c43afab4ac3beafa6b7b20710aba6f0ef6e46bf9507eefec4f68'}.items():
            assert sha(coords/name)==digest
        run('03-adapter',py+[ROOT/'export290.py','--baseline',out/'pr290','--output',B,'--base-export',coords])
        assert sha(B/'COHORT249-RECORDS.bin')==WORD
        run('04-restore',[exe('restore'),B,B,D])
        run('05-signed-audit',py+[ROOT/'audit.py','--candidate',D,'--old',B,'--base-export',coords,'--bank-export',out/'bank-base'])
        jobs=[('06-banks',[exe('banks290'),out/'bank-base',D/'COHORT249-INITIAL.json',D/'COHORT249-FRAMES.json',D,'gen5-kernel-restoration']),
              ('07-global',[exe('global'),D/'COHORT249-RECORDS.bin',out/'bank-base/249-states.json',D/'GLOBAL.json'])]
        with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:list(pool.map(lambda j:run(*j),jobs))
        run('08-price',[exe('price'),D/'COHORT249-REPLAY.json',D/'BANK-REVIEW.json',D/'PRICE.json'])
        run('09-finite',[exe('finite'),D/'COHORT249-RECORDS.bin',D/'PRICE.json',D/'BANK-REVIEW.json',D/'GLOBAL.json',D/'FINITE.json'])
        run('10-fixed',[exe('fixed'),D/'PRICE.json',D/'FINITE.json',D/'FIXED-PRICE.json'])
        run('11-invoice-audit',py+[ROOT/'check.py','--replay',out])
        proof=load(D/'INVOICE-AUDIT.json');assert integrity(ROOT)==own and integrity(base)==PIN
        result=dict(status='PASS_FRESH_PR290_AND_440_EARLY_RESTORATIONS',manifest_sha256=own,base_manifest_sha256=PIN,
                    inputs_unchanged=True,fresh_stages=sorted(stages,key=lambda x:x['stage']),seconds=time.monotonic()-started,
                    word_sha256=proof['word_sha256'],kappa=proof['kappa'],kappa_decimal=proof['kappa_decimal'],scope=proof['scope'])
        (out/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS kappa = '+result['kappa_decimal'],flush=True)
    except BaseException as e:
        (out/'FAILURE.json').write_text(json.dumps(dict(error=str(e),completed_stages=stages),indent=2)+'\n');raise
if __name__=='__main__':main()
