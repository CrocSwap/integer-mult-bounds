from pathlib import Path
import json,shutil,collections,subprocess
def unique(items):
 out=[];seen=set()
 for item in items:
  key=json.dumps(item,sort_keys=True)
  if key not in seen:out.append(item);seen.add(key)
 return out
P=Path('/tmp/pr-efficient2600');R=Path('/tmp/integer-mult-efficient1100-20261015');A=R/'research/community-efficient2600-audit';A.mkdir(parents=True,exist_ok=True)
ledger=json.loads((R/'docs/research/pr-ledger.json').read_text());prior={x['number']:x for x in ledger['pull_requests']}
for rel in list(ledger['source_sha256'])+['research/pr-reconciliation-20261012/starting-snapshot.json']:
 f=R/rel
 if not f.exists():f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(subprocess.check_output(['git','show','HEAD:'+rel],cwd=R))
selection=json.loads((P/'selection.json').read_text());intake=json.loads((P/'INTAKE.json').read_text());status={x['number']:x for x in intake['pull_requests']};states=json.loads((P/'integration-state.json').read_text()) if (P/'integration-state.json').exists() else {};rows=[]
for m in selection['prs']:
 n=m['number'];x=status[n];old=prior.get(n,{});ready=x['status'] in ('archive_ready','reviewed_ready');validated=x['status']=='reviewed_ready';v=states.get(str(n));pub=v is not None;historical=x.get('archive_mode')=='historical_source_snapshot'
 scope=('ARCHIVE ONLY: '+('Complete original commit retained in main ancestry at the linked immutable tree; its differing files and attributes are deliberately NOT installed in the default checkout.' if historical else 'Exact original research blobs retained in the default checkout.')+' Source diff, identity, syntax and available flat manifest pins checked. No submitted code run, scientific validation or selected-frontier change.' if ready else 'Cached exact-head obligations and source-only triage; '+x['status']+'.')
 if validated:scope=x['review_scope']
 remaining=('Scoped review complete; publication pending.' if validated and not pub else x['remaining'])
 if x['errors']:remaining+=' Source integrity hold: '+json.dumps(x['errors'])
 if x.get('extra_paths'):remaining+=' Unreviewed stacked changes: '+', '.join(x['extra_paths'])
 rows.append(dict(number=n,metadata={k:m[k] for k in ('number','title','author','headRefOid','isDraft')},reviewed_head=m['headRefOid'],current_head=m['headRefOid'],disposition='incorporated' if validated and pub else 'partially_reviewed',github_state='MERGED' if pub else 'OPEN',integration_location=([x['source_tree_url']] if historical else x['paths']) if pub else [],unresolved_question=remaining,closure=dict(kind='merged_with_scoped_review' if validated else 'merged_for_historical_archive_only' if historical else 'merged_for_archive_only',url=m['url'],merge_commit=v['mergeCommit']['oid']) if pub else None,scope=scope,review_completion=dict(changed_file_coverage=ready,scoped_mechanism_review=validated,required_execution_complete=validated,published=pub),verification_evidence=unique(old.get('verification_evidence',[])+['research/community-efficient2600-audit/INTAKE.json',f'research/community-efficient2600-audit/packets/{n}.json']+(['research/community-efficient2600-audit/TOOLING-REPLAY.json','research/community-efficient2600-audit/TEST-SCOPE.md'] if n in (2958,2928) else ['research/community-efficient2600-audit/NAVIGATION-REVIEW.json'] if n==2945 else []))))
for name in ['selection.json','live.json','QUEUE.json','prepare.py','classify.py','intake.py','INTAKE.json','ancestry-screen.json','RESOLUTIONS.json','TOOLING-REPLAY.json','TEST-SCOPE.md','NAVIGATION-REVIEW.json','INSTALLED-BRANCH-FILTERS.json','run_tooling.py','run_2928.py','run_2928_scoped.py','hydrate_selected.py','report.py','integrate.py','verify.py','premerge.json','integration-state.json','source-retention.json','live-final.json']:
 if (P/name).exists():shutil.copy2(P/name,A/name)
shutil.copytree(P/'packets',A/'packets',dirs_exist_ok=True)
for log in P.glob('*-normal.log'):
 shutil.copy2(log,A/log.name)
for log in P.glob('*-optimized.log'):
 shutil.copy2(log,A/log.name)
shutil.copytree(P/'resolutions',A/'resolutions',dirs_exist_ok=True)
(A/'DISPOSITIONS.json').write_text(json.dumps(dict(scope=selection['scope'],pull_requests=rows),indent=2)+'\n')
metrics=dict(selected=len(rows),merged=len(states),archived=sum(status[int(n)]['status']=='archive_ready' for n in states),reviewed_tooling_or_navigation=sum(status[int(n)]['status']=='reviewed_ready' for n in states),scientifically_validated=0,remaining_open=len(rows)-len(states),intake=dict(collections.Counter(x['status'] for x in status.values())))
(A/'METRICS.json').write_text(json.dumps(metrics,indent=2)+'\n')
lines=['# Twenty-sixth 100-head reconciliation','','Shared tooling/navigation review plus source archival intake. **'+str(len(states))+' merged; '+str(len(rows)-len(states))+' remain open in this batch.** No scientific claim or new κ was validated. Focused tooling tests ran under a sampled1GiB watchdog and150-second per-command limit; no Lean or Docker ran. Archived scientific claims retain their proof/replay obligations.','','Competing package versions are retained at their complete original Git commits in canonical main ancestry. The links below identify the precise version; those versions do not overwrite frozen default-tree packages. New isolated packages use their exact original blobs in the default tree. Root attributes in historical snapshots remain inactive.','','[Archive policy](../../docs/research/research-archive-intake.md) · [Central ledger](../../docs/research/pr-ledger.md)','','| PR / author | Intake | Source / retained version |','| --- | --- | --- |']
for row in rows:
 x=status[row['number']];m=row['metadata'];label=('Reviewed tooling/navigation' if status[row['number']]['status']=='reviewed_ready' else 'Historical snapshot' if x.get('archive_mode')=='historical_source_snapshot' else 'Default-tree archive') if row['github_state']=='MERGED' else x['status'];link=x.get('source_tree_url','https://github.com/CrocSwap/integer-mult-bounds/tree/'+row['current_head']);lines.append(f'| [#{m["number"]}](https://github.com/CrocSwap/integer-mult-bounds/pull/{m["number"]}) / {m["author"]["login"]} | {label} | [Exact author commit]({link}) |')
lines+=['','## Open next questions','','Resolve the remaining shared-code changes, known correctness/integrity holds and stacked dependencies. [Dispositions](DISPOSITIONS.json) retain exact outstanding obligations. [Tooling test scope](TEST-SCOPE.md) distinguishes completed relevant checks from unavailable live-inventory suites; the latter are not reported as passed.','']
(A/'README.md').write_text('\n'.join(lines));print(metrics)
