"""Authenticate and replay the new claims in a disposable Git-free copy."""
from pathlib import Path
from hashlib import sha256
import argparse,gzip,json,shutil,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parent

def need(ok,msg):
 if not ok:raise ValueError(msg)
def mathematical(x):
 if isinstance(x,dict):return{k:mathematical(v)for k,v in x.items()if k not in('seconds','caller_sha256')}
 if isinstance(x,list):return[mathematical(v)for v in x]
 return x

def authenticate():
 pins=json.loads((ROOT/'BUNDLE-MANIFEST.json').read_bytes())
 for pin in pins['files']:
  p=Path(pin['path']);need(not p.is_absolute()and'..'not in p.parts,'Relative bundle path')
  b=(ROOT/p).read_bytes();need(len(b)==pin['bytes']and sha256(b).hexdigest()==pin['sha256'],'Frozen bundle byte '+str(p))
 return pins

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--full-native',action='store_true');args=ap.parse_args();pins=authenticate()
 print('PASS bundle authentication',len(pins['files']),'files',flush=True)
 with tempfile.TemporaryDirectory(prefix='kappa-20261104-replay-')as td:
  dest=Path(td)/'construction';shutil.copytree(ROOT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  def run(path):
   print('REPLAY',path,flush=True);subprocess.run([sys.executable,'-I','-B',str(dest/path)],check=True,cwd=dest)
  if args.full_native:run('fragment/verify.py')
  run('two-fragment/verify.py')
  for script,receipt,word in[('bit/verify_retired.py','bit/RETIRED-BIT-ADMISSION.json','bit/RETIRED-CALLER.json.gz'),('bit/verify_fragment.py','bit/FRAGMENT-BIT-ADMISSION.json','bit/FRAGMENT-CALLER.json.gz')]:
   frozen=json.loads((ROOT/receipt).read_bytes());run(script);fresh=json.loads((dest/receipt).read_bytes())
   oldword=(ROOT/word).read_bytes();newword=(dest/word).read_bytes()
   need(sha256(oldword).hexdigest()==frozen['caller_sha256']and sha256(newword).hexdigest()==fresh['caller_sha256'],'Each receipt binds its actual compressed caller')
   need(json.loads(gzip.decompress(oldword))==json.loads(gzip.decompress(newword)),'Literal caller is unchanged across gzip implementations')
   need(mathematical(frozen)==mathematical(fresh),'All mathematical fields match '+receipt)
 authenticate()
 print('PASS_PORTABLE_CONDITIONAL_KAPPA_00330720_AND_ORDINARY_BIT_00376669',flush=True)
 print('Same five framework assumptions; selected frontier unchanged.',flush=True)
if __name__=='__main__':main()
