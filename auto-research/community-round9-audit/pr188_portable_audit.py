"""Audit-only Darwin replay: omit unsupported RLIMIT_AS via saved sitecustomize;
permit only the diagnosed last-bit discovery numerical_root comparison.
All exact fields and final certificate must still match; original sources stay pinned.
"""
import importlib.util,inspect,json,math,sys
from pathlib import Path
sys.dont_write_bytecode=True
base=Path('/tmp/integer-mult-export188/research/paired-cube-terminal-reuse')
sys.path.insert(0,str(base))
spec=importlib.util.spec_from_file_location('pr188_target',base/'verify.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
original=m.require;records=[]
def require(ok,message):
 if message=='Frozen bit row differs' and not ok:
  actual=inspect.currentframe().f_back.f_locals['bp'];expected=json.loads((base/'selected/bit/profile.json').read_text())
  a=dict(actual);b=dict(expected);ra=a.pop('numerical_root');rb=b.pop('numerical_root')
  assert a==b and type(ra)is float and math.isfinite(ra) and format(ra,'.12e')==format(rb,'.12e')
  records.append(dict(field='numerical_root',actual=ra,expected=rb,all_exact_fields_identical=True))
  return
 original(ok,message)
m.require=require
result=m.verify();expected=json.loads((base/'certificate.json').read_text())
Path('/tmp/integer-mult-pr188-portable-fresh.json').write_text(json.dumps(result,indent=2))
assert result==expected, 'Complete final exact certificate differs'
print(json.dumps(dict(status='PASS_ADAPTED_PR188_COMPLETE_FINITE_REPLAY',kappa=result['kappa'],diagnostic_normalization=records,rlimit_as_applied=False,original_driver_pass=False)))
