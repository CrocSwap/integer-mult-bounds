"""Fair route comparison checks; Apache-2.0. Dugongue with OpenAI Codex assistance."""
from pathlib import Path
from hashlib import sha256
import json,subprocess,sys,tempfile,shutil
R=Path(__file__).resolve().parent

def need(ok,why):
 if not ok:raise ValueError(why)

def authenticate(root):
 m=json.loads((root/'MANIFEST.json').read_bytes())
 names={str(f.relative_to(root)).replace(chr(92),'/') for f in root.rglob('*') if f.is_file() and '__pycache__' not in f.parts and f!=root/'MANIFEST.json'}
 need(names==set(m),'Unexpected or missing file')
 for n,h in m.items():need(sha256((root/n).read_bytes()).hexdigest()==h,'Source drift: '+n)
 return len(m)

def check():
 count=authenticate(R)
 if '--hash-only' in sys.argv:return {'status':'PASS_COMPARISON_HASHES','files':count}
 sources=json.loads((R/'SCIENTIFIC-SOURCES.json').read_bytes())
 for n,h in sources['native']['files'].items():need(sha256((R/'native'/n).read_bytes()).hexdigest()==h,'Native source drift')
 native=json.loads((R/'native/RESULT.json').read_bytes())
 need(native['word_ram_kappa']=='15108879/5000000000','Native comparison exponent changed')
 with tempfile.TemporaryDirectory(prefix='ram-compare-') as td:
  temp=Path(td);outputs={}
  for i,s in enumerate(['baseline/check_comparison.py','check_packed_simulation.py']):
   r=subprocess.run([sys.executable,'-I','-B','-X','pycache_prefix='+str(temp/str(i)),str(R/s)],cwd=R,capture_output=True,text=True,encoding='utf-8',timeout=90)
   need(r.returncode==0,s+': '+r.stderr);outputs[s]=json.loads(r.stdout)
  need(outputs['baseline/check_comparison.py']['strict_computational_superiority_established'] is False,'Scope changed')
  copy=temp/'controls';shutil.copytree(R,copy,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  def guard():return subprocess.run([sys.executable,'-I','-O','-B','-X','pycache_prefix='+str(temp/'guard'),str(copy/'verify.py'),'--hash-only'],capture_output=True,timeout=20).returncode
  need(guard()==0,'Clean baseline rejected');f=copy/'baseline/PROOF.md';b=f.read_bytes();f.write_bytes(b+bytes([10]));need(guard()!=0,'Changed source accepted');f.write_bytes(b);need(guard()==0,'Restored baseline rejected')
 return {'status':'PASS_FAIR_RAM_ROUTE_COMPARISON','new_kappa_claimed':False,'strict_native_superiority_claimed':False,'source_corruption_control':'REJECTED_AFTER_CLEAN_BASELINE_ACCEPTED','components':outputs,'scope':'Exact finite source/parameter/window controls and supplied informal constructive proofs. No full multiplier, practical benchmark, new Lean audit or new exponent.'}
if __name__=='__main__':print(json.dumps(check(),indent=2))
