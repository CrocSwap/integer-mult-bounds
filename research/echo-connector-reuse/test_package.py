"""Relocation and corruption controls; never edits the submitted package."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def main():
    with tempfile.TemporaryDirectory(prefix='echo-reuse-check-') as tmp:
        package = Path(tmp) / 'standalone'
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        command = [sys.executable, '-I', '-O', '-B', str(package / 'verify.py')]
        def run(should_pass, expected):
            result = subprocess.run(command, cwd=tmp, capture_output=True, text=True)
            output = result.stdout + result.stderr
            if (result.returncode == 0) != should_pass or expected not in output:
                raise ValueError('wrong check outcome: ' + output)
        run(True, 'PASS_ECHO_CONNECTOR_REUSE')
        print('PASS relocated isolated optimized replay', flush=True)
        path = package / 'vendor/pr730_optimize.py'
        raw = path.read_bytes()
        path.write_bytes(raw + b'\n# changed pinned source\n')
        run(False, 'source drift')
        path.write_bytes(raw)
        print('PASS immutable-source corruption rejection', flush=True)
        path = package / 'CERTIFICATE.json'
        raw = path.read_bytes()
        for value in (860, True):
            certificate = json.loads(raw)
            certificate['enumerated_trees'] = value
            path.write_text(json.dumps(certificate, indent=2, sort_keys=True) + '\n')
            run(False, 'certificate mismatch')
        path.write_bytes(raw)
        print('PASS integer/boolean certificate corruption rejection', flush=True)
        path = package / 'reuse.py'
        raw = path.read_text()
        changed = raw.replace('4 * m[0]', '2 * m[0]')
        if changed == raw:
            raise ValueError('cost mutation was not applied')
        path.write_text(changed)
        run(False, 'exhaustive optimum mismatch')
        path.write_text(raw)
        print('PASS undercharged-middle implementation rejection', flush=True)
    print('PASS_ECHO_REUSE_PACKAGE: relocation and four corruptions')


if __name__ == '__main__':
    main()
