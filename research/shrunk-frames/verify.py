#!/usr/bin/env python3
"""Read-only verification of the frozen terminal-elided shrunk-frame package.

Regeneration occurs only in a temporary repository-shaped copy. Source hashes,
complete profile ledgers, exact certificate, parent reflection audit, and an
independent terminal-elision audit are required. General transfer proofs and
the inherited round-seven bit word/frame justification remain dependencies.
Prepared with OpenAI Codex assistance; inherited authorship and licenses are retained.
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
PR125_HEAD = 'dda535bdcfc321a13a1ebd3c2d70e2b5bb72368e'
PR122_HEAD = 'b1a6f24e57141637b3ff040d6f2ce9d896ffb9bb'
BIT_PINS = {
    'witness_23.json.gz': 'b2486aa2bb222bacea6e52162a3920780e45dd8edc5d7cb03eabea336a1c6588',
    'deferred_23.json.gz': '8c38e947ff9e021e308000dd82bb5e2194eb265d8b75194e22ce783d3e75317c',
}
REQUIRED = {
    'README.md', 'verify.py', 'test_controls.py', 'producer.py', 'complex_deferred.py',
    'bit_round7.py', 'certificate.py', 'bit-profile.json',
    'complex-profile.json', 'certificate.json',
    'replayed_producer.py', 'prepare.py', 'terminal_elision.py',
    'terminal_elision_audit.py', 'terminal-elision.json.gz',
    'terminal-selection.json', 'terminal-elision-audit.json',
    'inputs/complex-dag.json.gz', 'controls/pr114-complex-profile.json',
    'controls/pr125-complex-profile.json',
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
        schema=2,
        scope='Frozen finite terminal-elided producer, profiles, exact assembly, parent reflection and independent terminal audit; inherited all-size transfer remains conditional.',
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
            shrunk_frame_parent=dict(pull_request='https://github.com/CrocSwap/integer-mult-bounds/pull/125',
                                     commit=PR125_HEAD),
            terminal_elision=dict(pull_request='https://github.com/CrocSwap/integer-mult-bounds/pull/122',
                                  commit=PR122_HEAD),
            round7_repository='https://github.com/Swapnil-jain/integer-mult-kappa',
            round7_commit='741e7aa078392553815df7926ee17ac5e25a8c38',
            round7_sha256=BIT_PINS),
        attribution='Avi Eisenberg / ikeboy (PR62 and PR110, Anthropic Claude assistance); Rohan Arun (PR111, Anthropic Claude assistance); Swapnil Jain (round-seven bit word); icekylinx (retained stopped-product, copied-center and finite assembly interfaces); Zhihao Chen and RaD (retained assembly). PR117 scalar DAG is separate upstream work by eumemic with Anthropic Claude assistance, retained byte for byte with its original attribution. PR125 shrunk-frame step by Joel Pulikkan with Anthropic Claude assistance. PR122 terminal-role elimination by SovereignSteak is the predecessor for source-time redirects. Their work is preserved and cited; the fixed-parent composition, candidate generation, independent audit, and certificate integration were prepared with OpenAI Codex assistance. Original source notices remain authoritative.')


def check_sources(package, repository, manifest=None):
    manifest = manifest or json.loads((package / 'SOURCE.json').read_text())
    require(manifest['schema'] == 2, 'Unsupported source-manifest schema')
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
    require(manifest['provenance']['shrunk_frame_parent']['commit'] == PR125_HEAD and
            manifest['provenance']['terminal_elision']['commit'] == PR122_HEAD,
            'PR122/PR125 source lineage changed')
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
    if label in ('complex', 'complex-parent'):
        compiled_roles = profile['additions']+profile['roots']-profile['links']
        if label == 'complex' and 'terminal_elimination_count' in profile:
            removed = profile['terminal_elimination_count']
            require(profile['pre_elimination_R'] == compiled_roles and R + removed == compiled_roles,
                    'complex: addition/roots/matching role ledger')
            require(type(profile.get('terminal_direct_updates')) is int and
                    profile['terminal_direct_updates'] >= removed,
                    'complex: direct terminal updates not charged')
            require(profile.get('role_count_scope', '').startswith('Terminal-elided physical word'),
                    'complex: physical role-count scope')
        else:
            require(R == compiled_roles, 'complex: addition/roots/matching role ledger')
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
        parent_word = root / 'pr125-parent-word.json.gz'
        run('prepare.py', '--parent-word', parent_word)
        compare_json(target / 'complex-profile.json', package / 'complex-profile.json')
        print('PASS pinned PR #125 parent and terminal-elided profile regenerated', flush=True)
        terminal_audit = root / 'terminal-elision-audit.json'
        run('terminal_elision_audit.py',
            '--parent-word', parent_word,
            '--parent-profile', target / 'controls/pr125-complex-profile.json',
            '--parent-audit', target / 'reflection-audit.json',
            '--receipt', target / 'terminal-elision.json.gz',
            '--profile', target / 'complex-profile.json',
            '--output', terminal_audit)
        compare_json(terminal_audit, target / 'terminal-elision-audit.json')
        print('PASS independent terminal event, scalar, and reflected-frame audit', flush=True)
        run('certificate.py')
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
