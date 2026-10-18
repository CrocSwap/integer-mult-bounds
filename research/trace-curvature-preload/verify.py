"""Offline changed-word replay. No network and no optimizer are required."""
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
TEXT={'.py','.json','.md','.txt','.sh','.lean','.cpp','.h','.hpp','.sha256','.yml','.yaml','.toml'}
def textfile(p):return p.suffix.lower()in TEXT or p.name in {'LICENSE','NOTICE','SOURCE'}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8',newline='\n')
def main():
 if not __debug__:raise SystemExit('Assertions must be enabled; do not use Python -O.')
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--cxx',default=os.environ.get('CXX','c++'));ap.add_argument('--boost-include',type=Path,default=Path(os.environ.get('BOOST_INCLUDE','/usr/include')));ap.add_argument('--jobs',type=int,default=3);a=ap.parse_args()
 root=Path(__file__).resolve().parent;work=a.work.resolve();assert not work.exists()and root not in work.parents
 assert(a.boost_include/'boost/multiprecision/cpp_int.hpp').is_file(),'Install genuine Boost headers or set --boost-include.'
 man=read(root/'MANIFEST.json');assert man['format']=='sha256-lf-text-v1';expect=read(root/'EXPECTED.json')
 present={x.relative_to(root).as_posix()for x in root.rglob('*')if x.is_file()and '__pycache__'not in x.parts}
 assert present==set(man['files'])|{'MANIFEST.json'},('unlisted/missing',present^(set(man['files'])|{'MANIFEST.json'}))
 for rel,z in man['files'].items():
  f=(root/rel).resolve();assert root in f.parents;b=f.read_bytes()
  if z['mode']=='lf-text':b=b.replace(b'\r\n',b'\n')
  assert hashlib.sha256(b).hexdigest()==z['sha256'],('input hash changed',rel)
 t=time.monotonic();work.mkdir(parents=True);src=work/'source';shutil.copytree(root,src,ignore=shutil.ignore_patterns('__pycache__'))
 for f in src.rglob('*'):
  if f.is_file()and textfile(f):f.write_bytes(f.read_bytes().replace(b'\r\n',b'\n'))
 stages=[];env=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0')
 def run(name,script,*args):
  began=time.monotonic()
  with(work/(name+'.log')).open('w',encoding='utf-8')as log:r=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],stdout=log,stderr=subprocess.STDOUT,env=env)
  stages.append(dict(name=name,exit=r.returncode,seconds=time.monotonic()-began));dump(work/'STAGES.json',stages)
  if r.returncode:print((work/(name+'.log')).read_text(encoding='utf-8'),file=sys.stderr);raise SystemExit(name+' failed')
  print('PASS',name,round(stages[-1]['seconds'],2),flush=True)
 v=src/'vendor';word=work/'constructed/WORD.json.gz';n=work/'native';g=work/'global'
 run('construct-trace',src/'code/build_preload60.py','--input',v/'e8-r480-dead-totals/data/bitE8mut-r480.json.gz','--out',work/'constructed')
 run('native-checks',src/'code/run_native.py',v/'e8-bit-carrier-skeleton',word,n,'--cxx',a.cxx,'--boost-include',a.boost_include,'--jobs',a.jobs)
 geo=work/'NINE-GEOMETRY.json';geo.write_bytes(gzip.decompress((src/'inputs/NINE-GEOMETRY.json.gz').read_bytes()))
 run('global-owner-and-invoice',src/'code/run_global.py',v/'e8-r480-nine-stage',n,word,g,geo)
 run('curvature-cone',src/'code/audit_curvature.py',src/'inputs/PR510-EXPECTED.json',n/'cout/legality.json',g/'INVOICE.json',work/'CURVATURE.json')
 run('exact-assembly',src/'code/assemble_meta.py',src,g/'INVOICE.json',work/'assembly')
 run('neutral-version-transport',src/'code/transport_compensation.py',v/'e8-r480-dead-totals/data/bitE8mut-r480.json.gz',work/'neutral')
 if(src/'appendix/static44/replay.py').exists():run('static44-local-appendix',src/'appendix/static44/replay.py','--out',work/'static44')
 ans=read(work/'assembly/EXACT-ASSEMBLY.json');invoice=read(g/'INVOICE.json');own=read(g/'hosted/AUDIT.json');native=read(n/'NATIVE-REVIEW.json')
 result=dict(status='PASS_TRACE_CURVATURE_PRELOAD',kappa=ans['kappa'],kappa_decimal=ans['kappa_decimal'],bit_lower=ans['bit_lower'],complex_lower=ans['complex_lower'],global_profile=invoice['bit_profile'],word_sha256=native['word_sha256'],template_sha256=own['template_sha256'],emitted_program_sha256=own['emitted_program_sha256'],formal_columns_nine_stage=1440,hosted_residuals=own['hosted_residuals'],global_prefix_bits=invoice['bit']['prefix_bits'],two_level_coefficient_bits=invoice['bit']['two_level_coefficient_bits'],row_coefficient=invoice['bit']['row_coefficient'],outer_constraints=len(ans['strict_outer_constraints']),stages=stages,elapsed_seconds=time.monotonic()-t,scope=ans['scope'])
 for k,x in expect.items():assert result[k]==x,('frozen result mismatch',k,result[k],x)
 assert result['outer_constraints']==47 and result['hosted_residuals']==138240
 dump(work/'RESULT.json',result);print(json.dumps({k:result[k]for k in ['status','kappa_decimal','elapsed_seconds']}),flush=True)
if __name__=='__main__':main()
