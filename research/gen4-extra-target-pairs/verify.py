#!/usr/bin/env python3
"""Fresh immutable PR283 replay followed by twenty additional target pairs."""
import sys
if not __debug__:raise SystemExit('Assertions must be enabled')
sys.dont_write_bytecode=True
import argparse,concurrent.futures,gzip,hashlib,json,os,struct,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE_MANIFEST='bbaddd0d899baf91ccb7364da9251c93fea64c5fbaf7ccb6057c39600d4cf521'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def integrity(root):
    manifest=root/'MANIFEST.json';expected=load(manifest)['files'];actual={}
    for p in root.rglob('*'):
        assert not p.is_symlink(),'Symlink in pinned source package'
        if p.is_file()and p!=manifest:actual[p.relative_to(root).as_posix()]=sha(p)
    assert actual==expected,'Changed, missing or unpinned source file'
    return sha(manifest)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--base',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--cxx',default='g++');ap.add_argument('--boost-include',type=Path);a=ap.parse_args()
    base,out=a.base.resolve(),a.output.resolve();assert not out.exists()and not out.is_relative_to(ROOT)and not out.is_relative_to(base)
    own=integrity(ROOT);assert integrity(base)==BASE_MANIFEST
    out.mkdir(parents=True);(out/'logs').mkdir();began=time.monotonic();stages=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    def run(label,cmd):
        print(label,flush=True);start=time.monotonic()
        with (out/'logs'/(label+'.log')).open('w')as log:subprocess.run(list(map(str,cmd)),stdout=log,stderr=subprocess.STDOUT,env=env,check=True)
        stages.append(dict(stage=label,seconds=time.monotonic()-start))
    py=[sys.executable,'-B'];replay=out/'pr283';candidate=out/'candidate';candidate.mkdir()
    try:
        cmd=py+[base/'verify.py','--output',replay,'--cxx',a.cxx]
        if a.boost_include:cmd+=['--boost-include',a.boost_include.resolve()]
        run('01-pr283',cmd)
        admitted=load(replay/'CERTIFICATE.json')
        assert admitted['status']=='PASS_SOURCE_REGENERATED_COMPOSITION'and admitted['upstream_fresh_nine_stages']
        assert admitted['package_manifest_sha256']==BASE_MANIFEST
        pairs=json.loads(gzip.decompress((ROOT/'pairs.json.gz').read_bytes()));assert len(pairs)==20
        selection=load(base/'inputs/targets220.json');assert len(selection['groups'])==220
        original=list(struct.iter_unpack('<6i',(replay/'base/249-records.bin').read_bytes()))
        for pair in pairs:
            e=original[pair['close_after_record']]
            assert [e[j]for j in(0,1,2,3,5)]==pair['reference_close_scalar']
        selection['groups']+=pairs
        selected=out/'targets240.json';selected.write_text(json.dumps(selection,separators=(',',':'))+'\n')
        def exe(name):return replay/'bin'/(name+('.exe'if os.name=='nt'else''))
        X=replay/'restored'
        run('02-target-pairs',[exe('target'),X,X,selected,candidate,replay/'base/249-records.bin',replay/'sinks/OLD-TO-NEW.json'])
        jobs=[('03-target-grams',[exe('target-gram'),X,candidate,candidate/'TARGET279-GRAM.json']),
            ('04-legality',[exe('legality'),X,candidate,candidate/'LEGALITY.json']),
            ('05-prefix',[exe('prefix'),X,candidate,candidate/'PREFIX.json']),
            ('06-banks',[exe('banks'),X,candidate/'COHORT249-INITIAL.json',candidate/'COHORT249-FRAMES.json',candidate,'gen4-extra-target-pairs']),
            ('07-global',[exe('global'),candidate/'COHORT249-RECORDS.bin',X/'249-states.json',candidate/'GLOBAL.json'])]
        with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:list(pool.map(lambda x:run(*x),jobs))
        run('08-price',[exe('price'),candidate/'COHORT249-REPLAY.json',candidate/'BANK-REVIEW.json',candidate/'PRICE.json'])
        run('09-finite',[exe('finite'),candidate/'COHORT249-RECORDS.bin',candidate/'PRICE.json',candidate/'BANK-REVIEW.json',candidate/'GLOBAL.json',candidate/'FINITE.json'])
        run('10-fixed',[exe('fixed'),candidate/'PRICE.json',candidate/'FINITE.json',candidate/'FIXED-PRICE.json'])
        run('11-independent',py+[ROOT/'check.py','--base-replay',replay,'--candidate',candidate])
        assert integrity(ROOT)==own and integrity(base)==BASE_MANIFEST
        proof=load(candidate/'INDEPENDENT.json')
        result=dict(status='PASS_IMMUTABLE_EXTRA_TARGET_PAIRS_ON_GEN4_COMPOSITION',manifest_sha256=own,base_manifest_sha256=BASE_MANIFEST,
            inputs_unchanged=True,fresh_stages=sorted(stages,key=lambda x:x['stage']),seconds=time.monotonic()-began,
            word_sha256=proof['word_sha256'],kappa=proof['kappa'],kappa_decimal=proof['kappa_decimal'],scope=proof['scope'])
        (out/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS kappa = '+result['kappa_decimal'],flush=True)
    except BaseException as e:
        (out/'FAILURE.json').write_text(json.dumps(dict(error=str(e),completed_stages=stages),indent=2)+'\n');raise

if __name__=='__main__':main()
