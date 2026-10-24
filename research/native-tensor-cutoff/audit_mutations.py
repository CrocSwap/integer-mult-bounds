"""Check that the replay rejects four mathematical changes in private copies."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
MUTATIONS = (
    ('one-copy-phase-repair', 'native.py', 'points.extend((z, z))', 'points.extend((z,))',
     'complete phase-character statistics'),
    ('ignore-central-residue', 'native.py', 'f = floor + (c - floor) % 4', 'f = floor',
     'complete phase-character statistics'),
    ('drop-native-constant', 'native.py', 'c = phase_function(0) % 4', 'c = 0',
     'separate composition formulas'),
    ('omit-last-dirty-return', 'check_certificate.py', 'need(a == b and certificate.get(',
     'need(a[:-1] == b[:-1] and certificate.get(', 'negative control was accepted'),
)


def main():
    results = []
    for name, filename, old, new, message in MUTATIONS:
        with tempfile.TemporaryDirectory(prefix='native-cutoff-mutation-') as tmp:
            target = Path(tmp) / 'package'
            shutil.copytree(HERE, target, ignore=shutil.ignore_patterns('__pycache__'))
            path = target / filename
            text = path.read_text()
            if text.count(old) != 1:
                raise ValueError('mutation anchor is not unique')
            path.write_text(text.replace(old, new))
            for optimized in (False, True):
                command = [sys.executable, '-I', '-B', '-W', 'error']
                if optimized:
                    command.append('-O')
                command.append(str(target / 'verify.py'))
                run = subprocess.run(command, capture_output=True, text=True, timeout=120)
                if run.returncode == 0 or 'ValueError: ' + message not in run.stderr:
                    raise ValueError('mutation did not fail at its mathematical check: ' + name + '\n' + run.stderr)
                results.append({'mutation': name, 'optimized': optimized, 'exit_code': run.returncode,
                                'rejection': message})
    print(json.dumps({'status': 'PASS_NATIVE_CUTOFF_MUTATIONS', 'cases': results}, indent=2))


if __name__ == '__main__':
    main()
