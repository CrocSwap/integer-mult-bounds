#!/usr/bin/env python3
"""Read-only verification of the frozen cyclic/deferred finite package.

Regeneration occurs only in a temporary repository-shaped copy. Source hashes,
complete profile ledgers, the exact certificate, and the independent reflection
audit are required. General transfer and common-basis/address-adapter assumptions remain
separate dependencies; the nested finite bit word is independently replayed. Prepared for eumemic
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
from bit_adapter import package_inventory as bit_package_inventory

HERE = Path(__file__).resolve().parent
COMPLEX_DAG_PIN = '3c034d0aae388ef567a454826f4f48b26fd8a94c71e8ffed4835271b349a783b'
PARTITION_PIN = '9117d3f010354fa2f32d5c5fb324b280977e82e76060a70a867767a90989ccaa'
BIT_PINS = {
    'witness_23.json.gz': 'b2486aa2bb222bacea6e52162a3920780e45dd8edc5d7cb03eabea336a1c6588',
    'deferred_23.json.gz': '8c38e947ff9e021e308000dd82bb5e2194eb265d8b75194e22ce783d3e75317c',
}
REQUIRED = {
    'verify.py', 'test_controls.py', 'producer.py', 'complex_deferred.py',
    'bit_round7.py', 'certificate.py', 'bit-profile.json',
    'bit_adapter.py', 'shared-bit-profile.json',
    'complex-profile.json', 'certificate.json', 'replayed_producer.py',
    'inputs/complex-dag.json.gz',
    'sharing.py', 'phase_check.py', 'phase_check.json',
    'shared-complex-profile.json', 'inputs/shared-partition.json',
    'reuse.py', 'reuse-pairs.json', 'gauge_phase.py',
    'gauge-phase-audit.json', 'gauge-phase-witness.json',
    'README.md', 'SHARING.md', 'BITSHARING.md', 'PR128-NOTICE',
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

    All outer package scripts are roots, covering explicit importlib loading.
    The independently frozen nested bit package is checked through its exact
    manifest/verifier boundary; unused inherited APIs are not entry points.
    Only stdlib outer imports may be unresolved. The sole external arithmetic
    data read is listed separately.
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
    nested_bit = bit_package_inventory(package)
    names = REQUIRED | set(scripts) | {reflection_script, reflection_receipt} | set(nested_bit)
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
            scalar_dag=dict(pull_request='https://github.com/CrocSwap/integer-mult-bounds/pull/117',
                            commit='cbb05ce504d571546d9b7794c186a613c659c3bf',
                            file='inputs/complex-dag.json.gz', sha256=COMPLEX_DAG_PIN),
            completed_core_partition=dict(pull_request='https://github.com/CrocSwap/integer-mult-bounds/pull/128',
                            commit='530588a019b4a74f09180680c9e3961bf649ec89',
                            file='inputs/shared-partition.json', sha256=PARTITION_PIN),
            compensated_birth_reuse='https://github.com/CrocSwap/integer-mult-bounds/pull/124',
            bit161=dict(manifest='bit-sharing/MANIFEST.json',
                        manifest_sha256=nested_bit['bit-sharing/MANIFEST.json'],
                        verifier='bit-sharing/verify.py',
                        scope='Independent frozen full geometry, physical word, partition and moment replay'),
            round7_repository='https://github.com/Swapnil-jain/integer-mult-kappa',
            round7_commit='741e7aa078392553815df7926ee17ac5e25a8c38',
            round7_sha256=BIT_PINS),
        attribution='Avi Eisenberg / ikeboy (PR62 and PR110, Anthropic Claude assistance); Rohan Arun (PR111, Anthropic Claude assistance); Swapnil Jain (round-seven bit word); icekylinx (retained stopped-product, copied-center and finite assembly interfaces); Zhihao Chen and RaD (retained assembly). PR117 scalar DAG is separate upstream work by eumemic with Anthropic Claude assistance, retained byte for byte with its original attribution. Completed-core sharing and signed orthogonal partition: an664 PR128 with OpenAI Codex assistance, using Xiande Zhang and Gennian Ge (2010). Compensated birth-cut reuse follows jamesyc PR124. Physical hull frames, generalized gauge sharing, 161-group bit sharing and verification for eumemic with OpenAI Codex assistance. Original source notices remain authoritative.')


def check_sources(package, repository, manifest=None):
    manifest = manifest or json.loads((package / 'SOURCE.json').read_text())
    require(manifest['schema'] == 1, 'Unsupported source-manifest schema')
    names = set(manifest['package_files'])
    reflection = manifest['reflection']
    require(REQUIRED | {reflection['script'], reflection['receipt']} <= names,
            'Incomplete package source/finite-input closure')
    bit_files = bit_package_inventory(package)
    require({name for name in names if name.startswith('bit-sharing/')} == set(bit_files),
            'Incomplete or stale nested bit-package closure')
    require(all(manifest['package_files'][name] == expected for name, expected in bit_files.items()),
            'Nested bit-package manifest binding mismatch')
    for collection, base in ((manifest['package_files'], package),
                             (manifest['repository_files'], repository)):
        for name, expected in collection.items():
            require(digest(safe_file(base, name)) == expected, 'Source hash mismatch: ' + name)
    scripts = sorted(name for name in names if name.endswith('.py') and not name.startswith('bit-sharing/'))
    expected = dependency_closure(package, repository, scripts)
    require(set(manifest['repository_files']) == expected,
            'Incomplete or stale transitive repository dependency closure')
    for name, expected in BIT_PINS.items():
        require(manifest['package_files']['inputs/' + name] == expected,
                'Round-seven provenance digest mismatch: ' + name)
    require(manifest['package_files']['inputs/complex-dag.json.gz'] == COMPLEX_DAG_PIN,
            'PR117 scalar-DAG provenance digest mismatch')
    require(manifest['package_files']['inputs/shared-partition.json'] == PARTITION_PIN,
            'PR128 completed-core partition provenance digest mismatch')
    return manifest


def validate_profile(profile, label):
    fields = ('h', 'v', 'R', 'm', 'N', 'W', 'L', 'total_rank', 'deficit', 'maxchild')
    require(all(type(profile[key]) is int and profile[key] > 0 for key in fields),
            label + ': nonpositive or noninteger ledger value')
    h, v, R, m, N, W, L = (profile[key] for key in fields[:7])
    require(v == comb(h, 3) and m == h*h and N == v*v, label + ': dimensions')
    if label == 'shared-complex':
        groups = {int(g): count for g, count in profile['group_sizes'].items()}
        require(groups == {8: 4, 24: 83} and profile['shared_groups'] == sum(groups.values()),
                label + ': completed-core group ledger')
        require(profile['core_pre_exterior_inner_sink_rank'] == h,
                label + ': completed-core gauges')
        outer_width = profile['shared_groups']
    elif label == 'shared-bit':
        groups = {int(g): count for g, count in profile['group_sizes'].items()}
        require(groups == {11: 161} and profile['groups'] == 161,
                label + ': completed-core group ledger')
        outer_width = profile['groups']
    else:
        outer_width = v
    require(W == 2*N + 2*outer_width*R and L == 2*v*h*(h-1), label + ': physical ledger')
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
    if label in ('complex', 'shared-complex'):
        require(profile['virtual_R'] == profile['additions']+profile['roots']-profile['links'] and
                type(profile['reused_roles']) is int and profile['reused_roles'] >= 0 and
                R + profile['reused_roles'] == profile['virtual_R'],
                'complex: addition/roots/matching role ledger')
        require(sum(profile['deferred_dims'].values()) == profile['deferred_roles'],
                'complex: deferral inventory')
        from gauge_phase import validate_inventory
        validate_inventory(profile['physical_auxiliary_source_frames'], R, h)
    if label == 'shared-bit':
        require(profile['paid_projector_calls'] == sum(rows.values()),
                label + ': paid projector adapter calls')
        classes = profile['classes']
        require(sum(part['rank'] for part in classes.values()) == profile['total_rank'] and
                sum(part['calls'] for part in classes.values()) == profile['paid_projector_calls'],
                label + ': class-wise paid rank/call ledger')
    return rows


def validate_shared_composition(package):
    from sharing import profile as shared_profile
    local = json.loads((package / 'complex-profile.json').read_text())
    shared = json.loads((package / 'shared-complex-profile.json').read_text())
    partition = json.loads((package / 'inputs/shared-partition.json').read_text())
    phase = json.loads((package / 'phase_check.json').read_text())
    gauge = json.loads((package / 'gauge-phase-audit.json').read_text())
    require(gauge['local_profile_sha256'] == digest(package / 'complex-profile.json') and
            gauge['reflection_receipt_sha256'] == digest(package / 'reflection-audit.json') and
            gauge['checker_sha256'] == digest(package / 'gauge_phase.py'),
            'Physical gauge audit does not bind the local source evidence')
    reconstructed = shared_profile(local, partition, phase, gauge)
    require(json.loads(json.dumps(reconstructed)) == shared,
            'Shared profile does not match local completed cores and paid exterior')


def validate_bit_composition(package, certificate=None):
    bit = json.loads((package / 'shared-bit-profile.json').read_text())
    nested = json.loads((package / 'bit-sharing/profile161.json').read_text())
    nested_certificate = json.loads((package / 'bit-sharing/certificate.json').read_text())
    require(bit == nested, 'Shared bit profile differs from its independently verified supplier')
    validate_profile(bit, 'shared-bit')
    if certificate is not None:
        account = certificate['finite_bridge']['bit_coarse']
        require(certificate['coarse_bit_saving'] == nested_certificate['certified_bit_saving'] and
                account['halving_degree'] == nested_certificate['halving_degree'],
                'Shared bit exact saving or halving degree mismatch')
        require(account['completed_core_groups'] == bit['groups'] and
                account['paid_projector_adapter_calls'] == bit['paid_projector_calls'],
                'Shared bit paid adapter call binding mismatch')


def check_completed_core_audit(audit, local, certificate):
    require(audit['completed_core_source_inventory_bound'] is True and
            audit['completed_core_pre_exterior_frames_full'] is True and
            audit['reflected_core_active_frames_complement_source'] is True and
            audit['exact_birth_cut_invariants'] is True and
            audit['physical_aliased_numeric_replay'] is True,
            'Completed cores require bound source gauges and reflected active frames')
    require(audit['physical_auxiliary_source_frames'] == local['physical_auxiliary_source_frames'] and
            audit['virtual_R'] == local['virtual_R'] and audit['reused_roles'] == local['reused_roles'],
            'Physical source inventory or reused-role binding mismatch')
    require((audit['h'], audit['v'], audit['R']) == (local['h'], local['v'], local['R']) and
            audit['child_multiplicities'] == local['child_multiplicities'],
            'Local reflection audit does not bind the completed-core profile')
    actual = audit['literal_global_scalar_groups']
    account = certificate['finite_bridge']['complex']
    upper = account['scalar_group_upper']
    core_upper = account['core_scalar_group_upper']
    phase_upper = account['shared_basis_phase_group_upper']
    shared = certificate['complex_profile']
    expected_phase = 64 * shared['m']**2 * (2 * shared['shared_groups'] * shared['R'])
    require(type(actual) is int and type(upper) is int and type(core_upper) is int and
            0 < actual <= core_upper and upper == core_upper + phase_upper,
            'Literal reflected scalar charge exceeds exact certificate guard')
    require(type(phase_upper) is int and phase_upper == expected_phase,
            'Missing paid shared basis and phase-wrapper reserve')


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
    for label in ('bit', 'shared-bit', 'complex', 'shared-complex'):
        validate_profile(json.loads((package / (label + '-profile.json')).read_text()), label)
    validate_shared_composition(package)
    validate_bit_composition(package, json.loads((package / 'certificate.json').read_text()))
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    environment.pop('PYTHONPATH', None)
    with tempfile.TemporaryDirectory(prefix='cyclic-deferred-verify-') as directory:
        root = Path(directory)
        target = root / 'research/cyclic-deferred'
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

        run('bit_adapter.py')
        compare_json(target / 'shared-bit-profile.json', package / 'shared-bit-profile.json')
        print('PASS independent full bit replay and 161-group profile regenerated', flush=True)
        run('bit_round7.py', target / 'inputs')
        compare_json(target / 'bit-profile.json', package / 'bit-profile.json')
        print('PASS pinned round-seven bit ledger regenerated', flush=True)
        run('complex_deferred.py')
        compare_json(target / 'complex-profile.json', package / 'complex-profile.json')
        compare_json(target / 'reuse-pairs.json', package / 'reuse-pairs.json')
        print('PASS complete complex producer and deferred profile regenerated', flush=True)
        reflection = manifest['reflection']
        actual_reflection = target / reflection['receipt']
        run(reflection['script'], '--source', target / 'complex_deferred.py',
            '--output', actual_reflection)
        compare_json(actual_reflection, package / reflection['receipt'])
        run('phase_check.py', target / 'inputs/shared-partition.json')
        compare_json(target / 'phase_check.json', package / 'phase_check.json')
        run('gauge_phase.py')
        for name in ('gauge-phase-audit.json', 'gauge-phase-witness.json'):
            compare_json(target / name, package / name)
        run('sharing.py')
        compare_json(target / 'shared-complex-profile.json', package / 'shared-complex-profile.json')
        validate_shared_composition(target)
        print('PASS signed partition phases and completed-core shared profile regenerated', flush=True)
        run('certificate.py')
        validate_bit_composition(target, json.loads((target / 'certificate.json').read_text()))
        check_completed_core_audit(json.loads(actual_reflection.read_text()),
                                  json.loads((package / 'complex-profile.json').read_text()),
                                  json.loads((package / 'certificate.json').read_text()))
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
