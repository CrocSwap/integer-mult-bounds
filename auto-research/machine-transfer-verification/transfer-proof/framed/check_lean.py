#!/usr/bin/env python3
"""Compile the address-gauge bundle in isolation using a pinned existing Lake project."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
AUDIT = re.compile(r"^'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", re.M)
ALLOWED = {'propext', 'Quot.sound', 'Classical.choice'}


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lake-project', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    project, output = args.lake_project.resolve(), args.output.resolve()
    manifest = json.loads((HERE / 'proof-manifest.json').read_text())
    require((project / 'lean-toolchain').read_text().strip() == manifest['lean_toolchain'], 'Lean project pin')
    packages = json.loads((project / 'lake-manifest.json').read_text())['packages']
    mathlib = [p for p in packages if p['name'] == 'mathlib']
    require(len(mathlib) == 1 and mathlib[0]['rev'] == manifest['mathlib_revision'], 'Mathlib project pin')
    for name, record in manifest['sources'].items():
        source = (HERE / name).read_text()
        require(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == record['sha256'], 'Source hash: ' + name)
        require(not re.search(r'\b(sorry|admit|native_decide)\b|^\s*(axiom|constant)\s', source, re.M), 'Proof escape: ' + name)
        prints = re.findall(r'^#print axioms (\S+)\s*$', source, re.M)
        require(prints == record['printed_theorems'], 'Printed theorem inventory: ' + name)
    env = os.environ.copy()
    env.pop('LEAN_PATH', None)
    result = subprocess.run(['lake', 'env', sys.executable, '-c',
                             'import json,os;print(json.dumps(dict(os.environ)))'],
                            cwd=project, env=env, capture_output=True, text=True, check=True)
    lean_env = json.loads(result.stdout)
    output.mkdir(parents=True, exist_ok=True)
    objects = output / 'olean'
    objects.mkdir(exist_ok=True)
    lean_env['LEAN_PATH'] = str(objects) + os.pathsep + lean_env.get('LEAN_PATH', '')
    version = subprocess.run(['lean', '--version'], cwd=project, env=lean_env, capture_output=True, text=True, check=True).stdout.strip()
    require(re.search(r'Lean \(version 4\.21\.0(?:[, )])', version), 'Actual Lean compiler version')
    report = dict(status='PASS', compiler=version, mathlib_revision=manifest['mathlib_revision'], sources={})
    for name, record in manifest['sources'].items():
        result = subprocess.run(['lean', '--root=' + str(HERE), '-o',
                                 str(objects / (Path(name).stem + '.olean')), str(HERE / name)],
                                cwd=project, env=lean_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        (output / (Path(name).stem + '.log')).write_text(result.stdout)
        require(result.returncode == 0, 'Compilation failed: ' + name + '\n' + result.stdout)
        audits = AUDIT.findall(result.stdout)
        expected = [n if '.' in n else Path(name).stem + '.' + n for n in record['printed_theorems']]
        require([n for n, _ in audits] == expected, 'Axiom audit inventory: ' + name)
        require(all({a.strip() for a in ax.split(',') if a.strip()} <= ALLOWED for _, ax in audits), 'Nonstandard axioms: ' + name)
        report['sources'][name] = dict(sha256=record['sha256'], axiom_reports=[dict(theorem=n, axioms=[a.strip() for a in ax.split(',') if a.strip()]) for n, ax in audits])
        print('PASS', name, len(audits), 'axiom reports', flush=True)
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
