"""Fresh paid-complex parent, R715 local word and whole-hosted global assembly.
Usage: verify.py NEW_ABSOLUTE_OUT [--quick] [--parent-output VERIFIED458_OUT]
Explicit parent reuse has a distinct receipt status. Apache-2.0.
Chafreaky with OpenAI Codex assistance; source authors in NOTICE.md.
"""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time
assert __debug__
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);ap.add_argument('--quick',action='store_true');ap.add_argument('--parent-output',type=Path)
args=ap.parse_args();out=args.output.resolve()
assert not out.exists() and not out.is_relative_to(ROOT.parent)
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inventory(p):return {f.relative_to(p).as_posix():sha(f) for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts}
def integrity():
 actual=inventory(ROOT);actual.pop('MANIFEST.json');assert actual==read(ROOT/'MANIFEST.json')
 for name,expected in read(ROOT/'SOURCE.json')['packages'].items():assert inventory(ROOT.parent/name)==expected['files'],name
integrity();out.mkdir(parents=True)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',PYTHON=sys.executable);env.pop('PYTHONOPTIMIZE',None)
steps=[]
def run(name,command):
 log=out/(name+'.log');started=time.monotonic();print('RUN',name,flush=True)
 with log.open('w') as f:r=subprocess.run(list(map(str,command)),env=env,stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError((name,r.returncode,log.read_text()[-5000:]))
 steps.append(dict(name=name,seconds=round(time.monotonic()-started,2),log_sha256=sha(log)));print('PASS',name,flush=True)
def py(name,path,*extra):run(name,[sys.executable,'-B',path,*extra])
try:
 parent_pkg=ROOT.parent/'e8-complex-adapted-kernel'
 if args.parent_output:parent=args.parent_output.resolve()
 else:
  parent=out/'parent458';py('parent458',parent_pkg/'verify.py',parent,*(['--quick'] if args.quick else []))
 receipt=read(parent/'RECEIPT.json');pr=read(parent/'RESULT.json')
 assert receipt['status']=='PASS_COMPLEX_ADAPTED_KERNEL_FULL_COMPOSITION'
 assert receipt['manifest_sha256']==sha(parent_pkg/'MANIFEST.json') and receipt['source_sha256']==sha(parent_pkg/'SOURCE.json')
 for k,v in read(parent_pkg/'EXPECTED.json').items():assert pr[k]==v,(k,pr[k],v)
 parent451=parent/'parent454/parent451'
 old=ROOT.parent/'e8-r740-replica32/parent436';B=old/'code/bit';ck=B/'checkers'
 local=out/'local';host=out/'bit';word=ROOT/'data/word.json.gz';bins=out/'bin';bins.mkdir()
 py('export-records',B/'export_records.py',word,local/'records')
 py('exact-reconstruction',ROOT/'code/rebuild.py',local/'records')
 py('mixing-controls',ROOT.parent/'e8-target-mixing-whole/upstream450/mix_check.py',word,local/'records','--controls',ROOT/'data/kernel-word.json.gz')
 py('physical-target-labels',ROOT/'code/labels.py',local/'records')
 py('stage-cohort',B/'regression/stage_cohort.py',local/'records',local/'records',local/'cin',local/'cout')
 for name,source,ncopy in [('legality','legality_h',9),('legality_ncopy_h','legality_h',8),('columns_h','columns_h',9),('columns_k5','columns_k',9)]:
  command=[os.environ.get('CXX','c++'),'-O2','-std=c++17','-DHDIM=8','-DVPORTS=120','-DRHELP=715','-DKPAIRS=5',f'-DNCOPY={ncopy}',
           '-I'+str(old/'portable-include'),'-I'+str(ck)]
  if os.environ.get('BOOST_INCLUDE'):command+=['-I'+os.environ['BOOST_INCLUDE']]
  command += [ck/(source+'.cpp'),'-o',bins/name];run('build-'+name,command)
 run('official-legality',[bins/'legality',local/'cin',local/'cout',local/'cout/legality.json'])
 run('official-columns',[bins/'columns_h',local/'cout/COHORT249-RECORDS.bin',local/'cout/columns.json'])
 run('official-eleven-stage-columns',[bins/'columns_k5',local/'cout/COHORT249-RECORDS.bin',local/'cout/columns_k5.json'])
 column=read(local/'cout/columns_k5.json')
 assert column['formal_columns_checked']==1915 and len(column['stages'])==11 and len(column['negative_controls'])==24
 assert all(x['rejected'] for x in column['negative_controls'])
 py('record-mutations',B/'mutate_records.py',local/'records',local/'cin',local/'cout',bins/'legality',bins/'columns_k5',bins/'legality_ncopy_h')
 py('positive-gram',ck/'gram_frames.py',local/'records','--gram','e8ham','--h',8,'--positive')
 host.mkdir();(host/'GEOMETRY.json').write_bytes((parent451/'bit/GEOMETRY.json').read_bytes())
 py('global-emission',ROOT/'code/emit.py','--word',word,'--local-check',local,'--out',host,'--isometries',ROOT/'data/residual-isometries.json')
 py('independent-global-audit',ROOT/'code/audit.py',local,parent451/'parent445/parent444/base443/candidate/nine',host)
 assert len(read(host/'AUDIT.json')['mutations_rejected'])==22
 py('finite-invoices-and-outer-assembly',ROOT/'code/assemble.py',parent,host)
 (out/'RESULT.json').write_bytes((host/'RESULT.json').read_bytes());actual=read(out/'RESULT.json')
 for k,v in read(ROOT/'EXPECTED.json').items():assert actual[k]==v,(k,actual[k],v)
 integrity()
 result=dict(status='PASS_R715_COMPONENTS_WITH_VERIFIED_PARENT_REUSE' if args.parent_output else 'PASS_R715_WHOLE_HOSTED_FULL_COMPOSITION',
             mode='parent-reuse' if args.parent_output else 'quick' if args.quick else 'full',kappa=actual['kappa'],python=sys.version.split()[0],
             manifest_sha256=sha(ROOT/'MANIFEST.json'),source_sha256=sha(ROOT/'SOURCE.json'),parent_receipt_sha256=sha(parent/'RECEIPT.json'),
             parent_manifest_sha256=receipt['manifest_sha256'],parent_mode=receipt['mode'],emitted_program_sha256=actual['emitted_program_sha256'],checks=steps)
 (out/'RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
except BaseException as e:
 (out/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),completed=steps),indent=2)+'\n');raise
