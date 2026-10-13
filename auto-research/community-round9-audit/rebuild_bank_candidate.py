"""Fresh bank-only replay; parent supplier audits are tracked separately."""
import importlib.util,sys,json,hashlib
from pathlib import Path
n=int(sys.argv[1]);assert n in (197,205)
pkg={197:'packed-source-assisted-bit',205:'packed-diagonal-bit'}[n]
base=Path(f'/tmp/integer-mult-export{n}/research/{pkg}')
bit=Path('/tmp/integer-mult-export'+('187' if n==197 else '200'))
sys.path.insert(0,str(base));spec=importlib.util.spec_from_file_location('bank_target',base/'packing.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.build(bit)
assert json.loads(json.dumps(r))==json.loads((base/'certificate.json').read_text())['physical']
print(json.dumps(dict(status='PASS_FRESH_BANK_CERTIFICATE_EQUALITY',pr=n,physical=r,scope='Fresh exact bank/chart allocation only; parent supplier and default source-pin/arithmetic replay recorded separately'),indent=2))
