#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Kernel-check the proof and deliberately invalid variants in temporary storage."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
MARKER = 'PASS_P104_AFFINE_COMPLEMENT_LEAN statements=8 declarations=13 standard_axioms_only'
LEAN_COMMIT = '6741444a63eec253a7eae7a83f1beb3de015023d'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run(argv, formal_root, timeout=90):
    env = os.environ.copy()
    for key in ('LEAN_PATH', 'LEAN_SYSROOT', 'LEAN_SRC_PATH'):
        env.pop(key, None)
    return subprocess.run(argv, check=False, cwd=formal_root, env=env, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)


def check_environment(lake, formal_root):
    sources = json.loads((PACKAGE / 'SOURCES.json').read_text())['files']
    require(len(sources) <= 16, 'source pin count bound')
    formal_pins = [row for row in sources if row['path'].startswith('formal/lean/')]
    require(len(formal_pins) == 3, 'three formal environment pins')
    for row in formal_pins:
        data = (formal_root / Path(row['path']).name).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row['sha256'], 'formal environment hash')
    for flag, expected in [('--short-version', '4.21.0'), ('--githash', LEAN_COMMIT)]:
        result = run([lake, 'env', 'lean', flag], formal_root, 30)
        require(result.returncode == 0 and result.stdout.strip() == expected,
                'official Lean 4.21.0 required: ' + result.stdout)
    pinned = json.loads((ROOT / 'formal/lean/lake-manifest.json').read_text())
    actual = json.loads((formal_root / 'lake-manifest.json').read_text())
    require(actual == pinned, 'pinned Mathlib environment manifest')
    require(len(pinned['packages']) <= 16, 'dependency count bound')
    for dep in pinned['packages']:
        folder = formal_root / '.lake/packages' / dep['name']
        result = run(['git', '-C', str(folder), 'rev-parse', 'HEAD'], formal_root, 10)
        require(result.returncode == 0 and result.stdout.strip() == dep['rev'],
                'wrong or unavailable dependency: ' + dep['name'])


def replace_once(source, old, new):
    require(source.count(old) == 1, 'unique control anchor')
    return source.replace(old, new, 1)


def controls(source):
    yield ('wrong_complement', replace_once(source,
           '((f + q) x = 0 ↔ f x ≠ 0)', '((f + q) x = 0 ↔ f x = 0)'), 'unsolved goals')
    yield ('wrong_dimension', replace_once(source,
           'Module.finrank F₂ (LinearMap.ker f) = 7 ∧',
           'Module.finrank F₂ (LinearMap.ker f) = 8 ∧'), 'omega could not prove')
    start = source.index('  have htwo :')
    end = source.index('\n/-- The odd demand', start)
    yield ('incomplete_proof', source[:start] + '  sorry\n' + source[end:], "uses 'sorry'")
    fake = source[:start] + '  exact False.elim P104AffineComplement.injected\n' + source[end:]
    fake = replace_once(fake, 'namespace P104AffineComplement',
                        'namespace P104AffineComplement\naxiom injected : False')
    yield ('custom_axiom', fake, 'axiom in P104AffineComplement.')
    yield ('missing_audit', replace_once(source, 'run_cmd auditP104AffineComplement', ''), None)


def check(lake, formal_root):
    check_environment(lake, formal_root)
    source = (PACKAGE / 'AffineComplement.lean').read_text()
    with tempfile.TemporaryDirectory(prefix='p104-affine-lean-') as tmp:
        path = Path(tmp) / 'AffineComplement.lean'
        path.write_text(source)
        command = [lake, 'env', 'lean', '-j1', '-DwarningAsError=true']
        positive = run(command + [str(path)], formal_root)
        require(positive.returncode == 0 and MARKER in positive.stdout, positive.stdout)
        print(positive.stdout, end='')
        count = 0
        for name, mutated, diagnostic in controls(source):
            path.write_text(mutated)
            result = run(command + [str(path)], formal_root)
            if diagnostic is None:
                require(result.returncode == 0 and MARKER not in result.stdout,
                        'missing-audit control did not isolate marker check')
            else:
                require(result.returncode != 0 and diagnostic in result.stdout,
                        'control did not reject for expected reason: ' + name + '\n' + result.stdout)
            print('REJECTED_' + name)
            count += 1
        require(count == 5, 'five proof controls')
    print('PASS_P104_AFFINE_FORMAL_CONTROLS rejected=5')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lake', default='lake')
    parser.add_argument('--formal-root', type=Path, default=ROOT / 'formal/lean')
    args = parser.parse_args()
    lake = shutil.which(args.lake)
    require(lake is not None, 'lake unavailable; provision the pinned environment')
    check(lake, args.formal_root.resolve())


if __name__ == '__main__':
    main()
