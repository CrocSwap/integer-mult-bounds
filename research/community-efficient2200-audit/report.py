from pathlib import Path
import json,shutil,collections
P=Path('/tmp/pr-efficient2200');R=Path('/tmp/integer-mult-efficient1100-20261015');A=R/'research/community-efficient2200-audit';A.mkdir(parents=True,exist_ok=True)
import subprocess
ledger=json.loads((R/'docs/research/pr-ledger.json').read_text())
for rel in list(ledger['source_sha256'])+['research/pr-reconciliation-20261012/starting-snapshot.json']:
 path=R/rel
 if not path.exists():
  path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(subprocess.check_output(['git','show','HEAD:'+rel],cwd=R))
selection=json.loads((P/'selection.json').read_text());intake=json.loads((P/'INTAKE.json').read_text());status={x['number']:x for x in intake['pull_requests']};prior={x['number']:x for x in json.loads((R/'docs/research/pr-ledger.json').read_text())['pull_requests']};states=json.loads((P/'integration-state.json').read_text()) if (P/'integration-state.json').exists() else {};rows=[]
for m in selection['prs']:
 n=m['number'];x=status[n];pub=str(n) in states;ready=x['status']=='archive_ready';old=prior.get(n,{});v=states.get(str(n));scope=('ARCHIVE ONLY: original author sources retained; source identity, new research paths, syntax and available flat manifest pins checked. No author code execution, mathematical validation, full reproduction or new selected kappa. Stored author receipts retain their original status.' if ready else 'Source-inventory triage only; substantive review remains open. '+x['status']+'.')
 remaining=x['remaining']
 if x.get('reason'):remaining+=' Intake hold: '+x['reason']
 if x.get('errors'):remaining+=' Intake issue: '+json.dumps(x['errors'])
 if x.get('collisions'):remaining+=' Conflicting versions across this batch: '+', '.join(x['collisions'])
 rows.append(dict(number=n,metadata={k:m[k] for k in ('number','title','author','headRefOid','isDraft')},reviewed_head=m['headRefOid'],current_head=m['headRefOid'],disposition='partially_reviewed',github_state='MERGED' if pub else 'OPEN',integration_location=x['paths'] if pub else [],unresolved_question=remaining,closure=dict(kind='merged_for_archive_only',url=m['url'],merge_commit=v['mergeCommit']['oid']) if pub else None,scope=scope,review_completion=dict(changed_file_coverage=ready,scoped_mechanism_review=False,required_execution_complete=False,published=pub),verification_evidence=old.get('verification_evidence',[])+['research/community-efficient2200-audit/INTAKE.json',f'research/community-efficient2200-audit/packets/{n}.json']))
for name in ['selection.json','INTAKE.json','INTAKE-first.json','live.json','prepare.py','intake.py','report.py','integrate.py','verify.py','integration-state.json','premerge.json','source-retention.json','live-final.json','STACK-1231.json','FSTAR-2936.json']:
 if (P/name).exists():shutil.copy2(P/name,A/name)
shutil.copytree(P/'packets',A/'packets',dirs_exist_ok=True)
(A/'DISPOSITIONS.json').write_text(json.dumps(dict(scope=selection['scope'],pull_requests=rows),indent=2)+'\n')
counts=dict(collections.Counter(x['status'] for x in status.values()));metrics=dict(selected=len(selection["prs"]),merged_for_archive=len(states),scientifically_validated=0,remaining_open=len(selection["prs"])-len(states),intake=counts);(A/'METRICS.json').write_text(json.dumps(metrics,indent=2)+'\n')
lines=['# Twenty-second intake: final unbatched remainder','','**'+str(len(states))+' archived/merged; '+str(len(selection['prs'])-len(states))+' still open.** No scientific claim or selected result was newly validated. Archive acceptance preserves the original sources and contributor credit; every archived submission remains partially reviewed with its prior proof/replay obligations open.','','The complete Git diff is authenticated for all frozen heads. Archive candidates only add research files absent from the baseline; source syntax and available flat local manifest pins are checked without executing submitted code. Shared-code changes, known correctness objections, unresolved file conflicts and intake failures remain open.','', 'JSON syntax validation parses integer tokens as text to support large exact integers without expensive conversion. No author source or expected hash was changed.','','[Archive policy](../../docs/research/research-archive-intake.md) · [Central ledger](../../docs/research/pr-ledger.md)','','| PR / contributor | Intake | Scientific review remaining |','| --- | --- | --- |']
for row in rows:
 n=row['number'];login=row['metadata']['author']['login'];stage='Archived, not independently validated' if row['github_state']=='MERGED' else status[n]['status'];lines.append(f'| [#{n}](https://github.com/CrocSwap/integer-mult-bounds/pull/{n}) / {login} | {stage} | {row["unresolved_question"].replace("|","/").replace(chr(10)," ")} |')
lines+=['','## Open next questions','','Resolve the shared-code, version-conflict and known-correctness holds; scientifically validate only the prioritized frontier or dependent mechanism work. Archive publication alone does not discharge these obligations.','']
(A/'README.md').write_text('\n'.join(lines));print(metrics)
