from pathlib import Path
import json,subprocess,hashlib
P=Path('/tmp/pr-efficient1900');R=Path('/tmp/integer-mult-efficient1100-20261015');A=R/'research/community-efficient1900-audit';n=928
meta=json.loads((P/f'{n}.json').read_text());head=meta['headRefOid']
live=json.loads(subprocess.check_output(['gh','pr','view',str(n),'--repo','CrocSwap/integer-mult-bounds','--json','number,state,isDraft,headRefOid,url'],text=True));assert live['headRefOid']==head and live['state']=='OPEN' and not live['isDraft']
def tree(prefix):
 raw=subprocess.check_output(['git','ls-tree','-r',head,'--',prefix],cwd=R,text=True);out={}
 for line in raw.splitlines():
  m,path=line.split('\t');mode,kind,oid=m.split();out[path[len(prefix)+1:]]=[mode,oid]
 return out
original=tree('research');mirror=tree('auto-research');mirror.pop('README.md');assert original==mirror and len(mirror)==20119
unique={}
for rel in ['auto-research.md','auto-research/README.md']:
 raw=subprocess.check_output(['git','show',head+':'+rel],cwd=R);dst=A/'originals/928'/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw);unique[rel]=hashlib.sha256(raw).hexdigest()
current={}
for rel in ['AGENTS.md','autoresearch.md','docs/research/research-package-guide.md','scripts/new_research_package.py','scripts/research_package.py','docs/research/agent-task-catalog.json']:
 raw=subprocess.check_output(['git','show','HEAD:'+rel],cwd=R);current[rel]=hashlib.sha256(raw).hexdigest()
receipt=dict(number=n,head=head,status='verified_superseded_proposal',live_before_closure=live,mirrored_file_count=len(mirror),mode_and_blob_identity=True,unique_proposal_files=unique,current_workflow_sha256=current,scope='Entire20121-file inventory checked:20119 identical historical research copies and two instruction documents. Current canonical AGENTS/autoresearch/package guide cover orientation, task selection, source pins, reproducible commands, attribution and PR handoff. The proposed duplicate tree and conflicting submission path are not adopted. No scientific result is discarded or newly claimed.')
(P/'check-928-workflow.json').write_text(json.dumps(receipt,indent=2)+'\n')
(P/'finding-928.json').write_text(json.dumps(dict(number=n,reviewed_head=head,status='ready_to_close_superseded',scope=receipt['scope'],reason='Later canonical workflow supersedes the organizational proposal; importing a20119-file mirror creates a second discovery/submission tree contrary to current AGENTS.md. Unique documents retained under originals/928; Rohan Arun credited.'),indent=2)+'\n')
f=R/'CONTRIBUTORS.md';s=f.read_text();needle='- Maintainer integration by Douglas Colkitt with OpenAI Codex assistance adds native macOS process-observer replays';assert needle in s
s=s.replace(needle,'- **Rohan Arun / rohanarun** — [#928](https://github.com/CrocSwap/integer-mult-bounds/pull/928), early agent-workflow and research-package standardization proposal. The later canonical `AGENTS.md` / `autoresearch.md` workflow supersedes this proposal; its two original instruction documents are retained in the round1900 audit, while the duplicate research tree is not imported.\n'+needle);f.write_text(s)
print('Verified20119 identical copied blobs; retained both proposal documents; ready to close superseded.')
