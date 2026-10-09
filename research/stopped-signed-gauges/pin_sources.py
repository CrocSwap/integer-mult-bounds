#!/usr/bin/env python3
"""Pin the complete inherited and selected source closure; check without repinning."""
import sys
if not __debug__:raise RuntimeError('Assertions required')
sys.dont_write_bytecode=True
import json
from hashlib import sha256
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENTS=('stopped-pairtree','merged-span-frames')
RECEIPTS={'SOURCE.json','validation.json','integration-validation.json',
          'independent-audit.json','bit-audit.json','gauge-audit.json','endpoint-audit.json'}

def digest(p):return sha256(p.read_bytes()).hexdigest()
def paths():
    files={p for p in HERE.rglob('*')if p.is_file()and p.name not in RECEIPTS
           and p.suffix not in('.log','.pyc','.pyo')and '__pycache__'not in p.parts}
    for name in PARENTS:
        base=ROOT/'research'/name;source=base/'SOURCE.json'
        files.add(source)
        files|={ROOT/n for n in json.loads(source.read_text())['files']}
        files|={p for p in base.glob('*audit.json')}
    files|={ROOT/'research/stopped-pairtree/literal-audit.json',
            ROOT/'research/stopped-pairtree/interface-audit.json',
            ROOT/'research/merged-span-frames/replay-25.json'}
    return sorted(files)

def check():
    manifest=json.loads((HERE/'SOURCE.json').read_text())
    assert {str(p.relative_to(ROOT))for p in paths()}==set(manifest['files']),'Source closure differs'
    for name,value in manifest['files'].items():assert digest(ROOT/name)==value,name
    for name in PARENTS:
        for path,value in json.loads((ROOT/'research'/name/'SOURCE.json').read_text())['files'].items():
            assert digest(ROOT/path)==value,path
    return manifest

if __name__=='__main__':
    data=dict(files={str(p.relative_to(ROOT)):digest(p)for p in paths()},
              scope='Selected signed-gauge/whole-rank bit composition plus complete frozen stopped-pairtree and merged-span source closures. Run receipts are separate.')
    (HERE/'SOURCE.json').write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
    check();print('PASS stopped signed-gauge source closure frozen')
