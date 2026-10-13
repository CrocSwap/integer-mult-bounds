"""Fresh changed bit/frame/bank checks, with separately audited parent suppliers.
Does not claim to execute original --full (which reruns the parent complex code).
"""
import importlib.util,sys,json
from pathlib import Path
n=int(sys.argv[1]);assert n in (211,223)
pkg={211:'cascade-frames-bit',223:'served-diagonal-bit'}[n]
base=Path(f'/tmp/integer-mult-export{n}/research/{pkg}')
bit=Path('/tmp/integer-mult-export200');complex_root=Path('/tmp/integer-mult-export193')
sys.path.insert(0,str(base))
spec=importlib.util.spec_from_file_location('candidate_verifier',base/'verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
sys.argv=[str(base/'verify.py'),'--complex-root',str(complex_root),'--bit-root',str(bit)]
v.main() # complete original source binding, cached-profile arithmetic and controls
old=json.loads((base/'certificate.json').read_text())
if n==211:
 admitted=v.serial(v.frames.admit(bit));assert admitted==old['admitted']
 physical=v.packing.build(bit,admitted['profile'])
 result=v.arithmetic.build(complex_root,bit,physical,admitted)
 fresh=dict(admitted=admitted,physical=physical,arithmetic=result)
else:
 derivation=v.rederive(bit)
 served=v.capture(base/'bit/served_prove.py',str(bit/v.BIT_PACKAGE),str(v.SERVED))
 physical=v.packing.build(bit,v.SERVED,served['profile'])
 result=v.arithmetic.build(complex_root,bit,physical,served)
 fresh=dict(derivation=derivation,served=served,physical=physical,arithmetic=result)
fresh['independent']=v.audit.run(result,result['unpacked_profile']);fresh['bank_controls']=v.controls.run()
for k,val in v.serial(fresh).items():assert val==old[k],('Fresh changed-work certificate mismatch',k)
v.main() # repeat source binding after changed-work replay
print(json.dumps(dict(status='PASS_FRESH_CHANGED_BIT_AND_BANKS',pr=n,parent_supplier_replays_separate=True,original_full_entrypoint_executed=False,kappa=v.serial(result)['after_packing']['kappa'],fresh=v.serial(fresh)),indent=2))
