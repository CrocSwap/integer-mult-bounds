from pathlib import Path,PurePosixPath
import json,hashlib,subprocess,tarfile
P=Path('/tmp/pr-efficient1900');R=Path('/tmp/integer-mult-efficient1100-20261015')
for n,name in [(2899,'physical-ordinary-interchange'),(2915,'selected-bit-fast-primitives')]:
 pkg=P/'sources'/str(n)/'research'/name;records=[]
 for pin in json.loads((pkg/'SOURCES.json').read_text())['archives']:
  source=pin['head']+':'+pin['source_path'];tree=subprocess.check_output(['git','rev-parse',source],cwd=R,text=True).strip();assert tree==pin['git_tree']
  listed=subprocess.check_output(['git','ls-tree','-r','-z',source],cwd=R).split(b'\0');entries={}
  for row in listed:
   if row:
    left,path=row.split(b'\t');mode,kind,oid=left.decode().split();assert kind=='blob';entries[path.decode()]=(mode,oid)
  archive=pkg/pin['path'];assert hashlib.sha256(archive.read_bytes()).hexdigest()==pin['sha256'];seen=set()
  with tarfile.open(archive) as tar:
   for member in tar:
    if member.isdir():continue
    assert member.isfile() and member.name in entries and member.name not in seen
    raw=tar.extractfile(member).read();mode,oid=entries[member.name];assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==oid
    assert bool(member.mode&0o111)==(mode=='100755');seen.add(member.name)
  assert seen==set(entries);records.append(dict(**pin,authenticated_files=len(seen)))
 (P/f'provenance-{n}-archives.json').write_text(json.dumps(dict(status='PASS',number=n,archives=records,scope='Every regular member of each complete source archive matched original pinned Git subtree inventory, blob and executable mode.'),indent=2)+'\n');print(n,[r['authenticated_files'] for r in records])
