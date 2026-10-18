from pathlib import Path
import json,subprocess,hashlib,time
P=Path('/tmp/pr-efficient2100');R=Path('/tmp/integer-mult-efficient1100-20261015')
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
base=git('rev-parse','HEAD').decode().strip();old={x['number'] for batch in (1900,2000) for x in json.loads(Path(f'/tmp/pr-efficient{batch}/selection.json').read_text())['prs']}
ns=sorted((x for x in json.loads((P/'live.json').read_text()) if not x['isDraft'] and x['number'] not in old),key=lambda x:x['number'])[:100];assert len(ns)==100
(P/'selection.json').write_text(json.dumps(dict(baseline=base,observed_unix=time.time(),scope='Next100open non-draft heads, excluding frozen rounds19–20; source-only archive intake or explicit substantive hold.',prs=ns),indent=2)+'\n')
missing=[]
for x in ns:
 if subprocess.run(['git','cat-file','-e',x['headRefOid']+'^{commit}'],cwd=R,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:missing.append(x['headRefOid'])
if missing:subprocess.run(['git','-c','gc.auto=0','-c','maintenance.auto=false','fetch','origin',*missing],cwd=R,check=True,stdout=subprocess.DEVNULL)
tree={}
for rec in git('ls-tree','-r','-z',base).split(b'\0'):
 if rec:
  meta,name=rec.split(b'\t',1);mode,kind,oid=meta.decode().split();tree[name.decode()]=dict(mode=mode,kind=kind,oid=oid)
(P/'packets').mkdir(exist_ok=True)
for x in ns:
 n=x['number'];(P/f'{n}.json').write_text(json.dumps(x,indent=2)+'\n');mb=git('merge-base',x['headRefOid'],x['baseRefOid']).decode().strip();raw=git('diff','--raw','--no-renames','--abbrev=40','-z',mb,x['headRefOid']).split(b'\0');files=[]
 for i in range(0,len(raw)-1,2):
  info=raw[i].decode().split();name=raw[i+1].decode();mode=info[1];source=None if mode=='000000' else dict(mode=mode,kind='blob' if mode!='160000' else 'commit',oid=info[3]);target=tree.get(name)
  files.append(dict(path=name,source=source,baseline=target,change=info[4],baseline_relation='identical' if source==target else 'absent_on_baseline' if target is None else 'different_on_baseline'))
 pk=dict(number=n,head=x['headRefOid'],baseline=base,merge_base=mb,author=x['author'],title=x['title'],url=x['url'],files=files,scope='Complete Git raw diff, no rename inference, exact source and baseline identities. Not scientific review.')
 (P/'packets'/f'{n}.json').write_text(json.dumps(pk,indent=2)+'\n')
print('Prepared100metadata and complete Git-diff packets; fetched',len(missing),'heads.')
