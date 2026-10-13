"""Reproduce the frozen all-cold44 owner nomination from explicit inputs.

By default, replay the exact integer optimizer from the included frozen seed.
--rebuild-seed additionally repeats the original two floating-cost Hungarian
discovery passes; that optional route requires NumPy and SciPy.
"""
from pathlib import Path
from collections import Counter
import argparse
import copy
import json
import shutil
import subprocess
import sys

from audit_frozen import HERE, add_inputs, bound_inputs, semantic_sha
from reuse_owners import audit_roles, read, sha


def run(name, *args):
    subprocess.run([sys.executable, str(HERE/name), *map(str, args)], check=True)


def seed_plan(parent, seed_owners, new_signature):
    """Build a signature-only resizer input; never an admitted provider PLAN."""
    plan = copy.deepcopy(parent)
    plan['provider_registry']['jp8']['widths'] = new_signature['widths']
    plan['provider_registry']['jp8']['actual_paid_profile'] = new_signature['profile']
    call_widths = {
        (c['stage'], c['replica']): plan['provider_registry'][c['provider']]['widths']
        for c in plan['provider_calls']
    }
    used, families = audit_roles(seed_owners, plan, call_widths, 112, 492)
    profile = Counter()
    for c in plan['provider_calls']:
        profile.update({int(r): n for r, n in plan['provider_registry'][c['provider']]['actual_paid_profile'].items()})
    for key, (cap, times) in plan['windows'].items():
        rep, child = map(int, key.split(','))
        for port in range(112):
            left = cap-len(used[rep, child, port])
            if left:
                profile[left] += 1
    assert 73*7168-sum(r*n for r, n in profile.items()) == 2560
    plan['profile'] = dict(sorted(profile.items()))
    plan['per_call_widths'] = [
        {'stage': s, 'replica': r, 'widths': call_widths[s, r]}
        for s, r in plan['order']
    ]
    plan['status'] = 'INTERMEDIATE_SIGNATURE_ONLY_OWNER_SEED_NOT_PROVIDER_ADMISSION'
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_inputs(parser)
    parser.add_argument('--rebuild-seed', action='store_true')
    parser.add_argument('--out', type=Path, required=True, help='New output directory')
    args = parser.parse_args()
    manifest = read(HERE/'frozen/MANIFEST.json')
    parent, sig, provider = bound_inputs(args, manifest)
    args.out.mkdir(parents=True, exist_ok=False)
    seed_dir = args.out/'seed'
    if args.rebuild_seed:
        run('reuse_owners.py', '--plan', args.parent_plan, '--owners', args.parent_owners,
            '--signature', f'jp8={provider}', '--passes', '2', '--price-b', '0.001638923', '--out', seed_dir)
    else:
        seed_dir.mkdir()
        shutil.copyfile(HERE/'frozen/SEED-OWNERS.json.gz', seed_dir/'OWNERS.json.gz')
    assert semantic_sha(seed_dir/'OWNERS.json.gz') == manifest['artifacts']['SEED-OWNERS.json.gz']['semantic_sha256'], (
        'Seed differs; use the default frozen-seed replay, or the recorded NumPy/SciPy versions for discovery replay.'
    )
    plan = seed_plan(parent, read(seed_dir/'OWNERS.json.gz'), sig)
    plan_path = seed_dir/'PLAN-FOR-RESIZER.json'
    plan_path.write_text(json.dumps(plan, indent=2)+'\n')
    final_dir = args.out/'all72'
    run('expand_owners.py', '--plan', plan_path, '--owners', seed_dir/'OWNERS.json.gz',
        '--signature', f'jp8={provider}', '--signature', f'ck={provider}',
        '--max-passes', '8', '--out', final_dir)
    for name in ('OWNERS.json.gz', 'MAJORIZATION.json.gz'):
        assert semantic_sha(final_dir/name) == manifest['artifacts'][name]['semantic_sha256'], (name, 'Frozen semantic digest mismatch')
    kwargs = ('--local44', args.local44) if args.local44 is not None else ('--raw-word', args.raw_word)
    run('audit_frozen.py', '--parent-plan', args.parent_plan, '--parent-owners', args.parent_owners,
        *kwargs, '--owners', final_dir/'OWNERS.json.gz', '--majorization', final_dir/'MAJORIZATION.json.gz',
        '--out', args.out/'FROZEN-AUDIT.json')
    receipt = {
        'status': 'PASS_FROZEN_OWNER_AND_INTEGER_MAJORIZATION_REPLAY',
        'seed_mode': 'two_pass_hungarian_discovery_rebuilt' if args.rebuild_seed else 'included_frozen_seed',
        'parent_plan_sha256': sha(args.parent_plan), 'parent_owners_sha256': sha(args.parent_owners),
        'owners_semantic_sha256': semantic_sha(final_dir/'OWNERS.json.gz'),
        'owners_gzip_sha256': sha(final_dir/'OWNERS.json.gz'),
        'majorization_semantic_sha256': semantic_sha(final_dir/'MAJORIZATION.json.gz'),
        'global_profile': read(final_dir/'PROFILE.json'),
        'scope': 'Exact hosting nomination and callwise fixed-point replay; full supplier admission is separate.',
    }
    (args.out/'REPRODUCTION.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
