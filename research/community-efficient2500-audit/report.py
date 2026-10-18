from pathlib import Path
import json,shutil,collections,subprocess
def unique(items):
 out=[];seen=set()
 for item in items:
  key=json.dumps(item,sort_keys=True)
  if key not in seen:out.append(item);seen.add(key)
 return out
P=Path('/tmp/pr-efficient2500');R=Path('/tmp/integer-mult-efficient1100-20261015');A=R/'research/community-efficient2500-audit';A.mkdir(parents=True,exist_ok=True)
ledger=json.loads((R/'docs/research/pr-ledger.json').read_text());prior={x['number']:x for x in ledger['pull_requests']}
for rel in list(ledger['source_sha256'])+['research/pr-reconciliation-20261012/starting-snapshot.json']:
 f=R/rel
 if not f.exists():f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(subprocess.check_output(['git','show','HEAD:'+rel],cwd=R))
selection=json.loads((P/'selection.json').read_text());intake=json.loads((P/'INTAKE.json').read_text());status={x['number']:x for x in intake['pull_requests']};states=json.loads((P/'integration-state.json').read_text()) if (P/'integration-state.json').exists() else {};rows=[]
for m in selection['prs']:
 n=m['number'];x=status[n];old=prior.get(n,{});ready=x['status']=='archive_ready';v=states.get(str(n));pub=v is not None;historical=x.get('archive_mode')=='historical_source_snapshot'
 scope=('ARCHIVE ONLY: '+('Complete original commit retained in main ancestry at the linked immutable tree.' if historical else ('Exact original research blobs retained; workflow configuration separately resolved to manual-only execution with read-only credentials and bounded concurrency. Original workflow preserved in the audit.' if x.get('archive_mode')=='workflow_resolution' else 'Exact original research blobs retained in the default checkout.'))+' Source diff, identity, syntax and available flat manifest pins checked. No submitted code run, scientific validation or selected-frontier change.' if ready else 'Cached exact-head obligations and source-only triage; '+x['status']+'.')
 remaining=x['remaining']
 if x['errors']:remaining+=' Source integrity hold: '+json.dumps(x['errors'])
 if x.get('extra_paths'):remaining+=' Unreviewed stacked changes: '+', '.join(x['extra_paths'])
 rows.append(dict(number=n,metadata={k:m[k] for k in ('number','title','author','headRefOid','isDraft')},reviewed_head=m['headRefOid'],current_head=m['headRefOid'],disposition='partially_reviewed',github_state='MERGED' if pub else 'OPEN',integration_location=([x['source_tree_url']] if historical else x['paths']) if pub else [],unresolved_question=remaining,closure=dict(kind='merged_for_historical_archive_only' if historical else 'merged_for_archive_only',url=m['url'],merge_commit=v['mergeCommit']['oid']) if pub else None,scope=scope,review_completion=dict(changed_file_coverage=ready,scoped_mechanism_review=False,required_execution_complete=False,published=pub),verification_evidence=unique(old.get('verification_evidence',[])+['research/community-efficient2500-audit/INTAKE.json',f'research/community-efficient2500-audit/packets/{n}.json']+(['research/community-efficient2500-audit/WORKFLOW-RESOLUTIONS.json'] if x.get('archive_mode')=='workflow_resolution' else []))))
for name in ['selection.json','live.json','QUEUE.json','prepare.py','classify.py','intake.py','INTAKE.json','ancestry-screen.json','WORKFLOW-RESOLUTIONS.json','workflows.json','action-pins.json','workflow-consumers.json','workflow_review.py','manifest-issues.json','report.py','integrate.py','verify.py','premerge.json','integration-state.json','source-retention.json','live-final.json']:
 if (P/name).exists():shutil.copy2(P/name,A/name)
shutil.copytree(P/'packets',A/'packets',dirs_exist_ok=True)
for folder in ('original-workflows','resolved-workflows'):
 if (P/folder).exists():shutil.copytree(P/folder,A/folder,dirs_exist_ok=True)
(A/'DISPOSITIONS.json').write_text(json.dumps(dict(scope=selection['scope'],pull_requests=rows),indent=2)+'\n')
metrics=dict(selected=len(rows),archived=len(states),scientifically_validated=0,remaining_open=len(rows)-len(states),intake=dict(collections.Counter(x['status'] for x in status.values())))
(A/'METRICS.json').write_text(json.dumps(metrics,indent=2)+'\n')
lines=['# Twenty-fifth 100-head reconciliation','','Source archival intake only. **'+str(len(states))+' archived; '+str(len(rows)-len(states))+' remain open in this batch.** No scientific claim or new κ was validated. No submitted scientific code, Lean or Docker ran. Prior proof/replay obligations remain open.','','Research sources retain their exact author blobs. Eligible workflow configurations are manual-only, with read-only permissions, disabled checkout credential persistence, immutable action references, one active replay and one matrix leg at a time. Existing replay commands are preserved. Original workflow bytes are retained in this audit. No workflow was dispatched and no runtime success is claimed.','','[Archive policy](../../docs/research/research-archive-intake.md) · [Central ledger](../../docs/research/pr-ledger.md)','','| PR / author | Intake | Source / retained version |','| --- | --- | --- |']
for row in rows:
 x=status[row['number']];m=row['metadata'];label=('Historical snapshot' if x.get('archive_mode')=='historical_source_snapshot' else ('Source archive + reviewed manual workflow' if x.get('archive_mode')=='workflow_resolution' else 'Default-tree archive')) if row['github_state']=='MERGED' else x['status'];link=x.get('source_tree_url','https://github.com/CrocSwap/integer-mult-bounds/tree/'+row['current_head']);lines.append(f'| [#{m["number"]}](https://github.com/CrocSwap/integer-mult-bounds/pull/{m["number"]}) / {m["author"]["login"]} | {label} | [Exact author commit]({link}) |')
lines+=['','## Open next questions','','Resolve the remaining shared-code changes, integrity/version conflicts and known correctness holds. Scientific and hosted replay validation remains separate from archival/configuration approval. [Dispositions](DISPOSITIONS.json) retain the exact outstanding obligations; [workflow resolutions](WORKFLOW-RESOLUTIONS.json) record the reviewed configuration changes and their limits.','']
(A/'README.md').write_text('\n'.join(lines));print(metrics)
