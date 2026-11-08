"""Authenticate the actual physical Ordinary/selected-caller cohort.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Unchanged sources and the source loader retain their authors and notices.
"""
from contextlib import contextmanager
from hashlib import sha1, sha256
import importlib
import json
from pathlib import Path
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    rows = [row for row in manifest['files'] if row['usage'] == 'input']
    seen = set()
    for row in rows:
        path = ROOT / row['path']
        need(row['path'] not in seen and path.is_file() and not path.is_symlink(),
             'unique regular source: ' + row['path'])
        seen.add(row['path'])
        raw = path.read_bytes()
        need(len(raw) == row['bytes'] and sha256(raw).hexdigest() == row['sha256']
             and sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'],
             'exact source: ' + row['path'])
    return len(rows)


@contextmanager
def opened():
    authenticate()
    archived_names = set()
    for archive in ('pr2809.tar', 'pr2808.tar'):
        with tarfile.open(ROOT / 'research/physical-ordinary-interchange/inputs' / archive, 'r:') as handle:
            archived_names.update(Path(member.name).stem for member in handle.getmembers()
                                  if member.isfile() and member.name.endswith('.py'))
    names = ('source', 'loader', 'physical_words', 'words', 'records', 'macro_machine',
             'macro_binding', 'numeric', 'controller', 'bank_codec')
    cold = archived_names.union(names, ('frozen_caller_verifier', 'padding', 'outer'))
    need(not any(name in sys.modules for name in cold), 'cold capacity-audit cohort')
    old = sys.path[:]
    sys.path.insert(0, str(ROOT / 'research/physical-ordinary-interchange'))
    cohort = None
    try:
        import source
        cohort = source
        source.activate()
        modules = {name: importlib.import_module(name) for name in names}
        need(Path(modules['source'].__file__).resolve() ==
             (ROOT / 'research/physical-ordinary-interchange/source.py').resolve(),
             'actual authenticated source loader')
        need(Path(modules['physical_words'].__file__).resolve() ==
             (ROOT / 'research/physical-ordinary-interchange/physical_words.py').resolve(),
             'actual authenticated physical numerical banks')
        expected = {
            'macro_machine': 'macro_machine.py', 'macro_binding': 'macro_binding.py',
            'residual_blocks': 'residual_blocks.py', 'role_parking': 'role_parking.py',
            'layout': 'inputs/pr2753/layout.py', 'trace': 'inputs/pr2753/trace.py',
            'packet_engine': 'inputs/pr2753/packet_engine.py',
            'bank_codec': 'inputs/pr2769/codec.py',
        }
        for name in ('words', 'controller', 'children', 'numeric', 'records', 'directory',
                     'forms', 'matrices', 'stream'):
            expected[name] = 'inputs/pr2753/predecessor/vendor/' + name + '.py'
        for name, relative in expected.items():
            module = importlib.import_module(name)
            need(Path(module.__file__).resolve() == (modules['loader'].HERE / relative).resolve(),
                 'actual archived capacity module: ' + name)
        yield modules
    finally:
        sys.path[:] = old
        if cohort is not None and getattr(cohort, '_temporary', None) is not None:
            cohort._temporary.cleanup()
