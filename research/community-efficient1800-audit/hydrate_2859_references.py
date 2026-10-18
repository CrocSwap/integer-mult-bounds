from pathlib import Path
import json,subprocess,ast,importlib.util,hashlib
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'combined-2859'
paths=set(subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD'],cwd=R,text=True).splitlines());proc=subprocess.Popen(['git','cat-file','--batch'],cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE);added={}
def put(rel):
 f=D/rel
 if f.exists():return f
 if rel not in paths:raise ValueError('Not on main: '+rel)
 proc.stdin.write(('HEAD:'+rel+'\n').encode());proc.stdin.flush();header=proc.stdout.readline().decode().split();assert len(header)==3 and header[1]=='blob',header;data=proc.stdout.read(int(header[2]));assert proc.stdout.read(1)==b'\n';f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data);added[rel]=hashlib.sha256(data).hexdigest();return f
for path in paths:
 if path.startswith(('references/','notes/')) or path=='upstream/SOURCES.json':put(path)
proc.stdin.close();proc.wait()
(P/'provenance-2859-reference-hydration.json').write_text(json.dumps(dict(added=added),indent=2)+'\n');print('Added',len(added),'files')
