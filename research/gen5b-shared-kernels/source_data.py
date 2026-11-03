"""Read immutable PR299/PR300 data; never import or execute upstream programs."""
from pathlib import Path
import gzip
import hashlib
import json
import os

if not __debug__:
    raise RuntimeError('Run without -O; certificate assertions must remain enabled.')

HERE = Path(__file__).resolve().parent
MANIFEST = json.loads((HERE / 'inputs.json').read_text())
HEAD = MANIFEST['commit']


def source_root():
    value = os.environ.get('CORETIME_SOURCE_DIR')
    if not value:
        raise RuntimeError('Set CORETIME_SOURCE_DIR to the pinned input directory; see README.md.')
    return Path(value).expanduser().resolve()


def verify_bytes(name, data):
    pin = MANIFEST['files'][name]
    if len(data) != pin['bytes'] or hashlib.sha256(data).hexdigest() != pin['sha256']:
        raise ValueError('Pinned input bytes changed: ' + name)
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    if blob != pin['git_blob']:
        raise ValueError('Pinned Git blob changed: ' + name)
    return data


def read_bytes(name):
    if name not in MANIFEST['files']:
        raise ValueError('Unpinned input: ' + name)
    return verify_bytes(name, (source_root() / name).read_bytes())


def read_json(name):
    data = read_bytes(name)
    if name.endswith('.gz'):
        data = gzip.decompress(data)
    return json.loads(data)


def verify_all():
    for name in MANIFEST['files']:
        read_bytes(name)
    return len(MANIFEST['files'])
