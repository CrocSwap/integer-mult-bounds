"""Freeze discovery recomputations before a separate strict global replay.

Based on PR676's code/freeze_spec.py; control counts come from actual receipts,
not its single-provider constants. Prepared with substantial OpenAI Codex
assistance for tekuuu; Apache-2.0.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--spec', type=Path, required=True,
                    help='Candidate spec skeleton, modified in place unless --out is given')
    ap.add_argument('--discovery', type=Path, required=True)
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    replay = read(args.discovery / 'REPLAY.json')
    need(replay['status'] == 'PASS_FRAME_RETIMING_DISCOVERY', 'Require completed discovery replay')
    need(hashlib.sha256(args.spec.read_bytes()).hexdigest() == replay['spec_sha256'],
         'Spec changed since discovery')
    need(all(stage['exit_code'] == 0 for stage in replay['stages']), 'Failed discovery stage')
    spec = read(args.spec)
    observed = {}
    for line in (args.discovery / 'WITNESS-RECORD.jsonl').read_text().splitlines():
        key, value = json.loads(line)
        need(key not in observed or observed[key] == value,
             'Conflicting independent recomputations: ' + key)
        observed[key] = value
    for key, value in observed.items():
        parts = key.split('.')
        if len(parts) > 3 and parts[0] == 'providers' and parts[2] == 'artifacts':
            parts = parts[:3] + ['.'.join(parts[3:])]
        target = spec
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        if parts[-1] in target:
            need(target[parts[-1]] == value, 'Stale expectation in candidate skeleton: ' + key)
        target[parts[-1]] = value
    assembly = read(args.discovery / 'ASSEMBLY.json')
    expected = spec.setdefault('expected', {})
    for key in ('complex_lower', 'conservative_complex_lower', 'kappa',
                'kappa_decimal', 'conservative_kappa_decimal'):
        expected[key] = assembly[key]
    admission = read(args.discovery / 'ADMISSION-CONTROLS.json')
    attempted = admission['rejected_controls'] + admission['discovery_accepted_controls']
    need(len(attempted) == len(set(attempted)) and attempted, 'Unique admission control census required')
    expected['assembly_controls_rejected'] = len(attempted)
    counts = dict(Counter(provider for _, _, provider in spec['dispatch']))
    need(counts == assembly['provider_counts'] == replay['provider_counts'], 'Dispatch receipt mismatch')
    need(set(spec['providers']) == set(counts), 'Stale or missing spec provider')
    expected['provider_counts'] = counts
    controller = read(args.discovery / 'global/audit/ASYNC-AUDIT.json')
    need(controller['mutation_controls_run'] is True, 'Controller controls were not run')
    need(len(controller['mutations_rejected']) == len(set(controller['mutations_rejected'])),
         'Duplicate controller control names')
    expected['mutations_rejected'] = len(controller['mutations_rejected'])
    (args.out or args.spec).write_text(json.dumps(spec, indent=2) + '\n')
    print('Frozen candidate:', assembly['kappa_decimal'],
          'strict admission controls required:', len(attempted))


if __name__ == '__main__':
    main()
