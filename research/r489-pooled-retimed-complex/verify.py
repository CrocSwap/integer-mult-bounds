"""Fresh pinned suppliers, whole-owner pooling, independent physical audits and exact assembly.
OpenAI Codex. No network or optimizer; outputs must be outside immutable source.
"""
import argparse,concurrent.futures,gzip,hashlib,json,os,subprocess,sys,threading,time
from pathlib import Path
if not __debug__:raise RuntimeError('assertions must remain enabled')
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('out',type=Path);ap.add_argument('--boost-include',type=Path,required=True);ap.add_argument('--cxx',default='c++');a=ap.parse_args()
OUT=a.out.resolve();assert not OUT.exists() and not OUT.is_relative_to(ROOT)
BIT=ROOT/'vendor/bit';COMPLEX=ROOT/'vendor/complex/e8-complex-gauge-kernel';CODE=ROOT/'code'
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inventory():return {str(p.relative_to(ROOT)):sha(p)for p in ROOT.rglob('*')if p.is_file()and p!=ROOT/'MANIFEST.json'and '__pycache__'not in p.parts}
def integrity():
 assert inventory()==read(ROOT/'MANIFEST.json'),'root source manifest'
 for p,h in read(ROOT/'SOURCE.json')['files'].items():assert sha(ROOT/p)==h,p
