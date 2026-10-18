import json,pathlib,subprocess,hashlib
P=pathlib.Path('/tmp/pr-efficient1900');R=pathlib.Path('/tmp/integer-mult-efficient1100-20261015');s=json.load(open(P/'integration-state.json'));res={(r['number'],r['path']):r for r in json.load(open(P/'resolution-plan.json'))}
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
head=git('rev-parse','HEAD').decode().strip();tree={}
for line in git('ls-tree','-r',head).decode().splitlines():
 meta,path=line.split('\t',1);mode,kind,oid=meta.split();tree[path]=(mode,oid)
count=0;fixes=[]
for key,v in s.items():
 n=int(key);packet=json.load(open(P/'packets'/f'{n}.json'));assert v['state']=='MERGED' and v['headRefOid']==packet['head']
 subprocess.run(['git','merge-base','--is-ancestor',packet['head'],head],cwd=R,check=True)
 for f in packet['files']:
  rel=f['path'];src=f['source'];r=res.get((n,rel));got=tree.get(rel)
  if r:
   assert got and got[0]==r.get('resolved_mode',src['mode']) and hashlib.sha256(git('show',head+':'+rel)).hexdigest()==r['resolved_sha256'];fixes.append(dict(number=n,path=rel,sha256=r['resolved_sha256']))
  else:assert got==((src['mode'],src['oid']) if src else None),(n,rel)
  count+=1
# Include repaired existing files outside a PR's original changed-file list.
for (n,rel),r in res.items():
 if str(n) not in s or any(x['number']==n and x['path']==rel for x in fixes):continue
 assert hashlib.sha256(git('show',head+':'+rel)).hexdigest()==r['resolved_sha256'],(n,rel)
 fixes.append(dict(number=n,path=rel,sha256=r['resolved_sha256']))
baseline='a7482490b4ca256db67d767a33fa6f7553060807';selected='certificates/selected-result.json';assert git('show',head+':'+selected)==git('show',baseline+':'+selected)
r=dict(status='PASS',checked_commit=head,merged_prs=sorted(map(int,s)),changed_files=count,resolved_files=fixes,selected_sha256=hashlib.sha256(git('show',head+':'+selected)).hexdigest(),scope='Every reviewed author head is an ancestor; every changed file is original Git blob/mode or an explicitly reviewed integration resolution. GitHub MERGED observations retained separately. No new full-supplier claim.')
(P/'combined-source-integrity.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(s),'merged PRs;',count,'files;',len(fixes),'explicit resolutions')
