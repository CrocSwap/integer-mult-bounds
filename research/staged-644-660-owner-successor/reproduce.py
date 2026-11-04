"""Long original-admission recipe, separate from the bounded replay.

Historical objects and the original source dependencies are required. The wrapper
is a reproducible recipe; its complete cold tail is not claimed tested here.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse,json,os,subprocess,sys,types
P=Path(__file__).resolve().parent
def need(v,s):
 if not v:raise ValueError(s)
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for n in ('repo','work'):ap.add_argument('--'+n,type=Path,required=True)
 ap.add_argument('--retained',type=Path);ap.add_argument('--jobs',type=int,choices=(1,2),default=1);a=ap.parse_args()
 need(__debug__,'inherited validators require unoptimized Python')
 work=a.work.resolve();repo=a.repo.resolve();need(not work.exists() and not work.is_relative_to(P) and not P.is_relative_to(work),'fresh disjoint work');work.mkdir(parents=True)
 m=types.ModuleType('predecessor');m.__file__=str(P/'predecessor.py');exec(compile((P/'predecessor.py').read_bytes(),m.__file__,'exec'),m.__dict__)
 pred,word=m.extract(work/'predecessor')
 env=dict(os.environ,GIT_NO_REPLACE_OBJECTS='1',PYTHONDONTWRITEBYTECODE='1',PYTHONPYCACHEPREFIX=str(work/'pycache'),OWNER_SOURCE_REPO=str(repo))
 for k in ('PYTHONPATH','PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_RECORD','WITNESS_DISCOVER'):env.pop(k,None)
 def run(name,args):
  with (work/(name+'.log')).open('wb') as f:r=subprocess.run([sys.executable,'-B',*map(str,args)],env=env,stdout=f,stderr=subprocess.STDOUT)
  need(r.returncode==0,'failed '+name);print('PASS',name,flush=True)
 prep=work/'source-preparation';args=[pred/'reproduce.py','--repo',repo,'--word-package',word,'--work',prep,'--prepare-only','--jobs',a.jobs]
 if a.retained:args+=['--retained',a.retained.resolve()]
 run('original-source-native-preparation',args)
 run('fresh-successor-owners-and-arithmetic',[P/'verify.py','--repo',repo,'--out',work/'independent'])
 sw=prep/'source-stages';helper=sw/'parent-export/pr2894/vendor/pr2857/vendor/pr2839';fill=work/'independent/candidate';adapters=prep/'adapters';candidate=work/'candidate'
 run('complete-original-admission',[adapters/'admit_extension.py','--source',prep/'source','--fill',fill/'COMPOSED-FILL.json.gz','--order',fill/'ORDER.json','--dispatch',fill/'DISPATCH.json','--native-cache',prep/'native/native-cache','--native-receipt',prep/'native/NATIVE-RECEIPT.json','--work',candidate,'--replica-helper-dir',helper,'--reconstructor',helper/'reconstruct_replica.py','--blocknorm-checker',adapters/'extension_blocknorm.py','--comparison-claim',sw/'pr2969/CLAIM.json','--source-profile','staged-pair','--comparison-profile','pr2969','--jobs',a.jobs])
 read=lambda p:json.loads(p.read_bytes())
 release=read(candidate/'release/RELEASE-RECEIPT.json');result=read(candidate/'RESULT.json');fresh=read(work/'independent/RESULT.json');old=read(pred/'CLAIM.json')
 need(release['status']=='PASS_RELEASE' and result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE','complete original release')
 need(Q(release['kappa_decimal'])==Q(result['kappa'])==Q(fresh['kappa'])>Q(old['kappa']),'same fresh strict successor K')
 (work/'RESULT.json').write_text(json.dumps(dict(status='PASS_FULL_OWNER_SUCCESSOR_RELEASE',kappa=fresh['kappa'],retained_bootstrap_reused=bool(a.retained),scope='Conditional finite release; all inherited all-size hypotheses remain.'),indent=2)+'\n')
if __name__=='__main__':main()
