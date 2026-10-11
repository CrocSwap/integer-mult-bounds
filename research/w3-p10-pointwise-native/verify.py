#!/usr/bin/env python3
"""Complete source-bound Design T/twins, native banks and exact finite assembly.
OpenAI Codex-assisted integration; provenance and upstream notices are retained.
"""
import sys
if not __debug__:raise SystemExit('Assertions must remain enabled; refusing optimization')
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,hashlib,json,os,subprocess,time
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
STAGES=['immutable-source325','regenerate-design-and-compact','immutable-complex-reserve','export-native']+['compile-'+s for s in ('legality','columns','changed-charts','banks','invoice')]+['legality','columns','both-reflected-ledgers','tiling','bank-frames-and-assignment','changed-charts','geometry-admission','all-frame-prime-minors','price','finite-invoice','prime-threshold-bootstrap','complete-admission']

def integrity():
    files={}
    for p in ROOT.rglob('*'):
        assert not p.is_symlink()
        if p.is_file()and p!=ROOT/'MANIFEST.json':files[p.relative_to(ROOT).as_posix()]=sha(p)
    assert files==read(ROOT/'MANIFEST.json')['files'], 'Missing, changed or unpinned file'
    pin=read(ROOT/'SOURCE.json')
    for k in ('predecessor','complex_reserve'):
        assert sha(ROOT/'vendor'/k.replace('_','-')/'MANIFEST.json')==pin[k]['manifest_sha256']
    return sha(ROOT/'MANIFEST.json')

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--cxx',default='c++');p.add_argument('--boost-include',type=Path);a=p.parse_args()
    assert sys.version_info>=(3,11)and sys.byteorder=='little'
    digest=integrity();pin=read(ROOT/'SOURCE.json');out=a.output.resolve();assert not out.exists()and not out.is_relative_to(ROOT);out.mkdir()
    for d in ('logs','bin','bank','charts'):(out/d).mkdir()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');py=[sys.executable,'-B'];code=ROOT/'code';src=ROOT/'vendor/predecessor';reserve=ROOT/'vendor/complex-reserve';start=time.monotonic();stages=[]
    def run(label,args):
        assert label==STAGES[len(stages)];print(label,flush=True);t=time.monotonic()
        with(out/'logs'/(label+'.log')).open('w')as log:subprocess.run(list(map(str,args)),check=True,stdout=log,stderr=subprocess.STDOUT,env=env,cwd=out)
        stages.append(dict(stage=label,seconds=time.monotonic()-t))
    try:
        run('immutable-source325',py+[src/'verify.py','--output',out/'predecessor'])
        args=py+[code/'materialize.py',out,'--cxx',a.cxx]
        if a.boost_include:args+=['--boost-include',a.boost_include.resolve()]
        run('regenerate-design-and-compact',args)
        run('immutable-complex-reserve',py+[reserve/'verify.py','--output',out/'complex-reserve'])
        run('export-native',py+[code/'export_native.py','--base',out/'materialized/base','--candidate',out/'materialized/final','--output',out/'native-export'])
        for n in ('base','candidate','EXPORT.json','ROLE-MAP.json'):(out/'native-export'/n).rename(out/n)
        (out/'native-export').rmdir()
        for n in ('legality','columns','changed-charts','banks','invoice'):
            cmd=[a.cxx,'-O2','-std=c++17','-I',ROOT/'vendor/native']
            if a.boost_include:cmd+=['-I',a.boost_include.resolve()]
            run('compile-'+n,cmd+[code/(n+'.cpp'),'-o',out/'bin'/n])
        b=out/'base';c=out/'candidate';bin=out/'bin'
        run('legality',[bin/'legality',b,c,out/'LEGALITY.json'])
        run('columns',[bin/'columns',c/'COHORT249-RECORDS.bin',out/'COLUMNS.json','960','7620','20'])
        run('both-reflected-ledgers',py+[code/'reflected_ledgers.py','--candidate',c,'--output',out/'REFLECTED-LEDGERS.json'])
        run('tiling',py+[code/'tiling.py',b,c,out/'TILING.json'])
        run('bank-frames-and-assignment',[bin/'banks',b,c/'COHORT249-INITIAL.json',c/'COHORT249-FRAMES.json',out/'bank','w3-p10-complete',out/'TILING.json',c/'COHORT249-FINAL.json'])
        run('changed-charts',[bin/'changed-charts',b,c,out/'charts'])
        run('geometry-admission',py+[code/'admit_geometry.py','--base',b,'--candidate',c,'--bank',out/'bank','--charts',out/'charts','--output',out/'BANK.json'])
        run('all-frame-prime-minors',py+[code/'frame_prime_minors.py',c/'frames.json',out/'FRAME-PRIMES.json'])
        run('price',py+[code/'price.py',c,'--bank',out/'BANK.json','--complex',out/'predecessor/complex.json','--complex-reserve',reserve,'--complex-reserve-proof',out/'complex-reserve','--output',out/'PRICE.json'])
        run('finite-invoice',[bin/'invoice',c/'COHORT249-RECORDS.bin',out/'PRICE.json',out/'BANK.json',out/'COLUMNS.json',out/'INVOICE.json'])
        run('prime-threshold-bootstrap',py+[code/'threshold_bootstrap.py','--arithmetic-stage','--source',ROOT,'--replay',out,'--expected-word',pin['final_word_sha256'],'--require-frame-primes','--output',out/'REFINEMENT.json'])
        run('complete-admission',py+[code/'finish.py',out])
        assert [s['stage']for s in stages]==STAGES and integrity()==digest
        c=read(out/'CERTIFICATE.json');v=dict(status=c['status'],kappa=c['kappa'],word_sha256=c['word_sha256'],manifest_sha256=digest,inputs_unchanged=True,fresh_stages=stages,seconds=time.monotonic()-start,scope=c['scope'])
        (out/'VERIFICATION.json').write_text(json.dumps(v,sort_keys=True,indent=2)+'\n');print('PASS conditional kappa = '+c['kappa'],flush=True)
    except BaseException as e:
        (out/'FAILURE.json').write_text(json.dumps(dict(status='FAIL',error=str(e),completed=stages),indent=2)+'\n');raise
if __name__=='__main__':main()
