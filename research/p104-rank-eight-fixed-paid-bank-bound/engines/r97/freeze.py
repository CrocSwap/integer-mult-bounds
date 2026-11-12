from hashlib import sha256
from pathlib import Path
import json
root=Path('.')
lead=root/'lead'
one=json.loads((lead/'CONTINUATION.json').read_bytes())
two=json.loads((root/'modular/RESULT.json').read_bytes())
old=json.loads((root/'input/lead/SUFFIX.json').read_bytes())
assert [(r['key'],r['status']) for r in one['rows']]==[(r['key'],r['status']) for r in two['results']]
for a,b in zip(one['rows'],two['results'],strict=True):
    for part in ('prefix','suffix'):
        if a[part] is not None:
            assert all(a[part][f]==b[part]['bank'][f] for f in ('public','owned','pivots'))
known=[(41740,242),(45266,242)]
new=[(40243,242),(45675,1091)]
by_key={tuple(r['key']): r for r in old['rows']}
by_key.update({tuple(r['key']): r['prefix'] for r in one['rows'] if r['status']=='dual_drop'})
selected=[{k:by_key[key][k] for k in ('key','public','owned','pivots')} for key in known+new]
all_open=set(known+[tuple(r['key']) for r in one['rows'] if r['status']=='dual_drop'])
out={'selected':selected,'unselected':sorted(all_open-set(known+new)),
     'basis':'Inherited first two. Added smallest/earliest chart-242 bank and first of distinct chart-1091 owned-coexistence banks, after two independent primes agreed.',
     'inputs':{name:sha256((root/name).read_bytes()).hexdigest() for name in ('lead/CONTINUATION.json','modular/RESULT.json','input/lead/SUFFIX.json')}}
data=(json.dumps(out,indent=2,sort_keys=True)+'\n').encode()
(lead/'SELECTION.json').write_bytes(data)
source=(root/'input/lead/exact_four.py').read_text()
source=source.replace('"lead/SELECTION.json": "b95765ffa0bd426b3dae781aaafc1c21e3b25bcebc71b71a3871824f9009fd5f"',f'"../lead/SELECTION.json": "{sha256(data).hexdigest()}"')
source=source.replace('raw["lead/SELECTION.json"]','raw["../lead/SELECTION.json"]')
(lead/'exact_four.py').write_text(source)
print(sha256(data).hexdigest())
