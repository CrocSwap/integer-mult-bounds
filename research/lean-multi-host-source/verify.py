#!/usr/bin/env python3
"""Build the complete Lean 4.21 contribution through Lake and audit its axioms.

No compilation flags, environment overrides, or resource-limit changes are
applied. A receipt distinguishes a fresh local build from an incremental run.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import signal
import subprocess
import time
import tomllib
from update_port_manifest import code

ROOT = Path(__file__).resolve().parent
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}
FORBIDDEN = re.compile(
    r'\b(sorry|admit|axiom|native_decide|implemented_by|extern|unsafe|opaque)\b'
    r'|\bdecide\s*\+\s*native\b'
    r'|set_option\s+(?!maxHeartbeats\b|maxRecDepth\b)')
AUDIT_COUNTS = {'task_a': 21, 'task_b': 931, 'hosting': 47,
                'source_invocation': 422, 'single_stream': 15}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def inherited_stack_limits(expected=None):
    """Observe the host's limits without imposing or changing a machine default.

    A limit alone cannot establish whether the caller previously changed it.
    The workflow must use its ordinary environment; the receipt records the
    inherited values and checks that this verifier leaves them unchanged.
    """
    limits = resource.getrlimit(resource.RLIMIT_STACK)
    require(all(type(n) is int and (n == resource.RLIM_INFINITY or n > 0)
                for n in limits), 'Invalid inherited OS stack limit')
    require(limits[1] == resource.RLIM_INFINITY or
            (limits[0] != resource.RLIM_INFINITY and limits[0] <= limits[1]),
            'Invalid inherited OS stack limit ordering')
    require(expected is None or limits == expected,
            'OS stack limit changed during verification')
    return limits


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def footprint(root):
    records = [(p.relative_to(root).as_posix(), p.stat().st_size, sha(p))
               for p in sorted(root.rglob('*')) if p.is_file()]
    raw = json.dumps(records, separators=(',', ':')).encode()
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'files': len(records),
            'bytes': sum(size for _, size, _ in records)}


def validate_manifest():
    manifest = json.loads((ROOT / 'port-manifest.json').read_text())
    require(manifest['scope'] == 'lean421-full-port', 'Wrong manifest scope')
    for name, digest in manifest['files'].items():
        require(sha(ROOT / name) == digest, 'Changed manifested source: ' + name)
    config = tomllib.loads((ROOT / 'lakefile.toml').read_text())
    require(config['lean_lib'] == manifest['libraries'], 'Changed Lake library configuration')
    require(config['defaultTargets'] == manifest['defaultTargets'], 'Changed default targets')
    require(config['require'] == [{'name': 'mathlib',
        'git': 'https://github.com/leanprover-community/mathlib4',
        'rev': manifest['mathlibCommit']}], 'Changed Mathlib requirement')
    modules = {r['module']: r for r in manifest['modules']}
    configured = [name for lib in config['lean_lib'] for name in lib['roots']]
    configured_paths = {name: (ROOT / lib.get('srcDir', '.') /
        (name.replace('.', '/') + '.lean')).resolve()
        for lib in config['lean_lib'] for name in lib['roots']}
    require(len(modules) == len(manifest['modules']) == len(configured) and
            set(configured) == set(modules), 'Wrong complete module inventory')
    originals = manifest['originalContribution']
    require(len(originals) == 66, 'Wrong original contribution inventory')
    original_sources = {(ROOT / row['source']).resolve() for row in originals}
    module_sources = {(ROOT / row['source']).resolve() for row in manifest['modules']}
    audit_sources = {(ROOT / row['source']).resolve() for row in manifest['audits'].values()}
    require(len(original_sources) == 66 and len(module_sources) == len(modules),
            'Duplicate original or module source')
    require(len(original_sources & module_sources) == 64 and
            len(original_sources - module_sources) == 2 and
            original_sources <= module_sources | audit_sources,
            'Original contribution is not fully covered by 64 modules and two audits')
    for row in originals:
        require(sha(ROOT / row['source']) == row['sha256'],
                'Changed original contribution source: ' + row['source'])
    supports = [row['module'] for row in manifest['modules']
                if (ROOT / row['source']).resolve() not in original_sources]
    require(manifest['supportModules'] == supports and len(modules) == 64 + len(supports),
            'Wrong support-module inventory')
    task_b = json.loads((ROOT / 'proof-manifest.json').read_text())
    require(len(task_b['modules']) == len({r['module'] for r in task_b['modules']}) and
            all(modules.get(row['module']) == row for row in task_b['modules']),
            'Task B module inventory differs from the full package')
    require(task_b['audit_declarations'] == manifest['audits']['task_b']['declarations'],
            'Task B audit differs from the permanent inventory')
    require(manifest['inventoryCounts'] == {'originalContributionFiles': 66,
        'originalCompiledModules': 64, 'originalAuditFiles': 2,
        'supportModules': len(supports), 'localModules': len(modules),
        'taskBModules': len(task_b['modules'])}, 'Inconsistent derived module counts')
    require(len(manifest['archivedExclusions']) == 9, 'Wrong archival inventory')
    exclusions = {(ROOT / row['source']).resolve() for row in manifest['archivedExclusions']}
    require(len(exclusions) == 9 and not exclusions & (module_sources | audit_sources),
            'Archived evidence is duplicated or included in the build or audits')
    for row in manifest['archivedExclusions']:
        require(sha(ROOT / row['source']) == row['sha256'] == row['baseline_sha256'],
                'Changed archived evidence: ' + row['source'])
    for row in manifest['modules']:
        source = ROOT / row['source']
        require(source.resolve() == configured_paths[row['module']],
                'Module source differs from its Lake root: ' + row['module'])
        require(source.resolve() not in exclusions, 'Archived evidence in build target')
        require(sha(source) == row['sha256'], 'Changed module: ' + row['module'])
        text = code(source.read_text())
        require(not FORBIDDEN.search(text), 'Forbidden source construct: ' + row['module'])
        imports = [n for line in re.findall(r'^import\s+(.+)$', text, re.M) for n in line.split()]
        require(imports == row['imports'], 'Changed imports: ' + row['module'])
        require(all(n in modules or n in ('Std', 'Lean')
                    or n.startswith(('Std.', 'Lean.', 'Mathlib.')) for n in imports),
                'Unmanifested local import: ' + row['module'])
    require(set(manifest['audits']) == set(AUDIT_COUNTS), 'Wrong audit groups')
    for key, audit in manifest['audits'].items():
        source = ROOT / audit['source']
        require(source.resolve() not in exclusions and sha(source) == audit['sha256'],
                'Changed audit source: ' + key)
        text = code(source.read_text())
        require(not FORBIDDEN.search(text), 'Forbidden audit source: ' + key)
        wanted = re.findall(r'^#print axioms (\S+)\s*$', text, re.M)
        require(wanted == audit['declarations'] and len(wanted) == len(set(wanted)) == AUDIT_COUNTS[key],
                'Wrong audit inventory: ' + key)
        require(all(n in modules for n in re.findall(r'^import (\S+)\s*$', text, re.M)),
                'Unmanifested audit import: ' + key)
    require('SourceInvocation.actualContract' in manifest['audits']['task_b']['declarations'],
            'Missing actualContract audit')
    lake_manifest = json.loads((ROOT / 'lake-manifest.json').read_text())
    pins = {p['name']: p['rev'] for p in lake_manifest['packages']}
    require(pins == manifest['dependencyPins'] and len(pins) == 9, 'Changed dependency pins')
    require((ROOT / 'lean-toolchain').read_text().strip() == 'leanprover/lean4:v4.21.0',
            'Wrong toolchain file')
    return manifest


def dependency_sources(manifest):
    result = {}
    lake_manifest = json.loads((ROOT / 'lake-manifest.json').read_text())
    for package in lake_manifest['packages']:
        directory = ROOT / lake_manifest['packagesDir'] / package['name']
        head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=directory, text=True).strip()
        require(head == manifest['dependencyPins'][package['name']], 'Wrong dependency revision: ' + package['name'])
        dirty = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'],
                                        cwd=directory, text=True)
        require(not dirty, 'Modified dependency: ' + package['name'])
        extra = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '-z'],
                                        cwd=directory).decode().split('\0')
        require(not any(n.endswith('.lean') for n in extra), 'Untracked dependency Lean source: ' + package['name'])
        paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=directory).decode().split('\0')
        records = [(name, sha(directory / name)) for name in sorted(filter(None, paths))]
        result[package['name']] = {'commit': head, 'trackedSourceSha256': hashlib.sha256(
            json.dumps(records, separators=(',', ':')).encode()).hexdigest()}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lake', default='lake', help='Lake executable selection only')
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    tuning = ['LEAN_PATH', 'LEAN_OPTS', 'LEAN_NUM_THREADS', 'LEAN_SYSROOT', 'LEAN_SRC_PATH',
              'MATHLIB_CACHE_DIR', 'LAKE_OVERRIDE_LEAN', 'LEAN_GITHASH', 'LAKE_JOBS',
              'LEAN_STACK_SIZE', 'LEAN_MAX_MEMORY']
    require(not any(os.environ.get(key) for key in tuning), 'External Lean tuning detected')
    stack = inherited_stack_limits()
    manifest = validate_manifest()
    started = time.monotonic()
    receipt = {'schemaVersion': 1, 'status': 'RUNNING', 'scope': 'lean421-full-port',
        'manifestSha256': sha(ROOT / 'port-manifest.json'),
        'startedUtc': datetime.now(timezone.utc).isoformat(),
        'stackLimit': list(stack), 'stackLimitPolicy': 'inherited-unchanged',
        'environmentOverrides': {}, 'commands': [], 'audits': {},
        'sourceFiles': manifest['files'],
        'freshLocalBuild': not any(p.is_file() for p in (ROOT / '.lake/build').rglob('*')),
        'gitCommit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'trackedClean': not subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=ROOT, text=True)}

    def run(arguments, display_output=True):
        start = time.monotonic()
        cpu_before = resource.getrusage(resource.RUSAGE_CHILDREN)
        print('$ lake ' + ' '.join(arguments), flush=True)
        process = subprocess.Popen([args.lake, *arguments], cwd=ROOT, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)
        timed_out = False
        try:
            output, _ = process.communicate(timeout=max(1, 2700 - (time.monotonic() - started)))
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                output, _ = process.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                output, _ = process.communicate()
        elapsed = round(time.monotonic() - start, 3)
        cpu_after = resource.getrusage(resource.RUSAGE_CHILDREN)
        receipt['commands'].append({'command': ['lake', *arguments], 'seconds': elapsed,
            'cpuSeconds': round(cpu_after.ru_utime + cpu_after.ru_stime
                - cpu_before.ru_utime - cpu_before.ru_stime, 3),
            'exitCode': process.returncode, 'timedOut': timed_out,
            'outputSha256': hashlib.sha256(output.encode()).hexdigest()})
        if display_output or process.returncode or timed_out:
            print(output, end='', flush=True)
        require(not timed_out and process.returncode == 0, 'Lake command failed or total verification exceeded 45 minutes')
        require("declaration uses 'sorry'" not in output, 'Incomplete proof')
        return output

    try:
        version = run(['env', 'lean', '--version']).strip()
        require(version.startswith('Lean (version 4.21.0,'), 'Wrong Lean version')
        revision = run(['env', 'lean', '--githash']).strip()
        require(revision == manifest['leanCommit'], 'Wrong Lean revision')
        prefix = Path(run(['env', 'lean', '--print-prefix'], display_output=False).strip())
        receipt['toolchain'] = {'version': '4.21.0', 'description': version,
            'leanCommit': revision, 'mathlibCommit': manifest['mathlibCommit'],
            'leanBinarySha256': sha(prefix / 'bin/lean'), 'lakeBinarySha256': sha(prefix / 'bin/lake'),
            'bundledLibraries': footprint(prefix / 'lib/lean')}
        before = dependency_sources(manifest)
        lake_manifest = json.loads((ROOT / 'lake-manifest.json').read_text())
        artifacts_before = {name: footprint(ROOT / lake_manifest['packagesDir'] / name / '.lake/build')
                            for name in before}
        build_output = run(['build'])
        modules = {r['module'] for r in manifest['modules']}
        built = set(re.findall(r'\bBuilt (\S+)', build_output)) & modules
        replayed = set(re.findall(r'\bReplayed (\S+)', build_output)) & modules
        receipt['compiledLocalModules'] = sorted(built)
        receipt['replayedLocalModules'] = sorted(replayed)
        if receipt['freshLocalBuild']:
            require(built == modules and not replayed, 'Fresh build did not compile every local module')
        for key, audit in manifest['audits'].items():
            output = run(['env', 'lean', audit['source']])
            rows = re.findall(r"^'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", output, re.M)
            wanted = audit['declarations']
            require(len(rows) == len(wanted) and {n for n, _ in rows} == set(wanted),
                    'Incomplete, duplicate, or extra axiom reports: ' + key)
            declarations = {n: list(filter(None, axioms.split(', '))) for n, axioms in rows}
            require(all(set(names) <= ALLOWED for names in declarations.values()), 'Nonstandard axiom: ' + key)
            receipt['audits'][key] = {'source': audit['source'], 'declarationCount': len(declarations),
                'declarations': declarations, 'seconds': receipt['commands'][-1]['seconds']}
        after = dependency_sources(manifest)
        require(before == after, 'Dependency sources changed during verification')
        receipt['dependencies'] = after
        for name, record in receipt['dependencies'].items():
            record['buildArtifacts'] = footprint(ROOT / lake_manifest['packagesDir'] / name / '.lake/build')
            record['buildArtifactsBefore'] = artifacts_before[name]
            record['artifactsChangedDuringBuild'] = record['buildArtifacts'] != artifacts_before[name]
        require(sha(prefix / 'bin/lean') == receipt['toolchain']['leanBinarySha256']
                and sha(prefix / 'bin/lake') == receipt['toolchain']['lakeBinarySha256']
                and footprint(prefix / 'lib/lean') == receipt['toolchain']['bundledLibraries'],
                'Toolchain files changed during verification')
        receipt['toolchainFingerprintUnchanged'] = True
        require(validate_manifest() == manifest, 'Manifest changed during verification')
        require(sha(ROOT / 'port-manifest.json') == receipt['manifestSha256'], 'Manifest changed during verification')
        receipt['sourceFilesUnchanged'] = True
        receipt['localArtifacts'] = footprint(ROOT / '.lake/build')
        receipt['moduleOleanSha256'] = {name: sha(ROOT / '.lake/build/lib/lean' / (name.replace('.', '/') + '.olean')) for name in sorted(modules)}
        receipt['stackLimitAfter'] = list(inherited_stack_limits(stack))
        require(time.monotonic() - started < 2700, 'Total verification exceeded 45 minutes')
        receipt['status'] = 'PASS'
    except Exception as exc:
        receipt['status'] = 'FAIL'
        receipt['error'] = str(exc)
        raise
    finally:
        receipt['completedUtc'] = datetime.now(timezone.utc).isoformat()
        receipt['totalSeconds'] = round(time.monotonic() - started, 3)
        if args.receipt:
            args.receipt.parent.mkdir(parents=True, exist_ok=True)
            args.receipt.write_text(json.dumps(receipt, indent=2) + '\n')
    kind = 'fresh' if receipt['freshLocalBuild'] else 'incremental (not a fresh-build receipt)'
    print(f"PASS full Lean 4.21 port: {len(modules)} modules, five audits; {kind}")


if __name__ == '__main__':
    main()
