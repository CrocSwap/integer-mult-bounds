"""Full pinned complex supplier plus fresh R715 component; explicit completed-parent reuse."""
from pathlib import Path
import argparse,json,hashlib,subprocess,sys,os,time,shutil
assert __debug__
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);ap.add_argument('--research-root',type=Path,default=ROOT.parent);ap.add_argument('--complex-output',type=Path);a=ap.parse_args();research=a.research_root.resolve();out=a.output.resolve();assert not out.exists() and not out.is_relative_to(research)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inv(p):return {f.relative_to(p).as_posix():sha(f) for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts}
def integrity():
 actual=inv(ROOT);actual.pop('MANIFEST.json');assert actual==read(ROOT/'MANIFEST.json')
 source=read(ROOT/'SOURCE.json');cx=research/'e8-complex-adapted-kernel';pin=source['complex']
 assert sha(cx/'MANIFEST.json')==pin['manifest_sha256'] and sha(cx/'SOURCE.json')==pin['source_sha256']
 actual=inv(cx);actual.pop('MANIFEST.json');assert actual==read(cx/'MANIFEST.json')
 for name,p in read(cx/'SOURCE.json')['packages'].items():assert inv(research/name)==p['files'],name
 assert sha(research/'complex-kernel-mixed151/code/parent_runner.py')==source['metadata_runner_sha256']
 assert sha(research/'complex-kernel-mixed151/code/bash-env.sh')==source['bash_env_sha256']
integrity();out.mkdir();steps=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',PYTHON=sys.executable,E8_REPLAY_PHASES='1',PYTHONPATH=os.pathsep.join([str(research/'e8-r740-replica32/code'),str(research/'idle-axis-hosting')]));env.pop('PYTHONOPTIMIZE',None)
if ' ' in str(research) or ' ' in str(out):env['BASH_ENV']=str(research/'complex-kernel-mixed151/code/bash-env.sh')
if 'BOOST_INCLUDE' not in env and Path('/opt/homebrew/include/boost').exists():env['BOOST_INCLUDE']='/opt/homebrew/include'
def run(name,cmd):
 print('RUN',name,flush=True);log=out/(name+'.log');start=time.monotonic()
 with log.open('w') as f:q=subprocess.run(list(map(str,cmd)),env=env,stdout=f,stderr=subprocess.STDOUT)
 if q.returncode:raise RuntimeError((name,q.returncode,log.read_text()[-4000:]))
 steps.append(dict(name=name,seconds=round(time.monotonic()-start,2),log_sha256=sha(log)));print('PASS',name,flush=True)
def py(name,path,*args):run(name,[sys.executable,'-B',path,*args])
try:
 cx=a.complex_output.resolve() if a.complex_output else out/'complex458'
 if not a.complex_output:py('full-complex458',research/'complex-kernel-mixed151/code/parent_runner.py',research/'e8-complex-adapted-kernel/verify.py',cx)
 receipt=read(cx/'RECEIPT.json');pin=read(ROOT/'SOURCE.json')['complex'];assert receipt['status']=='PASS_COMPLEX_ADAPTED_KERNEL_FULL_COMPOSITION' and receipt['mode']=='full'
 assert receipt['manifest_sha256']==pin['manifest_sha256'] and receipt['source_sha256']==pin['source_sha256']
 py('source-reconstruction',ROOT/'verify_component.py',out/'reconstruction','--research-root',research)
 B=research/'e8-r740-replica32/parent436/code/bit';base=out/'local';bit=out/'bit';bins=out/'bin';bins.mkdir();word=read(ROOT/'data/word.json');R=word['R']
 py('export',B/'export_records.py',ROOT/'data/word.json.gz',base/'records')
 py('physical-labels',ROOT/'code/labels.py',base/'records')
 py('mixing-controls',research/'e8-target-mixing-whole/upstream450/mix_check.py',ROOT/'data/word.json.gz',base/'records','--controls',ROOT/'data/base.json.gz')
 py('stage-cohort',B/'regression/stage_cohort.py',base/'records',base/'records',base/'cin',base/'cout')
 cxx=os.environ.get('CXX',shutil.which('c++'));assert cxx
 inc=['-I'+str(research/'e8-r740-replica32/parent436/portable-include'),'-I'+str(B/'checkers')]
 boost=os.environ.get('BOOST_INCLUDE','/opt/homebrew/include' if Path('/opt/homebrew/include/boost').exists() else '/usr/include');inc+=['-I'+boost]
 for name,src,defs in [('legality','legality_h.cpp',['-DNCOPY=9']),('legality_ncopy_h','legality_h.cpp',[]),('columns_h','columns_h.cpp',['-DNCOPY=9','-DVPORTS=120',f'-DRHELP={R}']),('columns_k5','columns_k.cpp',['-DNCOPY=9','-DVPORTS=120',f'-DRHELP={R}','-DKPAIRS=5'])]:
  run('compile-'+name,[cxx,'-O2','-std=c++17','-DHDIM=8',*defs,*inc,'-o',bins/name,B/'checkers'/src])
 run('official-legality',[bins/'legality',base/'cin',base/'cout',base/'cout/legality.json'])
 for name,file in [('columns_h','columns.json'),('columns_k5','columns_k5.json')]:run(name,[bins/name,base/'cout/COHORT249-RECORDS.bin',base/'cout'/file])
 py('record-mutations',ROOT/'code/mutate_records.py',base/'records',base/'cin',base/'cout',bins/'legality',bins/'columns_k5',bins/'legality_ncopy_h')
 py('gram',B/'checkers/gram_frames.py',base/'records','--gram','e8ham','--h',8,'--positive')
 py('geometry',ROOT/'code/geometry.py','--source',research/'e8-r740-replica32/parent436','--out',bit)
 py('emit',ROOT/'code/emit.py','--word',ROOT/'data/word.json.gz','--local-check',base,'--out',bit,'--isometries',ROOT/'data/residual-isometries.json')
 py('audit',ROOT/'code/audit.py',base,cx/'parent454/parent451/parent445/parent444/base443/candidate/nine',bit)
 py('invoice-and-outer',ROOT/'assemble.py',bit,research,cx)
 result=read(bit/'RESULT.json');expected=read(ROOT/'EXPECTED.json')
 for k,v in expected.items():assert result[k]==v,(k,result[k],v)
 (out/'RESULT.json').write_bytes((bit/'RESULT.json').read_bytes());integrity()
 receipt=dict(status='PASS_R715_WARM_FACTORS_COMPONENT_COMPLETED_COMPLEX_REUSED' if a.complex_output else 'PASS_FULL_R715_WARM_FACTORS_COMPOSITION',python=sys.version.split()[0],kappa=result['kappa'],manifest_sha256=sha(ROOT/'MANIFEST.json'),source_sha256=sha(ROOT/'SOURCE.json'),complex_receipt_sha256=sha(cx/'RECEIPT.json'),metadata_portability_sha256=sha(cx/'METADATA-PORTABILITY.json'),steps=steps)
 (out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
except BaseException as e:
 (out/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),steps=steps),indent=2)+'\n');raise
