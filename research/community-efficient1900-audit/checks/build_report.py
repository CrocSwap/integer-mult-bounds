from pathlib import Path
import json,shutil,hashlib,collections
P=Path('/tmp/pr-efficient1900');R=Path('/tmp/integer-mult-efficient1100-20261015');A=R/'research/community-efficient1900-audit';A.mkdir(parents=True,exist_ok=True)
sel=json.loads((P/'selection.json').read_text());ledger=json.loads((R/'docs/research/pr-ledger.json').read_text());old={x['number']:x for x in ledger['pull_requests']};states=json.loads((P/'integration-state.json').read_text()) if (P/'integration-state.json').exists() else {};ready=json.loads((P/'ready-scopes.json').read_text()) if (P/'ready-scopes.json').exists() else {}
# Sparse merges can remove unchanged historical ledger inputs. Restore only missing bytes.
import subprocess
for rel in list(ledger['source_sha256'])+['research/pr-reconciliation-20261012/starting-snapshot.json']:
 f=R/rel
 if not f.exists():
  f.parent.mkdir(parents=True,exist_ok=True)
  f.write_bytes(subprocess.check_output(['git','show','HEAD:'+rel],cwd=R))
shutil.copytree(P/'packets',A/'packets',dirs_exist_ok=True);shutil.copy2(P/'selection.json',A/'SELECTION.json');shutil.copy2(P/'live-snapshot.json',A/'LIVE-SNAPSHOT.json');(A/'checks').mkdir(exist_ok=True)
for pat in ['check-*.json','check-*.log','provenance-*.json','finding-*.json','run_2921.py','run_2906.py','run_2906_supplement.py','prepare_2906.py','baseline_2906.py','hydrate_2906.py','extract_native_group.py','prepare_native_inputs.py','run_native_group.py','run_native_traffic_stock.py','authenticate_native_exports.py','register_native_group.py','extract_structural_group.py','prepare_structural_inputs.py','run_structural_group.py','authenticate_structural_references.py','register_structural_group.py','prepare_numerical_inputs.py','run_numerical_group.py','authenticate_numerical_exports.py','run_navigation_followup.py','diagnose_2904_positions.py','run_position_diagnostic.py','position-audit-2904-*.json','register_numerical_group.py','review-holds.json','diagnose_fstar_group.py','prepare_cover_inputs.py','run_cover_group.py','live-fstar-cover.json','diagnose_cover_profiles.py','register_cover_review.py','run_blocus.py','review_workflow_928.py','closed-superseded.json','register_blocus_review.py','preflight-2830.json','integrate_plain.py','process_tree_watch.py','test_process_tree_watch.py','diagnose_twin_fold.py','prepare_evidence1007.py','run_evidence1007.py','register_evidence1007.py','run_drift2255.py','prepare_drift2255_stream.py','run_drift2255_stream.py','register_drift2255.py','preflight-2255.json','extract_native_continuation.py','prepare_native_continuation.py','run_native_continuation.py','authenticate_native_continuation.py','prepare_catalogue2915_stream.py','run_native2915_stream.py','register_native_continuation.py','register_native2899.py','register_native2915.py','preflight-native-continuation.json','prepare_h6_review.py','run_h6_review.py','check_h6_selected.py','prepare_echo_review.py','run_echo_review.py','register_h6_echo.py','live-open-sixth-refresh.json','live-sixth-classification.json','run_lines_review.py','resolve_lines_review.py','register_lines_review.py','archive_intake.py','configure_archive_intake.py','register_archive_intake.py','archive-intake.json','live-open-eighth-refresh.json','external-closure-*.json','archive-index-optimization.json']:
 for f in P.glob(pat):shutil.copy2(f,A/'checks'/f.name)
