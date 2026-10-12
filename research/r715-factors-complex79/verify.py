"""Source-bound fresh supplier composition, with explicit completed-provider reuse."""
from pathlib import Path
import argparse,json,hashlib,subprocess,sys,os,time,shutil
assert __debug__
SELF=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);ap.add_argument('--research-root',type=Path,default=SELF.parent);ap.add_argument('--provider-output',type=Path);a=ap.parse_args();out=a.output.resolve();research=a.research_root.resolve();assert not out.exists() and not out.is_relative_to(research)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inv(p):return {f.relative_to(p).as_posix():sha(f) for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts}
pin=read(SELF/'SOURCE.json');ROOT=SELF.parent/pin['bit_package']
def integrity():
 own=inv(SELF);own.pop('MANIFEST.json');assert own==read(SELF/'MANIFEST.json')
 assert inv(SELF/'upstream478')==read(SELF/'UPSTREAM-INVENTORY.json')
 assert sha(ROOT/'MANIFEST.json')==pin['bit_manifest_sha256'];actual=inv(ROOT);actual.pop('MANIFEST.json');assert actual==read(ROOT/'MANIFEST.json')
 # The inherited bit/native engines are covered by the same pinned dependency inventory as the earlier full wrapper.
 source=read(ROOT/'SOURCE.json');cx=research/'e8-complex-adapted-kernel';cp=source['complex']
 assert sha(cx/'MANIFEST.json')==cp['manifest_sha256'] and sha(cx/'SOURCE.json')==cp['source_sha256']
 actual=inv(cx);actual.pop('MANIFEST.json');assert actual==read(cx/'MANIFEST.json')
 for name,x in read(cx/'SOURCE.json')['packages'].items():assert inv(research/name)==x['files'],name
integrity();out.mkdir();steps=[]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',PYTHONPATH=os.pathsep.join([str(research/'e8-r740-replica32/code'),str(research/'idle-axis-hosting')]));env.pop('PYTHONOPTIMIZE',None)
if Path('/opt/homebrew/include/boost').exists():env.setdefault('BOOST_INCLUDE','/opt/homebrew/include')
portable=research/'e8-r740-replica32/parent436/portable-include';env['CPLUS_INCLUDE_PATH']=str(portable)+(os.pathsep+env['CPLUS_INCLUDE_PATH'] if env.get('CPLUS_INCLUDE_PATH') else '')
if sys.platform=='darwin':env.setdefault('CXX','/usr/bin/clang++')
def run(name,cmd):
 print('RUN',name,flush=True);start=time.monotonic();log=out/(name+'.log')
 with log.open('w') as f:q=subprocess.run(list(map(str,cmd)),env=env,stdout=f,stderr=subprocess.STDOUT)
 if q.returncode:raise RuntimeError((name,q.returncode,log.read_text()[-4000:]))
 steps.append(dict(name=name,seconds=round(time.monotonic()-start,2),log_sha256=sha(log)));print('PASS',name,flush=True)
def py(name,path,*args):run(name,[sys.executable,'-B',path,*args])
try:
 up=out/'provider-source';shutil.copytree(SELF/'upstream478',up)
 declared=read(up/'MANIFEST.json');assert sha(up/'MANIFEST.json')==pin['original_manifest_sha256']
 actual=inv(up);actual.pop('MANIFEST.json');assert set(declared)-set(actual)=={'.gitattributes'} and declared['.gitattributes']==pin['missing_attributes_sha256'];assert all(declared[k]==v for k,v in actual.items())
 assert read(SELF/'ADAPTED-PROVIDER-MANIFEST.json')==actual
 (up/'MANIFEST.json').write_bytes((SELF/'ADAPTED-PROVIDER-MANIFEST.json').read_bytes());assert sha(up/'MANIFEST.json')==pin['adapter_manifest_sha256']
 (out/'MANIFEST-ADAPTER.json').write_text(json.dumps(dict(original=pin['original_manifest_sha256'],adapted=pin['adapter_manifest_sha256'],only_change='Remove absent .gitattributes from manifest inventory; all existing source/input bytes unchanged'),indent=2)+'\n')
 provider=a.provider_output.resolve() if a.provider_output else out/'provider'
 if a.provider_output:
  for rel,h in pin['reuse_files'].items():assert sha(provider/rel)==h,rel
 else:py('fresh-full-provider478',up/'verify.py',provider)
 receipt=read(provider/'RECEIPT.json');assert receipt['status']=='PASS_R715_NEXT_FULL_COMPOSITION' and receipt['manifest_sha256']==pin['adapter_manifest_sha256']
 previous=read(provider/'RESULT.json');expected=read(up/'EXPECTED.json')
 for k in ['kappa','bit_lower','complex_lower','bit_profile','complex_profile']:assert previous[k]==expected[k],k
 py('complex-byte-and-content-binding',SELF/'verify_complex_content.py',provider,SELF/'COMPLEX-CONTENT.json',out/'COMPLEX-CONTENT-RECEIPT.json')
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
 py('fresh-nine-stage-reference',up/'vendor/runtime/geometry_k.py','--source',up/'inputs/geometry','--out',out/'reference-nine','--stages',9,'--no-timing')
 py('audit',ROOT/'code/audit.py',base,out/'reference-nine',bit)

 py('combined-invoice-and-outer',up/'code/assemble.py',out,bit,bit/'AUDIT.json',out/'RESULT.json','--complex',provider/'complex','--engines',up/'engines','--inherited',up/'inherited','--route-extra',6,'--nine','bit','--label','PR478','--parent-kappa','1295508560071773/1000000000000000000')
 result=read(out/'RESULT.json');expected=read(SELF/'EXPECTED.json')
 for key in ['kappa','bit_lower','complex_lower','binding_component','bit_profile','complex_profile','bit','complex','bit_template_sha256','emitted_program_sha256']:assert result[key]==expected[key],key
 assert result['complex_template_sha256']==read(out/'COMPLEX-CONTENT-RECEIPT.json')['actual_template_sha256']
 integrity();receipt=dict(status='PASS_FACTORS_COMPLEX79_COMPLETED_PROVIDER_REUSED' if a.provider_output else 'PASS_FULL_FACTORS_COMPLEX79_COMPOSITION',kappa=result['kappa'],python=sys.version.split()[0],manifest_sha256=sha(SELF/'MANIFEST.json'),source_sha256=sha(SELF/'SOURCE.json'),provider_receipt_sha256=sha(provider/'RECEIPT.json'),steps=steps,scope='Whole-family residuals, same-owner spectators and inherited conditional compiler/analytic interfaces; inventory-only upstream packaging adapter is explicit.')
 (out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
except BaseException as e:
 (out/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),steps=steps),indent=2)+'\n');raise
