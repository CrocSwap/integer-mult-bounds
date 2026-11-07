#!/usr/bin/env python3
"""Replay the complete scoped obstruction package without regenerating evidence."""
from hashlib import sha256
from pathlib import Path
import json
import os
import tempfile
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CHECKS = [('shortest-root', 'verify.py', '"status": "PASS"'),
          ('support-cut', 'support-cut/verify.py', 'PASS_FOUR_ARM_CUT_BOUND'),
          ('hub-carrier', 'hub-carrier/verify.py', 'PASS_HUB_CARRIER_DEFECT'),
          ('complete-price', 'price_ceiling.py', 'PASS_FOUR_ARM_PRICE_CEILING'),
          ('all-aligned-rank', 'all-aligned/verify.py', 'PASS_ALL_ALIGNED_ARM_RANK'),
          ('all-arm-price', 'all_arms_price.py', 'PASS_ALL_ALIGNED_ARMS_PRICE')]


def main():
    pins = json.loads((HERE/'SOURCE-PINS.json').read_text())
    for name, expected in pins['retained_files'].items():
        if sha256((HERE/name).read_bytes()).hexdigest() != expected:
            raise ValueError('retained source mismatch: '+name)
    rows = []
    with tempfile.TemporaryDirectory(prefix='coupling-source-replay-') as cache:
        env = dict(os.environ)
        env['PYTHONPYCACHEPREFIX'] = cache
        for name, path, marker in CHECKS:
            flags = ['-O', '-B'] if sys.flags.optimize else ['-B']
            result = subprocess.run([sys.executable, *flags, str(HERE/path)],
                                    text=True, capture_output=True, check=True, env=env)
            if marker not in result.stdout:
                raise ValueError('missing success marker: '+name)
            rows.append({'check': name, 'status': 'PASS'})
    print('PASS_COUPLING_ROOT_OBSTRUCTIONS '+json.dumps({
        'checks': rows, 'retained_sources': len(pins['retained_files']),
        'optimization': bool(sys.flags.optimize), 'new_kappa': False}, sort_keys=True))


if __name__ == '__main__':
    main()
