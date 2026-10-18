"""Authenticate selected inputs and compile retained predecessor bytes directly.

The selected archive binding follows credited PR2534 source.py. Import handling
uses the authenticated bytes, never an adjacent timestamp bytecode cache.
"""
from pathlib import Path
import gzip, hashlib, importlib.abc, importlib.util, io, json, sys, tarfile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KERNEL = 'research/complex-multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford/clifford_exact.py'

def need(ok, why):
    if not ok:
        raise ValueError(why)

def load():
    raw = {}
    for name, root in [('SOURCES.json', ROOT), ('VENDOR.json', HERE)]:
        for row in json.loads((HERE / name).read_text())['files']:
            if row.get('usage', 'input') != 'input':
                continue
            data = (root / row['path']).read_bytes()
            need(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256 ' + row['path'])
            need(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == row['git_blob'],
                 'source Git blob ' + row['path'])
            raw[row['path']] = data
    prefix = 'candidate/strict/global/'
    suffixes = {'recipes': 'base/providers/gauge44/CLIFFORD-RECIPES.json',
                'word': 'base/providers/gauge44/CANONICAL-WORD.json.gz',
                'programs': 'base/providers/gauge44/LOCAL-PROGRAMS.json.gz',
                'template': 'hosted/GLOBAL-TEMPLATE.json.gz',
                'invoice': 'audit/PREFIX-AND-INVOICE.json'}
    data, pins = {}, {}
    with tarfile.open(fileobj=io.BytesIO(raw['research/community-frontier1094-audit/selected-replay.tar.gz']), mode='r:gz') as ar:
        for name, suffix in suffixes.items():
            matches = [m for m in ar.getmembers() if m.name == prefix + suffix]
            need(len(matches) == 1 and matches[0].isfile(), 'unique selected member')
            member = ar.extractfile(matches[0]).read()
            pins[suffix] = hashlib.sha256(member).hexdigest()
            data[name] = json.loads(gzip.decompress(member) if suffix.endswith('.gz') else member)
    invoice = data['invoice']['providers']['gauge44']['artifacts']
    for path, pin in pins.items():
        if '/providers/gauge44/' in path:
            need(invoice[path.rsplit('/', 1)[-1]] == pin, 'selected invoice binding')
    need(data['template']['local_providers']['gauge44']['local_programs'] == data['programs'], 'actual selected programs')
    child = data['recipes']['children'][7]
    need((child['old'], child['new'], child['rank']) == (0, 9, 1), 'selected child7')
    for orientation in ('forward', 'backward'):
        need(data['programs'][orientation][9394] == ['climb', 'A', 224, 0, 9, 1] and
             data['programs'][orientation][9396] == ['climb', 'A', 225, 0, 9, 1], 'actual selected occurrences')
    frame = data['word']['frames'][9]
    need(data['word']['frames'][0] == [] and len(frame) == 1, 'selected directed frame')
    spec = importlib.util.spec_from_file_location('invocation_frame_native', ROOT / KERNEL)
    native = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = native
    exec(compile(raw[KERNEL], str(ROOT / KERNEL), 'exec', optimize=0), native.__dict__)
    names = ('streams', 'pipeline', 'compact', 'monomial', 'arithmetic', 'compose', 'oracle')
    class AuthenticatedLoader(importlib.abc.MetaPathFinder, importlib.abc.Loader):
        def find_spec(self, fullname, path=None, target=None):
            if fullname in names:
                return importlib.util.spec_from_loader(fullname, self)
        def create_module(self, spec):
            return None
        def exec_module(self, module):
            path = 'vendor/' + module.__name__ + '.py'
            module.__file__ = str(HERE / path)
            exec(compile(raw[path], module.__file__, 'exec'), module.__dict__)
    need(not any(name in sys.modules for name in names), 'retained module names are fresh')
    loader = AuthenticatedLoader()
    sys.meta_path.insert(0, loader)
    try:
        # pipeline installs the observational TrackingTape before descendants.
        import pipeline, compose, oracle
    finally:
        sys.meta_path.remove(loader)
    return child, frame, native, pins, compose, oracle
