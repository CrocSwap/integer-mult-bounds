"""Standalone source-bound replay. Standard library, Python 3.11 or later."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent
sys.dont_write_bytecode=True

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def need(ok,label):
 if not ok:raise ValueError(label)
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def bindings(authoring=False):
 manifest=P/'MANIFEST.json'
 need(manifest.exists() or authoring,'missing package manifest')
 if manifest.exists():
  record=json.loads(manifest.read_text());files=record['files']
  actual={str(f.relative_to(P)) for f in P.rglob('*') if f.is_file() and f!=manifest}
  need(set(files)==actual,'package file coverage')
  for name,sha in files.items():
   need(not Path(name).is_absolute() and '..' not in Path(name).parts,'relative package path')
   need(hashlib.sha256((P/name).read_bytes()).hexdigest()==sha,'package hash: '+name)
 sources=json.loads((P/'SOURCES.json').read_text())
 need(len(sources['files'])==22,'source inventory')
 for row in sources['files']:
  path=row['path'];need(not Path(path).is_absolute() and '..' not in Path(path).parts,'relative source path')
  raw=(P/path).read_bytes()
  need(hashlib.sha256(raw).hexdigest()==row['sha256'],'retained source SHA: '+path)
  blob=b'blob '+str(len(raw)).encode()+b'\0'+raw
  need(hashlib.sha1(blob).hexdigest()==row['git_blob'],'retained source Git object: '+path)
 return dict(base=sources['base'],files=len(sources['files']),source_pins_sha256=hashlib.sha256((P/'SOURCES.json').read_bytes()).hexdigest())

def calculate():
 core=load('dirty_cubic_core',P/'core.py');symbolic=load('dirty_free_algebra',P/'symbolic.py')
 algebra=load('dirty_algebra_checks',P/'check_algebra.py');budget_check=load('independent_budget',P/'check_budget.py')
 numeric=load('dirty_numeric',P/'numeric.py')
 rows=[]
 for r in range(3,513):
  if not core.primepower(r):continue
  for p in (1,32,128,1024,1048576):
   for m in (0,20,1024):
    for incoming in (0,160,1048576):
     row=core.uniform(r,p,m,incoming);core.check_uniform(row);rows.append(row)
 budgets=budget_check.check(rows);print('PASS uniform budgets',len(rows),flush=True)
 free=[]
 for n in list(range(1,65))+[95,127,128,129,191,255,256]:
  for sign in [1,-1]:free.append(symbolic.run(n,sign))
 print('PASS free polynomial prefixes',len(free),flush=True)
 dense=algebra.check();print('PASS frozen words, dense paths and controls',flush=True)
 rounded=[]
 for data in json.loads((P/'vendor/628/FACTORS.json').read_text()):
  state=numeric.v.w.k.certify(data)
  for length in [1,2,3,8]:
   for direction in [-1,1]:
    rounded.append(numeric.evaluate(state,length,direction,11 if direction==1 else -7))
  print('PASS full-grid dirty kernel',state['radix'],state['embedding'],flush=True)
 need(all(r['all_input_low_bits_odd'] and r['nonzero_rounding'] for r in rounded),'full-grid and nonzero error coverage')
 return dict(status='PASS_DIRTY_CUBIC_PRECISION',kappa='unchanged',budgets=budgets,
             symbolic=free,algebra=dense,rounded_kernels=rounded,
             scope='Sufficient cubic precision for balanced arbitrary-dirty cyclic inverse arithmetic; inherited analytic/preparation/leaf hypotheses, no common-label or multiplication-exponent claim.')

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--write',type=Path,help='authoring: create a fresh mathematical receipt; no overwrite')
 ap.add_argument('--out',type=Path,help='verify the committed receipt and also write a fresh copy')
 ap.add_argument('--bindings-only',action='store_true',help='source and package checks only; does not execute mathematics')
 args=ap.parse_args();need(sum(bool(x) for x in (args.write,args.out,args.bindings_only))<=1,'choose one mode')
 destination=args.write or args.out
 if destination:need(not destination.exists(),'receipt already exists')
 pins=bindings(authoring=args.write is not None)
 if args.bindings_only:
  print('PASS_PACKAGE_BINDINGS sources='+str(pins['files']));return
 result=calculate();result['sources']=pins
 if not args.write:need(canonical(result)==canonical(json.loads((P/'EXPECTED.json').read_text())),'mathematical receipt mismatch')
 if destination:
  with destination.open('x') as f:f.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print('PASS_DIRTY_CUBIC_PRECISION budgets='+str(result['budgets']['cases'])+' symbolic='+str(len(result['symbolic']))+' rounded='+str(len(result['rounded_kernels']))+' kappa=unchanged')

if __name__=='__main__':main()
