from pathlib import Path
import subprocess,json,shutil
P=Path('/tmp/pr-efficient2300');R=Path('/tmp/integer-mult-efficient1100-20261015');A=R/'research/community-efficient2300-audit'
def run(args):
 r=subprocess.run(args,cwd=R,text=True,capture_output=True,check=True);print(r.stdout[-900:],end='',flush=True);return r
run(['python3',str(P/'verify.py')]);run(['python3',str(P/'report.py')]);run(['python3','scripts/reconcile_pr_queue.py']);run(['python3','/tmp/pr-efficient1800/check_ledger.py']);shutil.copy2('/tmp/pr-efficient1800/combined-ledger-check.json',A/'ledger-check.json');run(['python3','/tmp/pr-efficient1900/sync_resolutions.py'])
rows={x['number']:x for x in json.loads((R/'docs/research/pr-ledger.json').read_text())['pull_requests']}
for key in json.loads((P/'integration-state.json').read_text()):
 x=rows[int(key)];assert x['disposition']=='partially_reviewed' and x['github_state']=='MERGED' and x['unresolved_question']
 assert x['review_completion']==dict(changed_file_coverage=True,scoped_mechanism_review=False,required_execution_complete=False,published=True)
shutil.copy2(P/'finish.py',A/'finish.py')
paths=['docs/research/pr-ledger.json','docs/research/pr-ledger.md','research/community-efficient2300-audit']+[f'research/community-efficient{n}-audit/INTEGRATION-RESOLUTIONS.json' for n in (1600,1700,1800,1900)]
run(['git','add','--sparse',*paths]);run(['git','diff','--cached','--check']);run(['git','commit','-m','Record archive admissions and unresolved obligations for next100 PRs'])
for n in (1600,1700,1800,1900):
 run(['python3',f'/tmp/pr-efficient{n}/verify_integration.py']);dest=R/f'research/community-efficient{n}-audit/combined-source-integrity.json';shutil.copy2(f'/tmp/pr-efficient{n}/combined-source-integrity.json',dest);run(['git','add','--sparse',str(dest)])
run(['python3','/tmp/pr-efficient2000/verify.py']);shutil.copy2('/tmp/pr-efficient2000/source-retention.json',R/'research/community-efficient2000-audit/source-retention.json');run(['git','add','--sparse','research/community-efficient2000-audit/source-retention.json'])
run(['python3','/tmp/pr-efficient2100/verify.py']);shutil.copy2('/tmp/pr-efficient2100/source-retention.json',R/'research/community-efficient2100-audit/source-retention.json');run(['git','add','--sparse','research/community-efficient2100-audit/source-retention.json'])
run(['python3','/tmp/pr-efficient2200/verify.py']);shutil.copy2('/tmp/pr-efficient2200/source-retention.json',R/'research/community-efficient2200-audit/source-retention.json');run(['git','add','--sparse','research/community-efficient2200-audit/source-retention.json'])
run(['python3',str(P/'verify.py')]);shutil.copy2(P/'source-retention.json',A/'source-retention.json');run(['git','add','--sparse',str(A/'source-retention.json')]);run(['git','commit','-m','Verify source retention across eight intake rounds'])
run(['git','fetch','origin','main']);run(['git','merge-base','--is-ancestor','origin/main','HEAD']);run(['git','push','origin','HEAD:main']);head=run(['git','rev-parse','HEAD']).stdout.strip();remote=run(['git','ls-remote','origin','refs/heads/main']).stdout.split()[0];assert head==remote and not run(['git','status','--porcelain']).stdout;print('VERIFIED_MAIN',head)
