"""Small file helpers for the frozen U8/E4 construction. Apache-2.0."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
T37 = ROOT / 'research/complex-t37-owners'
T21 = ROOT / 'research/complex-t21-owners'
SOURCE = ROOT / 'research/complex-k492-owner-repair/vendor/multicold'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    path = Path(path)
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def compressed(path, value):
    Path(path).write_bytes(gzip.compress(json.dumps(value, separators=(',', ':')).encode(), mtime=0))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_sources():
    sources = read(P / 'SOURCES.json')
    for relative, digest in sources['files'].items():
        require(sha(ROOT / relative) == digest, 'Source pin changed: ' + relative)
    return sources
