"""Build an explicit source-bound derived package; never modify the frozen parent."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,ast
if not __debug__:raise RuntimeError('Assertions must be enabled')
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def pins():return json.loads((P/'DERIVATION.json').read_text())
OLD=b"assert M.moment(H,73,owner['live'],b,True)[0]>1"
NEW=b"assert exact_coarse_moment(M,H,73,owner['live'],b,True)[0]>1"

def caller(payload,helper):
    pin=pins()
    assert sha(payload)==pin['caller_sha256'],'Caller source drift'
    assert sha(helper)==pin['helper_sha256'],'Arithmetic adapter source drift'
    assert payload.count(OLD)==1,'Expected exactly one targeted call'
    marker=b'from collections import Counter'
    newline=b'\r\n' if b'\r\n' in payload else b'\n'
    anchor=marker+newline
    assert payload.count(anchor)==1
    addition=b'from exact_coarse import moment as exact_coarse_moment'+newline
    changed=payload.replace(anchor,anchor+addition).replace(OLD,NEW)
    # Inverse transformation proves every original byte is retained otherwise.
    assert changed.replace(anchor+addition,anchor).replace(NEW,OLD)==payload
    before=ast.parse(payload.decode());after=ast.parse(changed.decode())
    assert sum(isinstance(n,ast.Assert) for n in ast.walk(before))==sum(isinstance(n,ast.Assert) for n in ast.walk(after))
    return changed

def build(parent,out):
    parent=parent.resolve();out=out.resolve();pin=pins()
    assert not out.exists() and not out.is_relative_to(parent),'Fresh separate output required'
    manifest_bytes=(parent/'MANIFEST.json').read_bytes()
    assert sha(manifest_bytes)==pin['parent_manifest_sha256'],'Parent manifest drift'
    manifest=json.loads(manifest_bytes)
    actual={f.relative_to(parent).as_posix() for f in parent.rglob('*') if f.is_file() and f!=parent/'MANIFEST.json'}
    assert actual==set(manifest),'Parent file set drift'
    for rel,h in manifest.items():
        rp=PurePosixPath(rel);assert not rp.is_absolute() and '..' not in rp.parts
        assert sha((parent/rel).read_bytes())==h,rel
    helper=(ROOT/pin['helper_source']).read_bytes()
    changed=caller((parent/'code/assemble.py').read_bytes(),helper)
    out.mkdir(parents=True)
    for rel in manifest:
        target=out/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((parent/rel).read_bytes())
    (out/'code/assemble.py').write_bytes(changed)
    (out/'code/exact_coarse.py').write_bytes(helper)
    record={'kind':'SOURCE_BOUND_EXACT_ARITHMETIC_CALLER_DERIVATION','parent_manifest_sha256':pin['parent_manifest_sha256'],'parent_head':pin['parent_head'],'original_caller_sha256':pin['caller_sha256'],'derived_caller_sha256':sha(changed),'adapter_sha256':sha(helper),'changed_source_files':['code/assemble.py'],'added_source_files':['code/exact_coarse.py'],'claim':'Same exact coarse moment interval; all original asserts, models, words, precision, prices and controls retained. New manifest identifies this derived package, not the frozen parent.'}
    (out/'EXACT-ARITHMETIC-DERIVATION.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
    derived={f.relative_to(out).as_posix():sha(f.read_bytes()) for f in sorted(out.rglob('*')) if f.is_file()}
    (out/'MANIFEST.json').write_text(json.dumps(derived,indent=2)+'\n',encoding='utf-8',newline='\n')
    return record

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--parent',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    build(a.parent,a.out);print('PASS_SOURCE_BOUND_DERIVED_PACKAGE_BUILD')
