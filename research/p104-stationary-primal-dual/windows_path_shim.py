"""Explicit in-memory Windows path compatibility shim; source files and hash checks stay unchanged."""
import sys,runpy,hashlib,importlib.machinery,subprocess,json
from pathlib import Path
SELF=Path(__file__).resolve();LOG=SELF.parent/'windows-path-adaptations.jsonl'
KNOWN='35a3a38c6fe57cfb703a57a0382ef6f6b738131753b5fb5b97a68185b82994e1'
old=importlib.machinery.SourceFileLoader.get_code
before="str(arc.relative_to(HERE))";after="arc.relative_to(HERE).as_posix()"
def get_code(self,fullname):
 path=Path(self.path)
 if path.name=='source.py':
  raw=path.read_bytes();h=hashlib.sha256(raw).hexdigest()
  if h==KNOWN:
   src=raw.decode();assert src.count(before)==1
   adapted=src.replace(before,after)
   with LOG.open('a') as f:f.write(json.dumps(dict(source_sha256=h,before=before,after=after,adapted_sha256=hashlib.sha256(adapted.encode()).hexdigest(),path_name=path.name))+'\n')
   return compile(adapted,str(path),'exec')
 return old(self,fullname)
importlib.machinery.SourceFileLoader.get_code=get_code
orig_run=subprocess.run
def run(args,*a,**kw):
 if isinstance(args,(list,tuple)) and str(args[0])==sys.executable:
  args=list(args)
  for i,x in enumerate(args[1:],1):
   if str(x).endswith('.py') and Path(str(x)).resolve()!=SELF:
    args.insert(i,str(SELF));break
 return orig_run(args,*a,**kw)
subprocess.run=run
sys.argv=sys.argv[1:];sys.path.insert(0,str(Path(sys.argv[0]).resolve().parent));runpy.run_path(sys.argv[0],run_name='__main__')

