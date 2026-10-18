#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run certificate controls through the public command-line checker."""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError('Choose a new output file')
    certificate = json.loads((HERE / 'CERTIFICATE.json').read_text())
    cases = [
        ('boolean_width_price', lambda d: d['width_prices'].__setitem__('4', True), 'integer width prices'),
        ('float_width_price', lambda d: d['width_prices'].__setitem__('4', -1.0), 'integer width prices'),
        ('boolean_capacity_bonus', lambda d: d['capacity_bonuses'].__setitem__('8', True), 'integer capacity bonuses'),
        ('float_capacity_bonus', lambda d: d['capacity_bonuses'].__setitem__('8', 2.0), 'integer capacity bonuses'),
        ('boolean_row_capacity', lambda d: d['packing'][0].__setitem__('capacity', True), 'integer packing capacity'),
        ('float_row_capacity', lambda d: d['packing'][0].__setitem__('capacity', 8.0), 'integer packing capacity'),
        ('boolean_bin_count', lambda d: d['packing'][0].__setitem__('bins', True), 'positive packing multiplicity'),
        ('float_width_count', lambda d: d['packing'][0]['width_counts'].__setitem__(3, 1.0), 'integer packing vector'),
        ('missing_bin', lambda d: d['packing'][0].__setitem__('bins', 24863), 'complete bin stock'),
        ('missing_width_four', lambda d: d['packing'][3]['width_counts'].__setitem__(0, 1), 'complete helper inventory'),
        ('nonintegral_replica_count', lambda d: d.__setitem__('replicas', 16), 'integral residual counts'),
        ('negative_bin_count', lambda d: d['packing'][0].__setitem__('bins', -1), 'positive packing multiplicity'),
        ('false_zero_price', lambda d: d['capacity_bonuses'].__setitem__('8', 3), 'zero and maximum residual'),
        ('wrong_root_interval', lambda d: d.__setitem__('root_interval', ['0.001676905273619680861301', '0.001676905273619680861302']), 'two exact root signs: lower'),
        ('next_outer_grid', lambda d: d.__setitem__('kappa_grid', '0.001674097969905391'), 'same outer grid cell'),
        ('float_root', lambda d: d['root_interval'].__setitem__(0, 0.0016769052736196808), 'rational root strings'),
    ]
    outcomes = []
    with tempfile.TemporaryDirectory(prefix='r480-owner-controls-') as tmp:
        directory = Path(tmp)
        for name, change, reason in cases:
            mutated = copy.deepcopy(certificate)
            change(mutated)
            path, result = directory / (name+'.json'), directory / (name+'-output.json')
            path.write_text(json.dumps(mutated)+'\n')
            command = [sys.executable, '-B', str(HERE / 'verify.py'), '--certificate', str(path), '--out', str(result)]
            process = subprocess.run(command, capture_output=True, text=True)
            if process.returncode == 0 or ('ValueError: '+reason) not in process.stderr or result.exists():
                raise ValueError('Wrong rejection for '+name+': '+process.stdout+process.stderr)
            outcomes.append(dict(name=name, rejected_by=reason, output_created=False))
        old = directory / 'retained.json'
        old.write_text('retain exact bytes\n')
        command = [sys.executable, '-B', str(HERE / 'verify.py'), '--out', str(old)]
        process = subprocess.run(command, capture_output=True, text=True)
        if process.returncode == 0 or old.read_text() != 'retain exact bytes\n':
            raise ValueError('Output preservation control failed')
        outcomes.append(dict(name='output_preservation', rejected_by='Choose a new output file', retained_bytes=True))
        optimized = directory / 'optimized.json'
        process = subprocess.run([sys.executable, '-O', '-B', str(HERE / 'verify.py'), '--out', str(optimized)], capture_output=True, text=True)
        if process.returncode == 0 or 'Retained outer assertions require Python without -O' not in process.stderr or optimized.exists():
            raise ValueError('Optimization guard failed')
        outcomes.append(dict(name='optimization_guard', rejected_by='Retained outer assertions require Python without -O'))
    result = dict(status='PASS_R480_OWNER_CERTIFICATE_CONTROLS', count=len(outcomes), cases=outcomes)
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], 'cases='+str(result['count']))


if __name__ == '__main__':
    main()
