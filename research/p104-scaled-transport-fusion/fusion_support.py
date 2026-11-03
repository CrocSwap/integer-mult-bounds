"""Read the exact source export before an import.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The retained source and export tools keep their original credit.
"""
from contextlib import contextmanager, ExitStack
from fractions import Fraction as Q
from hashlib import sha256, sha1
from pathlib import Path, PurePosixPath
import gzip
import importlib.util
import json
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def encode(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    return value


def authenticate(raw, pin):
    need(sha256(raw).hexdigest() == pin['sha256'], 'Source SHA256: '+pin['path'])
    need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'],
         'Source Git blob: '+pin['path'])


def unpack(destination):
    for pin in read(HERE/'SOURCES.json')['files']:
        if pin['usage'] == 'input':
            authenticate((HERE/Path(pin['path']).name).read_bytes(), pin)
    manifest = read(HERE/'SOURCE.json')
    archive = HERE/'source.tar'
    need(sha256(archive.read_bytes()).hexdigest() == manifest['archive_sha256'], 'Exact source export')
    pins = {x['path']: x for x in manifest['files']}
    need(len(pins) == 26, 'All source export members')
    seen = set()
    with tarfile.open(archive, 'r:') as tar:
        for member in tar.getmembers():
            path = PurePosixPath(member.name)
            need(member.isfile() and not path.is_absolute() and '..' not in path.parts
                 and ':' not in member.name and '\\' not in member.name,
                 'Safe regular source member')
            need(member.name not in seen, 'Unique source member')
            seen.add(member.name)
            raw = tar.extractfile(member).read()
            if member.name == '.research-export.json':
                need(sha256(raw).hexdigest() == manifest['export_manifest_sha256'], 'Exact export manifest')
                need(json.loads(raw)['commit'] == manifest['head'], 'Exact source head')
            else:
                need(member.name in pins, 'Declared source member')
                authenticate(raw, pins[member.name])
                need(pins[member.name]['pin'] == 'head:'+manifest['head']+':'+member.name,
                     'Source head and path binding')
                target = destination/member.name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
        need(seen == set(pins)|{'.research-export.json'}, 'Complete source export')
    return destination/'research/p104-third-anchor-clean-mixed-root'


@contextmanager
def source_context():
    with ExitStack() as stack:
        root = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='scaled-fusion-')))
        old_cache = sys.pycache_prefix
        sys.pycache_prefix = str(root/'bytecode')
        try:
            package = unpack(root/'source')
            support = load(package/'support.py', 'support')
            retained = root/'retained'
            support.inputs(retained)
            source = load(package.parents[1]/'research/p104-root-relay-descent-2/sources.py', 'fusion_archive_source')
            parent = stack.enter_context(source.sources())
            cursor = stack.enter_context(source.load(parent/'sources.py', 'fusion_archive_top').sources())
            for depth in range(7):
                cursor, runtime = stack.enter_context(source.load(cursor/'sources.py', 'fusion_archive_'+str(depth)).sources())
            local = source.load(parent/'local.py', 'fusion_local')
            local.ROOT = runtime
            yield package, retained, local
        finally:
            sys.pycache_prefix = old_cache


def reject(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('Corruption accepted')
