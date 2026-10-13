#!/usr/bin/env python3
"""Build Phase 1 through ordinary Lake commands; audit and test literal mutations.

No compiler flags, environment overrides or resource-limit changes are applied.
Existing predecessor sources are checked byte-for-byte against their base pin.
"""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import shutil
import subprocess
import sys
import time

from negative_controls import run as controls
from update_manifest import declarations

HERE = Path(__file__).resolve().parent
ALLOWED = {'propext', 'Quot.sound', 'Classical.choice'}
TUNING = ['LEAN_PATH', 'LEAN_OPTS', 'LEAN_NUM_THREADS', 'LEAN_SYSROOT', 'LEAN_SRC_PATH',
          'MATHLIB_CACHE_DIR', 'LAKE_OVERRIDE_LEAN', 'LEAN_GITHASH', 'LAKE_JOBS',
          'LEAN_STACK_SIZE', 'LEAN_MAX_MEMORY']


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_fingerprint(root):
    rows = [(p.relative_to(root).as_posix(), p.stat().st_size, sha(p))
            for p in sorted(root.rglob('*.olean')) if p.is_file()]
    return {'files': len(rows), 'bytes': sum(row[1] for row in rows),
            'sha256': hashlib.sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()}


def plain_code(text):
    # Remove nested Lean block comments and line comments before scanning.
    out, depth, i = [], 0, 0
    while i < len(text):
        if text.startswith('/-', i):
            depth += 1; i += 2
        elif depth and text.startswith('-/', i):
            depth -= 1; i += 2
        elif not depth and text.startswith('--', i):
            i = text.find('\n', i)
            if i == -1:
                break
        else:
            if not depth:
                out.append(text[i])
            i += 1
    require(depth == 0, 'Unclosed Lean block comment')
    return ''.join(out)


