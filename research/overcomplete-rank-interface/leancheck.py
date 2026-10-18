#!/usr/bin/env python3
"""Replay the pinned formal proof and reject four altered theorem contracts.

Apache-2.0. Prepared for ywz65 with OpenAI Codex assistance.
This never downloads tools or modifies the supplied Mathlib checkout.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOTS = ['factor_rank', 'cross_rank', 'complement_rank',
         'rank_one_factorization', 'one_extra_factorization', 'one_extra_entries']


def require(ok, message):
    if not ok:
        raise ValueError(message)


def run(argv, **kwargs):
    return subprocess.run(argv, capture_output=True, text=True, encoding='utf-8',
                          errors='replace', timeout=180, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mathlib-root', type=Path, required=True)
    parser.add_argument('--lean-bin', type=Path, required=True)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.out:
        require(not args.out.exists(), 'output already exists')
    pin = json.loads((HERE / 'TOOLCHAIN.json').read_bytes())
    mathlib = args.mathlib_root.resolve()
    suffix = '.exe' if os.name == 'nt' else ''
    lean = args.lean_bin.resolve() / ('lean' + suffix)
    lake = args.lean_bin.resolve() / ('lake' + suffix)
    version = run([str(lean), '--version'])
    require(version.returncode == 0 and pin['lean_version'] in version.stdout
            and pin['lean_commit'] in version.stdout, 'Lean version/commit mismatch')
    head = run(['git', 'rev-parse', 'HEAD'], cwd=mathlib)
    require(head.returncode == 0 and head.stdout.strip() == pin['mathlib_commit'],
            'Mathlib commit mismatch')
    require(hashlib.sha256((mathlib / 'lake-manifest.json').read_bytes()).hexdigest()
            == pin['mathlib_manifest_sha256'], 'Mathlib dependency manifest mismatch')
    clean = run(['git', 'diff', '--quiet', 'HEAD', '--', 'Mathlib', 'lakefile.lean',
                 'lakefile.toml', 'lake-manifest.json', 'lean-toolchain'], cwd=mathlib)
    require(clean.returncode == 0, 'tracked Mathlib source differs')
    env = dict(os.environ, PATH=str(args.lean_bin.resolve()) + os.pathsep + os.environ.get('PATH', ''))
    code = (HERE / 'Coupling.lean').read_text(encoding='utf-8')
    # Compilation and axiom checks are authoritative; this catches obvious bypass edits early.
    require(not re.search(r'\b(sorry|admit|axiom|unsafe)\b', code), 'unproved declaration in source')
    with tempfile.TemporaryDirectory(prefix='oc-lean-') as temp:
        path = Path(temp) / 'Coupling.lean'
        path.write_text(code, encoding='utf-8')
        result = run([str(lake), 'env', 'lean', '-j', '2', str(path)], cwd=mathlib, env=env)
        require(result.returncode == 0, 'Lean failed:\n' + result.stdout + result.stderr)
        for name in ROOTS:
            expected = "'OvercompleteRank." + name + "' depends on axioms: [propext, Classical.choice, Quot.sound]"
            require(expected in result.stdout, 'axiom audit missing: ' + name)
        require('sorryAx' not in result.stdout + result.stderr, 'unproved axiom found')
        changes = [
            ('cross rank replaced by ambient size',
             '(Y.transpose * X).rank = Fintype.card T := by',
             '(Y.transpose * X).rank = Fintype.card M := by'),
            ('exactness replaced by zero product',
             'theorem cross_rank (X Y : Matrix T M K) (h : X * Y.transpose = 1)',
             'theorem cross_rank (X Y : Matrix T M K) (h : X * Y.transpose = 0)'),
            ('two extra columns called rank one',
             'theorem one_extra_rank (X Y : Matrix T M K) (h : X * Y.transpose = 1)\n    (hm : Fintype.card M = Fintype.card T + 1)',
             'theorem one_extra_rank (X Y : Matrix T M K) (h : X * Y.transpose = 1)\n    (hm : Fintype.card M = Fintype.card T + 2)'),
            ('normalization changed to zero',
             '(h : Matrix.vecMulVec a b * Matrix.vecMulVec a b = Matrix.vecMulVec a b) :\n    dotProduct b a = 1 := by',
             '(h : Matrix.vecMulVec a b * Matrix.vecMulVec a b = Matrix.vecMulVec a b) :\n    dotProduct b a = 0 := by')]
        rejected = []
        for label, before, after in changes:
            require(code.count(before) == 1, 'mutation anchor differs: ' + label)
            path.write_text(code.replace(before, after), encoding='utf-8')
            mutant = run([str(lake), 'env', 'lean', '-j', '2', str(path)], cwd=mathlib, env=env)
            require(mutant.returncode != 0 and 'error:' in mutant.stdout,
                    'altered contract did not fail elaboration: ' + label)
            rejected.append(label)
    receipt = dict(schema_version=1, status='kernel-checked',
                   source_sha256=hashlib.sha256(code.encode()).hexdigest(),
                   lean_version=pin['lean_version'], lean_commit=pin['lean_commit'],
                   mathlib_commit=pin['mathlib_commit'], audited_roots=ROOTS,
                   allowed_axioms=['propext', 'Classical.choice', 'Quot.sound'],
                   rejected_contract_mutants=rejected)
    if args.out:
        with args.out.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(receipt, indent=2) + '\n')
    else:
        require(receipt == json.loads((HERE / 'FORMAL-RESULT.json').read_bytes()),
                'formal receipt differs')
    print('PASS_OC_LEAN: six audited roots; four rejected contract mutants')


if __name__ == '__main__':
    main()
