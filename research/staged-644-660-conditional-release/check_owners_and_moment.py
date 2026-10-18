"""Fresh finite owner realization, complete invoice and rigorous outer arithmetic.

The separate local package verifies full word/native operators. This command
regenerates native frame tables and all literal owner rows, audits them without
importing the producer, then recomputes moment and outer inequalities. It does
not replace the complete cold source/physical/prefix release.
"""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time
P=Path(__file__).resolve().parent

def need(v,m):
 if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for n in ('repo','word-package','out'):ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args();repo=a.repo.resolve();word=a.word_package.resolve();out=a.out.resolve()
 need(not out.exists(),'fresh output required');need(not out.is_relative_to(P) and not P.is_relative_to(out),'output disjoint from proof inputs')
 files={}
 def pin(path,digest):
  need(path.is_file() and not path.is_symlink() and sha(path)==digest,'immutable input '+str(path));files[str(path)]=digest
 for rel,digest in read(P/'owners/SOURCE-PINS.json')['repo_files'].items():pin(repo/rel,digest)
 for rel,digest in read(P/'ARITHMETIC-PINS.json')['repo'].items():pin(repo/rel,digest)
 for rel,digest in read(P/'ARITHMETIC-PINS.json')['vendor'].items():pin(P/'vendor/pr3531'/rel,digest)
 local=read(word/'SOURCES.json')
 for item in local['files']:
  if item['usage']=='input':pin(repo/item['path'],item['sha256'])
 for tag,digest in [('base','735c540b1fe29d0ceeb4d2f304ec941e5f2bd3bc92bafc8cce2b4f9a67a3b653'),('extra','886338fc32da14f3389a82c8120a1bcf9c5e2f0ec3e9b2d377fdae809e1d977f')]:pin(word/f'STAGED644-660-{tag}.json.gz',digest)
 out.mkdir(parents=True);env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPYCACHEPREFIX=str(out/'pycache'),PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',OWNER_SOURCE_REPO=str(repo))
 for key in ('PYTHONPATH','PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_RECORD','WITNESS_DISCOVER'):env.pop(key,None)
 stages=[];started=time.monotonic()
 def run(name,script,*args):
  log=out/(name+'.log');start=time.monotonic();cmd=[sys.executable,'-B',str(script),*map(str,args)]
  with log.open('wb') as stream:r=subprocess.run(cmd,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=240)
  stages.append(dict(stage=name,seconds=time.monotonic()-start,exit_code=r.returncode,script_sha256=sha(script),log_sha256=sha(log)))
  save(out/'STAGES.json',stages);need(r.returncode==0,'stage failed '+name+'; see '+str(log));return log
 run('integer-primal-and-controls',P/'owners/verify_aggregate.py')
 run('literal-expansion',P/'owners/portable_expand.py','--out',out/'literal')
 native=repo/'research/t74-native-fast/vendor/native/new/code/borrow'
 for tag in ('base','extra'):run('transport-'+tag,native/'bw_transport.py',word/f'STAGED644-660-{tag}.json.gz',out/f'native/checked-{tag}')
 env.update(OWNER_LITERAL_DIR=str(out/'literal'),OWNER_NATIVE_DIR=str(out/'native'),OWNER_AUDIT_OUTPUT=str(out/'INDEPENDENT-OWNERS.json'))
 run('independent-whole-literal',P/'owners/independent_literal.py')
 run('rigorous-moment-and-outer',P/'check_arithmetic.py','--repo',repo,'--profile',out/'literal/PROFILE.json','--owner-result',out/'INDEPENDENT-OWNERS.json','--out',out/'arithmetic')
 need(all(sha(Path(path))==digest for path,digest in files.items()),'proof input drift')
 owner=read(out/'INDEPENDENT-OWNERS.json');arithmetic=read(out/'arithmetic/RESULT.json')
 result=dict(status='PASS_FRESH_FINITE_OWNER_MOMENT_AND_OUTER',roles=owner['roles'],profile=owner['profile'],idle=owner['idle'],kappa=arithmetic['kappa'],kappa_decimal=arithmetic['kappa_decimal'],root_interval=arithmetic['root_interval'],stages=stages,seconds=time.monotonic()-started,input_sha256=files,scope='Fresh finite owner/source-window/family/prefix/invoice and rigorous moment/outer checks. Full local native operators and complete source/physical/prefix release are separately required; inherited all-size hypotheses remain.')
 save(out/'RESULT.json',result);print(json.dumps({k:result[k] for k in ('status','roles','profile','kappa_decimal','seconds')},sort_keys=True))
if __name__=='__main__':main()