def validate():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    manifest = json.loads((HERE / 'MANIFEST.json').read_text())
    require(sha(HERE / manifest['workflow']['path']) == manifest['workflow']['sha256'],
            'CI workflow differs from manifest')
    require(declarations() == manifest['declarations'], 'Axiom inventory changed')
    wanted = [r['name'] for r in manifest['declarations']]
    require(len(wanted) == len(set(wanted)), 'Duplicate audited declaration')
    require(re.findall(r'^#print axioms (\S+)$', (HERE / 'Audit.lean').read_text(), re.M)
            == wanted, 'Permanent audit differs from inventory')
    for name, expected in manifest['files'].items():
        require(sha(HERE / name) == expected, 'Manifest mismatch: ' + name)
    actual = {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()
              and not any(x in ('.lake', '__pycache__', 'validation')
                          for x in p.relative_to(HERE).parts)
              and p.name != 'MANIFEST.json'}
    require(actual == set(manifest['files']), 'Package file inventory differs')
    forbidden = re.compile(r'\b(sorry|admit|axiom|native_decide|implemented_by|extern|unsafe|opaque)\b'
                           r'|\bdecide\s*\+\s*native\b'
                           r'|set_option\s+(?!maxHeartbeats\b|maxRecDepth\b)')
    for module in manifest['modules']:
        source = plain_code((HERE / (module + '.lean')).read_text())
        require(not forbidden.search(source), 'Forbidden Lean construct: ' + module)
        require(not re.search(r'\b(inLevel|pendingAxes|derivedPendingTag)\b', source),
                'Circular pending-mask dependency: ' + module)
    base = json.loads((HERE / 'BASE-FILES.json').read_text())
    require(base['base_commit'] == pins['base_commit'], 'Wrong base file pin')
    for name, expected in base['files'].items():
        require(sha(HERE / name) == expected, 'Modified predecessor: ' + name)
    for name, expected in pins['inputs'].items():
        data = (HERE / name).read_bytes()
        require(hashlib.sha256(data).hexdigest() == expected['sha256_compressed'],
                'Compressed input hash: ' + name)
        require(hashlib.sha256(gzip.decompress(data)).hexdigest() == expected['sha256_uncompressed'],
                'Uncompressed input hash: ' + name)
    require((HERE / 'lean-toolchain').read_text().strip() == pins['lean'] ==
            'leanprover/lean4:v4.21.0', 'Wrong toolchain')
    lake = json.loads((HERE / 'lake-manifest.json').read_text())
    parent = json.loads((HERE.parent / 'lean-multi-host-source/lake-manifest.json').read_text())
    gitpins = {p['name']: p['rev'] for p in lake['packages'] if p['type'] == 'git'}
    require(gitpins == {p['name']: p['rev'] for p in parent['packages']}, 'Dependency pins differ')
    require(gitpins['mathlib'] == pins['mathlib_commit'], 'Wrong Mathlib pin')
    return manifest, gitpins


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lake', default='lake', help='Executable selection only')
    parser.add_argument('--receipt', type=Path)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    require(not any(os.environ.get(k) for k in TUNING), 'External Lean tuning detected')
    stack = resource.getrlimit(resource.RLIMIT_STACK)
    manifest, gitpins = validate()
    receipt = {'schema': 1, 'status': 'RUNNING', 'phase': 1,
               'startedUtc': datetime.now(timezone.utc).isoformat(),
               'gitCommit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=HERE, text=True).strip(),
               'manifestSha256': sha(HERE / 'MANIFEST.json'),
               'sourceFiles': manifest['files'], 'dependencyPins': gitpins,
               'stackLimitBefore': list(stack), 'environmentOverrides': {}, 'commands': []}
    start = time.monotonic()

    def command(cmd, timeout=2700):
        tick = time.monotonic()
        r = subprocess.run(cmd, cwd=HERE, text=True, capture_output=True, timeout=timeout)
        output = r.stdout + r.stderr
        # Receipts use portable commands and paths, without private workspace paths.
        display = [('lake' if i == 0 and v == args.lake else
                    'python3' if i == 0 and v == sys.executable else str(v))
                   for i, v in enumerate(cmd)]
        receipt['commands'].append({'command': display, 'seconds': round(time.monotonic()-tick, 3),
                                    'exitCode': r.returncode,
                                    'outputSha256': hashlib.sha256(output.encode()).hexdigest()})
        print(output, end='', flush=True)
        require(r.returncode == 0, 'Failed command: ' + ' '.join(display))
        return output

    try:
        command([sys.executable, '-I', '-B', 'generate_sources.py', '--check'])
        if args.check_only:
            receipt['status'] = 'PASS_SOURCE_CHECK_ONLY'
            return
        version = command([args.lake, 'env', 'lean', '--version']).strip()
        require('version 4.21.0' in version, 'Wrong executing Lean version')
        receipt['leanVersion'] = version
        lean_path = Path(command([args.lake, 'env', 'which', 'lean']).strip())
        lake_path = Path(shutil.which(args.lake) or args.lake)
        receipt['executables'] = {'leanSha256': sha(lean_path),
                                  'lakeSha256': sha(lake_path)}
        dependency_sources = {}
        for name, pin in gitpins.items():
            directory = HERE / '.lake/packages' / name
            head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=directory, text=True).strip()
            require(head == pin, 'Dependency checkout mismatch: ' + name)
            require(not subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'],
                                                cwd=directory, text=True), 'Dirty dependency: ' + name)
            untracked = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '-z'],
                                                cwd=directory).decode().split('\0')
            require(not any(n.endswith('.lean') for n in untracked),
                    'Untracked dependency Lean source: ' + name)
            names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=directory).decode().split('\0')
            source_records = [(n, sha(directory / n)) for n in sorted(filter(None, names))]
            dependency_sources[name] = {'commit': pin, 'trackedSourcesSha256':
                hashlib.sha256(json.dumps(source_records, separators=(',', ':')).encode()).hexdigest()}
        receipt['dependencySources'] = dependency_sources
        receipt['freshNewModules'] = not any((HERE / '.lake/build').rglob('*.olean'))
        parent_build = HERE.parent / 'lean-multi-host-source/.lake/build'
        receipt['freshPredecessorModules'] = not any(parent_build.rglob('*.olean'))
        command([args.lake, 'build'])
        output = command([args.lake, 'env', 'lean', 'Audit.lean'])
        audit = {}
        for match in re.finditer(r"'([\w.]+)' (does not depend on any axioms|depends on axioms:\s*\[([^\]]*)\])", output):
            require(match[1] not in audit, 'Duplicate audit output: ' + match[1])
            audit[match[1]] = sorted(x.strip() for x in (match[3] or '').split(',') if x.strip())
        require(set(audit) == {r['name'] for r in manifest['declarations']}, 'Incomplete axiom audit')
        require(all(set(v) <= ALLOWED for v in audit.values()), 'Nonstandard axiom found')
        receipt['axioms'] = audit
        receipt['negativeControls'] = controls(args.lake)
        receipt['newArtifacts'] = {p.relative_to(HERE).as_posix(): sha(p)
                                   for p in sorted((HERE / '.lake/build').rglob('*.olean'))}
        receipt['runtimeArtifactFingerprints'] = {
            'leanCore': artifact_fingerprint(lean_path.resolve().parent.parent / 'lib/lean'),
            'predecessor': artifact_fingerprint(parent_build),
            **{name: artifact_fingerprint(HERE / '.lake/packages' / name / '.lake/build')
               for name in gitpins}}
        validate()
        require(resource.getrlimit(resource.RLIMIT_STACK) == stack, 'Stack limit changed')
        receipt['status'] = 'PASS'
        print('PASS_PR442_LEVEL_MODEL_PHASE1', flush=True)
    except BaseException as e:
        receipt['status'] = 'FAIL'
        receipt['failure'] = str(e).replace(str(HERE), '<package>')
        raise
    finally:
        receipt['totalSeconds'] = round(time.monotonic() - start, 3)
        receipt['stackLimitAfter'] = list(resource.getrlimit(resource.RLIMIT_STACK))
        receipt['completedUtc'] = datetime.now(timezone.utc).isoformat()
        if args.receipt:
            args.receipt.parent.mkdir(parents=True, exist_ok=True)
            args.receipt.write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    main()
