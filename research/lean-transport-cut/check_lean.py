#!/usr/bin/env python3
"""Compile both proof files and reject weakened statements and unexpected axioms.

Requires the pinned Lean/Mathlib environment described in README.md.
Apache-2.0. Prepared for commdata2338 with substantial OpenAI Codex assistance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}
ROOTS = {
    'TransportCut.lean': ['one_receive_attains', 'factors_receive', 'runs_factor', 'runs_rank',
                          'recovery_requires_receives', 'p104_unsplit_floor',
                          'p104_refined_floor'],
    'SourceCut.lean': ['source_count', 'target_count', 'source_entrances',
                       'target_exits', 'transport_count', 'inward_count'],
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def audit(output, namespace, roots):
    found = {}
    pattern = r"'([^']+)' (?:depends on axioms:\s*\[([^]]*)\]|does not depend on any axioms)"
    for match in re.finditer(pattern, output, re.S):
        name, listed = match.groups()
        require(name not in found, f'duplicate axiom probe: {name}')
        axioms = set() if listed is None else set(re.findall(r'[^,\s]+', listed))
        require(axioms <= ALLOWED, f'forbidden axioms for {name}: {sorted(axioms-ALLOWED)}')
        found[name] = sorted(axioms)
    expected = {f'{namespace}.{name}' for name in roots}
    require(set(found) == expected, f'missing or extra axiom probes: {expected ^ set(found)}')
    return found


def run(lake, path):
    return subprocess.run([lake, 'env', 'lean', '-j4', '-DwarningAsError=true', str(path)],
                          cwd=PACKAGE, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, timeout=90)


def rejected(lake, path, namespace, roots):
    result = run(lake, path)
    if result.returncode:
        require('error:' in result.stdout, 'negative control failed without a Lean error')
        return 'compiler'
    try:
        audit(result.stdout, namespace, roots)
    except ValueError:
        return 'axiom_audit'
    raise ValueError(f'weakened proof accepted: {path.name}')


def one_replace(source, old, new):
    require(source.count(old) == 1, 'nonunique mutation anchor')
    return source.replace(old, new, 1)


def proof_mutants(source):
    yield 'uncounted_receive', one_replace(source,
        'Runs (n + 1) (keep.comp (s.prod t))',
        'Runs n (keep.comp (s.prod t))')
    yield 'informative_initialization', one_replace(source,
        '| init (s : X →ₗ[K] L) : Runs 0 s 0',
        '| init (s : X →ₗ[K] L) (t : X →ₗ[K] R) : Runs 0 s t')
    yield 'too_strong_97_floor', one_replace(source, ': 96 ≤ k := by', ': 97 ≤ k := by')
    yield 'too_strong_49_floor', one_replace(source, ': 48 ≤ b := by', ': 49 ≤ b := by')
    start = source.index('  induction h with', source.index('theorem runs_factor'))
    end = source.index('\n/-- The output block', start)
    yield 'sorry_dependency', source[:start] + '  sorry\n' + source[end:]
    injected = source[:start] + '  cases h <;> exact False.elim injectedFalse\n' + source[end:]
    yield 'custom_axiom_dependency', one_replace(injected,
        'namespace TransportCut', 'namespace TransportCut\naxiom injectedFalse : False')
    yield 'missing_recovery_probe', one_replace(source,
        '#print axioms recovery_requires_receives\n', '')


def dependency_pins():
    manifest = json.loads((PACKAGE/'lake-manifest.json').read_text())
    pins = {}
    for package in manifest['packages']:
        folder = PACKAGE/'.lake'/'packages'/package['name']
        result = subprocess.run(['git', '-C', str(folder), 'rev-parse', 'HEAD'],
                                text=True, capture_output=True, timeout=10)
        require(result.returncode == 0, f'missing dependency: {package["name"]}')
        require(result.stdout.strip() == package['rev'], f'wrong dependency: {package["name"]}')
        pins[package['name']] = package['rev']
    return pins


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lake', default='lake')
    parser.add_argument('--out', type=Path, help='exclusively write a fresh proof receipt')
    args = parser.parse_args()
    lake = shutil.which(args.lake)
    require(lake is not None, 'lake unavailable; provision pinned environment first')
    pins = dependency_pins()
    version = subprocess.run([lake, 'env', 'lean', '--version'], cwd=PACKAGE,
                             text=True, capture_output=True, check=True, timeout=30).stdout.strip()
    require('version 4.21.0,' in version, f'wrong Lean version: {version}')
    probes, hashes, transcript = {}, {}, []
    for filename, roots in ROOTS.items():
        path = PACKAGE/filename
        result = run(lake, path)
        require(result.returncode == 0, result.stdout)
        namespace = filename.removesuffix('.lean')
        probes.update(audit(result.stdout, namespace, roots))
        hashes[filename] = hashlib.sha256(path.read_bytes()).hexdigest()
        transcript.append(result.stdout)
    controls = {}
    # The temporary proof copies import only the already provisioned libraries.
    with tempfile.TemporaryDirectory(prefix='transport-cut-') as tmp:
        for name, source in proof_mutants((PACKAGE/'TransportCut.lean').read_text()):
            path = Path(tmp)/(name+'.lean')
            path.write_text(source)
            controls[name] = rejected(lake, path, 'TransportCut', ROOTS['TransportCut.lean'])
        source = one_replace((PACKAGE/'SourceCut.lean').read_text(),
                             'inwardCount = 8', 'inwardCount = 7')
        path = Path(tmp)/'undercounted_source_cut.lean'
        path.write_text(source)
        controls['undercounted_source_cut'] = rejected(lake, path, 'SourceCut', ROOTS['SourceCut.lean'])
    require(controls['custom_axiom_dependency'] == 'axiom_audit', 'custom-axiom control did not reach audit')
    require(controls['missing_recovery_probe'] == 'axiom_audit', 'missing-probe control did not reach audit')
    receipt = {'lean': version, 'dependencies': pins, 'proof_sha256': hashes,
               'theorem_axioms': probes, 'rejected_controls': controls}
    payload = json.dumps(receipt, indent=2, sort_keys=True)+'\n'
    if args.out:
        with args.out.open('x') as f:
            f.write(payload)
    print(''.join(transcript), end='')
    print('PASS_LEAN_TRANSPORT_CUT theorems=13 rejected_controls=8 no_sorry_or_custom_axioms')


if __name__ == '__main__':
    main()
