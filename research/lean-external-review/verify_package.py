#!/usr/bin/env python3
"""Check the portable review inventory and the A/B proof/receipt source bindings."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = 'db0e57bc7f36b5ac0fc844ad7ce1396165ee6647'
DIRECTORIES = [
    'lean-whole-residual-hosting', 'lean-multi-host-framework',
    'lean-multi-host-source', 'lean-external-review',
    'lean-single-stream-obstruction', 'lean-source-invocation-audit',
    'lean-contribution-archive',
]
# Avoid a circular digest. The delivery SHA256SUMS covers both files.
EXCLUDED = {'research/lean-external-review/package-manifest.json',
            'research/lean-external-review/package-validation.json'}
ROOT_FILES = ['LICENSE', 'NOTICE', 'CONTRIBUTING.md', 'Makefile',
              '.github/workflows/verify.yml', 'certificates/mixed-point-audit.json']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def inventory():
    files = [ROOT / name for name in ROOT_FILES]
    for name in DIRECTORIES:
        for directory, subdirs, names in os.walk(ROOT / 'research' / name):
            subdirs[:] = sorted(n for n in subdirs if n not in {'.lake', '__pycache__', '.git'})
            files.extend(Path(directory) / n for n in names if not n.endswith('.pyc'))
    require(all(not p.is_symlink() for p in files), 'Symlink in review sources')
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(files)
            if str(p.relative_to(ROOT)) not in EXCLUDED}


def object_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def digest_string(value):
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value) is not None


def footprint(record, label):
    require(digest_string(record['sha256']), label + ': invalid fingerprint')
    require(type(record['files']) is int and record['files'] >= 0 and
            type(record['bytes']) is int and record['bytes'] >= 0,
            label + ': invalid footprint counts')


def audit_inventory(receipt, names, allowed, label):
    require(list(receipt['axioms']) == names, label + ': axiom inventory mismatch')
    require(all(isinstance(axioms, list) and set(axioms) <= allowed
                for axioms in receipt['axioms'].values()), label + ': unexpected axioms')


def bindings(allow_pending_task_b=False):
    # Only these fresh receipts establish the current build claim. Original
    # replay-result.json and archived review receipts remain inventory-covered
    # historical evidence; neither they nor a metadata reanchor authorize reuse.
    a = ROOT / 'research/lean-multi-host-framework'
    b = ROOT / 'research/lean-multi-host-source'
    ma = json.loads((a / 'proof-manifest.json').read_text())
    mb = json.loads((b / 'proof-manifest.json').read_text())
    current_a = json.loads((HERE / 'validation/task-a.json').read_text())
    task_b_receipt = HERE / 'validation/task-b.json'
    current_b = json.loads(task_b_receipt.read_text()) if task_b_receipt.exists() else None
    receipts = [('Task A', current_a, a)]
    if current_b is not None:
        receipts.append(('Task B', current_b, b))
    for label, receipt, directory in receipts:
        require(receipt['status'] == 'PASS', label + ': fresh replay failed')
        require(receipt['trust_level'] == 0, label + ': replay was not at trust level zero')
        require(receipt['replay_mode'] == 'fresh' and receipt['reused_modules'] == 0,
                label + ': current receipt is not a fully fresh build')
        require(receipt['manifest_sha256'] == sha(directory / 'proof-manifest.json'),
                label + ': fresh receipt/current manifest mismatch')
        require(receipt['lean_commit'] == ma['lean_commit'] == mb['lean_commit'],
                label + ': Lean pin mismatch')
        require(receipt['lean'].startswith('Lean (version 4.33.0,'),
                label + ': wrong Lean version')
    require(current_a['fresh_modules_compiled'] == len(ma['sha256']),
            'Task A fresh module count mismatch')
    require(current_a['source_sha256'] == ma['sha256'], 'Task A receipt/source mismatch')
    audit_inventory(current_a, ma['theorems'], {'propext', 'Quot.sound'}, 'Task A')
    footprint(current_a['toolchain'], 'Task A toolchain')
    require(digest_string(current_a['toolchain']['lean_binary_sha256']),
            'Task A compiler fingerprint is invalid')
    for name, digest in ma['sha256'].items():
        parent = a if name not in {'CoordinateSwap', 'Hosting', 'PhysicalHosting'} else a.parent / 'lean-whole-residual-hosting'
        require(sha(parent / (name + '.lean')) == digest, 'Task A source mismatch: ' + name)

    module_names = [module['module'] for module in mb['modules']]
    require(len(set(module_names)) == len(module_names), 'Duplicate Task B module')
    require('SourceInvocation.actualContract' in mb['audit_declarations'],
            'Task B actualContract is absent from the permanent axiom inventory')
    # A pending package still binds every manifested source and its import
    # graph. It makes no claim that the pending Lean replay has succeeded.
    prior_sources = set()
    for module in mb['modules']:
        name = module['module']
        source = (b / module['source']).resolve()
        require(source.is_relative_to(ROOT), 'Dependency outside delivery: ' + name)
        require(sha(source) == module['sha256'], 'Task B manifested source mismatch: ' + name)
        code = re.sub(r'--[^\n]*', '', re.sub(r'/\-[\s\S]*?\-/', '', source.read_text()))
        require(re.findall(r'^import (\S+)$', code, re.M) == module['imports'],
                'Task B manifested import mismatch: ' + name)
        require(all(dep in prior_sources or dep == 'Std' or dep.startswith('Mathlib.')
                    for dep in module['imports']), 'Unordered or unmanifested dependency: ' + name)
        prior_sources.add(name)
    versions = json.loads((b / 'source-versions.json').read_text())
    require(versions['mathlib']['commit'] == mb['mathlib_commit'],
            'Mathlib pin mismatch')
    require(versions['lean']['commit'] == mb['lean_commit'], 'Source version Lean mismatch')
    require(json.loads((HERE / 'validation/source-binding.json').read_text())['status'] == 'PASS',
            'Source binding receipt failed')
    run = json.loads((HERE / 'validation/run-metadata.json').read_text())
    require(run['upstream_base_commit'] == BASE, 'Run metadata upstream base mismatch')
    for key, script, mode in [('task_a', a / 'replay.py', 'fresh'),
                              ('task_b', b / 'replay.py', 'fresh'),
                              ('source_binding', b / 'check_sources.py', 'fresh regeneration')]:
        require(run[key]['script_sha256'] == sha(script) and run[key]['mode'] == mode,
                'Current runner metadata mismatch: ' + key)
    if current_b is None:
        require(allow_pending_task_b,
                'Fresh Task B receipt is absent; --allow-pending-task-b reports an explicitly unfinished package')
        require(run['task_b'].get('status') == 'running',
                'Pending Task B requires run metadata explicitly marked running')
        return {'status': 'PENDING_TASK_B', 'task_b_verified': False,
                'task_b_notice': 'Fresh Task B replay in progress; receipt will be added to this PR.',
                'task_a_modules': len(ma['sha256']), 'task_b_modules': len(module_names),
                'task_a_theorem_closures': len(ma['theorems']),
                'task_b_planned_audit_declarations': len(mb['audit_declarations']),
                'task_a_replay_mode': 'fresh', 'task_b_replay_mode': 'pending',
                'task_a_receipt_sha256': sha(HERE / 'validation/task-a.json'),
                'task_b_receipt_sha256': None}
    require(current_a['lean'] == current_b['lean'], 'Task A/B compiler version mismatch')
    require(current_b['mathlib_commit'] == mb['mathlib_commit'], 'Task B receipt Mathlib pin mismatch')
    require(list(current_b['modules']) == module_names, 'Task B module inventory mismatch')
    require(current_b['fresh_modules_compiled'] == len(module_names) and
            current_b['fresh_module_names'] == module_names and
            current_b['reused_module_names'] == [] and current_b['legacy_module_names'] == [] and
            current_b['legacy_reused_modules'] == 0,
            'Task B fresh/reuse inventory mismatch')
    require(current_b['historical_external_environment'] == 'fingerprinted_at_compile',
            'Task B compile environment was not fingerprinted')
    require('SourceInvocation.actualContract' in mb['audit_declarations'],
            'Task B actualContract is absent from the permanent axiom inventory')
    audit_inventory(current_b, mb['audit_declarations'],
                    {'propext', 'Quot.sound', 'Classical.choice'}, 'Task B')

    external = current_b['external_environment']
    components = external['components']
    require(components['schema'] == 1 and object_sha(components) == external['sha256'],
            'Task B external environment fingerprint mismatch')
    footprint(components['toolchain'], 'Task B toolchain')
    require(all(current_a['toolchain'][key] == components['toolchain'][key]
                for key in ['sha256', 'files', 'bytes']) and
            current_a['toolchain']['lean_binary_sha256'] == components['lean_binary_sha256'] and
            digest_string(components['lean_binary_sha256']),
            'Task A/B toolchain footprint mismatch')
    lake_manifest = json.loads((b / 'mathlib-lake-manifest.json').read_text())
    expected_dependencies = {'Mathlib': mb['mathlib_commit']}
    for package in lake_manifest['packages']:
        require(package['type'] == 'git' and not package.get('subDir'),
                'Unsupported external dependency layout: ' + package['name'])
        expected_dependencies[package['name']] = package['rev']
    dependencies = components['dependencies']
    require(set(dependencies) == set(expected_dependencies),
            'External dependency inventory mismatch')
    for name, commit in expected_dependencies.items():
        require(dependencies[name]['commit'] == commit, 'External dependency pin mismatch: ' + name)
        for key in ['tracked_sources', 'build_artifacts', 'lake_configuration_artifacts']:
            footprint(dependencies[name][key], name + '/' + key)
    allowed_search = {name + '/.lake/build/lib/lean' for name in dependencies} | {'toolchain/lib/lean'}
    search = components['library_search_order']
    require(set(search) <= allowed_search and len(set(search)) == len(search) and
            'Mathlib/.lake/build/lib/lean' in search, 'Unexpected external library search order')

    prior = {}
    for module in mb['modules']:
        name = module['module']
        record = current_b['modules'][name]
        source = (b / module['source']).resolve()
        require(source.is_relative_to(ROOT), 'Dependency outside delivery: ' + name)
        require(sha(source) == module['sha256'] == record['sha256'],
                'Task B source/receipt mismatch: ' + name)
        require(record['environment_sha256'] == external['sha256'] and
                record['historical_external_environment'] == 'fingerprinted_at_compile' and
                'legacy_receipt' not in record, 'Task B module lacks fresh environment binding: ' + name)
        artifacts = record['artifacts']
        require(artifacts.get('.olean') == record['olean_sha256'] and
                set(artifacts) <= {'.olean', '.olean.private', '.olean.server', '.ir', '.ir.sig', '.so'} and
                all(digest_string(digest) for digest in artifacts.values()),
                'Task B artifact fingerprint mismatch: ' + name)
        local = [dep for dep in module['imports'] if dep in prior]
        require(all(dep in prior or dep == 'Std' or dep.startswith('Mathlib.')
                    for dep in module['imports']), 'Unordered or unmanifested dependency: ' + name)
        require(record['dependency_hashes'] == {dep: prior[dep]['olean_sha256'] for dep in local},
                'Task B dependency olean binding mismatch: ' + name)
        require(record['dependency_artifacts'] == {dep: prior[dep]['artifacts'] for dep in local},
                'Task B dependency artifact binding mismatch: ' + name)
        require(record['dependency_source_sha256'] == {dep: prior[dep]['sha256'] for dep in local},
                'Task B dependency source binding mismatch: ' + name)
        prior[name] = record

    return {'status': 'PASS', 'task_b_verified': True, 'task_a_modules': len(ma['sha256']), 'task_b_modules': len(module_names),
            'task_a_theorem_closures': len(ma['theorems']),
            'task_b_theorem_closures': len(mb['audit_declarations']),
            'task_a_replay_mode': 'fresh', 'task_b_replay_mode': 'fresh',
            'task_a_receipt_sha256': sha(HERE / 'validation/task-a.json'),
            'task_b_receipt_sha256': sha(HERE / 'validation/task-b.json')}


def port_bindings(allow_pending=False, build_receipt=None):
    """Bind the full-port schema; never reinterpret historical direct-Lean receipts."""
    project = ROOT / 'research/lean-multi-host-source'
    manifest_path = project / 'port-manifest.json'
    manifest = json.loads(manifest_path.read_text())
    require(manifest['schemaVersion'] == 1 and manifest['scope'] == 'lean421-full-port',
            'Unsupported port manifest schema')
    for name in manifest['files']:
        require((project / name).resolve().is_relative_to(ROOT), 'Manifest source escapes delivery')
    # Reuse the runner's read-only structural checks, not its build entry point.
    spec = importlib.util.spec_from_file_location('pr442_port_verifier', project / 'verify.py')
    verifier = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(project))
    try:
        spec.loader.exec_module(verifier)
        require(verifier.validate_manifest() == manifest, 'Port manifest changed during validation')
    finally:
        sys.path.pop(0)
    require(manifest['leanVersion'] == '4.21.0' and
            manifest['leanCommit'] == '6741444a63eec253a7eae7a83f1beb3de015023d' and
            manifest['mathlibCommit'] == '308445d7985027f538e281e18df29ca16ede2ba3',
            'Port differs from exact upstream toolchain pins')
    modules = [row['module'] for row in manifest['modules']]
    require(len(modules) == len(set(modules)) ==
            64 + len(manifest['supportModules']) == manifest['inventoryCounts']['localModules'],
            'Wrong derived full-port module count')
    audit_counts = {'task_a': 21, 'task_b': 931, 'hosting': 47,
                    'source_invocation': 422, 'single_stream': 15}
    require(set(manifest['audits']) == set(audit_counts), 'Wrong port audit inventory')
    for key, count in audit_counts.items():
        require(len(manifest['audits'][key]['declarations']) == count, 'Wrong audit count: ' + key)
    receipt_path = build_receipt or HERE / 'validation/lean421-ci-fix-fresh.json'
    if not receipt_path.exists():
        require(allow_pending and build_receipt is None,
                'Current fresh Lean 4.21 receipt is absent; use --allow-pending-port only for preparation')
        return {'status': 'PENDING_PORT', 'task_b_verified': False,
                'port_verified': False, 'local_modules': len(modules),
                'support_modules': len(manifest['supportModules']),
                'original_contribution_files': 66, 'archived_exclusions': 9,
                'planned_audit_counts': audit_counts,
                'notice': 'Full fresh Lean 4.21 replay and CI runtime qualification are pending.'}
    receipt = json.loads(receipt_path.read_text())
    require(receipt['schemaVersion'] == 1 and receipt['scope'] == 'lean421-full-port' and
            receipt['status'] == 'PASS', 'Current port receipt is not a full PASS')
    require(receipt['manifestSha256'] == sha(manifest_path), 'Port receipt/manifest mismatch')
    require(receipt['sourceFiles'] == manifest['files'] and receipt['sourceFilesUnchanged'] is True,
            'Port receipt/source binding mismatch')
    require(receipt['freshLocalBuild'] is True and receipt['trackedClean'] is True,
            'Port receipt must record a fresh build from a clean tracked checkout')
    require(re.fullmatch(r'[0-9a-f]{40}', receipt['gitCommit']) is not None,
            'Invalid build commit')
    require(receipt['compiledLocalModules'] == sorted(modules) and
            receipt['replayedLocalModules'] == [], 'Port receipt reused or omitted local modules')
    limits = receipt['stackLimit']
    require(isinstance(limits, list) and len(limits) == 2 and
            all(type(n) is int and (n == -1 or n > 0) for n in limits) and
            (limits[1] == -1 or (limits[0] != -1 and limits[0] <= limits[1])),
            'Invalid recorded OS stack limits')
    require(receipt['environmentOverrides'] == {} and
            receipt['stackLimitPolicy'] == 'inherited-unchanged' and
            receipt['stackLimitAfter'] == limits, 'External build settings changed')
    toolchain = receipt['toolchain']
    require(toolchain['version'] == manifest['leanVersion'] and
            toolchain['leanCommit'] == manifest['leanCommit'] and
            toolchain['mathlibCommit'] == manifest['mathlibCommit'], 'Receipt toolchain pin mismatch')
    require(toolchain['description'].startswith('Lean (version 4.21.0,'), 'Wrong compiler description')
    for key in ['leanBinarySha256', 'lakeBinarySha256']:
        require(digest_string(toolchain[key]), 'Invalid toolchain binary fingerprint')
    footprint(toolchain['bundledLibraries'], 'Lean bundled libraries')
    require(receipt['toolchainFingerprintUnchanged'] is True,
            'Toolchain was not checked unchanged after verification')
    dependencies = receipt['dependencies']
    require(set(dependencies) == set(manifest['dependencyPins']), 'Wrong dependency inventory')
    for name, pin in manifest['dependencyPins'].items():
        record = dependencies[name]
        require(record['commit'] == pin and digest_string(record['trackedSourceSha256']),
                'Dependency source fingerprint mismatch: ' + name)
        footprint(record['buildArtifactsBefore'], name + ' artifacts before build')
        footprint(record['buildArtifacts'], name + ' artifacts after build')
        require(record['artifactsChangedDuringBuild'] ==
                (record['buildArtifactsBefore'] != record['buildArtifacts']),
                'Inconsistent dependency artifact reuse evidence: ' + name)
    footprint(receipt['localArtifacts'], 'Local build artifacts')
    require(set(receipt['moduleOleanSha256']) == set(modules) and
            all(digest_string(d) for d in receipt['moduleOleanSha256'].values()),
            'Incomplete local artifact fingerprints')
    require(set(receipt['audits']) == set(audit_counts), 'Incomplete receipt audit groups')
    for key, audit in manifest['audits'].items():
        record = receipt['audits'][key]
        require(record['source'] == audit['source'] and
                record['declarationCount'] == audit_counts[key] and
                list(record['declarations']) == audit['declarations'],
                'Receipt audit inventory mismatch: ' + key)
        require(all(isinstance(values, list) and set(values) <=
                    {'propext', 'Classical.choice', 'Quot.sound'}
                    for values in record['declarations'].values()),
                'Nonstandard axiom in ' + key)
    expected_commands = [['lake', 'env', 'lean', option]
                         for option in ['--version', '--githash', '--print-prefix']]
    expected_commands += [['lake', 'build']]
    expected_commands += [['lake', 'env', 'lean', audit['source']]
                          for audit in manifest['audits'].values()]
    require([r['command'] for r in receipt['commands']] == expected_commands,
            'Unexpected compilation or audit command')
    require(all(r['exitCode'] == 0 and r['timedOut'] is False and
                digest_string(r['outputSha256']) for r in receipt['commands']),
            'Build command did not pass or lacks output fingerprint')
    return {'status': 'PASS', 'task_b_verified': True, 'port_verified': True,
            'local_modules': len(modules), 'support_modules': len(manifest['supportModules']),
            'original_contribution_files': 66,
            'archived_exclusions': 9, 'audit_counts': audit_counts,
            'port_receipt_sha256': sha(receipt_path), 'port_replay_mode': 'fresh',
            'ci_runtime_qualification': 'Separate measured projection; not established by this integrity check.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write-manifest', action='store_true',
                   help='for package preparation only; reviewers should omit this')
    p.add_argument('--receipt', type=Path)
    p.add_argument('--allow-pending-task-b', action='store_true',
                   help='allow an absent Task B receipt only when explicitly marked running; result is PENDING_TASK_B')
    p.add_argument('--allow-pending-port', action='store_true',
                   help='check an unfinished Lean 4.21 inventory; report PENDING_PORT')
    p.add_argument('--build-receipt', type=Path,
                   help='validate a new full fresh Lake receipt instead of the packaged receipt')
    args = p.parse_args()
    files = inventory()
    if (ROOT / 'research/lean-multi-host-source/port-manifest.json').exists():
        counts = port_bindings(args.allow_pending_port, args.build_receipt)
    else:
        require(not args.allow_pending_port and args.build_receipt is None,
                'Port options require the full Lean 4.21 manifest')
        counts = bindings(allow_pending_task_b=args.allow_pending_task_b)
    manifest_path = HERE / 'package-manifest.json'
    if args.write_manifest:
        manifest_path.write_text(json.dumps({
            'base_commit': BASE, 'validation_status': counts['status'],
            'historical_task_a_commit': '13611a8958fc71046a83d8431d2bd6335e6a3e2f',
            'historical_task_b_commit': 'f7330c5f5b1c5e85f91a98c95e8efc0e27c03490',
            'excluded_from_recursive_hash': sorted(EXCLUDED), 'sha256': files,
        }, indent=2) + '\n')
    expected = json.loads(manifest_path.read_text())
    require(expected['base_commit'] == BASE, 'Package manifest upstream base mismatch')
    require(expected['validation_status'] == counts['status'] or
            (args.build_receipt is not None and expected['validation_status'] == 'PENDING_PORT'
             and counts['status'] == 'PASS'), 'Package validation status mismatch')
    require(files == expected['sha256'], 'Package inventory differs from package-manifest.json')
    result = {'status': counts['status'], 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'manifest_sha256': sha(manifest_path), 'files_checked': len(files), **counts,
              'scope': 'Inventory, manifested sources and available fresh receipt bindings; PENDING_TASK_B or PENDING_PORT means current verification is unfinished. This verifier does not run Lean or authenticate build provenance.'}
    if args.receipt:
        args.receipt.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
