"""Fresh standalone replay of four promotions, 72 cold ends and a literal integer owner assignment.

Python 3.11+, standard library only; no optimizer, network, or reused output.
Pinned historical baseline inputs are checked against a fresh ancestral replay.
"""
import argparse,gzip,hashlib,json,os,subprocess,sys,time
from pathlib import Path
assert __debug__, 'Assertions are required; do not use -O'
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=Path,required=True);a=ap.parse_args();O=a.work.resolve()
assert not O.exists() and not O.is_relative_to(P),'Use a new output directory outside the package'
read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=read(P/'MANIFEST.json');actual={f.relative_to(P).as_posix():sha(f)for f in P.rglob('*')if f.is_file()and f!=P/'MANIFEST.json'and '__pycache__'not in f.parts};assert actual==manifest,'package manifest'
for row in read(P/'provenance/SOURCE-FILES.json'):assert sha(P/row['path'])==row['sha256'],'vendored source pin '+row['path']
MAIN=P/'vendor/main';PR635=P/'vendor/pr635';S=MAIN/'research/complex-k492-owner-repair/vendor/multicold';B=S/'vendor/pr558';F=B/'vendor/pr552';V=F/'complex-global/vendor531';ROUTING=F/'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
O.mkdir(parents=True);start=time.monotonic();stages=[]
env=dict(os.environ,MULTICOLD_SOURCE=str(S),GAIN_PR564_SOURCE=str(S),PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',PYTHONUTF8='1');env.pop('PYTHONOPTIMIZE',None);env.pop('WITNESS_DISCOVER',None);env.pop('WITNESS_RECORD',None)
def dump(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
def run(name,script,*args):
 t=time.monotonic();log=O/(name+'.log');cmd=[sys.executable,'-B',str(S/'code/run_portable.py'),str(script),*map(str,args)];print('RUN',name,flush=True)
 with log.open('w',encoding='utf-8')as stream:r=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT,env=env)
 stages.append(dict(name=name,exit_code=r.returncode,seconds=time.monotonic()-t,log_sha256=sha(log)));dump(O/'STAGES.json',stages)
 if r.returncode:raise RuntimeError(name+' failed\n'+log.read_text()[-8000:])
 print('PASS',name,flush=True)
run('ancestral558-fresh',B/'verify.py','--work',O/'ancestral558')
# Exact semantic linkage to the historical baseline consumed by unchanged global admission.
fresh=O/'ancestral558';frozen=MAIN/'research/community-k492-audit/pr622/replay/baseline558';linked=[]
for rel in read(P/'data/UPSTREAM-PINS.json'):
 prefix='research/community-k492-audit/pr622/replay/baseline558/'
 if not rel.startswith(prefix):continue
 name=rel[len(prefix):];x=read(fresh/name);y=read(frozen/name)
 if name.endswith(('SCALAR-FRAME-AUDIT.json','CLIFFORD-REVIEW.json')):
  x.pop('seconds',None);y.pop('seconds',None)
 elif name.endswith('/INTEGRATION.json'):
  assert x['exact_phase_receipt_sha256']==sha(fresh/'complex-global/base/split-centres/CLIFFORD-REVIEW.json')
  assert y['exact_phase_receipt_sha256']==sha(frozen/'complex-global/base/split-centres/CLIFFORD-REVIEW.json')
  x.pop('exact_phase_receipt_sha256');y.pop('exact_phase_receipt_sha256')
 assert x==y,'fresh ancestral semantic mismatch '+name
 linked.append(dict(path=name,fresh_sha256=sha(fresh/name),pinned_sha256=sha(frozen/name)))
dump(O/'ANCESTRAL-LINK.json',dict(status='PASS_FRESH_ANCESTRAL_INPUTS_MATCH_PINNED_BASELINE',files=linked,scope='Only elapsed seconds and their validated phase-receipt hash are normalized; all mathematical data match.'))
run('gauge44-exact-construction',P/'construction/reproduce.py','--main',MAIN,'--pr635',PR635,'--out',O/'gauge44','--until','word')
run('notri56-construction',P/'construction/notri/reproduce_notri.py','--main',MAIN,'--pr635',PR635,'--word-dir',O/'gauge44','--out',O/'notri56','--word-only')
run('notri-control-g44',P/'construction/notri/reproduce_notri.py','--main',MAIN,'--pr635',PR635,'--word-dir',O/'gauge44','--out',O/'notri-control','--control-g44')
run('layered66-construction',P/'construction/layers_np/reproduce_np.py','--main',MAIN,'--pr635',PR635,'--notri-dir',O/'notri56','--hamming',O/'gauge44/hamming','--out',O/'layered66','--skip-phases')
run('cold72-exact-construction',P/'local/build_cold_end.py','--input',O/'layered66/hpe/FULL-WORD.json.gz','--recipe',P/'data/COLD72-RECIPE.json.gz','--out',O/'cold72')
run('four-promotions',P/'construction/promo/build_promotion.py','--input',O/'cold72/FULL-WORD.json.gz','--recipe',P/'data/PROMO4-RECIPE.json','--out',O/'promoted')
run('promotion-controls',P/'construction/promo/promo_controls.py','--input',O/'cold72/FULL-WORD.json.gz','--recipe',P/'data/PROMO4-RECIPE.json','--audit',P/'independent/audit_local.py','--out',O/'PROMO-CONTROLS.json')
W=O/'promoted/FULL-WORD.json.gz';L=O/'local'
run('all728-columns-native',P/'local/hpe_audit_and_transport.py','--raw',W,'--routing',ROUTING,'--out',L)
run('both-native-ledgers',P/'local/hpe_emit_local.py',L)
run('independent-native-controls',P/'local/hpe_audit_local.py',L)
run('residual-wrappers',P/'local/hpe_adapters_local.py',L/'CANONICAL-WORD.json.gz',L/'RESIDUAL-ADAPTERS.json',L/'WRAPPER-CHECKS.json')
run('all-native-phase-edges',B/'code/phases_full.py',L,V/'vendor/clifford')
run('independent-scalar-frames-cones',P/'independent/audit_local.py','--word',W,'--main',MAIN,'--output',O/'INDEPENDENT-LOCAL.json')
run('inherited-cold-controls',P/'local/cold_end_controls.py',W,ROUTING,O/'cold-controls')
run('six-end-controls',P/'extras/focused_controls.py','--word',W,'--out',O/'focused-controls')
run('owner-construction-controls',P/'extras/replay_owner_map.py','--out',O/'RECONSTRUCTED-OWNERS.json.gz','--controls',O/'OWNER-CONSTRUCTION-CONTROLS.json')
run('strict-global-admission',P/'verify_global.py','--main',MAIN,'--local',L,'--work',O/'global-replay')
run('independent-literal-map-moment',P/'extras/check_owner_map.py','--work',O/'global-replay','--provider','gauge44='+str(L),'--out',O/'INDEPENDENT-MAP.json')
run('independent-two-engine-outer47',P/'independent/price_profile.py','--main',MAIN,'--profile',O/'global-replay/global/PLAN.json','--output',O/'INDEPENDENT-PRICE.json')
assembly=read(O/'global-replay/ASSEMBLY.json');price=read(O/'INDEPENDENT-PRICE.json');spec=read(P/'data/SPEC.json')
assert assembly['kappa']==spec['expected']['kappa']==read(O/'INDEPENDENT-MAP.json')['kappa']==price['prices']['native']['outer_with_bit']['kappa']
assert len(read(O/'layered66/swap/PIVOT-SWAP.json')['negative_controls_rejected'])==30
assert len(read(O/'layered66/controls/COLD-END-CONTROLS.json')['rejected'])==59
assert len(read(O/'focused-controls/CONTROLS.json')['rejected'])==30
assert len(read(O/'cold-controls/COLD-END-CONTROLS.json')['rejected'])==59
assert len(read(O/'OWNER-CONSTRUCTION-CONTROLS.json')['rejected'])==7
assert len(read(O/'global-replay/ADMISSION-CONTROLS.json')['rejected_controls'])==69
assert len(read(O/'global-replay/BIT-SUPPLIER-CONTROLS.json')['rejected_controls'])==12
assert read(O/'PROMO-CONTROLS.json')['rejected']==11
assert read(O/'OWNER-CONSTRUCTION-CONTROLS.json')['idle']==read(P/'data/EXPECTED-IDLE.json')
result=dict(status='PASS_FRESH_LAYERED_COLD72_COMPLETE_NATIVE_OWNER_AND_EXACT_GLOBAL_REPLAY',kappa=assembly['kappa'],kappa_decimal=assembly['kappa_decimal'],complex_lower=assembly['complex_lower'],bit_lower=assembly['bit_lower'],profile=assembly['complex_profile'],seconds=time.monotonic()-start,reused=False,scope='Finite conditional witness. Fresh ancestor, gauge44 exact recipe, no-triangle construction and gauge44 control, six-pivot layered word and changed72-cold-end word, four entrance-promotion groups, native scalar/phases/wrappers, physical owner map and strict finite/outer admission. PR589 bit supplier is cited and repriced; its separate bit-circuit replay is not run by this command. All-size realization and analytic transfer remain assumptions.')
dump(O/'RESULT.json',result)
files=['RESULT.json','ANCESTRAL-LINK.json','STAGES.json','INDEPENDENT-LOCAL.json','INDEPENDENT-MAP.json','INDEPENDENT-PRICE.json','RECONSTRUCTED-OWNERS.json.gz','OWNER-CONSTRUCTION-CONTROLS.json','focused-controls/CONTROLS.json','cold-controls/COLD-END-CONTROLS.json','PROMO-CONTROLS.json','promoted/FULL-WORD.json.gz','cold72/COLD-END-CONSTRUCTION.json','cold72/FULL-WORD.json.gz','gauge44/STEPS.json','notri56/STEPS.json','notri56/cold44/CONSTRUCTION.json','notri-control/STEPS.json','layered66/STEPS.json','layered66/swap/PIVOT-SWAP.json','layered66/controls/COLD-END-CONTROLS.json','global-replay/REPLAY.json','global-replay/ASSEMBLY.json','global-replay/STAGES.json','global-replay/ADMISSION-CONTROLS.json','global-replay/BIT-SUPPLIER-CONTROLS.json','global-replay/global/audit/OWNERS-AND-PROFILE.json','global-replay/global/audit/PREFIX-AND-INVOICE.json','global-replay/global/audit/ASYNC-AUDIT.json']
files += ['local/'+f.name for f in L.iterdir()if f.is_file()]
dump(O/'RECEIPT.json',dict(status=result['status'],manifest_sha256=sha(P/'MANIFEST.json'),spec_sha256=sha(P/'data/SPEC.json'),stages=stages,artifacts={rel:sha(O/rel)for rel in files}))
print('PASS',result['kappa_decimal'],flush=True)
