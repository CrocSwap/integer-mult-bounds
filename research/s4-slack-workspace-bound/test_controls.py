#!/usr/bin/env python3
"""Semantic boundaries and real optimized-CLI corruptions of constructive evidence."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(test, message):
    if not test:
        raise ValueError(message)


def run():
    spec = importlib.util.spec_from_file_location('slack_primary_controls', HERE / 'verify.py')
    primary = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(primary)
    checks = [
        (lambda: primary.compress({'name': 'leak', 'roles': 2, 'active': 1, 'word': [[0, 3, 1]]}), 'restored'),
        (lambda: primary.gate(primary.identity(2), (0, 1, 2)), 'illegal'),
        (lambda: primary.gate(primary.identity(2), (3, 1, 1)), 'illegal'),
        (lambda: primary.coordinates([1, 1], 1), 'independent'),
        (lambda: primary.split(2, 4, 0), 'dimensions'),
        (lambda: primary.compress({'name': 'bad width', 'roles': 1, 'active': 2, 'word': []}), 'capacity'),
    ]
    for operation, expected in checks:
        try:
            operation()
        except ValueError as error:
            need(expected in str(error), 'wrong semantic rejection: ' + str(error))
        else:
            raise ValueError('invalid premise accepted: ' + expected)
    # Nonzero orthogonal dirt needs two directions if the factors are retained.
    columns, kept = primary.split(2, 1, 2)
    need(kept == 2 and primary.rank(columns) == 2, 'one-sided compression lost dirty functional')
    cases = ('basis_mixes_active', 'dependent_basis', 'wrong_projector', 'changed_label',
             'oversized_workspace', 'wrong_slack', 'shortened_word', 'local_count')
    for case in cases:
        with tempfile.TemporaryDirectory(prefix='s4-slack-control-') as directory:
            package = Path(directory) / 'package'
            shutil.copytree(HERE, package)
            path = package / 'RESULT.json'
            result = json.loads(path.read_text())
            row = result['fixtures'][1]
            if case == 'basis_mixes_active':
                row['basis_columns'][0] ^= 2
            elif case == 'dependent_basis':
                row['basis_columns'][-1] = row['basis_columns'][0]
            elif case == 'wrong_projector':
                row['reduced_word'][1][1] ^= 2
            elif case == 'changed_label':
                row['reduced_word'][0][0] = 2
            elif case == 'oversized_workspace':
                row['retained_roles'] = row['active'] + row['slack'] + 1
            elif case == 'wrong_slack':
                row['slack'] += 1
            elif case == 'shortened_word':
                row['reduced_word'].pop()
            else:
                result['local_charge']['peels'] += 1
            path.write_text(json.dumps(result))
            script = 'verify.py' if case == 'local_count' else 'independent.py'
            answer = subprocess.run([sys.executable, '-I', '-O', '-B', str(package / script)],
                                    cwd=package, capture_output=True, text=True, timeout=30)
            need(answer.returncode != 0 and 'ValueError:' in answer.stderr,
                 'corrupted evidence accepted or failed unexpectedly: ' + case)
    print('PASS_S4_SLACK_CONTROLS semantic_groups=7 optimized_cli_mutations=8')


if __name__ == '__main__':
    run()
