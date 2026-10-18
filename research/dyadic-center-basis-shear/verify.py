#!/usr/bin/env python3
"""Recompute the exact historical complex-center circuit improvement.

Copyright 2026 Curtis Dransfield. Apache-2.0; substantial OpenAI Codex assistance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from circuit import require, serializable


def verify_pins(root=ROOT, manifest=None):
    if manifest is None:
        manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for path, expected in manifest['sha256'].items():
        require(hashlib.sha256((root / path).read_bytes()).hexdigest() == expected,
                'Source pin mismatch: '+path)
    return dict(base_commit=manifest['base_commit'], pinned_inputs=len(manifest['sha256']))


def certificate():
    pins = verify_pins()
    # -I discards ambient PYTHONOPTIMIZE, and no -O is passed to inherited code.
    completed = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'source_worker.py')],
                               cwd=HERE, text=True, capture_output=True, check=True)
    source = json.loads(completed.stdout)
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    require(set(source['inherited_python_imports']) <= set(manifest['sha256']),
            'Inherited runtime import is missing a source pin')
    from independent import independent_check
    independent = independent_check()
    require(source['central_coefficient_sha256'] == independent['coefficients']['coefficient_sha256'],
            'Independent coefficient transcripts differ')
    for side, key in (('before', 'original_cost'), ('after', 'changed_cost')):
        require([source[side][k] for k in ('G', 'H', 'G_plus_H')] ==
                [independent[key][k] for k in ('gather', 'scatter', 'total')],
                'Independent scalar charges differ')
    require(source['full_scalar_charge']['saved_steps'] ==
            independent['closed_saving_at_26']['complete_three_stage_scalar_bound_saving'],
            'Independent full scalar saving differs')
    for key in ('candidate_moves', 'admissible_moves', 'rejected_moves', 'delta_histogram', 'minimum_delta'):
        require(source['one_shear_census'][key] == independent['orbit_census'][key],
                'Independent symmetry-orbit census differs: '+key)
    return serializable(dict(status='PASS_DYADIC_CENTER_BASIS_SHEAR', pins=pins, source_replay=source,
                independent=independent,
                scope='Historical complex scalar circuit improvement; unchanged rank profile; no new kappa; '
                      'one-shear optimum only in the declared finite alphabet, not global circuit optimality'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='Fresh certificate path; existing output is rejected')
    args = parser.parse_args()
    if args.out:
        require(not args.out.exists(), 'Refusing to overwrite output')
    result = certificate()
    if args.out:
        with args.out.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    else:
        require(result == json.loads((HERE / 'CERTIFICATE.json').read_text()),
                'Recomputed certificate differs from committed evidence')
    print('PASS_DYADIC_CENTER_BASIS_SHEAR h=26 moves=1300 admissible=650 '
          'G+H=45381->43909 full_scalar_saved=59704320000 no_new_kappa')


if __name__ == '__main__':
    main()
