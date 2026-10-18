from pathlib import Path
import json,subprocess,time,shutil
P=Path('/tmp/pr-efficient2600');R=Path('/tmp/integer-mult-efficient1100-20261015')
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
q=json.loads((P/'QUEUE.json').read_text());live={x['number']:x for x in json.loads((P/'live.json').read_text())};base=git('rev-parse','HEAD').decode().strip()
priority={'shared_code_or_docs':0,'new_head':1,'changed_head':1,'research_plus_attributes':2,'held_intake_errors':3}
chosen=sorted(q['pull_requests'],key=lambda x:(priority.get(x['lane'],5),-x['number']))[:100]
(P/'selection.json').write_text(json.dumps(dict(baseline=base,observed_unix=time.time(),scope='100-head reconciliation: shared-code review and source archive intake; unchanged substantive holds retained.',prs=[live[x['number']] for x in chosen]),indent=2)+'\n')
(P/'packets').mkdir(exist_ok=True)
for x in chosen:
 n=x['number']
 if x.get('source_packet'):
  pk=json.loads(Path(x['source_packet']).read_text());assert pk['head']==live[n]['headRefOid'];shutil.copy(x['source_packet'],P/'packets'/f'{n}.json')
 else:
  m=json.loads(subprocess.check_output(['gh','pr','view',str(n),'--repo','CrocSwap/integer-mult-bounds','--json','number,title,headRefOid,baseRefOid,isDraft,url,author,body,files']))
  (P/f'{n}.json').write_text(json.dumps(m,indent=2)+'\n')
  subprocess.run(['git','-c','gc.auto=0','fetch','origin',m['headRefOid']],cwd=R,check=True,capture_output=True)
  mb=git('merge-base',m['headRefOid'],m['baseRefOid']).decode().strip();raw=git('diff','--raw','--no-renames','--abbrev=40','-z',mb,m['headRefOid']).split(b'\0');files=[]
  for i in range(0,len(raw)-1,2):
   info=raw[i].decode().split();mode=info[1];files.append(dict(path=raw[i+1].decode(),source=None if mode=='000000' else dict(mode=mode,kind='blob' if mode!='160000' else 'commit',oid=info[3]),change=info[4]))
  pk=dict(number=n,head=m['headRefOid'],merge_base=mb,baseline=base,author=m['author'],title=m['title'],url=m['url'],files=files,scope='Complete source diff; no mathematical verification.')
  (P/'packets'/f'{n}.json').write_text(json.dumps(pk,indent=2)+'\n')
print('Frozen',len(chosen),'heads; new metadata fetched only for uncached heads.')
