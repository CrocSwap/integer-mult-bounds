import json,subprocess,datetime,shutil
from pathlib import Path
R=Path('/tmp/integer-mult-queue-20261013');A=R/'research/community-reconciliation-fourth100-audit';P=Path('/tmp/reconciliation-fourth100-20261013');archive=json.load(open(A/'ARCHIVE.json'))
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/main','refs/tags/'+archive['tag']],cwd=R,text=True);assert head+'\trefs/heads/main' in remote and archive['commit']+'\trefs/tags/'+archive['tag'] in remote
receipt=dict(integration_commit=head,source_archive_commit=archive['commit'],source_archive_tag=archive['tag'],observed_remote_refs=remote,observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Published scoped review and source retention; not approval of every historical claim.')
if (A/'PUBLICATION.json').exists():
 old=json.load(open(A/'PUBLICATION.json'));receipt['prior_publications']=old.pop('prior_publications',[])+[old]
(A/'PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');shutil.copyfile(P/'before-closure.json',A/'BEFORE-CLOSURE.json');d=json.load(open(A/'DISPOSITIONS.json'))
for r in d['pull_requests']:
 r['review_completion']['published']=True;r['publication']=dict(integration_commit=head,evidence='research/community-reconciliation-fourth100-audit/PUBLICATION.json')
 if all(r['review_completion'].values()):r['disposition']='incorporated';r['unresolved_question']=None
(A/'DISPOSITIONS.json').write_text(json.dumps(d,indent=2)+'\n');print(head)
