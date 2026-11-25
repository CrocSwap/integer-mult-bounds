"""Bounded registered replay; safe when the parent interpreter is optimized."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,tempfile
P=Path(__file__).resolve().parent
def need(v,s):
 if not v:raise ValueError(s)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--repo',type=Path,default=P.parents[1]);ap.add_argument('--out',type=Path);a=ap.parse_args()
 manifest=json.loads((P/'ARTIFACTS.json').read_bytes())
 for name,digest in manifest.items():need((P/name).is_file() and not (P/name).is_symlink() and sha(P/name)==digest,'package artifact '+name)
 out=a.out.resolve() if a.out else Path(tempfile.mkdtemp(prefix='owner-successor-'))/'replay'
 need(not out.exists(),'fresh output required')
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPYCACHEPREFIX=str(out.parent/(out.name+'-pycache')),GIT_NO_REPLACE_OBJECTS='1')
 for k in ('PYTHONOPTIMIZE','PYTHONPATH'):env.pop(k,None)
 r=subprocess.run([sys.executable,'-B',str(P/'check.py'),'--repo',str(a.repo.resolve()),'--out',str(out)],env=env,timeout=570)
 need(r.returncode==0,'fresh complete replay failed')
 r=subprocess.run([sys.executable,'-B',str(P/'check_release_binding.py'),'--fresh',str(out)],env=env,timeout=20)
 need(r.returncode==0,'recorded release binding failed')
 need(all(sha(P/name)==digest for name,digest in manifest.items()),'package changed during replay')
 print('PASS_REGISTERED_OWNER_SUCCESSOR',out/'RESULT.json')
if __name__=='__main__':main()
