from pathlib import Path
import json,subprocess,sys,tempfile
root=Path(__file__).resolve().parent;pkg=root/'research/complex-k492-frame-bound'
with tempfile.TemporaryDirectory(prefix='frame-bound-') as td:
 out=Path(td)/'result.json'
 subprocess.run([sys.executable,'-I','-B',str(pkg/'verify.py'),'--out',str(out)],check=True,timeout=300)
 actual=json.loads(out.read_text());expected=json.loads((pkg/'RESULT.json').read_text());assert actual==expected
 print('PASS complete fixed RESULT.json equality: four oriented provider programs and both global moment engines',flush=True)
r=subprocess.run([sys.executable,'-I','-B',str(pkg/'verify.py'),'--controls'],capture_output=True,text=True,timeout=600);print(r.stdout,flush=True);assert r.returncode==0,r.stderr
expected={'drop_component':'one certificate per component','inflate_dual':'negative reduced cost','alter_domain':'incomplete domain','accepted_endpoint':'baseline global moment must exceed one','suboptimal_baseline':'dual objective differs','wrong_word':'input payload pin'}
for ctl,reason in expected.items():
 lines=[l for l in r.stdout.splitlines()if l.startswith('REJECTED control '+ctl+' - ')];assert len(lines)==1 and reason in lines[0],(ctl,lines)
assert 'PASS_CONTROLS 6 of 6 rejected' in r.stdout
r=subprocess.run([sys.executable,'-I','-O','-B',str(pkg/'verify.py')],capture_output=True,text=True,timeout=30);assert r.returncode!=0 and 'assertions are the proof checks' in r.stderr
print('PASS six named rejection predicates and optimized-mode refusal',flush=True)
