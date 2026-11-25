#!/usr/bin/env python3
"""Fresh offline Lean kernel replay of Task A, independent of Task B."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
DEPS = ['CoordinateSwap', 'Hosting', 'PhysicalHosting']
MODULES = DEPS + ['MultiHosting', 'SingleHostRecovery', 'MultiHostControls']


def require(ok, message):
    if not ok:
        raise RuntimeError(message)



def sha256_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def toolchain_snapshot(lean, env):
    prefix = Path(subprocess.check_output([str(lean), '--print-prefix'], env=env,
                                         text=True, timeout=30).strip()).resolve(strict=True)
    require(lean == prefix / 'bin' / 'lean', 'Compiler is outside its reported toolchain prefix')
    records = [(str(p.relative_to(prefix)), p.stat().st_size, sha256_file(p))
               for p in sorted(prefix.rglob('*')) if p.is_file()]
    digest = hashlib.sha256(json.dumps(records, separators=(',', ':')).encode()).hexdigest()
    return {'sha256': digest, 'files': len(records), 'bytes': sum(r[1] for r in records),
            'lean_binary_sha256': sha256_file(lean),
            'meaning': 'Current installed compiler, libraries, and source bytes; not archive-origin attestation.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lean', required=True, type=Path)
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    lean = args.lean.resolve(strict=True)
    env = dict(os.environ)
    env.pop('LEAN_PATH', None)
    env.pop('LEAN_SRC_PATH', None)
    env.pop('LEAN_SYSROOT', None)
    version = subprocess.check_output([str(lean), '--version'], env=env,
                                      text=True, timeout=30).strip()
    require(version.startswith('Lean (version 4.33.0,'), 'Lean 4.33.0 required')
    manifest_bytes = (ROOT / 'proof-manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    revision = subprocess.check_output([str(lean), '--githash'], env=env, text=True, timeout=30).strip()
    require(revision == manifest['lean_commit'], 'Wrong Lean revision')
    toolchain = toolchain_snapshot(lean, env)
    sources = {}
    for module in MODULES:
        source_dir = ROOT.parent / 'lean-whole-residual-hosting' if module in DEPS else ROOT
        source = (source_dir / (module + '.lean')).read_bytes()
        require(hashlib.sha256(source).hexdigest() == manifest['sha256'][module],
                'Source mismatch: ' + module)
        code = re.sub(r'--[^\n]*', '', re.sub(r'/\-[\s\S]*?\-/', '', source.decode()))
        require(not re.search(r'\b(sorry|admit|native_decide|unsafe|axiom|opaque)\b', code),
                'Proof escape: ' + module)
        imports = re.findall(r'^import (\S+)$', code, re.M)
        require(imports == manifest['imports'][module], 'Import mismatch: ' + module)
        require(all(x == 'Std' or x in MODULES[:MODULES.index(module)] for x in imports),
                'Unlisted dependency: ' + module)
        sources[module] = source
    reports = {}
    with tempfile.TemporaryDirectory(prefix='multi-host-framework-') as tmp:
        build = Path(tmp)
        env['LEAN_PATH'] = str(build)
        for module, source in sources.items():
            (build / (module + '.lean')).write_bytes(source)
        for module in MODULES:
            result = subprocess.run([str(lean), '-t', '0', '-o', module + '.olean',
                                     module + '.lean'], cwd=build, env=env,
                                    text=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, timeout=90)
            require(result.returncode == 0 and 'warning:' not in result.stdout,
                    module + '\n' + result.stdout)
            if module in DEPS:
                continue
            for line in result.stdout.splitlines():
                match = re.fullmatch(r"'([^']+)' does not depend on any axioms", line)
                if match:
                    name, axioms = match[1], []
                else:
                    match = re.fullmatch(r"'([^']+)' depends on axioms: \[([^]]*)\]", line)
                    require(match is not None, 'Unexpected output: ' + line)
                    name, axioms = match[1], match[2].split(', ')
                require(name not in reports, 'Duplicate axiom report: ' + name)
                require(set(axioms) <= {'propext', 'Quot.sound'}, 'Unexpected axioms: ' + line)
                reports[name] = axioms
    require(list(reports) == manifest['theorems'], 'Theorem inventory mismatch')
    require(toolchain_snapshot(lean, env) == toolchain, 'Toolchain changed during replay')
    receipt = {'status': 'PASS', 'task': 'A only; no source endpoint contract supplied',
               'lean': version, 'lean_commit': revision, 'trust_level': 0,
               'completed_utc': datetime.now(timezone.utc).isoformat(),
               'manifest_sha256': hashlib.sha256(manifest_bytes).hexdigest(),
               'toolchain': toolchain, 'replay_mode': 'fresh',
               'fresh_modules_compiled': len(MODULES), 'reused_modules': 0,
               'source_sha256': manifest['sha256'], 'axioms': reports,
               'proved_boundary_inequalities': 2}
    if args.receipt:
        args.receipt.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'compiled_modules': len(MODULES),
                      'theorem_closures': len(reports), 'proved_boundary_inequalities': 2}))


if __name__ == '__main__':
    main()
