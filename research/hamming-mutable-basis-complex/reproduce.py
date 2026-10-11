import hashlib,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
scripts=['hamming_packets.py', 'hamming_full.py', 'audit_full.py', 'phase_full.py', 'integrate.py', 'replay_ir.py']
steps=[]
for script in scripts:
 start=time.monotonic()
 result=subprocess.run([sys.executable,'-B',str(ROOT/'work/complex-network'/script)],cwd=ROOT,check=True)
 steps.append({'script':script,'exit_code':result.returncode,'seconds':time.monotonic()-start})
 print('REPLAY STEP PASS',script,flush=True)
expected=json.loads((ROOT/'EXPECTED.json').read_text())
actual={name:hashlib.sha256((ROOT/'work/complex-network/hamming'/name).read_bytes()).hexdigest() for name in expected}
assert actual==expected,(actual,expected)
receipt=json.loads((ROOT/'work/complex-network/hamming/INDEPENDENT-REPLAY.json').read_text())
assert receipt['status']=='PASS_INDEPENDENT_NEW_STRUCTURAL_IR_REPLAY'
assembly=json.loads((ROOT/'work/complex-network/hamming/INTEGRATION.json').read_text())
out={'status':'PASS_FRESH_OFFLINE_STRUCTURAL_HAMMING_REPLAY','steps':steps,'byte_identical_artifacts':actual,
     'complex_b':assembly['complex_b'],'conditional_kappa':assembly['prospective_kappa'],
     'scope':'Finite written scalar-interface extension; inherited all-size compiler and analytic assumptions retained.'}
(ROOT/'REPLAY.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS FRESH OFFLINE STRUCTURAL HAMMING REPLAY',flush=True)
