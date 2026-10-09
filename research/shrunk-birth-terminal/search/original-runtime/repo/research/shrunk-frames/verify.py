#!/usr/bin/env python3
"""Read-only verification of the frozen shrunk-frame deferred finite package.

Regeneration occurs only in a temporary repository-shaped copy. Source hashes,
complete profile ledgers, the exact certificate, and the independent reflection
audit are required. General transfer proofs and the inherited round-seven bit
word/frame justification remain separate dependencies. Prepared for eumemic
with OpenAI Codex assistance; inherited authorship and licenses are retained.
"""
import sys
sys.dont_write_bytecode = True
if sys.flags.optimize:
    raise ValueError('Verification requires assertions; optimized Python is forbidden')

import argparse
import ast
from hashlib import sha256
import json
from math import comb
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
COMPLEX_DAG_PIN = '3c034d0aae388ef567a454826f4f48b26fd8a94c71e8ffed4835271b349a783b'
BIT_PINS = {
    'witness_23.json.gz': 'b2486aa2bb222bacea6e52162a3920780e45dd8edc5d7cb03eabea336a1c6588',
    'deferred_23.json.gz': '8c38e947ff9e021e308000dd82bb5e2194eb265d8b75194e22ce783d3e75317c',
}
REQUIRED = {
    'verify.py', 'test_controls.py', 'producer.py', 'complex_deferred.py',
    'bit_round7.py', 'certificate.py', 'bit-profile.json',
    'complex-profile.json', 'certificate.json', 'replayed_producer.py',
    'inputs/complex-dag.json.gz', 'controls/pr114-complex-profile.json',
    *('inputs/' + name for name in BIT_PINS),
}
DATA_DEPENDENCIES = {'certificates/copied-centers-network.json'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_file(directory, name):
    relative = Path(name)
    require(not relative.is_absolute() and '..' not in relative.parts,
            'Unsafe manifest path: ' + name)
    path = (directory / relative).resolve()
    require(path.is_relative_to(directory.resolve()) and path.is_file(),
            'Missing or escaping manifest file: ' + name)
    return path


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def dependency_closure(package, repository, package_scripts):
    """Include every local Python import, including package __init__ modules.

    All package scripts are roots, also covering explicit importlib loading of
    the producer and audited source. Only stdlib imports may be unresolved.
    The sole external data read used by exact assembly is listed separately.
    """
    pending = [package / name for name in package_scripts]
    seen, dependencies = set(), set(DATA_DEPENDENCIES)
    while pending:
        path = pending.pop().resolve()
        if path in seen:
            continue
        seen.add(path)
        imports = []
        for node in ast.walk(ast.parse(path.read_text(), filename=str(path))):
            if isinstance(node, ast.Import):
                imports.extend((alias.name, 0) for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append((node.module, node.level))
        for name, level in imports:
            parts = name.split('.')
            if not level and parts[0] in sys.stdlib_module_names:
                continue
            found = None
            bases = ((path.parent.parents[level-2] if level > 1 else path.parent),) if level else (package, repository / 'scripts')
            for base in bases:
                module = base.joinpath(*parts)
                for candidate in (module.with_suffix('.py'), module / '__init__.py'):
                    if candidate.is_file():
                        found = candidate.resolve()
                        break
                if found is not None:
                    pending.append(found)
                    if found.is_relative_to((repository / 'scripts').resolve()):
                        dependencies.add(str(found.relative_to(repository.resolve())))
                        parent = found.parent
                        while parent != (repository / 'scripts').resolve():
                            initializer = parent / '__init__.py'
                            if initializer.is_file():
                                pending.append(initializer)
                                dependencies.add(str(initializer.relative_to(repository)))
                            parent = parent.parent
                    break
            require(found is not None, 'Unpinned non-stdlib Python import: ' + name)
    return dependencies


def create_manifest(package, repository, reflection_script, reflection_receipt):
    scripts = sorted(path.name for path in package.glob('*.py'))
    names = REQUIRED | set(scripts) | {reflection_script, reflection_receipt}
    dependencies = dependency_closure(package, repository, scripts)
    return dict(
        schema=1,
        scope='Frozen finite producer, profiles, exact assembly and reflection audit; inherited all-size transfer remains conditional.',
        package_files={name: digest(safe_file(package, name)) for name in sorted(names)},
        repository_files={name: digest(safe_file(repository, name)) for name in sorted(dependencies)},
        reflection=dict(script=reflection_script, receipt=reflection_receipt),
        provenance=dict(
            base='https://github.com/CrocSwap/integer-mult-bounds/pull/110',
            cyclic_strips='https://github.com/CrocSwap/integer-mult-bounds/pull/111',
            saturated_base=dict(pull_request='https://github.com/CrocSwap/integer-mult-bounds/pull/114',
                                commit='7dfa16edfa5d6452f2b10dadcbef20d26222827e'),
            scalar_dag=dict(pull_request='https://github.com/CrocSwap/integer-mult-bounds/pull/117',
                            commit='cbb05ce504d571546d9b7794c186a613c659c3bf',
                            file='inputs/complex-dag.json.gz', sha256=COMPLEX_DAG_PIN),
            round7_repository='https://github.com/Swapnil-jain/integer-mult-kappa',
            round7_commit='741e7aa078392553815df7926ee17ac5e25a8c38',
            round7_sha256=BIT_PINS),
        attribution='Avi Eisenberg / ikeboy (PR62 and PR110, Anthropic Claude assistance); Rohan Arun (PR111, Anthropic Claude assistance); Swapnil Jain (round-seven bit word); icekylinx (retained stopped-product, copied-center and finite assembly interfaces); Zhihao Chen and RaD (retained assembly). PR117 scalar DAG is separate upstream work by eumemic with Anthropic Claude assistance, retained byte for byte with its original attribution. Saturated deferred-frame integration and verification for eumemic with OpenAI Codex assistance. Shrunk-frame step by Joel Pulikkan with Anthropic Claude assistance (PR114 base). Original source notices remain authoritative.')


def check_sources(package, repository, manifest=None):
    manifest = manifest or json.loads((package / 'SOURCE.json').read_text())
    require(manifest['schema'] == 1, 'Unsupported source-manifest schema')
    names = set(manifest['package_files'])
    reflection = manifest['reflection']
    require(REQUIRED | {reflection['script'], reflection['receipt']} <= names,
            'Incomplete package source/finite-input closure')
    for collection, base in ((manifest['package_files'], package),
                             (manifest['repository_files'], repository)):
        for name, expected in collection.items():
            require(digest(safe_file(base, name)) == expected, 'Source hash mismatch: ' + name)
    scripts = sorted(name for name in names if name.endswith('.py'))
    expected = dependency_closure(package, repository, scripts)
    require(set(manifest['repository_files']) == expected,
            'Incomplete or stale transitive repository dependency closure')
    for name, expected in BIT_PINS.items():
        require(manifest['package_files']['inputs/' + name] == expected,
                'Round-seven provenance digest mismatch: ' + name)
    require(manifest['package_files']['inputs/complex-dag.json.gz'] == COMPLEX_DAG_PIN,
            'PR117 scalar-DAG provenance digest mismatch')
    return manifest


def validate_profile(profile, label):
    fields = ('h', 'v', 'R', 'm', 'N', 'W', 'L', 'total_rank', 'deficit', 'maxchild')
    require(all(type(profile[key]) is int and profile[key] > 0 for key in fields),
            label + ': nonpositive or noninteger ledger value')
    h, v, R, m, N, W, L = (profile[key] for key in fields[:7])
    require(v == comb(h, 3) and m == h*h and N == v*v, label + ': dimensions')
    require(W == 2*N + 2*v*R and L == 2*v*h*(h-1), label + ': physical ledger')
    rows = {int(t): count for t, count in profile['child_multiplicities'].items()}
    require(len(rows) == len(profile['child_multiplicities']), label + ': duplicate child widths')
    require(all(0 < t < m and type(count) is int and count > 0 for t, count in rows.items()),
            label + ': invalid recursive child')
    require(sum(t*count for t, count in rows.items()) == profile['total_rank'] == W*m-N+L,
            label + ': rank mass')
    require(profile['deficit'] == N-L and profile['maxchild'] == max(rows),
            label + ': deficit or maximum child')
    require(rows.get((h-1)**2) == 2*N and rows.get(1, 0) >= N,
            label + ': omitted data projector or endpoint charge')
    if label == 'complex':
        require(R == profile['additions']+profile['roots']-profile['links'],
                'complex: addition/roots/matching role ledger')
        require(sum(profile['deferred_dims'].values()) == profile['deferred_roles'],
                'complex: deferral inventory')
    return rows


def compare_json(actual, expected):
    require(json.loads(actual.read_text()) == json.loads(expected.read_text()),
            'Frozen generated record mismatch: ' + expected.name)


def snapshot(package, repository, manifest):
    return {
        **{'package:' + n: digest(package / n) for n in manifest['package_files']},
        **{'repository:' + n: digest(repository / n) for n in manifest['repository_files']},
        'manifest': digest(package / 'SOURCE.json'),
    }


def verify(package, repository):
    manifest = check_sources(package, repository)
    before = snapshot(package, repository, manifest)
    for label in ('bit', 'complex'):
        validate_profile(json.loads((package / (label + '-profile.json')).read_text()), label)
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    environment.pop('PYTHONPATH', None)
    with tempfile.TemporaryDirectory(prefix='shrunk-frames-verify-') as directory:
        root = Path(directory)
        target = root / 'research/shrunk-frames'
        for collection, source, destination in (
                (manifest['package_files'], package, target),
                (manifest['repository_files'], repository, root)):
            for name in collection:
                out = destination / name
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source / name, out)
        shutil.copyfile(package / 'SOURCE.json', target / 'SOURCE.json')

        def run(script, *arguments):
            subprocess.run([sys.executable, str(target / script), *map(str, arguments)],
                           cwd=root, env=environment, check=True)

        run('bit_round7.py', target / 'inputs')
        compare_json(target / 'bit-profile.json', package / 'bit-profile.json')
        print('PASS pinned round-seven bit ledger regenerated', flush=True)
        run('complex_deferred.py')
        compare_json(target / 'complex-profile.json', package / 'complex-profile.json')
        print('PASS complete complex producer and deferred profile regenerated', flush=True)
        run('certificate.py')
        reflection = manifest['reflection']
        actual_reflection = root / 'actual-reflection.json'
        run(reflection['script'], '--source', target / 'complex_deferred.py',
            '--output', actual_reflection)
        compare_json(actual_reflection, package / reflection['receipt'])
        print('PASS independent literal reflection and scalar-charge audit', flush=True)
        run('test_controls.py', '--repository-root', root)
    require(snapshot(package, repository, manifest) == before,
            'Verification changed the frozen package or a dependency')
    print('PASS read-only finite package verification; inherited transfer remains conditional', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository-root', type=Path, default=HERE.parents[1])
    parser.add_argument('--freeze-manifest', action='store_true',
                        help='Explicit authoring operation: replace SOURCE.json from reviewed files')
    parser.add_argument('--reflection-script', default='reflection_audit.py')
    parser.add_argument('--reflection-receipt', default='reflection-audit.json')
    args = parser.parse_args()
    repository = args.repository_root.resolve()
    if args.freeze_manifest:
        manifest = create_manifest(HERE, repository, args.reflection_script, args.reflection_receipt)
        (HERE / 'SOURCE.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
        print('Frozen source manifest; this operation does not certify the package')
    else:
        verify(HERE, repository)


if __name__ == '__main__':
    main()
