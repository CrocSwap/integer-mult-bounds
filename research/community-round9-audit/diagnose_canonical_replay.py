"""Run original pinned supplier build and report every saved-certificate difference.
This diagnoses a failed default comparison; it does not normalize or accept it.
"""
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
package = root / 'research/source-assisted-v4'
sys.path.insert(0, str(package))
import verify

assert not sys.flags.optimize
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
before = verify.pins()
built = verify.build()
assert verify.pins() == before, 'source bindings changed'
saved = json.loads((package / 'certificate.json').read_text())
differences = []

def walk(a, b, path=''):
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(a.keys() | b.keys()):
            if key not in a or key not in b:
                differences.append(dict(path=path+'/'+key, kind='missing', built=a.get(key), saved=b.get(key)))
            else:
                walk(a[key], b[key], path+'/'+key)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, path+'/'+str(i))
    elif a != b:
        differences.append(dict(path=path, kind='different', built=a, saved=b))

walk(built, saved)
output.mkdir(parents=True, exist_ok=True)
(output/'built.json').write_text(json.dumps(built, indent=2, sort_keys=True)+'\n')
receipt = dict(status='DIAGNOSTIC_ONLY', source_pins_unchanged=True,
               source_files=len(before), source_pin_digest=hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest(),
               saved_certificate_sha256=hashlib.sha256((package/'certificate.json').read_bytes()).hexdigest(),
               built_certificate_sha256=hashlib.sha256((output/'built.json').read_bytes()).hexdigest(),
               identical=(built == saved), differences=differences)
(output/'comparison.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
print(json.dumps(receipt, indent=2, sort_keys=True))
