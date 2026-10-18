"""Load authenticated predecessor bytes directly, never a bytecode cache."""
import hashlib
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

ROOT = Path(__file__).resolve().parent
MODULES = ('words', 'records', 'matrices', 'controller', 'forms', 'children', 'numeric', 'oracle2781')
HEAD = 'a53fdf4bcbe33c6732f0bec1badc8c023380f9d1'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def authenticate(root=ROOT):
    manifest = json.loads((root / 'INPUTS.json').read_text())
    require(manifest['repository'] == 'CrocSwap/integer-mult-bounds', 'repository pin')
    wanted = {'vendor/'+n+'.py' for n in MODULES} | {'vendor/NOTICE.md'} | {
        'evidence/PR'+str(n)+'.md' for n in (2759, 2770, 2778, 2781, 2796)}
    require(len(manifest['files']) == len(wanted), 'complete source inventory')
    data = {}
    for item in manifest['files']:
        name = item['path']
        require(name in wanted and name not in data, 'unique exact input path')
        path = root / name
        require(path.is_file() and not path.is_symlink(), 'regular source input')
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == item['sha256'], 'input SHA256')
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        require(blob == item['git_blob'], 'input Git blob')
        if name.startswith('vendor/') and name != 'vendor/oracle2781.py':
            leaf = Path(name).name
            expected = 'research/selected-bit-node/' + ('' if leaf == 'NOTICE.md' else 'vendor/') + leaf
            require(item['source_head'] == HEAD and item['source_path'] == expected, 'runtime source binding')
        data[name] = raw
    require(set(data) == wanted, 'closed source inventory')
    return data


def load():
    data = authenticate()
    require(not any(n in sys.modules for n in MODULES), 'no preloaded source modules')
    for name in MODULES:
        module = ModuleType(name)
        module.__file__ = str(ROOT / 'vendor' / (name+'.py'))
        sys.modules[name] = module
        exec(compile(data['vendor/'+name+'.py'], module.__file__, 'exec', dont_inherit=True), module.__dict__)
    return SimpleNamespace(**{n: sys.modules[n] for n in MODULES})
