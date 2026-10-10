#!/usr/bin/env python3
"""Fresh, network-free admission of the composed conditional gen4 construction."""
import sys
if not __debug__: raise SystemExit('Assertions required; refusing -O')
sys.dont_write_bytecode = True
import argparse, hashlib, json, os, shlex, shutil, subprocess, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent
BASE_MANIFEST = '6381aa8d881a4a89cf6c40db5bcd705b928a27599540a270bf3cd15f604c705d'
WORD = '00704c44a562a115454152cff41f1b39ec5491be192b1e792855a8541c3f34ee'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def integrity():
    manifest = ROOT/'MANIFEST.json'
    files = {}
    for p in ROOT.rglob('*'):
        assert not p.is_symlink(), 'Symlink in immutable package'
        if p.is_file() and p != manifest: files[p.relative_to(ROOT).as_posix()] = sha(p)
    assert files == json.loads(manifest.read_text())['files'], 'Changed, missing or unpinned source'
    assert sha(ROOT/'vendor/pr276/MANIFEST.json') == BASE_MANIFEST
    return sha(manifest)
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args(); out=a.output.resolve()
    assert not out.exists() and not out.is_relative_to(ROOT), 'Use a fresh output outside package'
    import sympy
    assert sys.version_info >= (3,11) and sympy.__version__ == '1.14.0'
    digest=integrity(); out.mkdir(parents=True); start=time.monotonic(); stages=[]
    env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    def run(name,args):
        print(name, flush=True); t=time.monotonic()
        with (out/(name+'.log')).open('w') as log:
            subprocess.run([str(x) for x in args],check=True,stdout=log,stderr=subprocess.STDOUT,env=env)
        stages.append({'stage':name,'seconds':time.monotonic()-t})
    py=[sys.executable,'-B']; code=ROOT/'code'; base=ROOT/'vendor/pr276'
    try:
        run('01-baseline',py+[base/'verify.py','--output',out/'baseline'])
        run('02-export',py+[code/'export.py','--base',base,'--output',out/'export'])
        run('03-retime',py+[code/'retime.py','--export-dir',out/'export','--output',out/'retimed'])
        run('04-cleanup',py+[code/'cleanup.py','--source-dir',out/'retimed','--export-dir',out/'export','--output',out/'cleanup'])
        run('05-entrances',py+[code/'entrances.py','--source-dir',out/'cleanup','--export-dir',out/'export','--output',out/'candidate'])
        # Exact F2 target-prefix compression (PR268's mechanism, native stage from PR273): 280 disjoint target groups whose
        # dependent's frame-20 prefix response is the F2 sum of its retained group-mates'; literal dependencies are recomputed
        # from the actual word and both all-column replays run before anything is emitted. Rewrites candidate/COHORT249-RECORDS.bin
        # in place (the pre-compression word is kept as COHORT249-PRE-TARGET-RECORDS.bin); every later checker re-reads the word.
        run('05b-target-prefix',py+[code/'target_prefix.py',out/'export',out/'candidate',ROOT/'data/target-selection.json'])
        assert sha(out/'candidate/COHORT249-RECORDS.bin') == WORD
        compiler=shlex.split(os.environ.get('CXX','c++'))
        for name in ['five-stage-columns','charts']:
            run('compile-'+name,compiler+['-std=c++17','-O2','-I'+str(ROOT/'vendor'),code/(name+'.cpp'),'-o',out/name])
        run('06-columns',[out/'five-stage-columns',out/'candidate/COHORT249-RECORDS.bin',out/'candidate/COHORT-FIVE-STAGE-COLUMNS.json','1760','16410'])
        # The binary and chart output directory must have distinct names.
        chartdir=out/'chart-audit'; chartdir.mkdir()
        run('07-charts',[out/'charts',out/'export',out/'candidate',chartdir])
        run('08-price',py+[code/'price.py',out/'candidate','--base',base,'--output',out/'PRICE.json'])
        run('09-admission',py+[code/'admit.py',out/'candidate','--export',out/'export','--baseline',out/'baseline','--charts',chartdir/'COMBINED-CHART-AUDIT.json','--price',out/'PRICE.json','--output',out/'admission'])
        assert integrity()==digest
        price=json.loads((out/'PRICE.json').read_text())
        report={'status':'PASS_IMMUTABLE_COMPOSED_GEN4_CONSTRUCTION','manifest_sha256':digest,'word_sha256':WORD,'kappa':price['kappa'],'kappa_decimal':price['kappa_decimal'],'inputs_unchanged':True,'fresh_stages':stages,'seconds':time.monotonic()-start,'scope':'Conditional finite construction. Inherited all-size compiler, common weighted chart, restored rows, selectors, routing, prime supply, precision/recovery, complex symbolic correctness and analytic interfaces remain assumptions. No claim about the latest public comparator is inferred by this offline verifier.'}
        (out/'VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
        print('PASS kappa = '+price['kappa_decimal'],flush=True)
    except BaseException as e:
        (out/'FAILURE.json').write_text(json.dumps({'status':'FAIL','error':str(e),'completed':stages},indent=2)+'\n')
        raise
if __name__=='__main__': main()
