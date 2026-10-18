from pathlib import Path
import json,subprocess,hashlib
P=Path('/tmp/pr-efficient2300');R=Path('/tmp/integer-mult-efficient1100-20261015')
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
head=git('rev-parse','HEAD').decode().strip();tree={}
for rec in git('ls-tree','-r','-z',head).split(b'\0'):
 if rec:
  meta,path=rec.split(b'\t',1);mode,kind,oid=meta.decode().split();tree[path.decode()]=(mode,oid)
states=json.loads((P/'integration-state.json').read_text());intake={x['number']:x for x in json.loads((P/'INTAKE.json').read_text())['pull_requests']};unique=set();files=0
resolution=json.loads((P/'ATTRIBUTE-RESOLUTION.json').read_text())
assert hashlib.sha256(git('show',head+':.gitattributes')).hexdigest()==resolution['resolved_sha256']
for key,v in states.items():
 n=int(key);pk=json.loads((P/'packets'/f'{n}.json').read_text());assert v['state']=='MERGED' and v['headRefOid']==pk['head'];git('merge-base','--is-ancestor',pk['head'],head)
 assert intake[n]['status']=='archive_ready'
 for f in pk['files']:
  if f['path']=='.gitattributes':
   original=R/f'research/community-efficient2300-audit/original-attributes/{n}.gitattributes'
   assert original.read_bytes()==git('cat-file','blob',f['source']['oid'])
  else:assert tree.get(f['path'])==(f['source']['mode'],f['source']['oid']),(n,f['path'])
  unique.add(f['path']);files+=1
base=json.loads((P/'selection.json').read_text())['baseline'];sel='certificates/selected-result.json';assert git('show',head+':'+sel)==git('show',base+':'+sel)
record=dict(status='PASS',checked_commit=head,merged_prs=sorted(map(int,states)),changed_file_entries=files,unique_files=len(unique),selected_sha256=hashlib.sha256(git('show',head+':'+sel)).hexdigest(),scope='All author heads ancestors; every original research blob and mode retained; root attribute resolution checked with original author blobs retained separately; selected result unchanged. Source-only archive, not scientific validation.')
(P/'source-retention.json').write_text(json.dumps(record,indent=2)+'\n');print(record)
