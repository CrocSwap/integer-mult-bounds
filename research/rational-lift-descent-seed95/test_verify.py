"""Public-CLI controls for a relocated, source-pinned certificate package."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(value, message):
    if not value:
        raise ValueError(message)


def main():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        package = root / HERE.relative_to(ROOT)
        package.parent.mkdir(parents=True)
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
        for name in sources['files']:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, path)

        def run():
            return subprocess.run([sys.executable, '-I', '-O', '-B',
                                   str(package / 'verify.py')],
                                  cwd=root, capture_output=True, text=True)

        baseline = run()
        require(baseline.returncode == 0 and 'PASS_RATIONAL_LIFT_DESCENT' in baseline.stdout,
                'relocated replay: ' + baseline.stderr)
        certificate = package / 'CERTIFICATE.json'
        original = certificate.read_bytes()
        for field in ('witness', 'boundary', 'controls', 'boolean_type'):
            value = json.loads(original)
            if field == 'witness':
                value['witnesses'][1]['b'][0] = '0'
            elif field == 'boundary':
                value['finite_field_boundary']['F2_witnesses'] = 1
            elif field == 'controls':
                value['rejected_controls'].pop()
            else:
                value['new_kappa'] = 0
            certificate.write_text(json.dumps(value), encoding='utf-8')
            failed = run()
            require(failed.returncode != 0 and 'certificate mismatch' in failed.stderr,
                    'certificate mutation admitted: ' + field)
        certificate.write_bytes(original)
        source = root / 'research/p112-complex-single-lift/PROOF.md'
        source.write_bytes(source.read_bytes() + b'\nchanged\n')
        failed = run()
        require(failed.returncode != 0 and 'source pin:' in failed.stderr,
                'source mutation admitted')
    print('PASS_RATIONAL_LIFT_CLI relocated=1 certificate_rejections=4 source_rejections=1')


if __name__ == '__main__':
    main()
