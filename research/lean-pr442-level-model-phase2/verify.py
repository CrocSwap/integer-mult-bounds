#!/usr/bin/env python3
"""Build/audit Phase 2 with default settings and reject semantic input mutations.

Frozen Phase 1 and predecessor sources/receipts are read and hash checked; this
verifier never regenerates them. No environment overrides, compiler tuning or
resource-limit changes are applied.
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
from update_manifest import declarations, theorem_document

HERE = Path(__file__).resolve().parent
ALLOWED = {'propext', 'Quot.sound', 'Classical.choice'}
FROZEN_PHASE1 = 'd418130e3bbee1cb6923f0f734d5788e09933f57'
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


def plain_code(source):
    """Remove nested block comments, line comments and string contents."""
    out, depth, i = [], 0, 0
    while i < len(source):
        if source.startswith('/-', i):
            depth += 1; i += 2
        elif depth and source.startswith('-/', i):
            depth -= 1; i += 2
        elif not depth and source.startswith('--', i):
            i = source.find('\n', i)
            if i == -1:
                break
        elif not depth and source[i] == '"':
            out.append('""'); i += 1
            while i < len(source) and source[i] != '"':
                i += 2 if source[i] == '\\' else 1
            require(i < len(source), 'Unclosed Lean string')
            i += 1
        else:
            if not depth:
                out.append(source[i])
            i += 1
    require(depth == 0, 'Unclosed Lean block comment')
    return ''.join(out)


def validate():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    manifest = json.loads((HERE / 'MANIFEST.json').read_text())
    protected = json.loads((HERE / 'PROTECTED-FILES.json').read_text())
    require(pins['phase1_commit'] == protected['phase1_commit'] == FROZEN_PHASE1,
            'Wrong frozen Phase 1 pin')
    require(sha(HERE.parent / 'lean-pr442-level-model/MANIFEST.json') ==
            pins['phase1_manifest_sha256'], 'Wrong frozen Phase 1 manifest')
    require(sha(HERE / manifest['workflow']['path']) == manifest['workflow']['sha256'],
            'CI workflow differs from manifest')
    require(declarations() == manifest['declarations'], 'Declaration inventory changed')
    require((HERE / 'THEOREMS.md').read_text() == theorem_document(), 'Exact statements changed')
    wanted = [row['name'] for row in manifest['declarations']]
    require(re.findall(r'^#print axioms (\S+)$', (HERE / 'Audit.lean').read_text(), re.M)
            == wanted, 'Permanent audit differs from inventory')
    for name, expected in manifest['files'].items():
        require(sha(HERE / name) == expected, 'Manifest mismatch: ' + name)
    actual = {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()
              and not any(x in ('.lake', '__pycache__', 'validation')
                          for x in p.relative_to(HERE).parts)
              and p.name != 'MANIFEST.json'}
    require(actual == set(manifest['files']), 'Phase 2 package inventory differs')
    forbidden = re.compile(r'\b(sorry|admit|axiom|native_decide|implemented_by|extern|unsafe|opaque)\b'
                           r'|\bdecide\s*\+\s*native\b|\bset_option\b')
    for module in manifest['modules']:
        source = plain_code((HERE / (module + '.lean')).read_text())
        require(not forbidden.search(source), 'Forbidden construct or nondefault option: ' + module)
        require(not re.search(r'\b(inLevel|derivedPendingTag)\b', source),
                'Circular level dependency: ' + module)
        # pendingAxes is permitted only in comparison statements/proofs in the
        # final module. It must never supply an endpoint or route definition.
        if module != 'IdleOperators':
            require(not re.search(r'\bpendingAxes\b', source), 'Early pending target dependency: ' + module)
        for match in re.finditer(r'^(?:noncomputable )?(def|abbrev)\s+(\w+)', source, re.M):
            following = re.search(r'\n(?:/--|theorem|lemma|def|abbrev|noncomputable|end)\b',
                                  source[match.end():])
            end = match.end() + following.start() if following else len(source)
            body = source[match.start():end]
            comparison = module == 'IdleOperators' and match[2] == 'pendingOperator'
            if comparison:
                require(not re.search(r'\b(sourceBefore|sourceAfter|sourceBeforeOperator|'
                                      r'sourceAfterOperator|idlePendingOperator|endpointOperator|'
                                      r'localProjector|liftedOperator|axisRoute)\b', body),
                        'Endpoint leaked into pending comparison target: ' + module)
                require('PendingDerivation.pendingAxes' in body,
                        'Comparison target lost inherited pendingAxes: ' + module)
            else:
                require(not re.search(r'\b(pendingAxes|pendingOperator|PendingDerivation)\b', body),
                        'Circular pending dependency in definition: ' + module + '.' + match[2])
    for name, expected in protected['files'].items():
        require(sha(HERE / name) == expected, 'Modified frozen source or receipt: ' + name)
    for directory in protected['protected_directories']:
        known = {str((HERE / name).resolve()) for name in protected['files']
                 if str((HERE / name).resolve()).startswith(str((HERE / directory).resolve()) + '/')}
        extra = [p for p in (HERE / directory).rglob('*.lean')
                 if not any(x in ('.lake', '__pycache__') for x in p.parts)
                 and str(p.resolve()) not in known]
        require(not extra, 'Untracked predecessor Lean source in ' + directory)
    for name, pin in pins['inputs'].items():
        blob = (HERE / name).read_bytes()
        require(hashlib.sha256(blob).hexdigest() == pin['sha256_compressed'], 'Compressed input: ' + name)
        require(hashlib.sha256(gzip.decompress(blob)).hexdigest() == pin['sha256_uncompressed'],
                'Uncompressed input: ' + name)
    require((HERE / 'lean-toolchain').read_text().strip() == pins['lean'] ==
            'leanprover/lean4:v4.21.0', 'Wrong toolchain')
    lake = json.loads((HERE / 'lake-manifest.json').read_text())
    phase1 = json.loads((HERE.parent / 'lean-pr442-level-model/lake-manifest.json').read_text())
    gitpins = {p['name']: p['rev'] for p in lake['packages'] if p['type'] == 'git'}
    require(gitpins == {p['name']: p['rev'] for p in phase1['packages'] if p['type'] == 'git'},
            'Dependency pins differ from frozen Phase 1')
    require(gitpins['mathlib'] == pins['mathlib_commit'], 'Wrong Mathlib pin')
    return manifest, protected, gitpins


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lake', default='lake', help='Executable selection only')
    parser.add_argument('--receipt', type=Path)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    require(not any(os.environ.get(k) for k in TUNING), 'External Lean tuning detected')
    stack = resource.getrlimit(resource.RLIMIT_STACK)
    manifest, protected, gitpins = validate()
    receipt = {'schema': 1, 'status': 'RUNNING', 'phase': 2,
               'startedUtc': datetime.now(timezone.utc).isoformat(),
               'gitCommit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=HERE, text=True).strip(),
               'gitBranch': subprocess.check_output(['git', 'branch', '--show-current'], cwd=HERE, text=True).strip(),
               'manifestSha256': sha(HERE / 'MANIFEST.json'), 'sourceFiles': manifest['files'],
               'frozenPhase1Commit': FROZEN_PHASE1, 'protectedFileCount': len(protected['files']),
               'protectedManifestSha256': sha(HERE / 'PROTECTED-FILES.json'),
               'dependencyPins': gitpins, 'stackLimitBefore': list(stack),
               'environmentOverrides': {}, 'defaultSettings': True, 'commands': []}
    start = time.monotonic()

    def command(cmd, timeout=2700):
        tick = time.monotonic()
        result = subprocess.run(cmd, cwd=HERE, text=True, capture_output=True, timeout=timeout)
        output = result.stdout + result.stderr
        display = [('lake' if i == 0 and value == args.lake else
                    'python3' if i == 0 and value == sys.executable else str(value))
                   for i, value in enumerate(cmd)]
        receipt['commands'].append({'command': display, 'seconds': round(time.monotonic()-tick, 3),
                                    'exitCode': result.returncode,
                                    'outputSha256': hashlib.sha256(output.encode()).hexdigest()})
        print(output, end='', flush=True)
        require(result.returncode == 0, 'Failed command: ' + ' '.join(display))
        return output

    try:
        # This read-only extraction check preserves the published descriptors;
        # it does not rebuild or replace the Phase 1 receipt.
        command([sys.executable, '-I', '-B', '../lean-pr442-level-model/generate_sources.py', '--check'])
        # This reconstruction is independent external rational corroboration,
        # recorded separately from the subsequent Lean kernel results.
        source_review = command([sys.executable, '-I', '-B', 'source_review.py'])
        receipt['externalSourceReview'] = json.loads(source_review)
        if args.check_only:
            validate()
            require(resource.getrlimit(resource.RLIMIT_STACK) == stack, 'Stack limit changed')
            receipt['status'] = 'PASS_SOURCE_CHECK_ONLY'
            return
        version = command([args.lake, 'env', 'lean', '--version']).strip()
        require('version 4.21.0' in version, 'Wrong executing Lean version')
        receipt['leanVersion'] = version
        lean_path = Path(command([args.lake, 'env', 'which', 'lean']).strip())
        lake_path = Path(shutil.which(args.lake) or args.lake)
        receipt['executables'] = {'leanSha256': sha(lean_path), 'lakeSha256': sha(lake_path)}
        dependency_sources = {}
        for name, pin in gitpins.items():
            directory = HERE / '.lake/packages' / name
            head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=directory, text=True).strip()
            require(head == pin, 'Dependency checkout mismatch: ' + name)
            require(not subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'],
                                                cwd=directory, text=True), 'Dirty dependency: ' + name)
            untracked = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '-z'],
                                                cwd=directory).decode().split('\0')
            require(not any(n.endswith('.lean') for n in untracked), 'Untracked dependency Lean source: ' + name)
            names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=directory).decode().split('\0')
            rows = [(n, sha(directory / n)) for n in sorted(filter(None, names))]
            dependency_sources[name] = {'commit': pin, 'trackedSourcesSha256': hashlib.sha256(
                json.dumps(rows, separators=(',', ':')).encode()).hexdigest()}
        receipt['dependencySources'] = dependency_sources
        receipt['freshNewModules'] = not any((HERE / '.lake/build').rglob('*.olean'))
        predecessor_build = HERE.parent / 'lean-pr442-level-model/.lake/build'
        receipt['freshPhase1Modules'] = not any(predecessor_build.rglob('*.olean'))
        invocation_build = HERE.parent / 'lean-multi-host-source/.lake/build'
        receipt['freshInvocationProofModules'] = not any(invocation_build.rglob('*.olean'))
        command([args.lake, 'build'])
        output = command([args.lake, 'env', 'lean', 'Audit.lean'])
        audit = {}
        for match in re.finditer(r"'([\w.]+)' (does not depend on any axioms|depends on axioms:\s*\[([^\]]*)\])", output):
            require(match[1] not in audit, 'Duplicate audit output: ' + match[1])
            audit[match[1]] = sorted(x.strip() for x in (match[3] or '').split(',') if x.strip())
        require(set(audit) == {row['name'] for row in manifest['declarations']}, 'Incomplete axiom audit')
        require(all(set(value) <= ALLOWED for value in audit.values()), 'Nonstandard axiom found')
        receipt['axioms'] = audit
        receipt['negativeControls'] = controls(args.lake)
        receipt['newArtifacts'] = {p.relative_to(HERE).as_posix(): sha(p)
                                  for p in sorted((HERE / '.lake/build').rglob('*.olean'))}
        receipt['runtimeArtifactFingerprints'] = {
            'leanCore': artifact_fingerprint(lean_path.resolve().parent.parent / 'lib/lean'),
            'frozenPhase1': artifact_fingerprint(predecessor_build),
            'invocationProof': artifact_fingerprint(invocation_build),
            **{name: artifact_fingerprint(HERE / '.lake/packages' / name / '.lake/build') for name in gitpins}}
        validate()
        require(resource.getrlimit(resource.RLIMIT_STACK) == stack, 'Stack limit changed')
        receipt['status'] = 'PASS'
        print('PASS_PR442_LEVEL_MODEL_PHASE2', flush=True)
    except BaseException as error:
        receipt['status'] = 'FAIL'
        receipt['failure'] = str(error).replace(str(HERE), '<package>')
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
