#!/usr/bin/env python3
"""Apply one disclosed packaging repair to a separate source copy; never relax data checks."""
import argparse,hashlib,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('number',type=int,choices=[350,355,360,390]);p.add_argument('source',type=Path);p.add_argument('--git-root',type=Path,required=True);a=p.parse_args();root=a.source.resolve();assert root.is_dir()
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=root/'MANIFEST.json';raw=manifest.read_bytes();data=json.loads(raw)
if a.number in (350,355,360):
 missing='retime/retime.log' if a.number==350 else '.gitattributes'
 if a.number!=350:assert data['files'][missing]=='ffe82f3c5b968ed009c2577fa38f32c83be167799ee565d40a18e3440c57b342'
 assert missing in data['files'] and not (root/missing).exists()
 actual={f.relative_to(root).as_posix():sha(f.read_bytes())for f in root.rglob('*')if f.is_file() and f.name!='MANIFEST.json'}
 assert actual=={k:v for k,v in data['files'].items()if k!=missing},'Other source mismatch'
 # No scientific code reads this absent historical log/checkout metadata; all actual bytes are already pinned.
 del data['files'][missing];manifest.write_text(json.dumps(data,indent=2)+'\n')
 print('Removed only the absent '+missing+' manifest entry; all original executable/data pins unchanged')
else:
 spec=json.loads((Path(__file__).parent/'pr390/RESTORE.json').read_text());assert sha(raw)==spec['manifest_sha256']
 for row in spec['missing']:
  target=root/row['path'];assert not target.exists()
  blob=subprocess.check_output(['git','cat-file','blob',row['blob']],cwd=a.git_root);assert sha(blob)==row['sha256']==data['files'][row['path']]
  target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob)
 for row in spec['extra']:
  target=root/row['path'];assert sha(target.read_bytes())==row['sha256'];destination=root.parent/(root.name+'-retained-convenience.rar');assert not destination.exists();target.rename(destination)
 actual={f.relative_to(root).as_posix():sha(f.read_bytes())for f in root.rglob('*')if f.is_file()and f!=manifest};assert actual==data['files']
 print('Restored 104 exact manifest-pinned files; retained the convenience RAR outside the checked root')