if (P/'combined-2906/tests/test_exit_cleanup_macos.py').exists():shutil.copy2(P/'combined-2906/tests/test_exit_cleanup_macos.py',A/'checks/test_exit_cleanup_macos.py')
archives=json.loads((P/'archive-intake.json').read_text()) if (P/'archive-intake.json').exists() else {}
holds=json.loads((P/'review-holds.json').read_text()) if (P/'review-holds.json').exists() else {}
closed=json.loads((P/'closed-superseded.json').read_text()) if (P/'closed-superseded.json').exists() else {}
rows=[]
for item in sel['prs']:
 n=item['number'];meta=json.loads((P/f'{n}.json').read_text());pk=json.loads((P/'packets'/f'{n}.json').read_text());prior=old.get(n,{});same=prior.get('reviewed_head')==pk['head'];accepted=str(n) in ready;state=states.get(str(n));published=state is not None and state['state']=='MERGED'
 question=prior.get('unresolved_question') if same else None
 if not question:question=('Revised head: compare against the prior reviewed source and complete affected review/replay obligations.' if prior else 'Review the complete changed-file inventory and claim scope; authenticate dependencies and finish declared checks before incorporation.')
 scope=ready[str(n)] if accepted else ('Carry forward prior unresolved obligations; this pass authenticates current metadata and the complete Git diff, not the mathematical claim.' if same else 'Exact-head metadata and complete Git-diff inventory only; substantive review and verification remain pending.')
 if str(n) in holds and not accepted:question=holds[str(n)]['question'];scope=holds[str(n)]['scope']
 rows.append(dict(number=n,metadata={k:meta[k] for k in ('number','title','author','headRefOid','isDraft')},reviewed_head=pk['head'],current_head=pk['head'],prior_reviewed_head=prior.get('reviewed_head'),disposition='incorporated' if published else 'partially_reviewed',github_state='MERGED' if published else 'OPEN',integration_location=list(pk['path_groups']) if published else [],unresolved_question=None if published else 'Reviewed; publication pending.' if accepted else question,closure=dict(kind='merged',merge_commit=state['mergeCommit']['oid'],url=meta['url']) if published else None,scope=scope,ready_to_integrate=accepted,review_completion=dict(changed_file_coverage=accepted,scoped_mechanism_review=accepted,required_execution_complete=accepted,published=published),verification_evidence=list(dict.fromkeys(prior.get('verification_evidence',[])+[f'research/community-efficient1900-audit/packets/{n}.json']+[f'research/community-efficient1900-audit/checks/{f.name}' for f in sorted(P.glob(f'check-{n}*.json'))]))))
for row in rows:
 archive=archives.get(str(row['number']))
 if archive:
  published=row['github_state']=='MERGED'
  row.update(disposition='partially_reviewed',scope=archive['scope'],unresolved_question=archive['remaining'],review_completion=dict(changed_file_coverage=True,scoped_mechanism_review=False,required_execution_complete=False,published=published))
  if published:row['closure']['kind']='merged_for_archive_only'
  row['verification_evidence']=list(dict.fromkeys(row['verification_evidence']+['research/community-efficient1900-audit/checks/check-archive-intake.json']))
for row in rows:
 external=P/f'external-closure-{row["number"]}.json'
 if external.exists() and row['github_state']=='OPEN':
  observation=json.loads(external.read_text())
  assert observation['state']=='CLOSED' and observation['headRefOid']==row['current_head']
  row['github_state']='CLOSED'
  row['closure']=dict(kind='externally_closed_not_integrated',observation=observation)
  row['scope']+=' Externally closed without merge; this observation grants no mathematical approval or source-incorporation credit.'
for row in rows:
 c=closed.get(str(row['number']))
 if c:
  assert c['state']=='CLOSED' and c['headRefOid']==row['reviewed_head']
  row.update(disposition='superseded',github_state='CLOSED',integration_location=c['retained_paths'],unresolved_question=None,scope=c['reason'],closure=dict(kind='superseded',reviewed_head=c['headRefOid'],closed_at=c['closedAt'],url=c['url'],reason=c['reason'],retained_at=c['retained_at']),review_completion=dict(changed_file_coverage=True,scoped_mechanism_review=True,required_execution_complete=True,published=True))
  row['verification_evidence']=list(dict.fromkeys(row['verification_evidence']+c['evidence']+['research/community-efficient1900-audit/checks/closed-superseded.json']))