integrity();OUT.mkdir();start=time.monotonic();steps=[];lock=threading.Lock()
env=dict(os.environ,PYTHON=sys.executable,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',BOOST_INCLUDE=str(a.boost_include),CXX=a.cxx);env.pop('PYTHONOPTIMIZE',None)
def record(name,rc,t,log):
 with lock:
  steps.append(dict(name=name,returncode=rc,seconds=round(time.monotonic()-t,3),log_sha256=sha(log)))
  (OUT/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n')
 assert rc==0,(name,log.read_text()[-6000:]);print('PASS',name,flush=True)
def run(name,args,cwd=None,extra=None):
 t=time.monotonic();log=OUT/(name+'.log');print('RUN',name,flush=True)
 with log.open('w')as f:r=subprocess.run(list(map(str,args)),cwd=cwd,env=env|dict(extra or {}),stdout=f,stderr=subprocess.STDOUT)
 record(name,r.returncode,t,log)
def py(name,p,*args,**kwargs):run(name,[sys.executable,'-B',p,*args],**kwargs)
def bit_worker():
 run('complete493',['bash',BIT/'verify.sh',OUT/'bit'])
 py('independent493-local-owners',CODE/'audit493/review_local.py',BIT,OUT/'bit',OUT/'BIT-LOCAL-OWNERS.json')
 py('independent493-invoice',CODE/'audit493/review_invoice.py',BIT,OUT/'bit',OUT/'BIT-INVOICE.json')
def complex_worker():
 # The guarded instance and end-to-end passes start only after the variant's
 # completed stage receipt exists; they then read immutable finished artifacts.
 log=OUT/'complete484.log';t=time.monotonic();guards=[];guarddir=OUT/'guarded';guarddir.mkdir()
 print('RUN complete484',flush=True)
 with log.open('w')as f:
  q=subprocess.Popen([sys.executable,'-B',str(COMPLEX/'verify.py'),str(OUT/'complex')],env=env,stdout=f,stderr=subprocess.STDOUT)
  while q.poll()is None:
   ready=OUT/'complex/gauge80-kernel42/STEPS.json'
   if ready.exists()and not guards:
    try:read(ready)
    except json.JSONDecodeError:
     time.sleep(.1);continue
    for script in ['lg_instances.py','lg_e2e.py']:
     name='guarded-'+Path(script).stem;gl=OUT/(name+'.log');gf=gl.open('w');gt=time.monotonic()
     print('RUN',name,flush=True)
     p=subprocess.Popen([sys.executable,'-B',str(CODE/'guarded_lemma.py'),str(COMPLEX),script,'gauge80-kernel42'],cwd=guarddir,env=env|{'LG_BASE':str(OUT/'complex')},stdout=gf,stderr=subprocess.STDOUT)
     guards.append((name,p,gf,gt,gl))
   time.sleep(.5)
  rc=q.wait()
 record('complete484',rc,t,log)
 if not guards:
  for script in ['lg_instances.py','lg_e2e.py']:
   py('guarded-'+Path(script).stem,CODE/'guarded_lemma.py',COMPLEX,script,'gauge80-kernel42',cwd=guarddir,extra={'LG_BASE':str(OUT/'complex')})
 for name,p,f,gt,gl in guards:
  rc=p.wait();f.close();record(name,rc,gt,gl)
try:
 header=a.boost_include.resolve()/'boost/multiprecision/cpp_int.hpp'
 assert header.is_file() and not (BIT/'portable-include/boost').exists()
 probe=OUT/'boost-probe.cpp'
 probe.write_text('#include <boost/multiprecision/cpp_int.hpp>\n#include <iostream>\nint main(){boost::multiprecision::cpp_int n=1; n<<=256; std::cout << n+1 << "\\n";}\n')
 run('compiler-version',[a.cxx,'--version'])
 run('boost-header-trace',[a.cxx,'-std=c++17','-H','-I'+str(BIT/'portable-include'),'-I'+str(a.boost_include),str(probe),'-o',OUT/'boost-probe'])
 run('boost-arbitrary-integer',[OUT/'boost-probe'])
 assert int((OUT/'boost-arbitrary-integer.log').read_text().strip())==(1<<256)+1
 trace=(OUT/'boost-header-trace.log').read_text();assert str(header) in trace or str(a.boost_include/'boost/multiprecision/cpp_int.hpp') in trace
 (OUT/'TOOLCHAIN.json').write_text(json.dumps(dict(compiler=a.cxx,compiler_version_log_sha256=sha(OUT/'compiler-version.log'),boost_cpp_int_header=str(header),boost_cpp_int_header_sha256=sha(header),header_trace_sha256=sha(OUT/'boost-header-trace.log'),exact_257bit_probe=True),indent=2)+'\n')
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
  futures=[pool.submit(bit_worker),pool.submit(complex_worker)]
  for f in futures:f.result()
 py('rebuild-retimed',CODE/'rebuild_retimed.py',COMPLEX,OUT/'complex/gauge80-kernel42',ROOT/'data/RETIME-FRAMES.json.gz',OUT/'retimed/gauge80-kernel42')
 base=OUT/'retimed/gauge80-kernel42';host=OUT/'hosted'
 py('independent-retimed-frames',CODE/'review_frames.py','--baseline',OUT/'complex/gauge80-kernel42/split-centres','--candidate',base/'split-centres','--out',OUT/'RETIME-FRAME-REVIEW.json')
 retimedguard=OUT/'retimed-guarded';retimedguard.mkdir()
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
  futs=[pool.submit(py,'retimed-guarded-'+Path(script).stem,CODE/'guarded_lemma.py',COMPLEX,script,'gauge80-kernel42',cwd=retimedguard,extra={'LG_BASE':str(OUT/'retimed')})for script in ['lg_instances.py','lg_e2e.py']]
  for f in futs:f.result()
 py('pooled-emitter',CODE/'emit_pooled.py',COMPLEX,base,ROOT/'data/COLORED-OWNERS.json.gz',host)
 py('independent-pooled-controller',CODE/'audit_pooled.py',base,host,OUT/'HOSTING-AUDIT.json')
 py('finite-serial-pool-operator',CODE/'finite_serial_pool.py',OUT/'FINITE-SERIAL-POOL.json')
 py('independent-pooled-physical-invoice',CODE/'audit484/audit_pooled_candidate.py','--parent',base,'--hosted',host,'--bit-result',OUT/'bit/RESULT.json','--phases',base/'work/complex-nine-native/DATA-PHASES.json','--controller-audit',OUT/'HOSTING-AUDIT.json','--out',OUT/'admission')
 py('independent-composition',CODE/'review_composition.py',OUT/'admission',OUT/'complex/p442/parent/changed',base/'split-centres',base/'hosted',host,OUT/'bit/RESULT.json',OUT/'COMPOSITION-REVIEW.json')
 r=read(OUT/'admission/EXACT-ASSEMBLY.json');own=read(OUT/'admission/OWNERS-AND-PROFILE.json');inv=read(OUT/'admission/PREFIX-AND-INVOICE.json');b=read(OUT/'bit/RESULT.json')
 mathresult={k:r[k]for k in ['complex_lower','next_b_rejected','bit_lower','kappa','kappa_decimal','bit_charged_three_level_coefficient_bits','external_row_allowance','binding_component','strict_outer_constraints','outer_controls','bootstrap']}
 mathresult.update(complex_profile=own['paid_profile'],complex_live=own['live'],complex_physical=own['physical'],complex_invoice=inv['finite'],bit_profile=b['bit_profile'],bit_finite=b['bit'],bit_emitted_program_sha256=b['emitted_program_sha256'])
 (OUT/'EXACT-MATH.json').write_text(json.dumps(mathresult,indent=2)+'\n')
 expected=read(ROOT/'EXPECTED.json')
 for k,v in expected.items():assert mathresult[k]==v,(k,mathresult.get(k),v)
 integrity()
 artifacts=['guarded/INSTANCES-gauge80-kernel42.json','guarded/E2E-gauge80-kernel42.json','retimed-guarded/INSTANCES-gauge80-kernel42.json','retimed-guarded/E2E-gauge80-kernel42.json','retimed/gauge80-kernel42/RECEIPT.json','retimed-guarded/PREOP-GUARDS-lg_instances.json','retimed-guarded/PREOP-GUARDS-lg_e2e.json','RETIME-FRAME-REVIEW.json','TOOLCHAIN.json','BIT-LOCAL-OWNERS.json','BIT-INVOICE.json','HOSTING-AUDIT.json','FINITE-SERIAL-POOL.json','COMPOSITION-REVIEW.json','complex/RECEIPT.json','bit/RESULT.json','admission/ADMISSION.json','admission/GLOBAL-PREFIX.json','admission/OWNERS-AND-PROFILE.json','admission/PREFIX-AND-INVOICE.json','admission/EXACT-ASSEMBLY.json','guarded/PREOP-GUARDS-lg_instances.json','guarded/PREOP-GUARDS-lg_e2e.json']
 receipt=dict(status='PASS_FRESH_R489_POOLED_RETIMED_WHOLE_COMPLEX',artifacts={p:sha(OUT/p)for p in artifacts},kappa=r['kappa'],kappa_decimal=r['kappa_decimal'],python=sys.version.split()[0],source_manifest_sha256=sha(ROOT/'MANIFEST.json'),exact_math_sha256=sha(OUT/'EXACT-MATH.json'),steps=steps,seconds=round(time.monotonic()-start,3),scope='Conditional whole-owner retimed finite construction; both pinned suppliers reconstructed and the changed word recompiled, scalar dirty restoration/reflected ledgers/actual owner maps/complete invoices and47inequalities checked. Inherited all-size compiler, LemmaA realization, precision/tape, restored-row and analytic contracts remain.')
 (OUT/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k!='steps'},indent=2))
except BaseException as e:
 (OUT/'FAILURE.json').write_text(json.dumps(dict(error=repr(e),steps=steps),indent=2)+'\n');raise
