import json,subprocess,time,datetime,sys
from pathlib import Path
R=Path('/tmp/integer-mult-queue-20261013');A=R/'research/community-reconciliation-fourth100-audit';P=Path('/tmp/reconciliation-fourth100-20261013');repo='CrocSwap/integer-mult-bounds';data=json.load(open(A/'DISPOSITIONS.json'));reviews=json.load(open(A/'REVIEW.json'));pub=json.load(open(A/'PUBLICATION.json'));receipt=P/'closure-receipts.json';receipts=json.load(open(receipt)) if receipt.exists() else [];done={x['number'] for x in receipts};review_url=f'https://github.com/{repo}/blob/{pub["integration_commit"]}/docs/research/community-reconciliation-fourth100-review.md';credits=f'https://github.com/{repo}/blob/{pub["integration_commit"]}/CONTRIBUTORS.md'
def call(args):return json.loads(subprocess.check_output(['gh',*args],text=True))
def save():receipt.write_text(json.dumps(receipts,indent=2)+'\n')
only=next((set(map(int,arg.split('=',1)[1].split(',')))for arg in sys.argv[1:]if arg.startswith('--only=')),None)
for r in data['pull_requests']:
 n=r['number']
 if only is not None and n not in only:continue
 if n in done or str(n) in sys.argv[1:]:continue
 if '--completed-only' in sys.argv and not(r['disposition']=='incorporated' and all(r['review_completion'].values())):continue
 current=call(['pr','view',str(n),'--repo',repo,'--json','number,state,isDraft,headRefOid,url,closedAt,mergedAt'])
 if current['headRefOid']!=r['reviewed_head'] or current['isDraft']:
  receipts.append(dict(number=n,status='changed_or_draft_keep_open',observed=current));save();print('KEPT',n,'changed',flush=True);continue
 if current['state']!='OPEN':
  receipts.append(dict(number=n,status='already_resolved',observed=current));save();print('ALREADY',n,current['state'],flush=True);continue
 v=reviews[str(n)];author=r['metadata']['author']['login'];source=f'https://github.com/{repo}/tree/{r["reviewed_head"]}';complete=r['disposition']=='incorporated' and all(r['review_completion'].values())
 if complete:
  body=f'''Thank you @{author}. This contribution is now retained on main in the [scoped 100-PR review]({review_url}) and [contributor credits]({credits}).

**Contribution:** {v['mechanism']}

**Review and limits:** {v['scope_and_limits']}

The [complete original source]({source}), notices and relevant execution evidence are retained through the pinned source archive. The review distinguishes fresh local runs, source-bound historical Linux CI and prior exact-head review; it does not claim 100 fresh full mathematical audits. Closing this historical PR as reconciled. This preserves parallel and cumulative credit without replacing the selected frontier or promoting priced research targets to completed constructions.

Reviewed head: `{r['reviewed_head']}`. Publication: `{pub['integration_commit']}`.'''
 else:
  body=f'''Thank you @{author}. Your work and attribution are retained in the [published 100-PR review]({review_url}), [credits]({credits}) and [complete original source]({source}).

**Covered:** {v['mechanism']} {v['scope_and_limits']}

**Keeping this PR open:** {r['unresolved_question']}

The source archive preserves the entire submission; it does not substitute for the remaining execution or review. The batch's machine-readable disposition records this as partial coverage. Reviewed head: `{r['reviewed_head']}`.'''
 payload=P/f'comment-{n}.json';payload.write_text(json.dumps({'body':body}));comment=call(['api',f'repos/{repo}/issues/{n}/comments','--method','POST','--input',str(payload),'--jq','{id: .id, url: .html_url, created_at: .created_at}'])
 if complete:
  check=call(['pr','view',str(n),'--repo',repo,'--json','headRefOid,state,isDraft'])
  if check['headRefOid']!=r['reviewed_head'] or check['isDraft']:raise RuntimeError(f'#{n} changed before closure; review posted comment')
  if check['state']=='OPEN':call(['api',f'repos/{repo}/pulls/{n}','--method','PATCH','-f','state=closed','--jq','{number,state,closed_at,merged_at,head: .head.sha}'])
 final=call(['pr','view',str(n),'--repo',repo,'--json','number,state,isDraft,headRefOid,url,closedAt,mergedAt'])
 assert final['headRefOid']==r['reviewed_head'] and final['state']==('CLOSED' if complete else 'OPEN'),final
 receipts.append(dict(number=n,status='closed_after_published_review' if complete else 'retained_open',comment=comment,observed=final,publication_commit=pub['integration_commit'],observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat()));save();print('CLOSED' if complete else 'KEPT OPEN',n,flush=True);time.sleep(1)
print('DONE',len(receipts),flush=True)
