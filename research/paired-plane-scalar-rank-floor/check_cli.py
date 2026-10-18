#!/usr/bin/env python3
"""Check optimized replay and corruption rejection without editing the checkout."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def run(argv, expected, fragment):
    result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
    if (result.returncode == 0) != expected or fragment not in result.stdout + result.stderr:
        raise ValueError('unexpected CLI result: ' + repr((argv, result.returncode, result.stdout, result.stderr)))


def main():
    prefix = [sys.executable, '-I', '-O', '-B', str(HERE / 'verify.py')]
    run(prefix, True, 'PASS_PAIRED_PLANE_SCALAR_RANK_FLOOR')
    with tempfile.TemporaryDirectory(prefix='paired-plane-rank-') as temp:
        root = Path(temp)
        package = root / 'research/paired-plane-scalar-rank-floor'
        package.parent.mkdir(parents=True)
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        sources = json.loads((HERE / 'SOURCES.json').read_text())
        for row in sources['files']:
            if row['usage'] == 'input':
                target = root / row['path']
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row['path'], target)
        relocated = [sys.executable, '-I', '-O', '-B', str(package / 'verify.py')]
        run(relocated, True, 'PASS_PAIRED_PLANE_SCALAR_RANK_FLOOR')
        cert = json.loads((HERE / 'CERTIFICATE.json').read_text())
        cert['plane_clique'][0] = cert['plane_clique'][1]
        bad_cert = root / 'bad-certificate.json'
        bad_cert.write_text(json.dumps(cert))
        run(relocated + ['--certificate', str(bad_cert)], False, '24 distinct clique planes')
        receipt = json.loads((HERE / 'RESULTS.json').read_text())
        receipt['scalar_rank_lower_bound'] = 47
        bad_receipt = root / 'bad-receipt.json'
        bad_receipt.write_text(json.dumps(receipt))
        run(relocated + ['--receipt', str(bad_receipt)], False, 'receipt mismatch')
        fixture = root / 'research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json'
        fixture.write_bytes(fixture.read_bytes() + b'\n')
        run(relocated, False, 'source sha256')
    print('PASS_PAIRED_PLANE_RANK_CLI optimized=1 relocated=1 rejected=3')


if __name__ == '__main__':
    main()
