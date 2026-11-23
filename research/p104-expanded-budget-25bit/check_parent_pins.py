"""Check retained #8072 changed-file blobs against the captured source list.

The recorded list and byte matches do not themselves query Git history.
"""
from hashlib import sha1, sha256
from pathlib import Path
import json

here=Path(__file__).resolve().parent
p=here/'SOURCE-8072-PINS.json'
assert sha256(p.read_bytes()).hexdigest() == '09eb1c710a6382226b43dace5c73761ec4b84681e87e061e7aab813dfd1276cd'
pins=json.loads(p.read_bytes())
assert pins['repository']=='CrocSwap/integer-mult-bounds' and pins['pull_request']==8072
assert pins['head']=='75f7e1c44f48c43983016bcf8878c4d9e5e87c62'
prefix='research/p104-weighted-capped-allocation-490950/'
files={'LICENSE':'LICENSE', 'NOTICE.md':'UPSTREAM-NOTICE.md', 'PEER-SOURCE.json':'PEER-SOURCE.json',
       'PROOF.md':'UPSTREAM-PROOF.md', 'README.md':'UPSTREAM-README.md',
       'check_ordinary_floor.py':'check_ordinary_floor.py', 'check_stage_seam.py':'check_stage_seam.py',
       'peer8057.tar.gz':'peer8057.tar.gz', 'prepare.py':'prepare.py', 'verify.py':'upstream_verify.py'}
assert set(pins['files'])=={prefix+k for k in files}
for source,local in files.items():
    data=(here/local).read_bytes()
    blob=sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    assert blob==pins['files'][prefix+source], source
print('PASS_PARENT_8072_CHANGED_FILE_BLOBS',len(files),pins['head'])
