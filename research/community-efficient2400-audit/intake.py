from pathlib import Path
import ast,json,hashlib,subprocess,collections
P=Path('/tmp/pr-efficient2400');R=Path('/tmp/integer-mult-efficient1100-20261015')
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
sel=json.loads((P/'selection.json').read_text());base=sel['baseline'];queue={x['number']:x for x in json.loads((P/'QUEUE.json').read_text())['pull_requests']};ledger={x['number']:x for x in json.loads((R/'docs/research/pr-ledger.json').read_text())['pull_requests']}
blocked={2914,2901,2890,2832,2276,2263,2257,2235,1900,1345}
for b in (1900,2000,2100,2200,2300):
 f=Path(f'/tmp/pr-efficient{b}/INTAKE.json')
 if f.exists():blocked|={x['number'] for x in json.loads(f.read_text())['pull_requests'] if x['status'] in ('held_known_correctness','held_intake_errors','held_unmerged_dependencies')}
reader=subprocess.Popen(['git','cat-file','--batch'],cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE);cache={};checks={};rows=[]
def blob(oid):
 if oid not in cache:
  reader.stdin.write((oid+'\n').encode());reader.stdin.flush();hdr=reader.stdout.readline().split();assert len(hdr)==3 and hdr[1]==b'blob';size=int(hdr[2]);assert size<256*1024*1024
  raw=reader.stdout.read(size);assert len(raw)==size and reader.stdout.read(1)==b'\n';assert hashlib.sha1(b'blob '+str(size).encode()+b'\0'+raw).hexdigest()==oid;cache[oid]=raw
 return cache[oid]
def tree(head):
 out={}
 for rec in git('ls-tree','-r','-z',head).split(b'\0'):
  if rec:
   meta,name=rec.split(b'\t',1);mode,kind,oid=meta.decode().split();out[name.decode()]=dict(mode=mode,kind=kind,oid=oid)
 return out
bt=tree(base)
for m in sel['prs']:
 n=m['number'];pk=json.loads((P/'packets'/f'{n}.json').read_text());q=queue[n];old=ledger.get(n,{});row=dict(number=n,head=pk['head'],status='held_shared_or_existing_obligation',remaining=old.get('unresolved_question') or 'Independent mechanism/proof review and source-bound replay remain open.',errors=[],paths=sorted({'/'.join(f['path'].split('/')[:2]) for f in pk['files']}))
 if n in blocked:row['status']='held_known_correctness_or_integrity'
 elif q['lane'] in ('research_plus_attributes','research_versions_or_new_files','new_head'):
  files=pk['files'];st=tree(pk['head']);assert all(f['source']==st.get(f['path']) for f in files)
  actual=set(git('diff','--name-only','--no-renames','-z',pk['merge_base'],pk['head']).decode().split('\0'))-{''};assert actual=={f['path'] for f in files}
  mb=git('merge-base',base,pk['head']).decode().strip();stack=set(git('diff','--name-only','--no-renames','-z',mb,pk['head']).decode().split('\0'))-{''}
  extras=stack-actual
  if extras:row.update(status='held_unreviewed_stack',extra_paths=sorted(extras))
  elif not all((f['path'].startswith('research/') or f['path']=='.gitattributes') and (f['source'] is None or f['source']['mode'] in ('100644','100755')) for f in files):row['status']='held_nonresearch_changes'
  else:
   rawfiles={f['path']:blob(f['source']['oid']) for f in files if f['source']};syntax=collections.Counter();pins=[]
   for name,raw in rawfiles.items():
    kind='python' if name.endswith('.py') else 'json' if name.endswith('.json') else None
    if kind:
     key=(hashlib.sha256(raw).hexdigest(),kind)
     if key not in checks:
      try:
       ast.parse(raw) if kind=='python' else json.loads(raw,parse_int=str);checks[key]=None
      except (ValueError,SyntaxError,UnicodeDecodeError) as e:checks[key]=str(e)
     if checks[key]:row['errors'].append(dict(path=name,error=checks[key],check='syntax'))
     syntax[kind]+=1
   for name,raw in rawfiles.items():
    if not name.endswith('/MANIFEST.json'):continue
    obj=json.loads(raw,parse_int=str);root=str(Path(name).parent);checked=0;outside=0
    if isinstance(obj,dict):
     for rel,h in obj.items():
      if not isinstance(h,str) or len(h)!=64 or not all(c in '0123456789abcdef' for c in h):continue
      if Path(rel).is_absolute() or '..' in Path(rel).parts:row['errors'].append(dict(path=rel,check='unsafe_manifest_path'));continue
      key=root+'/'+rel
      if key not in rawfiles:outside+=1;continue
      checked+=1
      if hashlib.sha256(rawfiles[key]).hexdigest()!=h:row['errors'].append(dict(path=key,check='manifest_sha256'))
    pins.append(dict(path=name,local_pins_checked=checked,outside_changed_files=outside))
   conflicts=[f['path'] for f in files if f['source']!=bt.get(f['path']) and f['path'] in bt]
   # New isolated packages enter the working tree; competing revisions are kept
   # at their complete original commits, never silently overwritten or endorsed.
   mode='historical_source_snapshot' if conflicts or '.gitattributes' in actual else 'default_tree_archive'
   row.update(status='archive_ready' if not row['errors'] else 'held_intake_errors',archive_mode=mode,conflicting_paths=conflicts,syntax=dict(syntax),manifests=pins,source_tree_url='https://github.com/CrocSwap/integer-mult-bounds/tree/'+pk['head'],files={k:dict(sha256=hashlib.sha256(v).hexdigest(),bytes=len(v)) for k,v in rawfiles.items()})
 rows.append(row)
reader.stdin.close();assert reader.wait()==0
(P/'INTAKE.json').write_text(json.dumps(dict(baseline=base,scope='Source identity, syntax and flat changed-file manifest integrity only. No submitted code executed; no scientific approval. Historical snapshots intentionally do not replace default-tree package versions.',unique_blobs_read=len(cache),unique_syntax_checks=len(checks),pull_requests=rows),indent=2)+'\n')
print(dict(collections.Counter(x['status'] for x in rows)));print('READY',[(x['number'],x['archive_mode']) for x in rows if x['status']=='archive_ready'])
for x in rows:
 if x['errors']:print('ERROR',x['number'],x['errors'][:2])
