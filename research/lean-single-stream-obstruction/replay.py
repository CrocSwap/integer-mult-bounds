#!/usr/bin/env python3
"""Offline, fresh trust-zero Lean check; uses only Python's standard library."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
NAMES = [
    'realizes_iff', 'no_owner_of_two_dependencies', 'run_visible_eq',
    'dirty_read_no_owner', 'dirty_read_no_local_program', 'whole_read_realizes',
    'two_reads_realize', 'split_residual_no_owner', 'two_residuals_realize',
    'two_helper_word_endpoint', 'correlated_two_helper_endpoint',
    'bit_factor_nontrivial', 'complex_factor_nontrivial',
    'split_bit_factor_no_owner', 'split_complex_factor_no_owner',
]
ARITHMETIC = {'dirty_read_no_owner', 'two_helper_word_endpoint',
              'correlated_two_helper_endpoint'}
# False mathematical claims, evaluated at explicit independent inputs. Each
# candidate must be rejected by Lean, rather than merely failing a Python test.
CONTROLS = {
    'omit_right_dirty_piece': 'dirtyRead 0 0 1 = 0 + 0',
    'omit_left_dirty_piece': 'dirtyRead 0 1 0 = 0 + 0',
    'one_owner_bit_split': '''
      (oneResidual .left bitFactor (bitWitness, bitWitness)).2 (true, false) =
      (splitResidual bitFactor bitFactor (bitWitness, bitWitness)).2 (true, false)''',
    'one_owner_complex_split': '''
      (oneResidual .right complexFactor (complexWitness, complexWitness)).1 true =
      (splitResidual complexFactor complexFactor (complexWitness, complexWitness)).1 true''',
    'wrong_cleanup_sign': '''
      (twoReads 0 0 1 - (-(-(0 : Int))) + (-(-(1 : Int)))) = 0''',
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lean', required=True, type=Path,
                        help='installed Lean 4.33.0 binary (not a downloading launcher)')
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    lean = args.lean.resolve(strict=True)
    env = dict(os.environ)
    for name in ('LEAN_PATH', 'LEAN_SRC_PATH'):
        env.pop(name, None)
    version = subprocess.check_output([str(lean), '--version'], env=env,
                                      text=True, timeout=30).strip()
    require(version.startswith('Lean (version 4.33.0,'), 'Lean 4.33.0 required')
    source = (ROOT / 'SingleStream.lean').read_bytes()
    source_text = source.decode()
    require(re.findall(r'^import (.+)$', source_text, re.M) == ['Std'],
            'Only the installed Std import is permitted')
    # Supplementary hygiene; transitive axiom reports are the proof check.
    require(not re.search(r'\b(sorry|admit|native_decide|unsafe)\b', source_text),
            'Disallowed proof escape')
    require(not re.search(r'^\s*(axiom|opaque)\s', source_text, re.M),
            'Project axioms/opaque declarations not permitted')
    manifest = json.loads((ROOT / 'proof-manifest.json').read_text())
    digest = hashlib.sha256(source).hexdigest()
    require(digest == manifest['SingleStream.lean'], 'Proof source hash changed')

    with tempfile.TemporaryDirectory(prefix='single-stream-lean-') as tmp:
        build = Path(tmp)
        (build / 'SingleStream.lean').write_bytes(source)

        def compile_file(name, output=None):
            command = [str(lean), '-t', '0']
            if output:
                command += ['-o', output]
            command += [name]
            return subprocess.run(command, cwd=build, env=env, text=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  timeout=60)

        result = compile_file('SingleStream.lean', 'SingleStream.olean')
        require(result.returncode == 0, result.stdout)
        reports = {}
        for name in NAMES:
            qualified = 'SingleStream.' + name
            expected = (f"'{qualified}' depends on axioms: [propext, Quot.sound]"
                        if name in ARITHMETIC else
                        f"'{qualified}' does not depend on any axioms")
            require(expected in result.stdout.splitlines(),
                    'Missing/unexpected axiom report: ' + qualified + '\n' + result.stdout)
            reports[qualified] = ['propext', 'Quot.sound'] if name in ARITHMETIC else []
        require(len(result.stdout.splitlines()) == len(NAMES),
                'Unexpected compiler output: ' + result.stdout)

        # Fresh proof module is the only extra import path, for controls only.
        env['LEAN_PATH'] = str(build)
        rejected = {}
        for name, statement in CONTROLS.items():
            text = ('import SingleStream\nopen SingleStream\n'
                    f'theorem {name} : {statement} := by decide\n')
            (build / 'Control.lean').write_text(text)
            control = compile_file('Control.lean')
            require(control.returncode != 0 and
                    'Tactic `decide` proved that the proposition' in control.stdout and
                    'is false' in control.stdout,
                    'Control not mathematically rejected: ' + name + '\n' + control.stdout)
            rejected[name] = control.stdout.strip()
        receipt = {
            'status': 'PASS', 'lean': version, 'trust_level': 0,
            'source_sha256': digest, 'fresh_modules_compiled': 1,
            'axioms': reports, 'negative_controls_rejected': rejected,
        }
    if args.receipt:
        args.receipt.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'compiled_modules': 1,
                      'axiom_reports': len(reports),
                      'negative_controls_rejected': len(rejected)}))


if __name__ == '__main__':
    main()
