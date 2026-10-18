"""Authenticate retained inputs before decoding/compiling; DLamdata/Codex, Apache-2.0."""
from pathlib import Path
import gzip, hashlib, io, json, sys, tarfile, types
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'

def need(condition, reason):
    if not condition:
        raise ValueError(reason)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()

def load():
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    authenticated = {}
    for entry in manifest['files']:
        if entry['usage'] != 'input':
            continue
        raw = (ROOT / entry['path']).read_bytes()
        need(digest(raw) == entry['sha256'], 'source SHA256: ' + entry['path'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == entry['git_blob'], 'source Git blob: ' + entry['path'])
        authenticated[entry['path']] = raw
    data = {}
    with tarfile.open(fileobj=io.BytesIO(authenticated[ARCHIVE]), mode='r:gz') as archive:
        for key, pin in manifest['archive_members'].items():
            matches = [m for m in archive.getmembers() if m.name == pin['path']]
            need(len(matches) == 1 and matches[0].isfile(), 'unique regular archive member')
            raw = archive.extractfile(matches[0]).read()
            need(digest(raw) == pin['sha256'], 'archive member SHA256: ' + key)
            data[key] = json.loads(gzip.decompress(raw) if pin['path'].endswith('.gz') else raw)
    def module(name, path):
        # Compile authenticated source directly; never read a predecessor .pyc.
        mod = types.ModuleType(name)
        mod.__file__ = str(ROOT / path)
        sys.modules[name] = mod
        exec(compile(authenticated[path], mod.__file__, 'exec'), mod.__dict__)
        return mod
    return data, module
