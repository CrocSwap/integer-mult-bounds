"""Reproduce the pinned Gaussian owner-census evidence in an existing restoration."""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import importlib
import json
import platform
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def need(ok, reason):
    if not ok:
        raise AssertionError(reason)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--runtime', type=Path, required=True)
    cli.add_argument('--output', type=Path, default=HERE / 'evidence')
    args = cli.parse_args()
    runtime = args.runtime.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    manifest = json.loads((HERE / 'SOURCE-BINDINGS.json').read_text())
    need(manifest['commit'] == 'dfd25d553a843a946ca0b94130a5ff8943e98fdd', 'wrong commit')
    sys.path.insert(0, str(runtime))
    from upstream import install
    install()
    for name, record in manifest['resolved_modules'].items():
        module = importlib.import_module(name)
        data = Path(module.__file__).read_bytes()
        need(len(data) == record['size'] and sha256(data).hexdigest() == record['sha256'],
             'resolved source differs: ' + name)
    print('PASS_CENSUS_SOURCE_BINDINGS', len(manifest['resolved_modules']), flush=True)
    jobs = (('census_raw.py', 'raw-census.json', ()),
            ('census_raw.py', 'raw-retirement-control.json', ('--mutation',)),
            ('census_schedule.py', 'schedule-census.json', ()),
            ('census_primitives.py', 'primitive-census.json', ()))
    for script, result, options in jobs:
        subprocess.run([sys.executable, '-B', str(HERE / script), '--runtime', str(runtime),
                        '--output', str(output / result), *options], check=True)
    raw = json.loads((output / 'raw-census.json').read_text())
    need(raw['source_targets'] == 105216 and raw['max_extra_fields'] == 9841,
         'changed field census')
    per_context = 105216 + 9841 + 1
    need(per_context < 2**17, 'local context bound')
    need(6**77 > 2**20 * 5**77 and 564144 < 2**20, 'delay exponent bound')
    need(1 - Fraction(2092819, 2**29) > Fraction(3, 4), 'density range changed')
    n = 1 << 1024
    need(2**20 * n**77 < (n**77 - 1) * (2**25)**77, 'lifetime upper bound')
    need(n**6 + 12*n < 12*n**6,
         'birth bound from the retained mass enclosure')
    need(2**18 * n**83 < n**92, 'public owner reserve does not cover auxiliaries')
    receipt = {'status': 'PASS_GAUSSIAN_OWNER_CENSUS', 'commit': manifest['commit'],
               'python': platform.python_version(),
               'elapsed_seconds': round(time.monotonic() - started, 3),
               'productive_zero_bound': 105216, 'raw_auxiliary_bound': 9841,
               'paid_replacement_allowance': 1, 'per_context_bound': per_context,
               'per_context_power_of_two_bound': '2^17',
               'exact_context_cover': 'sum_e count[e] * (Q*delay[e]+1)',
               'production_extra_owner_bound': '2^18 N^83 < N^92',
               'adapted_paid_cuts_checked': raw['adapted_paid'],
               'half_column_pairs_checked': raw['half_column_pairs'],
               'mass_enclosure_status': 'reused from pinned TRANSFER.md; not re-audited here',
               'scope': 'Gaussian field ownership and immediate replacement contracts; '
                        'no full ordinary-role or private-control byte census'}
    (output / 'RESULT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], flush=True)


if __name__ == '__main__':
    main()
