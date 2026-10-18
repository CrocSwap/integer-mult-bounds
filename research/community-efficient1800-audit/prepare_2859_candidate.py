from pathlib import Path
import json,subprocess,shutil,hashlib,tempfile
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');S=P/'sources/2859';D=P/'combined-2859';assert not D.exists();D.mkdir();pk=json.load(open(P/'packets/2859.json'));head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();conflicts=[];resolutions=[]
def show(ref,path):return subprocess.run(['git','show',ref+':'+path],cwd=R,capture_output=True)
for f in pk['files']:
 rel=f['path'];author=(S/rel).read_bytes();base=show(pk['merge_base'],rel);current=show(head,rel);new=author
 if base.returncode==0 and current.returncode==0 and current.stdout!=base.stdout and current.stdout!=author:
  with tempfile.TemporaryDirectory() as tmp:
   t=Path(tmp)
   for name,data in [('current',current.stdout),('base',base.stdout),('author',author)]: (t/name).write_bytes(data)
   run=subprocess.run(['git','merge-file','-p',str(t/'current'),str(t/'base'),str(t/'author')],capture_output=True)
   if run.returncode:conflicts.append(rel)
   new=run.stdout;resolutions.append({'path':rel,'conflicted':bool(run.returncode),'current_sha256':hashlib.sha256(current.stdout).hexdigest(),'author_sha256':hashlib.sha256(author).hexdigest()})
 dest=D/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(new)
(P/'provenance-2859-composition.json').write_text(json.dumps(dict(status='unreviewed_composition',baseline=head,author_head=pk['head'],conflicts=conflicts,resolutions=resolutions),indent=2)+'\n');print('Conflicts',conflicts);print('Composed',len(resolutions),'changed-on-both-side files')
