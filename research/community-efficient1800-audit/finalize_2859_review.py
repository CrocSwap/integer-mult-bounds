from pathlib import Path
import json,hashlib,subprocess,shutil
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'combined-2859';A=R/'research/community-efficient1800-audit'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pk=json.loads((P/'packets/2859.json').read_text());live=json.loads((P/'live-2859-final.json').read_text());assert live['headRefOid']==pk['head'] and live['state']=='OPEN' and not live['isDraft']
passed=['science','completion','records','snapshot','legacy-v2'];evidence=[]
for slug in passed:
 f=P/f'check-2859-{slug}.json';c=json.loads(f.read_bytes());assert c['status']=='passed' and not c['changed_files_after'];assert sha(P/f'check-2859-{slug}.log')==c['log_sha256'];assert len(c['commands'])==c['commands_expected']
 evidence.append(dict(path=f.name,sha256=sha(f),coverage='All declared commands pass'))
# Retain earlier failed fixture attempts honestly; reuse only individually passed commands.
for slug,count in [('tooling',3),('legacy',2)]:
 f=P/f'check-2859-{slug}.json';c=json.loads(f.read_bytes());assert not c['changed_files_after'];assert sha(P/f'check-2859-{slug}.log')==c['log_sha256'];assert all(x['exit_code']==0 and not x['stop_reason'] for x in c['commands'][:count]);assert c['commands'][count]['exit_code']!=0
 evidence.append(dict(path=f.name,sha256=sha(f),coverage=f'Only first {count} passing commands reused. Later fixture/discovery failure is retained, corrected and checked separately.'))
for name in ['provenance-2859-science-sources.json','provenance-2859-historical-snapshots.json','provenance-2859-derived-receipts.json','provenance-2859-ledger-prefix.json','finding-2859-candidate-source-gates.json']:
 evidence.append(dict(path=name,sha256=sha(P/name)))
paths=sorted({f['path'] for f in pk['files']}|{'tests/test_isolated_historical_completion.py'})
inputs={rel:sha(D/rel) for rel in paths}
# Every changed executable in the candidate is covered by a passing local receipt.
receipts=[json.loads((P/f'check-2859-{slug}.json').read_bytes()) for slug in passed+['tooling','legacy']]
for rel in paths:
 if rel.endswith('.py') and not rel.startswith('scripts/historical-ci-inputs/'):
  assert any(c['input_sha256'].get(rel)==inputs[rel] for c in receipts),rel
coverage=[]
for item in pk['files']:
 rel=item['path'];category=('scoped mathematical note and exact symbolic/physical replay' if rel.startswith('research/phase-order-bank-audit/') else 'immutable historical dependency and exact source authentication' if rel.startswith('scripts/historical-ci-inputs/') else 'existing exact-head Linux regeneration with complete unchanged receipt inputs' if rel.endswith(('joint-dual-validation.json','skip-frame-validation.json','frame-certificate.json')) else 'workflow routing retains original commands, immutable baselines, and clean-tree gates' if rel.startswith('.github/') else 'reviewed tooling and source-bound relevant local controls')
 coverage.append(dict(path=rel,source_oid=item['source']['oid'],candidate_sha256=inputs[rel],review=category))
finding=dict(number=2859,head=pk['head'],status='reviewed',coverage=coverage,evidence=evidence,limitations=['No local Lean or Docker run.','No new selected-supplier cold replay or full multiplication-theorem verification.','Hosted matrix is on exact author head, not the composed integration head. Reused mathematical evidence is restricted to byte-identical inputs.','Complete historical archived-ledger execution was observed on author-head hosted CI; local newer ledger validation covers its full current decision/source-hash prefix and mutation tests.','No new kappa or benchmark speedup claim.'],integration_changes=['Retain current PR2579 completion receipts, assertion and cancellation safeguards across all seven historical routes.','Retain efficient1800 authoritative ledger decisions.','Authenticate exact current and composed runner/test successors; retain immutable predecessor snapshots.','Add all-route actual-child completion and early-exit controls.'])
(P/'finding-2859-final-review.json').write_text(json.dumps(finding,indent=2)+'\n')
log=(json.dumps(finding,indent=2)+'\n').encode();(P/'check-2859.log').write_bytes(log)
(P/'check-2859.json').write_text(json.dumps(dict(number=2859,head=pk['head'],status='passed',seconds=0,scope='Review completion receipt; execution time is recorded in the separately retained component receipts. All 55 author files reviewed, plus current all-route completion adaptation. No fresh full Linux or Lean run claimed.',commands=[],commands_expected=0,input_sha256=inputs,changed_files_after={},log_sha256=hashlib.sha256(log).hexdigest(),evidence=evidence),indent=2)+'\n')
# Bank reproducer code and independently queried hosted run records with local findings.
for pattern in ['run_2859_*.py','hydrate_2859_*.py','check_2859_*.py','hosted-2859-*.json','resolve_2859_candidate.py','prepare_2859_candidate.py','finalize_2859_review.py']:
 for f in P.glob(pattern):shutil.copy2(f,A/f.name)
print('Complete changed-file review:',len(coverage),'author files,',len(inputs),'integration inputs')
