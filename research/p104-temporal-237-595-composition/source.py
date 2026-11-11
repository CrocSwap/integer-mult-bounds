"""Verify the frozen upstream artifacts before importing or executing their code."""
from contextlib import contextmanager
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import importlib.util
import json
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
SOURCE_SHA = 'ecb1f56ba06dbaae424d0f94ad41c6d08f39f5f1f2fec348f2d0c9c9873c657f'
PEER_HEAD = '3b61d41d81a4bc8f78252240c8fb02473dd3d94f'
SOURCE_HEAD = '154ef929894225674df48df2d6ea3b7a7d1f39a0'
# These modules are byte-for-byte copies of the complete parent package.
REUSE = ('derive_grid.py', 'split.py', 'support.py', 'temporal_construct.py')


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@contextmanager
def frozen(pr):
    manifest = read(HERE / f'PR{pr}-INPUTS.json')
    need((pr, manifest['head'], manifest['complete_package']) in
         ((7148, SOURCE_HEAD, True), (7147, PEER_HEAD, False)), 'Expected exact upstream head and inventory scope')
    arc = HERE / f'inputs/pr{pr}.tar.gz'
    need(manifest['archive'] == str(arc.relative_to(HERE)), 'Expected relative archive')
    need(sha256(arc.read_bytes()).hexdigest() == manifest['archive_sha256'], 'Complete archive hash')
    pins = {row['path']: row for row in manifest['files']}
    need(len(pins) == len(manifest['files']), 'Distinct manifest entries')
    with tempfile.TemporaryDirectory(prefix=f'chart-composition-{pr}-') as tmp:
        root = Path(tmp)
        parent = root / manifest['prefix']
        seen = set()
        with tarfile.open(arc, 'r:gz') as tar:
            for item in tar:
                path = root / item.name
                need(item.isfile() and item.name in pins and item.name not in seen
                     and parent.resolve().is_relative_to(root.resolve())
                     and path.resolve().is_relative_to(parent.resolve()), 'Safe listed archive member')
                row = pins[item.name]
                need(item.size == row['size'], 'Exact archive member length')
                raw = tar.extractfile(item).read()
                blob = sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
                need(sha256(raw).hexdigest() == row['sha256'] and blob == row['git_blob'], 'SHA256 and Git blob bytes')
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
                seen.add(item.name)
        need(seen == set(pins), 'Complete recorded source inventory')
        if pr == 7148:
            for name in REUSE:
                need((HERE / name).read_bytes() == (parent / name).read_bytes(), 'Byte-identical method: ' + name)
        yield parent


@contextmanager
def _parent_imports(parent):
    names = ('source', 'construct', 'support', 'split', 'temporal_construct', 'rechart', 'retime')
    saved = {name: sys.modules.pop(name, None) for name in names}
    oldpath = list(sys.path)
    try:
        sys.path.insert(0, str(parent))
        yield
    finally:
        sys.path[:] = oldpath
        for name, module in saved.items():
            sys.modules.pop(name, None)
            if module is not None:
                sys.modules[name] = module


@contextmanager
def sources():
    with frozen(7148) as parent:
        module = load('frozen_chart595_source', parent / 'source.py')
        with module.sources() as (vendor, archive, rank9, bundle, common, word):
            with _parent_imports(parent):
                constructor = load('frozen_chart595_construct', parent / 'construct.py')
                result = constructor.construct(word, read(parent / 'WITNESS.json'), read(parent / 'PATHS.json'))
            raw = canonical(result)
            need(raw == gzip.decompress((parent / 'WORD.json.gz').read_bytes())
                 and sha256(raw).hexdigest() == SOURCE_SHA, 'Reconstructed entire exact chart-595 source')
            yield vendor, archive, rank9, bundle, parent, result


@contextmanager
def bundles():
    with frozen(7148) as parent:
        module = load('frozen_chart595_bundles', parent / 'source.py')
        with module.bundles() as (parts, _, root):
            yield parts, parent, root
