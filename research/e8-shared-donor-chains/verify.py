"""Offline verification of the new shared-donor composition; no network or search."""
from pathlib import Path
from fractions import Fraction as Q
import argparse,hashlib,json,os,subprocess,sys,time
assert __debug__, 'Do not use Python -O'
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('output',type=Path)
ap.add_argument('--replay-bit',action='store_true',help='Optional fresh replay of the unchanged bundled bit component; default source-bound receipt reuse')
args=ap.parse_args();OUT=args.output.resolve()
assert not OUT.exists() and not OUT.is_relative_to(ROOT),'Use a fresh output directory outside this package'
OUT.mkdir(parents=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def snapshot():return {p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'MANIFEST.json'}
manifest=read(ROOT/'MANIFEST.json');assert snapshot()==manifest['files'],'Missing or changed package file'
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
for k in list(env):
 if k.startswith(('COMPLEX_','CX_')) or k=='PR315':env.pop(k,None)
checks=[]
def run(name,command):
 t=time.monotonic();log=OUT/(name+'.log');print('RUN',name,flush=True)
 with log.open('w',encoding='utf-8') as f:r=subprocess.run(list(map(str,command)),env=env,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,(name,r.returncode,str(log))
 checks.append(dict(name=name,seconds=round(time.monotonic()-t,3),log_sha256=sha(log)));print('PASS',name,flush=True)
def py(name,file,*argv):run(name,[sys.executable,'-B',ROOT/file,*argv])
try:
 reuse=read(ROOT/'inherited/BIT-REUSE.json');bm=read(ROOT/'inherited/BASE-MANIFEST.json');br=read(ROOT/'inherited/BASE-REPLAY.json')
 assert sha(ROOT/'inherited/BASE-MANIFEST.json')==reuse['base_manifest_sha256']
 assert sha(ROOT/'inherited/BASE-REPLAY.json')==reuse['base_replay_sha256']
 assert sha(ROOT/'inherited/BIT-COMPOSITION-RECEIPT.json')==reuse['receipt_sha256']
 bv=read(ROOT/'inherited/BASE-VALIDATION.json');assert sha(ROOT/'inherited/BASE-VALIDATION.json')==reuse['base_validation_sha256']
 assert all(sha(ROOT/n)==h==bm['files'][n]==bv['executed_sources_sha256'][n] for n,h in reuse['files'].items())
 assert bv['execution_checks']==br['checks'] and bv['kappa']==br['kappa']
 bit=read(ROOT/'inherited/BIT-COMPOSITION-RECEIPT.json');bit_coarse=bit['pricing']['bit_coarse']
 assert Q(bit_coarse)==Q(255384852701747,250000000000000000)==Q(br['bit_coarse'])
 py('reconstruct','frames/reconstruct.py',ROOT/'inputs/candidate781.json',OUT/'reconstructed',ROOT/'frames/selection.json')
 py('shared','shared/reconstruct.py',ROOT/'inputs/candidate781.json',OUT/'shared',ROOT/'shared/selection194.json','--reference119',OUT/'reconstructed/candidate.json')
 py('dual','dual/reconstruct.py',OUT/'shared/candidate.json',OUT/'dual','--source-sha256','141b7c732820f822d09f906a6f9206b2906777177bf7860c49f5acacb7da69a3')
 py('public-frame','code/frame-rewrite.py',OUT/'dual/candidate.json',OUT/'final')
 candidate=OUT/'final/candidate.json'
 py('local','local/local_admit.py',candidate,OUT/'local','--helper-baseline',ROOT/'inputs/helper781.json','--signed-baseline',ROOT/'inputs/candidate781.json')
 exe=OUT/('phase-replay.exe' if os.name=='nt' else 'phase-replay')
 run('compile-phase',[env.get('CXX','g++'),'-O2','-std=c++17','-I'+str(ROOT/'architecture/deps'),ROOT/'architecture/phase-replay.cpp','-o',exe])
 py('phase','architecture/phase.py',candidate,ROOT/'local/deps',exe,OUT/'phase',ROOT/'architecture/phase-replay.cpp')
 prior=ROOT/'architecture/inputs/GLOBAL-TEMPLATE.json.gz'
 py('banks','architecture/banks.py',candidate,ROOT/'inputs/bank-patterns.json',OUT/'phase/RESIDUALS.json',OUT/'local/LOCAL-PROGRAMS.json.gz',OUT/'local/RESULT.json',prior,ROOT/'local/deps',OUT/'banks',ROOT/'architecture/inputs/DATA-PHASES.json')
 py('bank-audit','architecture/audit.py',OUT/'banks',candidate,OUT/'phase/RESIDUALS.json',OUT/'local/LOCAL-PROGRAMS.json.gz',prior)
 py('bridge','architecture/bridge.py',OUT/'banks')
 admission=read(OUT/'banks/ADMISSION.json');audit=read(OUT/'banks/INDEPENDENT-ADMISSION.json')
 assert audit['template_sha256']==admission['template_sha256'] and audit['candidate_sha256']==sha(candidate)
 assert (admission['live'],admission['physical'],admission['banks_per_stage'],admission['deficit'])==(14322,15113,738,2496)
 assert admission['profile']==read(ROOT/'inputs/expected-profile.json')
 bridge=admission.get('bridge')
 if bridge is None:bridge=read(OUT/'banks/BRIDGE.json')
 price_input=dict(profile=admission['profile'],m=admission['m'],stock=admission['live'],bridge=bridge,bit_coarse=bit_coarse,supplier_receipt_sha256=sha(OUT/'banks/ADMISSION.json'))
 (OUT/'outer-input.json').write_text(json.dumps(price_input,indent=2)+'\n',encoding='utf-8')
 py('outer','code/outer.py',OUT/'outer-input.json',OUT/'OUTER.json');outer=read(OUT/'OUTER.json')
 assert Q(outer['kappa'])==Q(1016422320428301,1000000000000000000) and len(outer['strict_constraints'])==47
 if args.replay_bit:
  py('optional-bit','code/bit-compose-replay.py',OUT/'bit','--pr381',ROOT/'vendor/bit','--reuse',ROOT/'vendor/reuse','--complex',outer['complex_coarse'])
  assert Q(read(OUT/'bit/BIT-COMPOSITION-RECEIPT.json')['pricing']['bit_coarse'])==Q(bit_coarse)
 assert snapshot()==manifest['files'],'Package mutated during verification'
 result=dict(status='PASS_SHARED_DONOR_CHAINS_CONDITIONAL_COMPOSITION',kappa=outer['kappa'],kappa_decimal='0.001016422320428301',complex_coarse=outer['complex_coarse'],bit_coarse=bit_coarse,checks=checks,candidate_sha256=sha(candidate),manifest_sha256=sha(ROOT/'MANIFEST.json'),template_sha256=admission['template_sha256'],bit_evidence='fresh optional replay' if args.replay_bit else 'unchanged source-bound prior finite receipt',scope='Finite conditional changed composition. Inherited all-size window, correlated-bank, recursive compiler, ordinary-call/fixed-tape/restored-row, precision and analytic interfaces remain assumptions; no Lean or unconditional multiplication theorem.')
 (OUT/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(result['status'],result['kappa'],flush=True)
except BaseException as e:
 (OUT/'FAILURE.json').write_text(json.dumps(dict(error=str(e),completed=checks),indent=2)+'\n',encoding='utf-8');raise
