"""Build only the selected static source closure; never issue runtime records."""
import ast
import hashlib
import json
from pathlib import Path

W = Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453')
OLD = W / 'outputs/caller-proof-completion-20261107T0155Z'
WIRE = W / 'outputs/connected-supervisor-wiring-20261107T1931Z'
NEW = Path(__file__).resolve().parent
ORIGINAL = json.loads((OLD/'implementation/bindings/SOURCE-MANIFEST-v2.json').read_bytes())
COPIED = {}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def put(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.chmod(0o600)
    path.write_bytes(raw)
    path.chmod(0o444)

def pin(path):
    raw=path.read_bytes()
    return {'path':str(path),'bytes':len(raw),'sha256':sha(raw),'mode':0o444}

def verify(row):
    path=Path(row['path']); raw=path.read_bytes()
    assert len(raw)==row['bytes'] and sha(raw)==row['sha256'], str(path)
    assert path.resolve(strict=True)==path and path.stat().st_nlink==1
    assert path.stat().st_mode & 0o777 == row['mode']
    return raw

def relocate(value):
    if type(value) is str:
        return value.replace(str(OLD),str(NEW))
    if type(value) is list:
        return [relocate(v) for v in value]
    if type(value) is dict:
        return {relocate(k):relocate(v) for k,v in value.items()}
    return value

def encode(value):
    return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()

def prepare():
    # Only explicit source/profile pins and manifest-selected stage members.
    # Old controls and external original scientific/adoption sources remain
    # exact read-only references. No runtime tree is traversed or copied.
    for row in [*ORIGINAL['source_pins'].values(),*ORIGINAL['profiles'].values(),*ORIGINAL['control_pins']]:
        raw=verify(row); old=Path(row['path'])
        if old.is_relative_to(OLD):
            target=NEW/old.relative_to(OLD)
            put(target,raw);COPIED[str(target)]={'origin':dict(row),'kind':'unchanged'}
    for stage in ('joined-full-candidate-v1','joined-full-candidate-refusal-v1'):
        base=OLD/'implementation/bindings/stages'/stage
        declared=json.loads((base/'STAGE.json').read_bytes())
        for rel,entry in declared['files'].items():
            assert not Path(rel).is_absolute() and '..' not in Path(rel).parts
            raw=verify({'path':str(base/rel),'bytes':(base/rel).stat().st_size,**entry})
            target=NEW/'implementation/bindings/stages'/stage/rel
            put(target,raw);COPIED[str(target)]={'origin':pin(base/rel),'kind':'unchanged-scientific-payload'}
    # Nine exact successor bodies from PR6862, with an explicit path inverse.
    for path in sorted((WIRE/'implementation').rglob('*.py')):
        target=NEW/path.relative_to(WIRE);put(target,path.read_bytes())
        COPIED[str(target)]={'origin':pin(path),'kind':'PR6862-successor'}
    # Rebase owning code only, never an original scientific stage member.
    for target in sorted(COPIED):
        path=Path(target)
        if '/stages/' in target or path.suffix!='.py':
            continue
        raw=path.read_bytes(); changed=raw.replace(str(OLD).encode(),str(NEW).encode())
        changed=changed.replace(b'outputs/caller-proof-completion-20261107T0155Z',
                               b'outputs/connected-caller-assembly-20261107T2053Z')
        if changed!=raw:
            put(path,changed);COPIED[target]['path_inverse']='replace successor root with original root'
    for name in ORIGINAL['profiles']:
        path=NEW/'implementation/bindings/profiles'/(name+'.json')
        put(path,encode(relocate(json.loads(path.read_bytes()))))
    (NEW/'control/SOURCE-ORIGINS-v1.json').write_bytes(encode(COPIED))
    print(json.dumps({'copied_static_files':len(COPIED),'runtime_records_created':0,
                      'scientific_payloads_changed':0,'execution_permission':False}))

if __name__=='__main__':
    prepare()
