#!/usr/bin/env python3
"""Replay exact capacity duals and reject targeted corruptions (stdlib only)."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import capacity_ceiling as ceiling


def main():
    if sys.flags.optimize:
        raise SystemExit('Assertions required')
    directory = Path(__file__).resolve().parent
    verified = []
    for path in sorted(directory.glob('*CEILING.json')):
        receipt = json.loads(path.read_text())
        if 'dual' not in receipt:
            continue
        result = ceiling.verify(receipt)
        verified.append(dict(path=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                             status=result['status'], columns=result['columns']))
    assert verified
    source = json.loads((directory / 'CURRENT-ALPHABET-EXACT-CEILING.json').read_text())
    mutations = {
        'unbound_source': lambda d: d.update(source_plan_sha256='0' * 64),
        'missing_dual_coordinate': lambda d: d['dual'].pop(),
        'infeasible_call_potential': lambda d: d['dual'].__setitem__(-1, '1000000'),
        'zero_rate': lambda d: d.update(rejected_rate='0'),
        'false_kappa': lambda d: d.update(kappa_upper_bound='1/100'),
        'false_margin': lambda d: d.update(strict_rejection_margin='1'),
        'false_column_count': lambda d: d.update(pattern_and_provider_columns=1),
    }
    rejected = []
    for name, mutation in mutations.items():
        candidate = copy.deepcopy(source)
        mutation(candidate)
        try:
            ceiling.verify(candidate)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError('Accepted corruption: ' + name)
    optimized = subprocess.run([sys.executable, '-O', str(directory / 'capacity_ceiling.py'),
                                '--verify', str(directory / 'CURRENT-ALPHABET-EXACT-CEILING.json')],
                               capture_output=True, text=True)
    assert optimized.returncode != 0 and 'Assertions required' in optimized.stderr
    rejected.append('optimized_python_disables_proof_assertions')
    print(json.dumps(dict(status='PASS_CAPACITY_DUAL_REPLAYS_AND_NEGATIVE_CONTROLS',
                          verifier_sha256=hashlib.sha256((directory / 'capacity_ceiling.py').read_bytes()).hexdigest(),
                          verified=verified, rejected=rejected), indent=2))


if __name__ == '__main__':
    main()
