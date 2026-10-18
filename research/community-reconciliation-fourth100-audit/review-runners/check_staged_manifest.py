import hashlib,json,subprocess
from pathlib import Path
R=Path('/tmp/integer-mult-queue-20261013');base='research/community-reconciliation-fourth100-audit'
m=json.loads(subprocess.check_output(['git','show',':'+base+'/MANIFEST.json'],cwd=R));pairs=[(base+'/'+p,s) for p,s in m['files'].items()]+list(m.get('integrated_files',{}).items())
p=subprocess.Popen(['git','cat-file','--batch'],cwd=R,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
for path,expected in pairs:
 p.stdin.write((':'+path+'\n').encode());p.stdin.flush();header=p.stdout.readline().decode().split();assert len(header)==3,(path,header);raw=p.stdout.read(int(header[2]));assert p.stdout.read(1)==b'\n';assert hashlib.sha256(raw).hexdigest()==expected,path
p.stdin.close();assert p.wait()==0;print('PASS staged evidence manifest',len(pairs),'files')
