"""Full finite native/signed/geometry replay; Apache-2.0, OpenAI Codex assistance."""
import pathlib,sys,subprocess,shutil,json,hashlib,gzip,os
P=pathlib.Path(__file__).resolve().parent
if not __debug__:raise SystemExit('Assertions required')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rd=lambda p:json.loads(p.read_text())
manifest=rd(P/'SOURCE-MANIFEST.json')
for n,h in manifest['files'].items():assert sha(P/n)==h,n
D=P/'derived';D.mkdir(exist_ok=True)
W=D/'replay';shutil.copytree(P/'evidence',W,dirs_exist_ok=True)
F=W/'experiments/stage-search/pr441-signed-retime/full';B=F/'bit426-source-centres';S=W/'experiments/stage-search/pr441-signed-retime/signed';K=W/'experiments/bit-search/pr434/source/research/e8-early-reset-kernel'
E=rd(P/'EXPECTED.json')
def run(name,args,cwd=P):
 with (D/(name+'.log')).open('w')as o:subprocess.run([sys.executable,'-B',*map(str,args)],cwd=cwd,stdout=o,stderr=subprocess.STDOUT,check=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
run('source-bound-A-retiming-transfer',[W/'experiments/stage-search/pr440-signed-retime/transfer.py'])
run('source-bound-retiming-transfer',[F.parent/'transfer.py'])
assert sha(F.parent/'word.json')==E['transfer_candidate_sha256']
assert len(rd(F.parent/'TRANSFER.json')['moves'])==E['retimings']
assert len(rd(W/'experiments/stage-search/pr440-signed-retime/TRANSFER.json')['moves'])==E['retimings_A']
algebra=D/'algebra'
if algebra.exists():shutil.rmtree(algebra)
run('exact-relations-five-controls',[W/'experiments/stage-search/pr436-integer-kernel/reconstruct.py',F.parent/'baseline.json',F.parent/'SELECTION.json',algebra])
assert sha(algebra/'word.json')==E['transfer_candidate_sha256']
assert len(rd(algebra/'RECEIPT.json')['controls'])==5
run('export-native',[W/'experiments/bit-search/pr434/source/research/split-centres-global/vendor/export_records.py',B/'bit-source-centres.json',B/'records'])
assert sha(B/'records/249-records.bin')==E['native_record_sha256']
run('native-source-spans',[K/'source_span.py',B/'bit-source-centres.json',B/'records/frames.json'])
run('native-global',[F/'adapted/bit_global.py','--source',B,'--local-check',B,'--out',B/'global'],F)
run('native-bank-audit',[F/'adapted/bit_audit.py','--local-check',B,'--out',B/'global'],F)
g=rd(B/'global/GLOBAL.json');a=rd(B/'global/AUDIT.json')
for key,expected in [('live',E['live']),('physical',E['physical']),('local_invocations',E['calls']),('bank_assignments',E['placements']),('banks_per_stage',E['banks_per_stage']),('entrance_rank_total',E['entrance_rank']),('profile',E['profile'])]:assert g[key]==expected,key
assert 64*g['live']-g['rank_mass']==E['actual_deficit']
assert len(a['mutations_rejected'])==E['native_bank_controls']
assert len(g['omitted_bridge_shears_rejected'])==E['native_bridge_controls']
run('signed-local',[S/'signed_source.py'])
r=rd(S/'RESULT.json');assert sha(S/'signed-records.bin')==E['signed_record_sha256'];assert len(r['controls'])==E['signed_controls'];assert r['integer_kernel']['all_positive_start_responses_zero_over_Z']
assert sha(F.parent/'word.json')==E['transfer_candidate_sha256']
run('signed-complete-prefix-invoice',[S/'bound.py'])
b=rd(S/'GLOBAL-BOUND.json');assert b['finite']==E['finite']
# Frozen arithmetic closure is checked separately: timing/path-dependent native receipts
# are deliberately not substituted into frozen byte hashes.
run('composition',[P/'compose.py','--complex',P/'evidence/experiments/stage-search/pr433-split/full','--bit',P/'evidence/experiments/stage-search/pr441-signed-retime/signed','--native-bit',P/'evidence/experiments/stage-search/pr441-signed-retime/full','--engines',P/'evidence/experiments/bit-search/pr433/source/research/split-centres-global/vendor/engines'])
c=rd(D/'REFINED-ASSEMBLY.json');assert c['kappa']==E['kappa'];assert len(c['bootstrap_chain'])-1==E['continuations'];assert c['adjacent_grid_rejected']and c['complex_leaf_cap_rejected']
result=dict(status='PASS_SOURCE_CLOSED_NATIVE_SIGNED_GEOMETRY_AND_REFINED_FINITE_RELEASE',kappa=E['kappa'],source_manifest_sha256=sha(P/'SOURCE-MANIFEST.json'),actual_deficit=E['actual_deficit'],frozen_native_reported_deficit=g['deficit'],native_metadata_correction='Frozen GLOBAL.deficit is inherited stale metadata; exact T64 rank-mass subtraction checked and all price uses actual deficit.',native_bank_controls=8,native_bridge_controls=18,signed_controls=9,scope=E['scope'])
(D/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps(result,indent=2))
