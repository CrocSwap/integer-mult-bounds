# SPDX-License-Identifier: Apache-2.0
"""Source-bound T450 replay: fresh changed native providers, explicit parent reuse.
Substantial OpenAI Codex assistance. No allocation search is invoked.
"""
import argparse,gzip,hashlib,importlib.util,json,os,shutil,subprocess,sys
from fractions import Fraction
from pathlib import Path
if not __debug__ or sys.flags.optimize:
 raise RuntimeError('Assertions must be enabled for scientific replay')
HERE=Path(__file__).resolve().parent
RECIPE='54b4e3d38bf16b81d87827275325dfe0bf0b5cb6f7e4ce7543a1061c6ad89122'
OVERLAY='053de667b534bef38f71f0c86f39647c3af501a3f940bb3e3e797d4373ee2144'
PROFILE={1:9983580,2:2940300,3:936579,4:413100,5:87495,8:32400,48:172221}
FRONTIER=Fraction('17300065495388418470049999999999999999999998999999999999999999999999/10000000000000000000000000000000000000000000000000000000000000000000000')
EXPECTED_KAPPA=Fraction('.001730047552093344159584')-Fraction(1,10**46)-Fraction(1,10**70)
STOCK_SHA='6e6b8683cc87a84e5410c399b1128eb68694f852a3927cb124067f503ed7d7c7'
ENTRY_INPUTS={'source_builder.py': '0cb5f62d517ac35c44922abc338cd41356b3e08dc7c6d6d9f64a43a9a541378f', 'templates/prepare_extension_native.py': '0cdb4b8b8b565e3dc4a312d4174c86d7d1aebc531430cb726658c8feb0c3bcf4', 'supplier3605/ARTIFACTS.json': '867bd848d04505518463eb06b1905e70ccc9256bb73312d3cd1dc57623bb319b', 'supplier3605/PROOF.md': '525b010f3a895bdb11313f9938ad1b742df64bcee0b5671399230b1ded541baf', 'supplier3605/README.md': 'c1956badbcd92f2f88dcea833facc39eefb7eef8f220fb7b1941b4c552109d89', 'supplier3605/SOURCES.json': '005bf38ae679a9fb3ad1ee94b8c35bdfec58451ef58e0a87b0c7b68ef4fc51d5', 'supplier3605/STAGED-PAIR-RECORD-base.json.gz': 'a6ae4188be998990ecb176fef5929e8e1dfce3726e372c0da2a290fe8ea73532', 'supplier3605/STAGED-PAIR-RECORD-extra.json.gz': '33a39d46d4d19bdeb6f0b6abb38cc80c68219e1ae10dd7e1acaccedc14b47236', 'supplier3605/STAGED644-660-base.json.gz': '735c540b1fe29d0ceeb4d2f304ec941e5f2bd3bc92bafc8cce2b4f9a67a3b653', 'supplier3605/STAGED644-660-extra.json.gz': '886338fc32da14f3389a82c8120a1bcf9c5e2f0ec3e9b2d377fdae809e1d977f', 'supplier3605/TASK.json': 'b85158fedf4734ff028703353ac6e9929ddea6a8e7c845c8341c2428d628717a', 'supplier3605/VALIDATION.json': 'fa3803654e230cd50bc9fb874ec80e16dd838adebf13cd0cb174f18bc12fa04a', 'supplier3605/VERIFY.json': '21320da6b638366ccd42824e4b5865608f497cf2ba7323fffedb77f0a368c96a', 'supplier3605/check_residual.py': 'e34b06ae725f062d15ad83cbd3ef2f91d3d78c380ccc93c8d2deba1c9e354c70', 'supplier3605/check_scope.py': 'f8eefd425a0d570167e14febcacfbb38a6bb29d820d808be426180cf31b5a947', 'supplier3605/staged_pair.py': '25fc9b025dbb90358032013303adea650a5f19937fd3edf30b6c6fd023e2d747', 'supplier3605/verify.py': '0ef49b725fc132cd5fc26a9a81028739896232d938bae22cef132384c7cbab13'}
MATERIALIZER_SHA='b2a9e121c18abcf6a07024ef8938c1c461d15bb23756819ed78f28b18a759185'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--work',type=Path,required=True);a.add_argument('--allocation',type=Path);a.add_argument('--main-files',type=Path,default=HERE.parents[1]);a.add_argument('--t8-package',type=Path,required=True);a.add_argument('--materialize-only',action='store_true');x=a.parse_args()
 assert sha(x.t8_package/'materialize.py')==MATERIALIZER_SHA, 'materializer code before import'
 for name,h in ENTRY_INPUTS.items():assert sha(HERE/name)==h, 'entry dependency drift: '+name
 assert __debug__ and not sys.flags.optimize and not x.work.exists();work=x.work.resolve();work.mkdir()
 T8=x.t8_package.resolve();assert T8.name=='t8-rank7-two-swaps'
 old=work/'predecessor';m=module('pinned_t8_materialize',T8/'materialize.py');r=m.build(x.main_files.resolve(),T8/'MATERIALIZE.json',T8/'derived-overlay.tar.gz',old,RECIPE,OVERLAY)
 (work/'PREDECESSOR-MATERIALIZATION.json').write_text(json.dumps(r,indent=2)+'\n')
 assert sha(old/'adapters/extension_blocknorm.py')==STOCK_SHA, 'original unchanged stock checker'
 drivers=work/'driver-inputs';drivers.mkdir();shutil.copy2(old/'adapters/admit_extension.py',drivers/'admit_extension.py');shutil.copy2(HERE/'templates/prepare_extension_native.py',drivers/'prepare_extension_native.py')
 new=work/'changed';builder=module('staged_source_builder',HERE/'source_builder.py');builder.main(new,old/'source',HERE/'supplier3605',drivers,old/'native-cache',old/'NATIVE-RECEIPT.json')
 # Authenticate reused parent immediately; no changed-native claim from this check.
 prep=module('native_preparer',new/'prepare_extension_native.py');nr=read(old/'NATIVE-RECEIPT.json');assert sha(old/'NATIVE-RECEIPT.json')==prep.OLD_RECEIPT_SHA and prep.tree(old/'native-cache')==nr['cache_files']
 parent=new/'source/vendor/pr1297';prdir=old/'native-cache/_receipts'/prep.PARENT_SHA;pr=read(prdir/'RECEIPT.json')
 assert sha(parent/'MANIFEST.json')==prep.PARENT_SHA and prep.tree(parent,('MANIFEST.json',))==read(parent/'MANIFEST.json')
 assert sha(prdir/'RECEIPT.json')==nr['retained_parent_receipt_sha256']
 assert all(sha(prdir/name)==digest for name,digest in pr['files'].items())
 assert len(read(prdir/'STAGES.json'))==16 and all(s['exit_code']==0 for s in read(prdir/'STAGES.json'))
 status={'status':'PREPARED_STAGED_SOURCE_PARENT_BINDING_NOT_ADMITTED','manifest_sha256':sha(new/'source/MANIFEST.json'),'parent_reuse_receipt_sha256':sha(old/'NATIVE-RECEIPT.json')}
 (work/'PREPARED.json').write_text(json.dumps(status,indent=2)+'\n')
 if x.materialize_only:print(status['status']);return
 assert x.allocation is not None,'--allocation with literal FILL/ORDER/DISPATCH required'
 allocation=x.allocation.resolve();order=read(allocation/'ORDER.json');assert len(order)==4050 and set(map(tuple,order))=={(s,r)for s in range(9)for r in range(450)}
 fill=read(allocation/'FILL.json.gz');assert fill['columns']==['time','helper','owner_replica','child','port','offset'] and len(fill['rows'])==1652400
 assert not fill.get('dispatch_overrides',[]);fill['dispatch_overrides']=[];converted=work/'FILL-legacy.json.gz';converted.write_bytes(gzip.compress(json.dumps(fill,separators=(',',':')).encode(),mtime=0))
 assert read(converted)['rows']==read(allocation/'FILL.json.gz')['rows']
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONINTMAXSTRDIGITS='0')
 for key in ('PYTHONPATH','PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_RECORD','WITNESS_DISCOVER'):env.pop(key,None)
 stages=[]
 def run(name,command):
  with (work/(name+'.log')).open('w')as log:r=subprocess.run(command,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
  stages.append({'name':name,'command':command,'exit_code':r.returncode,'log_sha256':sha(work/(name+'.log'))});(work/'STAGES.json').write_text(json.dumps(stages,indent=2)+'\n');assert r.returncode==0,(name,work/(name+'.log'))
 run('fresh-native',read(new/'COMMANDS.json')['native'])
 cmd=[sys.executable,'-B',str(new/'admit_extension.py')]
 vals={'source':new/'source','fill':converted,'order':allocation/'ORDER.json','dispatch':allocation/'DISPATCH.json','native-cache':new/'native/native-cache','native-receipt':new/'native/NATIVE-RECEIPT.json','work':work/'admission','replica-helper-dir':old/'helpers','reconstructor':old/'helpers/reconstruct_replica.py','comparison-claim':old/'PR2969-CLAIM.json','blocknorm-checker':old/'adapters/extension_blocknorm.py'}
 for k,v in vals.items():cmd+=['--'+k,str(v)]
 cmd+=['--source-profile','staged3605','--comparison-profile','pr2969','--jobs','1'];run('full-admission',cmd)
 result=read(work/'admission/RESULT.json');assert result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'
 assert result['replicas']==450 and result['actual_expected_helpers']==408
 assert {int(k):v for k,v in result['profile'].items()}==PROFILE
 assert Fraction(result['kappa'])==EXPECTED_KAPPA,'frozen exact endpoint'
 assert Fraction(result['kappa'])>FRONTIER,'must beat reviewed latest3605, not merely inherited2969 comparison'
 (work/'RESULT.json').write_text(json.dumps({'status':'PASS_STAGED_WIDTH_T450_COMPLETE_RELEASE','kappa':result['kappa'],'baseline3605':str(FRONTIER),'gain3605':str(Fraction(result['kappa'])-FRONTIER),'release_receipt_sha256':sha(work/'admission/release/RELEASE-RECEIPT.json'),'stages':stages},indent=2)+'\n');print('PASS_STAGED_WIDTH_T450_COMPLETE_RELEASE')
if __name__=='__main__':main()