(A/'DISPOSITIONS.json').write_text(json.dumps(dict(scope=sel['scope'],pull_requests=rows),indent=2)+'\n')
archived=sum(x['github_state']=='MERGED' and str(x['number']) in archives for x in rows);merged=sum(x['github_state']=='MERGED' for x in rows);superseded=sum(x['disposition']=='superseded' for x in rows);metrics=dict(selected=100,ready=len(ready),merged=merged,archived_partially_reviewed=archived,superseded_closed=superseded,remaining=100-merged-superseded,open_remaining=sum(x['github_state']=='OPEN' for x in rows),baseline=sel['baseline'],new=44,revised=4,carry_forward=52,limits='Inventory collection is not a completed review. Heavy checks serial, sampled 1GiB descendant-process guard for new runs (historical receipt limitations retained); no Lean, Docker or new agents.')
(A/'METRICS.json').write_text(json.dumps(metrics,indent=2)+'\n')
if archives:
 (A/'ARCHIVE-INTAKE.json').write_text(json.dumps(archives,indent=2)+'\n')
lines=['# Efficient nineteenth 100-PR reconciliation','',f'**{merged} merged; {superseded} closed as superseded; {100-merged-superseded} pending.** Frozen selection: 44 new submissions, four revised heads and 52 carried-forward reviews. Baseline `{sel["baseline"]}`. Complete Git inventories are retained for all 100; this does not grant mathematical approval.','', f'Of the merged submissions, {archived} are archival admissions only and remain partially reviewed, with mathematical and replay obligations open. The selected conditional κ is unchanged. Attribution and predecessor notices remain with each contribution. Prior unresolved review obligations carry forward; neither age nor a smaller headline justifies closure.','', '## Integrated contributions and archive admissions','','| PR | Contributor | Scope |','| --- | --- | --- |']
for x in rows:
 if x['ready_to_integrate']:lines.append(f'| [#{x["number"]}](https://github.com/CrocSwap/integer-mult-bounds/pull/{x["number"]}) | {x["metadata"]["author"]["login"]} | {x["scope"]} |')
lines+=['','## Superseded proposals','','| PR | Contributor | Disposition |','| --- | --- | --- |']
for x in rows:
 if x['disposition']=='superseded':lines.append(f'| [#{x["number"]}](https://github.com/CrocSwap/integer-mult-bounds/pull/{x["number"]}) | {x["metadata"]["author"]["login"]} | {x["scope"]} |')
lines+=['','## Remaining review','','| PR | Contributor | Next step |','| --- | --- | --- |']
for x in rows:
 if not x['ready_to_integrate'] and x['github_state']=='OPEN':lines.append(f'| [#{x["number"]}](https://github.com/CrocSwap/integer-mult-bounds/pull/{x["number"]}) | {x["metadata"]["author"]["login"]} | {x["unresolved_question"].replace("|","/")} |')
lines+=['','## Evidence and limits','','Packets bind each author head, complete Git changed-file inventory and baseline. Checks retain commands, logs, exact inputs and failed setup attempts. Ready groups may integrate independently of longer reviews. Source-authenticated prior verification may be reused only for unchanged inputs and stated coverage. No full supplier replay, formal theorem audit or selected-bound change is implied.','','## Open next questions','','Complete the remaining mechanism, proof, compatibility and execution obligations, grouping shared dependencies and keeping expensive replays serial. Refresh the live queue before any closure decision.','']
text='\n'.join(lines);(A/'README.md').write_text(text);(R/'docs/research/community-efficient1900-review.md').write_text(text)
if (P/'resolution-plan.json').exists():shutil.copy2(P/'resolution-plan.json',A/'INTEGRATION-RESOLUTIONS.json')
print(metrics)
