"""Reproduce the complete staged-pair source/native/owner/outer release.

Requires a Git repository with the exact historical objects named in FETCH.txt,
plus the full dependencies declared by the inherited source. A fresh retained
bootstrap is the default; --retained explicitly reuses a fully authenticated
retained cache. This long command is separate from the bounded finite checker.
"""
from pathlib import Path
import argparse,hashlib,io,json,os,subprocess,sys,tarfile,time
P=Path(__file__).resolve().parent
PR3133='51eb9c4ee9e4722010d308aa3309e039d3940cc2'
PACKAGE='research/rank7-coupled-586-588-carrier-fold'
SOURCE='adb145b4f36ca330c34c0dbdb847351dafdc4ca9cd7bb4e1de01ed634d96bfe1'
HEADS=[PR3133,'51309592971e3b5be935599eed2a95404dc7781e','224bd5e56041c40078ff6b5fa7393733a215de5c','a027b0f6fdb0ab2b42ba10fc31b53960166bf2bf','b74b25f3ccc84c16e1a801d73b2f47e5ea764c78','e62d3eb9005117d82a9babcfa937ecc53237c490','e2ca469b08385d3d5e29a918d66dbefaf889e9f3','18d03c447886895ef9abf888398178e0428533ca','e9307b48d7d1b690939935ecef0f8e524e6d92f4']
def need(v,m):
 if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def tree(p):return {str(f.relative_to(p)):sha(f) for f in p.rglob('*') if f.is_file() and f!=p/'MANIFEST.json'}
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for n in ('repo','word-package','work'):ap.add_argument('--'+n,type=Path,required=True)
 ap.add_argument('--retained',type=Path);ap.add_argument('--jobs',type=int,choices=(1,2),default=1)
 ap.add_argument('--prepare-only',action='store_true',help='Build exact sources and owner/native inputs, then run inherited preparation without claiming release')
 a=ap.parse_args();repo=a.repo.resolve();pair=a.word_package.resolve();work=a.work.resolve()
 need(__debug__,'unoptimized Python required by inherited validators')
 need(not work.exists() and not work.is_relative_to(P) and not P.is_relative_to(work),'fresh disjoint work directory')
 for h in HEADS:
  need(subprocess.run(['git','-C',str(repo),'cat-file','-e',h+'^{commit}'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0,'missing historical Git object '+h+'; see FETCH.txt')
 work.mkdir(parents=True);old=work/'pr3133';old.mkdir()
 archive=subprocess.check_output(['git','-C',str(repo),'archive','--format=tar',PR3133+':'+PACKAGE])
 with tarfile.open(fileobj=io.BytesIO(archive)) as t:
  need(all(m.isfile() or m.isdir() for m in t.getmembers()),'regular historical source export')
  t.extractall(old,filter='data')
 need(sha(old/'MANIFEST.json')=='609209f577c9185b16825dd2e8bb30f0891205fddd2571a8f76c558e3cb1f70e' and tree(old)==read(old/'MANIFEST.json'),'exact full PR3133 package')
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPYCACHEPREFIX=str(work/'pycache'),PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 for k in ('PYTHONPATH','PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_RECORD','WITNESS_DISCOVER'):env.pop(k,None)
 # The inherited source manifests use LF; preserve this on Windows as well.
 lf=work/'lf-adapter';lf.mkdir();(lf/'sitecustomize.py').write_text("from pathlib import Path\n_w=Path.write_text\ndef _t(self,data,encoding=None,errors=None,newline=None):\n return _w(self,data,encoding=encoding,errors=errors,newline='\\n' if newline is None else newline)\nPath.write_text=_t\n")
 env['PYTHONPATH']=str(lf);stages=[]
 def run(name,command):
  start=time.monotonic();log=work/(name+'.log')
  with log.open('wb') as f:r=subprocess.run(list(map(str,command)),env=env,cwd=work,stdout=f,stderr=subprocess.STDOUT)
  stages.append(dict(stage=name,exit_code=r.returncode,seconds=time.monotonic()-start,log_sha256=sha(log)));save(work/'STAGES.json',stages)
  need(r.returncode==0,'failed '+name+'; inspect '+str(log));print('PASS',name,flush=True)
 py=[sys.executable,'-B'];sw=work/'source-stages'
 cmd=py+[old/'reproduce.py','--repo',repo,'--work',sw,'--dry-run']
 if a.retained:cmd+=['--retained',a.retained.resolve()]
 run('exact-predecessor-exports-and-recipe',cmd)
 recipe=read(sw/'PREFLIGHT.json')['commands'];names=[]
 for name,command in recipe:
  run(name,command);names.append(name)
  if name=='declared-edit-stage':break
 need(names[-1]=='declared-edit-stage','complete predecessor source chain')
 retained=a.retained.resolve() if a.retained else sw/'retained'
 source=work/'source'
 run('staged-source-overlay',py+[P/'portable_source_overlay.py','--source',sw/'source-edits','--pair',pair,'--review',P/'staged_pair_review.py','--out',source])
 need(sha(source/'MANIFEST.json')==SOURCE and tree(source)==read(source/'MANIFEST.json'),'exact 648-file staged source')
 env['BORROW_RECEIPTS']=str(work/'source-rebuild-receipts')
 run('complete-source-word-rebuild',py+[source/'new/rebuild_borrow.py'])
 run('staged-independent-word-controls',py+[source/'new/borrow/staged_pair_review.py','--borrow',source/'new/borrow','--out',work/'staged-review'])
 adapters=work/'adapters'
 cmd=py+[old/'tools/derive_adapters.py','--parent-package',sw/'pr2908','--source',source,'--retained-receipt',retained/'NATIVE-RECEIPT.json','--out',adapters,'--buffers','91','--source-commit','staged-pair644-660-on-pr3133','--source-profile','staged-pair','--upstream-head',PR3133]
 for name in ('pr2917','pr2966','pr2969'):cmd+=['--comparison',name+'='+str(sw/name/'CLAIM.json')]
 run('closed-source-adapters',cmd)
 run('fresh-changed-native',py+[adapters/'prepare_extension_native.py','--source',source,'--retained-cache',retained/'native-cache','--retained-receipt',retained/'NATIVE-RECEIPT.json','--out',work/'native','--jobs',a.jobs])
 env['OWNER_SOURCE_REPO']=str(repo)
 run('fresh-literal-owners',py+[P/'owners/portable_expand.py','--out',work/'owners'])
 helper=sw/'parent-export/pr2894/vendor/pr2857/vendor/pr2839'
 cmd=py+[adapters/'admit_extension.py','--source',source,'--fill',work/'owners/COMPOSED-FILL.json.gz','--order',work/'owners/ORDER.json','--dispatch',work/'owners/DISPATCH.json','--native-cache',work/'native/native-cache','--native-receipt',work/'native/NATIVE-RECEIPT.json','--work',work/'candidate','--replica-helper-dir',helper,'--reconstructor',helper/'reconstruct_replica.py','--blocknorm-checker',adapters/'extension_blocknorm.py','--comparison-claim',sw/'pr2969/CLAIM.json','--source-profile','staged-pair','--comparison-profile','pr2969','--jobs',a.jobs]
 if a.prepare_only:cmd+=['--prepare-only']
 run('complete-admission' if not a.prepare_only else 'admission-preparation-only',cmd)
 result=read(work/'candidate/RESULT.json')
 if a.prepare_only:
  need(result['status']=='PREPARED_REPLICA_SAME_WORD_DERIVATIVE_NOT_ADMITTED','preparation result')
  save(work/'RESULT.json',dict(status='PREPARED_STAGED_PAIR_NOT_ADMITTED',source_manifest_sha256=SOURCE,stages=stages,scope='Preparation only; no complete release or kappa claim.'));return
 release=read(work/'candidate/release/RELEASE-RECEIPT.json')
 need(result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE' and release['status']=='PASS_RELEASE','complete release result')
 run('fresh-independent-owner-moment-outer',py+[P/'check_owners_and_moment.py','--repo',repo,'--word-package',pair,'--out',work/'independent'])
 arithmetic=read(work/'independent/RESULT.json')
 from fractions import Fraction as Q
 need(Q(result['kappa'])==Q(release['kappa_decimal'])==Q(arithmetic['kappa'])>Q('0.00173'),'same exact released conditional candidate')
 need(tree(old)==read(old/'MANIFEST.json') and tree(source)==read(source/'MANIFEST.json'),'read-only source closure')
 save(work/'RESULT.json',dict(status='PASS_STAGED_PAIR_COMPLETE_CONDITIONAL_REPLAY',kappa=result['kappa'],source_manifest_sha256=SOURCE,release_receipt_sha256=sha(work/'candidate/release/RELEASE-RECEIPT.json'),explicit_retained_reuse=bool(a.retained),fresh_retained_bootstrap=not bool(a.retained),stages=stages,scope='Conditional finite source/native/owner/physical/prefix/outer release. All inherited all-size theorem hypotheses remain; no formal-kernel proof.'))
 print('PASS_STAGED_PAIR_COMPLETE_CONDITIONAL_REPLAY',arithmetic['kappa_decimal'],flush=True)
if __name__=='__main__':main()
