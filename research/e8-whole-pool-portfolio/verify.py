"""Offline changed-construction replay. Python3.11+, SymPy, C++17 and Boost headers.
All inherited all-size interfaces remain conditional. No network or optimizer.
"""
from pathlib import Path
import os,sys,json,gzip,hashlib,shutil,subprocess,time,importlib.util
assert __debug__
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
OUT=Path(sys.argv[1]).resolve();assert not OUT.exists() and not OUT.is_relative_to(ROOT)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def integrity():
 actual={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*') if p.is_file() and p.name!='MANIFEST.json' and '__pycache__' not in p.parts}
 assert actual==read(ROOT/'MANIFEST.json'),'Package manifest mismatch'
integrity();OUT.mkdir(parents=True);(OUT/'bin').mkdir();start=time.monotonic();steps=[]
env=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',PYTHONPATH=os.pathsep.join(map(str,[ROOT/'vendor/runtime',ROOT/'vendor/complex',ROOT/'code'])),TMP=str(OUT/'bin'),TEMP=str(OUT/'bin'));env.pop('PYTHONOPTIMIZE',None)
PY=sys.executable

def run(name,args,cwd=None):
 t=time.monotonic();p=OUT/(name+'.log');print('RUN',name,flush=True)
 with p.open('w',encoding='utf-8') as f:r=subprocess.run(list(map(str,args)),env=env,cwd=cwd,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,(name,p.read_text(encoding='utf-8')[-5000:])
 steps.append(dict(name=name,seconds=round(time.monotonic()-t,3),log_sha256=sha(p)));print('PASS',name,flush=True)
def py(name,path,*args,cwd=None):run(name,[PY,'-B',path,*args],cwd)
try:
 py('target-mixing',ROOT/'vendor/runtime/mix_target.py',ROOT/'inputs/rank149.json.gz',OUT/'mixed.json')
 sp=importlib.util.spec_from_file_location('prefix',ROOT/'code/prefix.py');mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
 w,rec=mod.construct(read(OUT/'mixed.json'));b=json.dumps(w,sort_keys=True,separators=(',',':')).encode()
 assert hashlib.sha256(b).hexdigest()=='c80eadc14fc3365e61c90e7c717fb0c35c9a9a4a90da6f4bb13d6c27f3789c97'
 (OUT/'word0.json').write_bytes(b);(OUT/'PREFIX-AUDIT.json').write_text(json.dumps(rec,indent=2)+'\n')
 py('provider-two',ROOT/'code/providers.py',OUT/'word0.json',ROOT/'inputs/providers.json',2,OUT/'word2.json')
 py('provider-independent',ROOT/'code/provider_audit.py',OUT/'word2.json',OUT/'PROVIDER-AUDIT.json',OUT/'word0.json')
 cxx=os.environ.get('CXX') or shutil.which('g++') or shutil.which('clang++')
 if not cxx and Path('C:/mingw64/bin/g++.exe').exists():cxx='C:/mingw64/bin/g++.exe'
 assert cxx,'Set CXX to a C++17 compiler'
 includes=[ROOT/'vendor/native'];boost=os.environ.get('BOOST_INCLUDE')
 if boost:includes.append(Path(boost))
 for name,file,defs in [('legality','legality_h.cpp',['NCOPY=9']),('columns','columns_h.cpp',['NCOPY=9','VPORTS=120','RHELP=740']),('columns_k5','columns_k.cpp',['NCOPY=9','VPORTS=120','RHELP=740','KPAIRS=5'])]:
  run('compile-'+name,[cxx,'-O2','-std=c++17','-DHDIM=8',*['-D'+d for d in defs],*['-I'+str(p) for p in includes],'-o',OUT/'bin'/(name+('.exe' if os.name=='nt' else '')),ROOT/'vendor/native'/file])
 def exe(name):return OUT/'bin'/(name+('.exe'if os.name=='nt'else''))
 for variant in [0,2]:
  local=OUT/('local'+str(variant));local.mkdir();shutil.copyfile(OUT/('word'+str(variant)+'.json'),local/'word.json');tag='v'+str(variant)+'-'
  py(tag+'records',ROOT/'vendor/runtime/export_records.py',local/'word.json',local/'records')
  py(tag+'mixed-word',ROOT/'vendor/runtime/mix_check.py',local/'word.json',local/'records')
  py(tag+'cohort',ROOT/'vendor/runtime/stage_cohort.py',local/'records',local/'records',local/'cin',local/'cout')
  run(tag+'legality',[exe('legality'),local/'cin',local/'cout',local/'cout/legality.json'])
  for name in ['columns','columns_k5']:run(tag+name,[exe(name),local/'cout/COHORT249-RECORDS.bin',local/'cout'/(name+'.json')])
  py(tag+'gram',ROOT/'vendor/native/gram_frames.py',local/'records','--gram','e8ham','--h',8,'--positive')
  py(tag+'geometry',ROOT/'vendor/runtime/geometry_k.py','--source',ROOT/'inputs/geometry','--out',local/'nine','--stages',11,'--no-timing')
  py(tag+'global',ROOT/'vendor/runtime/global_k.py','--word',local/'word.json','--local-check',local,'--out',local/'nine','--isometries',ROOT/'inputs/residual-isometries.json','--stages',11,'--replicas',8,'--no-banks')
 py('whole-bit',ROOT/'code/emit_whole.py',OUT/'local0/nine',OUT/'local0',ROOT/'inputs/bit-selection.json',OUT/'bit',OUT/'local2')
 py('whole-bit-independent',ROOT/'code/audit_whole.py',OUT/'local0',OUT/'bit',OUT/'bit/AUDIT.json',OUT/'local2')
 cs=OUT/'complex-base/split-centres';shutil.copytree(ROOT/'inputs/complex',cs)
 py('complex-local-programs',ROOT/'vendor/complex/complex_emit.py',cwd=cs.parent)
 for ori,z in read(cs/'LOCAL-CHECKS.json').items():assert z['sha256']==read(ROOT/'inputs/complex/LOCAL-CHECKS.json')[ori]['sha256']
 co=OUT/'complex';co.mkdir()
 py('complex-data-phases',ROOT/'vendor/complex/complex_phases.py',cs/'CANONICAL-WORD.json.gz',co/'DATA-PHASES.json')
 py('whole-complex',ROOT/'code/complex_whole_emit.py',cs,co,ROOT/'inputs/complex-selection.json')
 py('whole-complex-independent',ROOT/'code/complex_whole_audit.py',co,cs,ROOT/'inputs/complex-selection.json')
 py('exact-assembly',ROOT/'code/assemble.py',OUT/'local0',OUT/'bit',OUT/'bit/AUDIT.json',OUT/'RESULT.json','--complex',co,'--engines',ROOT/'engines','--inherited',ROOT/'inherited','--route-extra',3,'--label','PR451','--variant-globals',OUT/'local2/nine/GLOBAL.json')
 result=read(OUT/'RESULT.json');expected=read(ROOT/'EXPECTED.json')
 for k in ['kappa','bit_lower','complex_lower','bit_profile','bit_template_sha256','complex_template_sha256','emitted_program_sha256']:assert result[k]==expected[k],(k,result[k],expected[k])
 assert len(read(OUT/'bit/AUDIT.json')['mutations_rejected'])>=19
 assert len(read(co/'AUDIT.json')['mutations_rejected'])==10
 integrity();receipt=dict(status='PASS_CHANGED_WHOLE_POOL_PORTFOLIO',kappa=result['kappa'],python=sys.version,seconds=round(time.monotonic()-start,3),manifest_sha256=sha(ROOT/'MANIFEST.json'),steps=steps,scope='Fresh changed local programs, whole-residual global routing, data phases and assembly. Source-bound inherited local Clifford evidence and all-size interfaces retained; no full unchanged public wrapper replay and no Lean certification.')
 (OUT/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
except BaseException as e:
 (OUT/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),completed=steps),indent=2)+'\n');raise
