"""Fresh complete predecessor generation, sparse successor and exact transfer.

No optimizer or stored success receipt certifies the new owners. Full unchanged
native operators are a pinned predecessor premise; only their frame tables are
regenerated here. Complete strict supplier release is a separate long gate.
"""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,sys,time,types
from fractions import Fraction as Q
P=Path(__file__).resolve().parent
def load(name):
 path=P/(name+'.py');m=types.ModuleType(name);m.__file__=str(path)
 exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
extract=load('predecessor').extract
J=load('apply_journal');replay,PROFILE=J.replay,J.PROFILE
OLD_K=Q('0.001730006549538841847005')-Q(1,10**46)-Q(1,10**70)
def need(v,s):
 if not v:raise ValueError(s)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();repo=a.repo.resolve();out=a.out.resolve()
 need(not out.exists() and not out.is_relative_to(P) and not P.is_relative_to(out),'fresh disjoint output');out.mkdir(parents=True)
 pred,word=extract(out/'predecessor');pins={}
 for rel,digest in read(pred/'owners/SOURCE-PINS.json')['repo_files'].items():pins[rel]=digest
 pins.update(read(pred/'ARITHMETIC-PINS.json')['repo'])
 for item in read(word/'SOURCES.json')['files']:
  if item['usage']=='input':pins[item['path']]=item['sha256']
 for rel,digest in pins.items():need((repo/rel).is_file() and not (repo/rel).is_symlink() and sha(repo/rel)==digest,'live source '+rel)
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPYCACHEPREFIX=str(out/'pycache'),PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',OWNER_SOURCE_REPO=str(repo))
 for k in ('PYTHONPATH','PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_RECORD','WITNESS_DISCOVER'):env.pop(k,None)
 stages=[];started=time.monotonic()
 def run(name,script,*args):
  log=out/(name+'.log');t=time.monotonic()
  with log.open('wb') as f:r=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
  stages.append(dict(stage=name,seconds=time.monotonic()-t,exit_code=r.returncode,script_sha256=sha(script),log_sha256=sha(log)));save(out/'STAGES.json',stages);need(r.returncode==0,'failed '+name+'; '+str(log))
 run('predecessor-integer-primal-and-controls',pred/'owners/verify_aggregate.py')
 run('fresh-predecessor-literal',pred/'owners/portable_expand.py','--out',out/'before')
 candidate=out/'candidate';candidate.mkdir()
 for name in ('ORDER.json','DISPATCH.json','PROVIDERS.json'):shutil.copyfile(out/'before'/name,candidate/name)
 save(candidate/'PROFILE.json',PROFILE)
 change=replay(out/'before/COMPOSED-FILL.json.gz',P/'JOURNAL.json',candidate/'COMPOSED-FILL.json.gz');save(out/'JOURNAL-REPLAY.json',change)
 for tag in ('base','extra'):run('fresh-frame-table-'+tag,repo/'research/t74-native-fast/vendor/native/new/code/borrow/bw_transport.py',word/f'STAGED644-660-{tag}.json.gz',out/f'native/checked-{tag}')
 env.update(OWNER_LITERAL_DIR=str(candidate),OWNER_NATIVE_DIR=str(out/'native'),OWNER_PREDECESSOR_DIR=str(out/'before'),OWNER_AUDIT_OUTPUT=str(out/'INDEPENDENT-OWNERS.json'))
 run('independent-complete-successor',P/'independent_owners.py')
 run('full-moment-and-outer',pred/'check_arithmetic.py','--repo',repo,'--profile',candidate/'PROFILE.json','--owner-result',out/'INDEPENDENT-OWNERS.json','--out',out/'arithmetic')
 run('all-pattern-fixed-inventory-dual',P/'check_budget.py','--predecessor',pred,'--out',out/'DUAL.json')
 owner=read(out/'INDEPENDENT-OWNERS.json');arith=read(out/'arithmetic/RESULT.json')
 need(owner['roles']==2717280 and owner['profile']==PROFILE,'complete candidate histogram')
 need(Q(arith['kappa'])>OLD_K and Q(arith['root_interval'][0])==Q('0.001730006690311348872326'),'strict improvement at exact nominated endpoint')
 need(all(sha(repo/rel)==digest for rel,digest in pins.items()),'live input drift')
 result=dict(status='PASS_FRESH_FIVE_OWNER_SUCCESSOR_AND_EXACT_ARITHMETIC',roles=owner['roles'],profile=owner['profile'],idle=owner['idle'],kappa=arith['kappa'],kappa_decimal=arith['kappa_decimal'],root_interval=arith['root_interval'],gain=str(Q(arith['kappa'])-OLD_K),journal=change,stages=stages,seconds=time.monotonic()-started,source_sha256=pins,scope='Fresh finite literal and exact arithmetic. Unchanged native/source proofs are pinned predecessor evidence; full strict release and inherited all-size hypotheses are separate.')
 save(out/'RESULT.json',result);print(json.dumps({k:result[k] for k in ('status','roles','kappa_decimal','seconds')},sort_keys=True))
if __name__=='__main__':main()
