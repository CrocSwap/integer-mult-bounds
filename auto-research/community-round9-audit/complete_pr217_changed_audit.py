"""Complete PR217 assembly using separately executed fresh complex/bit stages.
Original aggregate was not run: installed scientific versions differ from its pins.
"""
from pathlib import Path
import sys,importlib.util,json,hashlib,copy
sys.dont_write_bytecode=True
base=Path('/tmp/integer-mult-export217/research/butterfly-coordinated-bit-211');sys.path.insert(0,str(base))
spec=importlib.util.spec_from_file_location('butterfly_verifier',base/'verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
c=Path('/tmp/integer-mult-export193');b=Path('/tmp/integer-mult-export202');out=Path('/tmp/integer-mult-pr217-changed')
v.check_package();before=v.check_sources(c,b)
accepted=json.loads(Path('/tmp/integer-mult-pr193-portable/complex-acceptance.json').read_text())
controls=json.loads(Path('/tmp/integer-mult-pr193-portable/adapter-controls.json').read_text())
assert accepted['stages_executed']==6 and accepted['source_pins']==before['complex']
assert controls['status']=='PASS two-root portability controls' and len(controls['accepted'])==4 and len(controls['rejected'])==22
fresh=v.read(out/'effective-bit/receipt.json');v.admit(fresh);v.admit_artifacts(out,fresh)
bad=copy.deepcopy(fresh);bad['terminal']['formal']=[]
try:v.admit(bad)
except AssertionError:pass
else:raise AssertionError('Truncated terminal receipt admitted')
packed=v.effective_packing.run(b,fresh);v.write(out/'packing-scalar.json',packed)
math=v.js(v.verify_math.run(c,b,fresh,packed));assert math==v.read(base/'certificate.json')
v.write(out/'certificate.json',math)
assert v.check_sources(c,b)==before;v.check_package()
v.write(out/'maintainer-completion.json',dict(status='PASS_FRESH_STAGES_AND_CHANGED_ASSEMBLY',kappa=math['kappa'],original_aggregate_executed=False,installed_scientific_versions={'numpy':'2.4.6','scipy':'1.17.1'},unchanged_parent_complex_stages=6,exact_packing_and_all47=True,scope='Conditional finite supplier; original dependency-version gate not passed, no all-size theorem'))
print('PASS fresh PR217 stages and assembly; kappa='+math['kappa'])
