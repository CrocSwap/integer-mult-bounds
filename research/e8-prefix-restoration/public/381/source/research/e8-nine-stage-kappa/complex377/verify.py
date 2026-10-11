#!/usr/bin/env python3
"""Replay the independent nine-stage component from pinned sources only."""
import argparse,hashlib,json,shutil,subprocess,sys,time
from pathlib import Path
assert __debug__, 'Run without -O'
assert sys.version_info>=(3,11)
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);a=ap.parse_args();wd=a.work.resolve();assert not wd.exists() and not wd.is_relative_to(ROOT)
expected=read(ROOT/'MANIFEST.json');actual={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and p.name!='MANIFEST.json'}
# Nested vendor MANIFEST.json files are themselves pinned, too.
actual={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'MANIFEST.json'}
assert actual==expected['files'] and not any(p.is_symlink() for p in ROOT.rglob('*'))
wd.mkdir();shutil.copytree(ROOT/'work',wd/'work');logs=wd/'logs';logs.mkdir();done=[];started=time.monotonic()
def run(name,argv):
 t=time.monotonic();log=logs/(name+'.log');print(name,flush=True)
 with log.open('w') as f:r=subprocess.run([sys.executable,'-B']+argv,cwd=wd,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,(name,r.returncode,str(log))
 done.append(dict(stage=name,returncode=0,seconds=time.monotonic()-t,log_sha256=sha(log)))
try:
 run('frozen-source-integrity',['-c',"import runpy; x=runpy.run_path('work/native358/vendor/complex-reserve/verify.py'); print(x['integrity']())"])
 run('fresh-local-admission',['work/native358/vendor/complex-reserve/admit.py','--source','work/native358/vendor/complex-reserve/upstream/pr352','--output','work/complex-nine-native/local-admission'])
 for name,script in [('finite-data-banks-profile','complex_candidate.py'),('exact-clifford-recipes','verify_clifford_frames.py'),('exact-data-and-cover-phases','data_phases.py'),('global-template-and-invoice','global_nine.py'),('independent-template-two-moments','audit_nine_template.py'),('fixed-bit-outer-check','outer_fixed.py')]:run(name,['work/odd-stages/'+script])
 out=wd/'work/complex-nine-native';price=read(out/'INDEPENDENT-TEMPLATE-AUDIT.json');outer=read(out/'OUTER-FIXED-BIT.json');invoice=read(out/'GLOBAL-REVIEW.json')
 assert price['coarse_complex']=='999240641319551/1000000000000000000' and outer['kappa']=='804849251275843/1000000000000000000'
 assert invoice['cover_correction_calls']==14727 and invoice['finite_invoice']['halving_degree']==2
 receipts={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()}
 result=dict(status='PASS_PORTABLE_NINE_STAGE_COMPLEX_FINITE_COMPONENT',source_manifest_sha256=sha(ROOT/'MANIFEST.json'),fresh_stages=done,complex_coarse=price['coarse_complex'],fixed_bit_kappa=outer['kappa'],new_final_kappa_claim=False,final_kappa_one_percent_milestone_reached=False,proof='work/complex-nine-native/PROOF.txt',receipt_sha256=receipts,seconds=time.monotonic()-started,scope='The explicit proof retains local E8, Clifford/compiler, common-grid and row/analytic interfaces. No Lean kernel build, astronomical cover enumeration, certificate-producer regeneration or improved bit-side theorem is claimed.')
 (wd/'VERIFICATION.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True)
except BaseException as e:
 (wd/'FAILURE.json').write_text(json.dumps(dict(error=str(e),completed=done),indent=2));raise
