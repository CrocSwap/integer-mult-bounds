#!/usr/bin/env python3
"""Remove only PR303's absent, non-executed historical stdout log from its manifest."""
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--package',type=Path,required=True);a=p.parse_args();root=a.package.resolve();spec=json.loads(Path(__file__).with_name('REPAIR.json').read_text());manifest=root/'MANIFEST.json';raw=manifest.read_bytes();digest=hashlib.sha256(raw).hexdigest()
if digest==spec['repaired_manifest_sha256']:print('Already repaired')
else:
    assert digest==spec['original_manifest_sha256'], 'Unexpected original manifest'
    key=spec['removed_missing_log'];assert not(root/key).exists()
    assert all(key not in f.read_text() for f in root.rglob('*.py'))
    data=json.loads(raw);assert data['files'].pop(key)==spec['missing_log_original_sha256']
    new=(json.dumps(data,indent=2)+'\n').encode();assert hashlib.sha256(new).hexdigest()==spec['repaired_manifest_sha256'];manifest.write_bytes(new)
    print('Removed one absent historical log entry; all scientific pins/assertions unchanged')
