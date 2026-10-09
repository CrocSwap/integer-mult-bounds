#!/usr/bin/env python3
"""Read-only finite replay of physical local reuse under the PR130 cover.

Prepared for eumemic with OpenAI Codex assistance. Apache-2.0;
the pinned upstream sources retain their original notices and proof scope.
"""
import sys
sys.dont_write_bytecode = True
if sys.flags.optimize:
    raise ValueError('Verification requires assertions; optimized Python is forbidden')
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
import argparse
import ast
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = 'research/cover-local-reuse'
LOCAL = 'research/cyclic-deferred'
DAG_PIN = '3c034d0aae388ef567a454826f4f48b26fd8a94c71e8ffed4835271b349a783b'
BASE_CERT = 'certificates/three-stage-cover-network.json'
BASE_PIN = 'bfca1f225394c8b50f3360b71920652baf9bd885ce84f9c0a9184c3ba7dd35ab'
BIT_MANIFEST = 'references/partial-gauge/pr97/SOURCE.json'
BIT_PIN = '68fb539abcd6df21d142e4e204b6e9482eb7f9cd3907650f54bd058070266596'
LOCAL_FILES = {
    'complex_deferred.py', 'producer.py', 'replayed_producer.py', 'reuse.py',
    'reflection_audit.py', 'arbitrary_frames.py', 'gauge_frames.py',
    'complex-profile.json', 'reuse-pairs.json',
    'reflection-audit.json', 'inputs/complex-dag.json.gz',
}
PACKAGE_FILES = {
    'verify.py', 'test_controls.py', 'certificate.py', 'certificate.json',
    'README.md', 'geometry_checks.py', 'geometry-audit.json',
    'padded_checks.py', 'padded-geometry.json', 'PADDED-GEOMETRY.md',
    'bit_padded.py', 'bit-padded.json', 'BIT-PADDED.md',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def safe_file(root, name):
    part = Path(name)
    path = (root / part).resolve()
    require(not part.is_absolute() and '..' not in part.parts and
            path.is_relative_to(root.resolve()) and path.is_file(),
            'Missing or unsafe source path: ' + name)
    return path


def adopted_sources(root):
    """Pin the adopted cover evidence and every frozen inherited bit input."""
    require(digest(safe_file(root, BASE_CERT)) == BASE_PIN,
            'Immutable PR130 baseline certificate mismatch')
    baseline = json.loads((root / BASE_CERT).read_text())
    names = {BASE_CERT, BIT_MANIFEST, 'LICENSE', 'NOTICE'}
    for name, value in baseline['source_sha256'].items():
        require(digest(safe_file(root, name)) == value,
                'Adopted PR130 source mismatch: ' + name)
        names.add(name)
    require(digest(safe_file(root, BIT_MANIFEST)) == BIT_PIN,
            'Immutable inherited PR97 manifest mismatch')
    bit = json.loads((root / BIT_MANIFEST).read_text())
    require(bit['pr97']['commit'] == 'e15350b66e4bf796153a68c240a6cc1b788abe3e' and
            bit['underlying']['commit'] == '741e7aa078392553815df7926ee17ac5e25a8c38',
            'Inherited bit provenance mismatch')
    for name, value in bit['sha256'].items():
        full = str(Path(BIT_MANIFEST).parent / name)
        require(digest(safe_file(root, full)) == value,
                'Inherited bit source mismatch: ' + name)
        names.add(full)
    return names


def python_closure(root, roots):
    """Close actual entry points, including explicitly loaded local modules.

    Adopted historical checker APIs are pinned as evidence but not invoked.
    The current PR97 rank reconstruction dynamically loads only deferred.py.
    """
    pending = [root / name for name in roots]
    seen = set()
    while pending:
        path = pending.pop().resolve()
        if path in seen:
            continue
        seen.add(path)
        for node in ast.walk(ast.parse(path.read_text(), filename=str(path))):
            imports = []
            if isinstance(node, ast.Import):
                imports = [(a.name, 0) for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports = [(node.module, node.level)]
            for name, level in imports:
                if not level and name.split('.')[0] in sys.stdlib_module_names:
                    continue
                bases = ((path.parent.parents[level-2] if level > 1 else path.parent),) if level else (
                    path.parent, root / PACKAGE, root / LOCAL, root / 'scripts')
                found = None
                for base in bases:
                    module = base.joinpath(*name.split('.'))
                    for candidate in (module.with_suffix('.py'), module / '__init__.py'):
                        if candidate.is_file():
                            found = candidate.resolve()
                            break
                    if found is not None:
                        break
                require(found is not None and found.is_relative_to(root.resolve()),
                        'Unpinned non-stdlib import: ' + name)
                pending.append(found)
                parent = found.parent
                while parent != root.resolve():
                    init = parent / '__init__.py'
                    if init.is_file():
                        pending.append(init)
                    parent = parent.parent
    return {str(path.relative_to(root.resolve())) for path in seen}


def inventory(root):
    names = adopted_sources(root)
    names.update(LOCAL + '/' + name for name in LOCAL_FILES)
    names.update(PACKAGE + '/' + name for name in PACKAGE_FILES)
    names.update(str(path.relative_to(root)) for path in (root / PACKAGE).iterdir()
                 if path.is_file() and path.name != 'SOURCE.json')
    roots = {name for name in names if name.endswith('.py') and
             (name.startswith(PACKAGE + '/') or name.startswith(LOCAL + '/'))}
    roots.add('references/partial-gauge/pr97/deferred.py')
    names.update(python_closure(root, roots))
    return names


def create_manifest(root):
    return dict(schema=1,
        scope='Finite arbitrary-frame and source-gauge local replay, padded complex/bit geometry and exact paid cover assembly; general cover/bit/analytic interfaces remain conditional.',
        files={name: digest(safe_file(root, name)) for name in sorted(inventory(root))},
        provenance=dict(cover_commit='6a9970a530119174507904e23592fd59ede19a5d',
                        cover_certificate_sha256=BASE_PIN,
                        scalar_dag_commit='cbb05ce504d571546d9b7794c186a613c659c3bf',
                        scalar_dag_sha256=DAG_PIN,
                        physical_local_source='PR129 physical-frame/reuse word extended by PR130 arbitrary-subspace Clifford frames; PR124 compensated birth-cut reuse'))


def check_sources(root, manifest=None):
    manifest = manifest or json.loads((root / PACKAGE / 'SOURCE.json').read_text())
    require(manifest['schema'] == 1, 'Unsupported source manifest')
    require(set(manifest['files']) == inventory(root), 'Incomplete or stale source dependency closure')
    for name, value in manifest['files'].items():
        require(digest(safe_file(root, name)) == value, 'Source hash mismatch: ' + name)
    require(manifest['files'][LOCAL + '/inputs/complex-dag.json.gz'] == DAG_PIN,
            'Immutable PR117 scalar-DAG provenance mismatch')
    return manifest


def compare_json(actual, expected):
    require(json.loads(actual.read_text()) == json.loads(expected.read_text()),
            'Frozen generated record mismatch: ' + expected.name)
    require(actual.read_bytes() == expected.read_bytes(),
            'Frozen generated byte mismatch: ' + expected.name)


def snapshot(root, manifest):
    return {**{name: digest(root / name) for name in manifest['files']},
            PACKAGE + '/SOURCE.json': digest(root / PACKAGE / 'SOURCE.json')}


def verify(root):
    manifest = check_sources(root)
    before = snapshot(root, manifest)
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    environment.pop('PYTHONPATH', None)
    with tempfile.TemporaryDirectory(prefix='cover-local-reuse-verify-') as directory:
        target = Path(directory)
        for name in [*manifest['files'], PACKAGE + '/SOURCE.json']:
            out = target / name
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / name, out)
        def run(name, *args):
            subprocess.run([sys.executable, str(target / name), *map(str, args)],
                           cwd=target, env=environment, check=True)
        run(LOCAL + '/complex_deferred.py')
        for name in ('complex-profile.json', 'reuse-pairs.json'):
            compare_json(target / LOCAL / name, root / LOCAL / name)
        print('PASS complete physical local compiler and compensated reuse regenerated', flush=True)
        run(LOCAL + '/reflection_audit.py', '--source', target / LOCAL / 'complex_deferred.py',
            '--output', target / LOCAL / 'reflection-audit.json')
        compare_json(target / LOCAL / 'reflection-audit.json', root / LOCAL / 'reflection-audit.json')
        print('PASS full independent reflection, dirty cleanup and scalar audit', flush=True)
        run(PACKAGE + '/geometry_checks.py')
        compare_json(target / PACKAGE / 'geometry-audit.json', root / PACKAGE / 'geometry-audit.json')
        run(PACKAGE + '/padded_checks.py')
        compare_json(target / PACKAGE / 'padded-geometry.json', root / PACKAGE / 'padded-geometry.json')
        run(PACKAGE + '/bit_padded.py')
        compare_json(target / PACKAGE / 'bit-padded.json', root / PACKAGE / 'bit-padded.json')
        run(PACKAGE + '/certificate.py')
        run(PACKAGE + '/test_controls.py')
    require(snapshot(root, manifest) == before, 'Verification mutated a frozen source or artifact')
    print('PASS read-only finite cover/local-reuse verification; general interfaces remain conditional', flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--freeze-manifest', action='store_true',
                    help='Explicit authoring operation; replace SOURCE.json without certifying it')
    args = ap.parse_args()
    if args.freeze_manifest:
        (HERE / 'SOURCE.json').write_text(json.dumps(create_manifest(ROOT), indent=2, sort_keys=True) + '\n')
        print('Frozen source manifest; this operation does not certify the package')
    else:
        verify(ROOT)


if __name__ == '__main__':
    main()
