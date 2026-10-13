#!/usr/bin/env python3
"""Fresh pinned build of outer-row and descriptor-volume proofs; installs nothing."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
DECL = re.compile(r'^theorem\s+(\w+)\s*(?=[:({])', re.M)
AUDIT = re.compile(r"^'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", re.M)

def require(test, message):
    if not test:
        raise SystemExit(message)

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lake-project', type=Path, required=True)
    parser.add_argument('--dependency-dir', type=Path, default=HERE.parents[1] / 'transfer-proof/recurrence')
    parser.add_argument('--output', type=Path, default=HERE / 'verification')
    args = parser.parse_args()
    project, output, dependencies = args.lake_project.resolve(), args.output.resolve(), args.dependency_dir.resolve()
    manifest = json.loads((HERE / 'proof-manifest.json').read_text())
    require((project / 'lean-toolchain').read_text().strip() == manifest['lean_toolchain'], 'Lean pin mismatch')
    packages = json.loads((project / 'lake-manifest.json').read_text())['packages']
    matches = [p for p in packages if p['name'] == 'mathlib']
    require(len(matches) == 1 and matches[0]['rev'] == manifest['mathlib_revision'], 'Mathlib pin mismatch')
    output.mkdir(parents=True, exist_ok=True)
    objects = output / 'olean'
    objects.mkdir(exist_ok=True)
    env = os.environ.copy()
    env.pop('LEAN_PATH', None)
    result = subprocess.run(['lake', 'env', sys.executable, '-c', 'import json,os; print(json.dumps(dict(os.environ)))'],
        cwd=project, env=env, text=True, capture_output=True, check=True)
    lean_env = json.loads(result.stdout)
    lean_env['LEAN_PATH'] = str(objects) + os.pathsep + lean_env.get('LEAN_PATH', '')
    version = subprocess.check_output(['lean', '--version'], cwd=project, env=lean_env, text=True).strip()
    require(re.search(r'Lean \(version 4\.21\.0(?:[, )])', version), 'Compiler version mismatch')
    report = {'status': 'PASS', 'compiler': version, 'mathlib_revision': manifest['mathlib_revision'],
              'new_theorems': 0, 'dependency_theorems': 0, 'modules': {}}
    allowed = {'propext', 'Classical.choice', 'Quot.sound'}
    require(set(manifest['allowed_axioms']) == allowed, 'Axiom policy mismatch')
    for name, spec in manifest['modules'].items():
        path = (dependencies if spec['dependency'] else HERE) / name
        source = path.read_text()
        require(digest(path) == spec['sha256'], 'Source hash mismatch: ' + name)
        require(not re.search(r'\b(sorry|admit|native_decide)\b', source), 'Proof escape: ' + name)
        require(not re.search(r'^\s*(axiom|constant)\s+\w+\s*[:({]', source, re.M), 'Custom axiom: ' + name)
        declared = [path.stem + '.' + n for n in DECL.findall(source)]
        require(declared == spec['declarations'], 'Declaration inventory mismatch: ' + name)
        require(len(re.findall(r'^#print axioms ', source, re.M)) == len(declared), 'Audit print inventory mismatch')
        result = subprocess.run(['lean', '--root=' + str(path.parent), '-o', str(objects / (path.stem + '.olean')), str(path)],
            cwd=project, env=lean_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        (output / (path.stem + '.log')).write_text(result.stdout)
        audits = AUDIT.findall(result.stdout)
        names = [n for n, _ in audits]
        require(result.returncode == 0 and names == declared, 'Compile/audit coverage failure: ' + name + '\n' + result.stdout)
        require(all({x.strip() for x in ax.split(',') if x.strip()} <= allowed for _, ax in audits), 'Nonstandard axiom')
        report['modules'][name] = {'sha256': spec['sha256'], 'dependency': spec['dependency'],
            'audits': {n: sorted(x.strip() for x in ax.split(',') if x.strip()) for n, ax in audits}}
        report['dependency_theorems' if spec['dependency'] else 'new_theorems'] += len(audits)
        print('PASS', name, len(audits), 'audits', flush=True)
    (output / 'axiom-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS all', report['new_theorems'], 'new and', report['dependency_theorems'], 'dependency audits')

if __name__ == '__main__':
    main()
