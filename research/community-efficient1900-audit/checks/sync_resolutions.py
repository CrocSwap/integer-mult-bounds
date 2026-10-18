from pathlib import Path
import hashlib,json,shutil,subprocess
P=Path('/tmp/pr-efficient1900');R=Path('/tmp/integer-mult-efficient1100-20261015')
published=set(json.loads((P/'integration-state.json').read_text()))
# Sparse checkout may omit a retained resolution after a merge. Restore only missing HEAD bytes.
for batch in [1900]:
 for entry in json.loads(Path(f'/tmp/pr-efficient{batch}/resolution-plan.json').read_text()):
  if str(entry['number']) not in published:continue
  target=R/entry['path']
  if not target.exists():
   target.parent.mkdir(parents=True,exist_ok=True)
   target.write_bytes(subprocess.check_output(['git','show','HEAD:'+entry['path']],cwd=R))
changed={'scripts/run_isolated_tests.py','scripts/replay_historical_check.py','scripts/reconcile_pr_queue.py','scripts/verify_pr_reconciliation.py','docs/research/current-status.md','docs/research/bottleneck-brief.md','CONTRIBUTORS.md','docs/research/pr-ledger.json','docs/research/pr-ledger.md'}
for batch in [1600,1700,1800]:
 p=Path(f'/tmp/pr-efficient{batch}');f=p/'resolution-plan.json';plan=json.loads(f.read_text())
 for x in plan:
  if x['path'] in changed:
   x['resolved_sha256']=hashlib.sha256((R/x['path']).read_bytes()).hexdigest();x['followup']=('Round1900 PR2903: retain prior P104/BIT navigation and add the independently reviewed QQ16 numerical-contract pointer; no selected change.' if x['path']=='docs/research/bottleneck-brief.md' else 'Round1900: reviewed solver lifetime repair, exact historical successor pin, updated ledger/navigation and contributor credit; no selected change.')
 f.write_text(json.dumps(plan,indent=2)+'\n');dest=R/f'research/community-efficient{batch}-audit/INTEGRATION-RESOLUTIONS.json';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
plan=json.loads((P/'resolution-plan.json').read_text())
for x in plan:
 if str(x['number']) not in published:continue
 x['resolved_sha256']=hashlib.sha256((R/x['path']).read_bytes()).hexdigest();x['resolved_mode']=subprocess.check_output(['git','ls-files','--stage','--',x['path']],cwd=R,text=True).split()[0]
(P/'resolution-plan.json').write_text(json.dumps(plan,indent=2)+'\n');shutil.copy2(P/'resolution-plan.json',R/'research/community-efficient1900-audit/INTEGRATION-RESOLUTIONS.json')
print('Updated explicit reviewed-successor resolutions for rounds16–19')
