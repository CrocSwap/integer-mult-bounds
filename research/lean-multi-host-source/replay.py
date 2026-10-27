#!/usr/bin/env python3
"""Build manifested local proofs from fresh sources at Lean trust level zero."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise RuntimeError(message)



def sha256_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def object_sha256(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def footprint(root, files=None):
    """Hash actual bytes, including companion olean/IR/native artifacts, not .hash claims."""
    if files is None:
        files = sorted(p for p in root.rglob('*') if p.is_file()) if root.exists() else []
    records = [(str(p.relative_to(root)), p.stat().st_size, sha256_file(p)) for p in files]
    return {'sha256': object_sha256(records), 'files': len(records),
            'bytes': sum(row[1] for row in records)}


def git_snapshot(root, expected):
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    require(revision == expected, 'Wrong dependency revision: ' + str(root))
    dirty = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'],
                                    cwd=root, text=True)
    require(not dirty, 'Modified tracked dependency sources: ' + str(root))
    extra = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '-z'],
                                    cwd=root).decode().split('\0')
    require(not any(x.endswith('.lean') for x in extra),
            'Untracked Lean dependency sources: ' + str(root))
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
    files = [root / x for x in sorted(tracked) if x and (root / x).is_file()]
    return {'commit': revision, 'tracked_sources': footprint(root, files),
            'build_artifacts': footprint(root / '.lake' / 'build'),
            'lake_configuration_artifacts': footprint(root / '.lake',
                sorted(x for x in (root / '.lake').glob('*') if x.is_file()))}


def external_environment(lean, env, mathlib, manifest, search_paths):
    """Current observation, not an attestation of a historical build environment."""
    prefix = Path(subprocess.check_output([str(lean), '--print-prefix'], env=env,
                                         text=True).strip()).resolve(strict=True)
    require(lean == prefix / 'bin' / 'lean', 'Compiler is outside its reported toolchain prefix')
    snapshot = {'schema': 1, 'toolchain': footprint(prefix),
                'lean_binary_sha256': sha256_file(lean), 'dependencies': {}}
    allowed = {prefix / 'lib' / 'lean': 'toolchain/lib/lean'}
    if mathlib is not None:
        snapshot['dependencies']['Mathlib'] = git_snapshot(mathlib, manifest['mathlib_commit'])
        allowed[(mathlib / '.lake/build/lib/lean').resolve()] = 'Mathlib/.lake/build/lib/lean'
        deps = json.loads((mathlib / 'lake-manifest.json').read_text())
        for package in deps['packages']:
            require(package['type'] == 'git' and not package.get('subDir'),
                    'Unsupported dependency layout: ' + package['name'])
            directory = (mathlib / deps['packagesDir'] / package['name']).resolve(strict=True)
            snapshot['dependencies'][package['name']] = git_snapshot(directory, package['rev'])
            allowed[(directory / '.lake/build/lib/lean').resolve()] = package['name'] + '/.lake/build/lib/lean'
    require(all(path in allowed for path in search_paths), 'Unexpected library search path')
    snapshot['library_search_order'] = [allowed[path] for path in search_paths]
    return {'sha256': object_sha256(snapshot), 'components': snapshot,
            'meaning': 'Observed current bytes and clean pinned Git sources; not historical provenance.'}


def module_artifacts(build, name):
    suffixes = ['.olean', '.olean.private', '.olean.server', '.ir', '.ir.sig', '.so']
    return {suffix: sha256_file(build / (name + suffix)) for suffix in suffixes
            if (build / (name + suffix)).is_file()}


def validate_build_artifact_inventory(build, modules):
    """The first LEAN_PATH entry must not shadow external library modules."""
    suffixes = ('.olean', '.olean.private', '.olean.server', '.ir', '.ir.sig', '.so')
    allowed = {name + suffix for name in [*modules, 'ClosureAudit'] for suffix in suffixes}
    for path in build.rglob('*'):
        require(not (path.is_symlink() and path.is_dir()),
                'Symlinked directory in resumed build: ' + str(path.relative_to(build)))
        if path.is_file() and path.name.endswith(suffixes):
            require(path.relative_to(build).as_posix() in allowed,
                    'Unmanifested library artifact in resumed build: ' + str(path.relative_to(build)))


def write_json_atomic(path, value):
    staging = path.with_name(path.name + '.tmp')
    staging.write_text(json.dumps(value, indent=2) + '\n')
    staging.replace(path)


def legacy_receipt(path, commit, manifest, version):
    """Anchor legacy progress to the committed successful receipt, not mutable progress alone."""
    raw = path.read_bytes()
    repository = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'],
                                              cwd=ROOT, text=True).strip())
    revision = subprocess.check_output(['git', 'rev-parse', commit + '^{commit}'],
                                       cwd=repository, text=True).strip()
    relative = (ROOT / 'replay-result.json').relative_to(repository).as_posix()
    committed = subprocess.check_output(['git', 'show', revision + ':' + relative], cwd=repository)
    require(raw == committed, 'Legacy receipt differs from the specified committed replay-result.json')
    receipt = json.loads(raw)
    require(receipt['status'] == 'PASS' and receipt['trust_level'] == 0 and receipt['lean'] == version,
            'Legacy receipt is not a matching successful trust-zero replay')
    require(receipt['lean_commit'] == manifest['lean_commit'] and
            receipt['mathlib_commit'] == manifest['mathlib_commit'], 'Legacy source pins changed')
    positions = {name: i for i, name in enumerate(receipt['modules'])}
    for name, record in receipt['modules'].items():
        require(all(dep in positions and positions[dep] < positions[name]
                    for dep in record['dependency_hashes']), 'Unordered legacy dependencies: ' + name)
        require(all(value == receipt['modules'][dep]['olean_sha256']
                    for dep, value in record['dependency_hashes'].items()),
                'Inconsistent legacy dependency receipt: ' + name)
    return receipt, {'sha256': hashlib.sha256(raw).hexdigest(), 'git_commit': revision,
                     'repository_path': relative}



def legacy_reuse_record(name, cached, original, anchor, environment_sha, allowed):
    require(allowed,
            'Legacy cache has no historical external fingerprint: ' + name +
            '; use the explicit receipt-anchored legacy mode or a fresh build')
    fields = ['sha256', 'dependency_hashes', 'olean_sha256', 'seconds', 'output']
    require(all(key in original and cached.get(key) == original[key] for key in fields),
            'Legacy progress differs from committed successful receipt: ' + name)
    return dict(cached, historical_external_environment='unrecorded',
                last_observed_environment_sha256=environment_sha, legacy_receipt=anchor)

def cache_matches(cached, source, expected_sha, source_copy, artifacts, dependencies,
                  dependency_artifacts, dependency_sources, environment_sha):
    if not (cached and cached.get('sha256') == expected_sha and
            source_copy.is_file() and source_copy.read_bytes() == source and
            cached.get('dependency_hashes') == dependencies and
            artifacts.get('.olean') == cached.get('olean_sha256')):
        return False
    if cached.get('environment_sha256'):
        return (cached['environment_sha256'] == environment_sha and
                cached.get('artifacts') == artifacts and
                cached.get('dependency_artifacts') == dependency_artifacts and
                cached.get('dependency_source_sha256') == dependency_sources)
    # Old receipts bound only a single .olean, so extra unrecorded companion parts cannot be reused.
    return (set(artifacts) == {'.olean'} and
            cached.get('last_observed_environment_sha256', environment_sha) == environment_sha)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lean', required=True, type=Path)
    p.add_argument('--mathlib', type=Path, help='pinned Mathlib checkout with required modules built')
    p.add_argument('--receipt', type=Path)
    p.add_argument('--build-dir', type=Path, help='new directory for retained sources and logs')
    p.add_argument('--module-timeout', type=int, default=7200,
                   help='seconds allowed per module (large kernel certificates can take tens of minutes)')
    p.add_argument('--resume', action='store_true',
                   help='resume this script\'s retained build, verifying source, dependency, and artifact hashes')
    p.add_argument('--allow-legacy-resume', action='store_true',
                   help='explicitly reuse receipt-anchored old artifacts with unrecorded historical external environment')
    p.add_argument('--legacy-receipt', type=Path,
                   help='successful old replay-result.json matching the committed receipt')
    p.add_argument('--legacy-commit', default='HEAD',
                   help='Git commit containing the old replay-result.json (default HEAD)')
    a = p.parse_args()
    require(not a.allow_legacy_resume or (a.resume and a.legacy_receipt),
            '--allow-legacy-resume requires --resume and --legacy-receipt')
    lean = a.lean.resolve(strict=True)
    env = dict(os.environ)
    env.pop('LEAN_PATH', None)
    env.pop('LEAN_SRC_PATH', None)
    env.pop('LEAN_SYSROOT', None)
    env['PATH'] = str(lean.parent) + os.pathsep + env.get('PATH', '')
    version = subprocess.check_output([str(lean), '--version'], env=env, text=True).strip()
    require(version.startswith('Lean (version 4.33.0,'), 'Lean 4.33.0 required')
    manifest_bytes = (ROOT / 'proof-manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    revision = subprocess.check_output([str(lean), '--githash'], env=env, text=True).strip()
    require(revision == manifest['lean_commit'], 'Wrong Lean revision')
    mathlib_path = ''
    mathlib = None
    search_paths = []
    if any(i.startswith('Mathlib.') for m in manifest['modules'] for i in m['imports']):
        require(a.mathlib is not None, '--mathlib required')
        mathlib = a.mathlib.resolve(strict=True)
        revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=mathlib,
                                           text=True).strip()
        require(revision == manifest['mathlib_commit'], 'Wrong Mathlib revision')
        require((mathlib / 'lake-manifest.json').read_bytes() ==
                (ROOT / 'mathlib-lake-manifest.json').read_bytes(), 'Wrong Mathlib dependencies')
        path = subprocess.check_output([str(lean.parent / 'lake'), 'env', 'printenv', 'LEAN_PATH'],
                                       cwd=mathlib, env=env, text=True).strip()
        search_paths = [(mathlib / x).resolve() for x in path.split(os.pathsep) if x]
        mathlib_path = os.pathsep.join(map(str, search_paths))
    external = external_environment(lean, env, mathlib, manifest, search_paths)
    old_receipt, old_anchor = (None, None)
    if a.allow_legacy_resume:
        old_receipt, old_anchor = legacy_receipt(a.legacy_receipt, a.legacy_commit, manifest, version)
    tmp = None
    if a.build_dir:
        build = a.build_dir.resolve()
        if not a.resume:
            build.mkdir(parents=True, exist_ok=False)
    else:
        require(not a.resume, '--resume requires --build-dir')
        tmp = tempfile.TemporaryDirectory(prefix='multi-host-source-')
        build = Path(tmp.name)
    progress_path = build / 'build-progress.json'
    identity = {'lean': version, 'mathlib_commit': manifest.get('mathlib_commit')}
    progress = {'identity': identity, 'modules': {}}
    if a.resume:
        validate_build_artifact_inventory(build, [m['module'] for m in manifest['modules']])
        progress = json.loads(progress_path.read_text())
        require(progress['identity'] == identity, 'Resumed toolchain changed')
    reports, results = {}, {}
    fresh, reused, legacy = [], [], []
    write_json_atomic(build / 'external-environment.json', external)
    try:
        env['LEAN_PATH'] = str(build) + (os.pathsep + mathlib_path if mathlib_path else '')
        prior = []
        for m in manifest['modules']:
            name = m['module']
            source = (ROOT / m['source']).read_bytes()
            require(hashlib.sha256(source).hexdigest() == m['sha256'], 'Source mismatch: ' + name)
            code = re.sub(r'--[^\n]*', '', re.sub(r'/\-[\s\S]*?\-/', '', source.decode()))
            require(not re.search(r'\b(sorry|admit|native_decide|unsafe)\b', code),
                    'Forbidden proof escape: ' + name)
            require(not re.search(r'^\s*(axiom|opaque)\s', code, re.M), 'Project axiom: ' + name)
            imports = re.findall(r'^import (\S+)$', code, re.M)
            require(imports == m['imports'], 'Import mismatch: ' + name)
            require(all(x == 'Std' or x in prior or x.startswith('Mathlib.') for x in imports),
                    'Unmanifested dependency: ' + name)
            dependency_hashes = {x: hashlib.sha256((build / (x + '.olean')).read_bytes()).hexdigest()
                                 for x in imports if x in prior}
            dependency_artifacts = {x: module_artifacts(build, x) for x in imports if x in prior}
            dependency_sources = {x: results[x]['sha256'] for x in imports if x in prior}
            cached = progress['modules'].get(name)
            artifact = build / (name + '.olean')
            artifacts = module_artifacts(build, name)
            is_match = a.resume and cache_matches(cached, source, m['sha256'],
                build / (name + '.lean'), artifacts, dependency_hashes, dependency_artifacts,
                dependency_sources, external['sha256'])
            if is_match and not cached.get('environment_sha256'):
                original = old_receipt['modules'].get(name, {}) if old_receipt else {}
                cached = legacy_reuse_record(name, cached, original, old_anchor,
                                             external['sha256'], a.allow_legacy_resume)
                legacy.append(name)
            if is_match:
                results[name] = cached
                progress['modules'][name] = cached
                write_json_atomic(progress_path, progress)
                reused.append(name)
                prior.append(name)
                label = 'legacy reuse; historical external environment unrecorded' if name in legacy else 'verified cached build'
                print(name + ': PASS (' + label + ')', flush=True)
                continue
            (build / (name + '.lean')).write_bytes(source)
            start = time.monotonic()
            result = subprocess.run([str(lean), '-t', '0', '-o', name + '.olean', name + '.lean'],
                                    cwd=build, env=env, text=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, timeout=a.module_timeout)
            (build / (name + '.log')).write_text(result.stdout)
            require(result.returncode == 0 and 'sorry' not in result.stdout,
                    name + '\n' + result.stdout)
            fresh.append(name)
            results[name] = {'environment_sha256': external['sha256'],
                             'historical_external_environment': 'fingerprinted_at_compile',
                             'artifacts': module_artifacts(build, name),
                             'dependency_artifacts': dependency_artifacts,
                             'dependency_source_sha256': dependency_sources,
                             'seconds': round(time.monotonic() - start, 3),
                             'sha256': m['sha256'], 'output': result.stdout,
                             'dependency_hashes': dependency_hashes,
                             'olean_sha256': hashlib.sha256(artifact.read_bytes()).hexdigest()}
            progress['modules'][name] = results[name]
            write_json_atomic(progress_path, progress)
            prior.append(name)
            print(name + ': PASS', flush=True)
        audit = '\n'.join('import ' + m['module'] for m in manifest['modules']) + '\n'
        audit += '\n'.join('#print axioms ' + name for name in manifest['audit_declarations']) + '\n'
        (build / 'ClosureAudit.lean').write_text(audit)
        result = subprocess.run([str(lean), '-t', '0', 'ClosureAudit.lean'], cwd=build,
                                env=env, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=300)
        require(result.returncode == 0, result.stdout)
        (build / 'ClosureAudit.log').write_text(result.stdout)
        for line in result.stdout.splitlines():
            match = re.fullmatch(r"'([^']+)' does not depend on any axioms", line)
            if match:
                name, axioms = match[1], []
            else:
                match = re.fullmatch(r"'([^']+)' depends on axioms: \[([^]]*)\]", line)
                require(match is not None, 'Unexpected audit output: ' + line)
                name, axioms = match[1], match[2].split(', ')
            require(name not in reports, 'Duplicate audit declaration')
            require(set(axioms) <= {'propext', 'Quot.sound', 'Classical.choice'},
                    'Unexpected transitive axioms: ' + line)
            reports[name] = axioms
        require(list(reports) == manifest['audit_declarations'], 'Axiom inventory mismatch')
        external_after = external_environment(lean, env, mathlib, manifest, search_paths)
        require(external_after['sha256'] == external['sha256'], 'External environment changed during replay')
        receipt = {'status': 'PASS', 'lean': version, 'trust_level': 0,
                   'lean_commit': manifest['lean_commit'],
                   'completed_utc': datetime.now(timezone.utc).isoformat(),
                   'manifest_sha256': hashlib.sha256(manifest_bytes).hexdigest(),
                   'mathlib_commit': manifest.get('mathlib_commit'),
                   'external_environment': external,
                   'replay_mode': 'resumed' if a.resume else 'fresh',
                   'fresh_modules_compiled': len(fresh), 'reused_modules': len(reused),
                   'legacy_reused_modules': len(legacy),
                   'fresh_module_names': fresh, 'reused_module_names': reused,
                   'legacy_module_names': legacy,
                   'historical_external_environment': 'unrecorded_for_legacy_modules' if legacy else 'fingerprinted_at_compile',
                   'closure_audit': 'rerun now with lean -t 0; axiom inventory, not leanchecker --fresh',
                   'modules': results, 'axioms': reports,
                   'scope': manifest['scope']}
        if a.receipt:
            a.receipt.write_text(json.dumps(receipt, indent=2) + '\n')
        print(json.dumps({'status': 'PASS', 'fresh_modules': len(fresh),
                          'reused_modules': len(reused), 'legacy_reused_modules': len(legacy),
                          'audited_declarations': len(reports), 'scope': manifest['scope']}))
    finally:
        if tmp:
            tmp.cleanup()


if __name__ == '__main__':
    main()
