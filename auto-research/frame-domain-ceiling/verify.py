"""Offline, standard-library reconstruction and complete fixed-word frame ceiling."""
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
if not __debug__:raise SystemExit('Keep assertions enabled')
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=Path,required=True);a=ap.parse_args();O=a.work.resolve();assert not O.exists() and not O.is_relative_to(P)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((P/'MANIFEST.json').read_text());assert manifest=={p.relative_to(P).as_posix():sha(p) for p in P.rglob('*') if p.is_file() and p!=P/'MANIFEST.json' and '__pycache__' not in p.parts}
source=json.loads((P/'SOURCES.json').read_text())
for rel,pin in source['files'].items():
 b=(P/rel).read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==pin['git_blob'],rel
O.mkdir(parents=True);env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
stages=[]
def run(name,script,*args,reject=False):
 log=O/(name+'.log')
 with log.open('w') as f:r=subprocess.run([sys.executable,'-B',str(P/'code/run.py'),str(script),*map(str,args)],env=env,stdout=f,stderr=subprocess.STDOUT)
 stages.append(dict(name=name,exit=r.returncode,rejection_expected=reject,log_sha256=sha(log)))
 assert (r.returncode!=0) if reject else (r.returncode==0),(name,log.read_text()[-3000:])
 print('PASS',name,flush=True)
run('source-static44',P/'vendor/static44/replay.py','--out',O/'static44')
run('source-548-lifts',P/'code/port_frames.py','--input',O/'static44/FULL-WORD.json.gz','--source',P/'data/PR534-WORD.json.gz','--gk',P/'vendor/static44/gk','--out',O/'lifted')
run('source-548-syndrome',P/'code/apply_syndrome.py','--input',O/'lifted/FULL-WORD.json.gz','--gk',P/'vendor/static44/gk','--out',O/'syndrome')
run('source-551-slice',P/'code/slice.py',O/'syndrome/FULL-WORD.json.gz',O/'sliced')
run('source-551-frames',P/'code/build_frames.py',O/'sliced/FULL-WORD.json.gz',O/'word')
word=O/'word/FULL-WORD.json.gz'
run('all-frame-duals-and-global-ceiling',P/'code/check_duals.py',word,O/'proof')
for mutant in ['drop_component','inflate_dual','alter_domain','accepted_endpoint']:
 run('reject-'+mutant,P/'code/check_duals.py',word,O/('mutant-'+mutant),'--mutant',mutant,reject=True)
result=json.loads((O/'proof/RESULT.json').read_text());result.update(controls=[s['name'] for s in stages if s['rejection_expected']],manifest_sha256=sha(P/'MANIFEST.json'))
assert result['status']=='PASS_COMPLETE_FIXED_WORD_FRAME_CEILING' and result['components']==71
assert manifest=={p.relative_to(P).as_posix():sha(p) for p in P.rglob('*') if p.is_file() and p!=P/'MANIFEST.json' and '__pycache__' not in p.parts}
(O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(O/'RECEIPT.json').write_text(json.dumps(dict(stages=stages,result_sha256=sha(O/'RESULT.json'),manifest_sha256=sha(P/'MANIFEST.json'),python=sys.version),indent=2)+'\n')
print(result['status'],result['excluded_b_decimal'],flush=True)
