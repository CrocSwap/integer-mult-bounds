"""Execute authenticated source bytes without reusing ambient bytecode caches.

Ross Richardson with OpenAI Codex assistance. Apache-2.0.
Callers bootstrap this helper with compile/exec of its source, not an importer.
The retained checker is unchanged: its transitive import runs inside a fresh
private tree containing only authenticated files. Its pure validate/roots API
is retained after loading; callers read data from the authenticated snapshots.
"""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load_source(name, path, source=None):
    """Compile these exact bytes; never consult a .pyc beside the source path."""
    path = Path(path)
    source = path.read_bytes() if source is None else source
    module = ModuleType(name)
    module.__file__ = str(path)
    # The retained Clifford compiler uses dataclasses, which resolves this name.
    sys.modules[name] = module
    exec(compile(source, str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def authenticated_inputs(package):
    """Return the same immutable bytes that passed each declared input hash."""
    package = Path(package)
    root = package.parent.parent
    sources = json.loads((package / 'SOURCES.json').read_bytes())
    inputs = {}
    for record in sources['files']:
        if record['usage'] == 'input':
            data = (root / record['path']).read_bytes()
            need(hashlib.sha256(data).hexdigest() == record['sha256'],
                 'input pin mismatch: ' + record['path'])
            inputs[record['path']] = data
    for record in sources['vendored_inputs']:
        data = (package / record['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == record['sha256'],
             'vendored input pin mismatch: ' + record['path'])
        inputs[record['path']] = data
    return inputs


def retained_checker(inputs):
    """Keep the retained transitive import inside a fresh authenticated tree.

    Only declared files are written, including no cache or symlink. The tree
    is private to this one load, so the unchanged checker's import of
    native_verify.py executes the authenticated source. The returned API does
    no file reads; the new checker consumes input data from `inputs` instead.
    """
    with tempfile.TemporaryDirectory(prefix='p104-authenticated-source-') as temporary:
        root = Path(temporary)
        for name, data in inputs.items():
            if name.startswith('research/'):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        name = 'research/p104-native-channel/check_native.py'
        return load_source('retained_p104_native_check', root / name, inputs[name])
