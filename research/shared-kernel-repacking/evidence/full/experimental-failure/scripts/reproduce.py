# SPDX-License-Identifier: Apache-2.0
"""Portable source derivation, two fresh native chains and full outer release.
Yiyang (@Lyy-iiis), with substantial OpenAI Codex assistance.
Unchanged retained native/parent evidence is explicitly reused by full-tree hashes.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
from fractions import Fraction as Q
import argparse,hashlib,json,os,subprocess,time
HERE=Path(__file__).resolve().parent
SCRIPT_PINS={
 'build_overlay.py':'4c83a251a03045144608456e6b3bdbcced9255ce7c2d89f7039e766972100666',
 'prepare_shared_native.py':'9d86bf49f6aec1d4f671a5d060815e97cb470151221a29fba736e91f06c74b07',
 'admit_shared_replica.py':'a8781eb619ba7584b5e193de0e9d766c245f7fcd3bfb6a799ebc92aff2d5e329',
}
HELPER_PINS={
 'lift_parent.py':'9a1edd7d4ab4a2f2ac8d15b42b7e40f93653d65026bac59e4c1ce80b486bd60e',
 'replica_parent.py':'48bdbf28f59d80edb266803ec61bf5e22e8fb5e5a0e2b88004b6039147589bd4',
 'reconstruct_replica.py':'5472811c24aef3852dc7e189dff5060076a6c0b25bfde928da50dcfe9b5bdc15',
 'blocknorm_certificate.py':'e5bfbad8e8e6cb4206f7ba92d333780f423918d8f217b474302346169e991f92',
}
WORD_PINS={'base':'001b14314d8db873d4d80826d4af9c40a3e5a1fecde743e5a26391bdf673f458','extra':'bc5bfe51178f0c3312d28318412ec490463c896ceed0660b9c443fcb76496546'}
CANDIDATE_PINS={'fill': '82218aaaf08825bd4a3cca676815c7e9c00d06d0da123b1c5ad234c8c91cb501', 'order': '84f030a59dde4fa4635988ef0931ebae66964b3a202df79d38247fbe8a5592dc', 'dispatch': '5513481a70c83767b5836b15fb7ff204d2a8f8fca83c6bcaee90a20b3d1ec6c4'}
EXPECTED_KAPPA='17200966286848326009719999999999999999999998999999999999999999999999/10000000000000000000000000000000000000000000000000000000000000000000000'
GENERATOR_SHA='b3241527e6c136dc4b54975ef401c49d452bd6159fb99030accaf095c8fbd3ed'
REVIEW_SHA='5b323e50fb5a10ac088472b3e085b54d7d2ae3a29f8552ff44b788a984eb97d1'
COMPARISON_SHA='aceb1394b3e8f3abcc9b1a0dc82756ab937ffbefc2f37305a229a00ccc5137e9'
SOURCE_SHA='c8ec4d1b7be08d2ad30730a07392ad9cb6d0222f2c35bef43c9a80a39b16e41f'
OVERLAY_SHA='54dc42f25c1d8b85adcf593c4bf6c0f83f7351388af857812790b8a0b4c3d869'
def need(ok,why):
 if not ok:raise ValueError(why)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def tree(p):
 need(not list(p.rglob('__pycache__')) and not list(p.rglob('*.pyc')),'no bytecode or cache dirs in immutable source')
 out={}
 for f in sorted(p.rglob('*')):
  need(not f.is_symlink(),'no source symlinks')
  if f.is_file()and f!=p/'MANIFEST.json':out[f.relative_to(p).as_posix()]=sha(f)
 return out

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for n in ['source','words','fill','order','dispatch','retained-cache','retained-receipt','comparison-claim','comparison-latest-claim','work']:ap.add_argument('--'+n,type=Path,required=True)
 ap.add_argument('--generator',type=Path,default=HERE/'shared_kernel.py');ap.add_argument('--review',type=Path,default=HERE/'review_four_groups.py');ap.add_argument('--helper-dir',type=Path,default=HERE/'vendor/pr2839');ap.add_argument('--jobs',type=int,choices=range(1,5),default=4);a=ap.parse_args()
 for name,value in vars(a).items():
  if isinstance(value,Path):setattr(a,name,value.resolve())
 need(not sys.flags.optimize,'assertions enabled');source=a.source.resolve();work=a.work.resolve()
 need(not work.exists()and not work.is_relative_to(source)and not source.is_relative_to(work),'fresh work external to source')
 need(not work.is_relative_to(HERE)and not HERE.is_relative_to(work),'fresh work external to replay package')
 need(sha(source/'MANIFEST.json')==SOURCE_SHA and tree(source)==read(source/'MANIFEST.json'),'complete original PR2833 source')
 files={}
 def bind(p,expected):
  p=p.resolve();need(sha(p)==expected,'pinned input '+str(p));files[str(p)]=expected
 for n,h in SCRIPT_PINS.items():bind(HERE/n,h)
 for n,h in HELPER_PINS.items():bind(a.helper_dir/n,h)
 for tag,h in WORD_PINS.items():bind(a.words/('WORD-'+tag+'.json.gz'),h)
 for n,h in CANDIDATE_PINS.items():bind(getattr(a,n),h)
 bind(a.generator,GENERATOR_SHA);bind(a.review,REVIEW_SHA);bind(a.comparison_claim,COMPARISON_SHA)
 bind(a.retained_receipt,'a56d2fe28812e93c5526564ef77f7e5e8d1cbb111efeb6c3b0f53c9ec01ca2bc')
 bind(a.comparison_latest_claim,'eb3260be191774b931cff6e562978a2af27bbc6ff666ca8c1d387a2b18dc86fa')
 latest=read(a.comparison_latest_claim);need(Q(latest['kappa'])==Q(latest['kappa_rational'])and Q(EXPECTED_KAPPA)>Q(latest['kappa_rational']),'exact improved target beats concurrent PR2853 full outer headline')
 source_before=tree(source);work.mkdir(parents=True);overlay=work/'source';native=work/'native';candidate=work/'candidate'
 commands=[('derive-source',[sys.executable,'-B',str(HERE/'build_overlay.py'),'--source',str(source),'--generator',str(a.generator),'--review',str(a.review),'--candidate-dir',str(a.words),'--out',str(overlay)]),
 ('fresh-current-native',[sys.executable,'-B',str(HERE/'prepare_shared_native.py'),'--source',str(overlay),'--retained-cache',str(a.retained_cache),'--retained-receipt',str(a.retained_receipt),'--out',str(native),'--jobs',str(min(a.jobs,2))]),
 ('complete-admission',[sys.executable,'-B',str(HERE/'admit_shared_replica.py'),'--source',str(overlay),'--fill',str(a.fill),'--order',str(a.order),'--dispatch',str(a.dispatch),'--native-cache',str(native/'native-cache'),'--native-receipt',str(native/'NATIVE-RECEIPT.json'),'--work',str(candidate),'--replica-helper-dir',str(a.helper_dir),'--reconstructor',str(a.helper_dir/'reconstruct_replica.py'),'--blocknorm-checker',str(a.helper_dir/'blocknorm_certificate.py'),'--comparison-claim',str(a.comparison_claim),'--source-profile','shared-four','--comparison-profile','pr2848','--jobs',str(a.jobs)])]
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 for n in ['PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_DISCOVER','WITNESS_RECORD']:env.pop(n,None)
 stages=[];start=time.monotonic()
 for name,cmd in commands:
  log=work/(name+'.log');begin=time.monotonic()
  with log.open('w')as f:r=subprocess.run(cmd,cwd=work,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT)
  stages.append(dict(stage=name,command=cmd,exit_code=r.returncode,log_sha256=sha(log),seconds=time.monotonic()-begin));write(work/'STAGES.json',stages)
  need(r.returncode==0,'failed '+name+'; '+str(log));print('PASS',name,flush=True)
  need(all(sha(Path(p))==h for p,h in files.items()),'bound replay input drift')
 result=read(candidate/'RESULT.json');release=read(candidate/'release/RELEASE-RECEIPT.json');nrec=read(native/'NATIVE-RECEIPT.json')
 need(result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'and release['status']=='PASS_RELEASE','complete release statuses')
 need(Q(result['kappa'])==Q(release['kappa_decimal'])==Q(EXPECTED_KAPPA),'exact expected headline')
 need(result['release_receipt_sha256']==sha(candidate/'release/RELEASE-RECEIPT.json')and result['package_manifest_sha256']==release['manifest_sha256']==sha(candidate/'package/MANIFEST.json'),'strict release chain')
 need(sha(overlay/'MANIFEST.json')==OVERLAY_SHA and tree(overlay)==read(overlay/'MANIFEST.json'),'unchanged exact derived source')
 need(tree(source)==source_before and sha(source/'MANIFEST.json')==SOURCE_SHA,'unchanged original source')
 need(nrec['fresh_current_provider_count']==2 and nrec['reused_retained_native_count']==2 and nrec['reused_retained_parent']is True,'accurate fresh/reused native provenance')
 final=dict(status='PASS_SHARED_KERNEL_PORTABLE_COMPLETE_REPLAY',kappa=result['kappa'],kappa_decimal=result['kappa_decimal'],gain=result['gain'],source_manifest_sha256=SOURCE_SHA,derived_source_manifest_sha256=OVERLAY_SHA,source_derivation_sha256=sha(work/'source-DERIVATION.json'),native_receipt_sha256=sha(native/'NATIVE-RECEIPT.json'),candidate_result_sha256=sha(candidate/'RESULT.json'),release_receipt_sha256=sha(candidate/'release/RELEASE-RECEIPT.json'),generated_package_manifest_sha256=result['package_manifest_sha256'],fresh_current_native_chains=2,reused_retained_native_chains=2,reused_retained_parent=True,wrapper_sha256=sha(Path(__file__)),input_sha256=files,stages=stages,seconds=time.monotonic()-start,scope='Conditional finite supplier and modern outer release; unchanged inherited all-size/compiler/hosting/precision/tape/analytic obligations remain. Two changed providers run fresh; retained provider/parent proof explicitly reused by full-tree hashes.')
 need(Q(result['kappa'])>Q(latest['kappa_rational']),'actual full release beats exact concurrent headline')
 final['secondary_comparison']=dict(pr=2853,head='d01045dfb67428679618027dff552f1d032fa999',claim_sha256=sha(a.comparison_latest_claim),field='kappa_rational',gain=str(Q(result['kappa'])-Q(latest['kappa_rational'])),approx_gain=float(Q(result['kappa'])-Q(latest['kappa_rational'])))
 write(work/'RESULT.json',final);print(final['status'],final['kappa_decimal'],flush=True)
if __name__=='__main__':main()
