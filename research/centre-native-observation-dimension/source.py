"""Authenticate all inputs before compiling retained source bytes."""
from pathlib import Path
import gzip, hashlib, io, json, sys, tarfile, types
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
KERNEL = 'research/frontier1094-recipes-exact-seed76/clifford.py'

def need(ok, why):
    if not ok:
        raise ValueError(why)

def load():
    raw = {}
    sources = json.loads((HERE / 'SOURCES.json').read_bytes())
    for manifest, root in ((sources, ROOT), (json.loads((HERE / 'PREDECESSORS.json').read_bytes()), HERE)):
        for row in manifest['files']:
            if row.get('usage') == 'provenance':
                continue
            b = (root / row['path']).read_bytes()
            need(hashlib.sha256(b).hexdigest() == row['sha256'], 'source SHA256 ' + row['path'])
            need(hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest() == row['git_blob'],
                 'source Git blob ' + row['path'])
            raw[row['path']] = b
    data = {}
    with tarfile.open(fileobj=io.BytesIO(raw[ARCHIVE]), mode='r:gz') as ar:
        for name, row in sources['archive_members'].items():
            matches = [m for m in ar.getmembers() if m.name == row['path']]
            need(len(matches) == 1 and matches[0].isfile(), 'unique selected member')
            b = ar.extractfile(matches[0]).read()
            need(hashlib.sha256(b).hexdigest() == row['sha256'], 'selected member SHA256 ' + name)
            data[name] = json.loads(gzip.decompress(b) if row['path'].endswith('.gz') else b)
    def module(name, path):
        mod = types.ModuleType(name)
        mod.__file__ = str(ROOT / path if path == KERNEL else HERE / path)
        sys.modules[name] = mod
        exec(compile(raw[path], mod.__file__, 'exec'), mod.__dict__)
        return mod
    return (data, module('pinned_observation_clifford', KERNEL),
            module('credited_owner_floor', 'source/pr2461/verify.py'),
            module('credited_native_lift', 'source/pr2048/verify.py'))
