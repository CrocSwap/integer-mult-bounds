#!/usr/bin/env python3
"""Group a saved intake plan by exact declared word identity and paid model.

Read-only. Uses data, never PR code. Profile ceilings are conditional relaxations,
not attained bounds or evidence of circuit equivalence. Apache-2.0.
"""
import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / 'docs/research/construction-profiles.json'


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def model_inputs(profile):
    if not isinstance(profile, dict):
        raise ValueError('profile must be an object')
    if profile.get('model') != 'one-unpaid-coordinate-halving-v1':
        raise ValueError('outside the supported coverage/halving model')
    for key in ('m', 'families', 'stages', 'centre', 'idle_rank_cap'):
        if type(profile.get(key)) is not int:
            raise ValueError('integer model input required: ' + key)
    if not (2 <= profile['m'] <= 128 and 1 <= profile['stages'] <= 1000000
            and 1 <= profile['families'] <= 10**9 and 0 <= profile['centre'] <= 10**9
            and 1 <= profile['idle_rank_cap'] < profile['m']):
        raise ValueError('model input outside bounded queue-pricing domain')
    local = profile['local_profile_per_call']
    if not isinstance(local, dict) or not local or len(local) >= profile['m']:
        raise ValueError('invalid local profile')
    counts = {}
    for rank, count in local.items():
        if not re.fullmatch(r'[1-9][0-9]*', rank) or not 0 < int(rank) < profile['m']:
            raise ValueError('invalid rank')
        if isinstance(count, bool) or not isinstance(count, (str, int)) or len(str(count)) > 60:
            raise ValueError('count must be a bounded exact rational')
        counts[int(rank)] = Fraction(count)
        if counts[int(rank)] < 0 or counts[int(rank)] > 10**9:
            raise ValueError('invalid count')
    return counts


def price(profile):
    local = model_inputs(profile)
    spec = importlib.util.spec_from_file_location('trusted_queue_ceiling',
              ROOT / 'research/complex-local-word-ceiling/ceiling.py')
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    lower, upper = engine.ceiling(local, profile['m'], profile['families'], profile['stages'],
                                 profile['centre'], R=profile['idle_rank_cap'])
    return {'status': 'conditional_relaxation', 'primitive_upper': str(upper),
            'primitive_lower_bracket': str(lower), 'kappa_upper': str(upper/(1+upper)),
            'kappa_upper_decimal': format(float(upper/(1+upper)), '.16g'),
            'scope': 'Only this paid profile, coverage law, idle-rank cap and outer transfer; not an attained supplier or scientific review.'}


def body_records(snapshot):
    if snapshot.get('schema_version') != 1 or snapshot.get('repository') != 'CrocSwap/integer-mult-bounds':
        raise ValueError('not a canonical overlap cache')
    result, warnings = [], []
    for row in snapshot.get('sources', {}).get('open_prs', {}).get('records', []):
        for block in re.findall(r'^```json\s*\n(.*?)^```\s*$', row.get('body', ''), re.M | re.S):
            if 'integer-mult-construction/v1' not in block:
                continue
            try:
                if len(block) > 16384:
                    raise ValueError('profile block exceeds 16 KiB')
                value = json.loads(block)
                if not isinstance(value, dict) or value.get('schema') != 'integer-mult-construction/v1':
                    raise ValueError('wrong profile schema')
                result.append(dict(value, number=row['number'], head=row['head'],
                                   evidence=row['url'], evidence_status='author-declared'))
            except (ValueError, TypeError) as exc:
                warnings.append(f"#{row['number']}: {exc}")
    return result, warnings


def group_plan(plan, inventory, extra=(), max_profiles=20, numbers=(), pricing=price):
    if inventory.get('schema_version') != 1:
        raise ValueError('unsupported profile inventory')
    if not 1 <= max_profiles <= 100:
        raise ValueError('max_profiles must be 1..100')
    records = defaultdict(list)
    for row in list(inventory['records']) + list(extra):
        if type(row.get('number')) is not int or not re.fullmatch(r'[0-9a-f]{40}', row.get('head', '')):
            raise ValueError('profile requires a PR number and exact head')
        records[(row['number'], row['head'])].append(row)
    groups, profiles, unknown = {}, {}, []
    prices = {}
    def get_price(profile):
        key = fingerprint(profile)
        if key not in prices:
            if len(prices) >= max_profiles:
                return {'status': 'not_calculated_budget'}
            try:
                prices[key] = pricing(profile)
            except (ValueError, KeyError, TypeError, OSError, RecursionError, ArithmeticError) as exc:
                prices[key] = {'status': 'unknown_or_outside_model', 'reason': str(exc)}
        return prices[key]
    live = {r['number']: r for r in plan.get('live', [])}
    for original in plan['pull_requests']:
        pr = dict(original, author=live.get(original['number'], {}).get('author'),
                  url=live.get(original['number'], {}).get('url'))
        if numbers and pr['number'] not in numbers:
            continue
        candidates = records.get((pr['number'], pr['head']), [])
        if not candidates:
            unknown.append(dict(pr, profile_status='unknown_or_stale_head'))
            continue
        identities = {fingerprint({'word': row.get('word_sha256'), 'reference': row.get('construction_ref'), 'profile': row.get('profile')}) for row in candidates}
        if len(identities) != 1:
            unknown.append(dict(pr, profile_status='conflicting_profile_metadata'))
            continue
        row = candidates[0]
        word = row.get('word_sha256')
        if word is not None and (not isinstance(word, str) or not re.fullmatch(r'[0-9a-f]{64}', word)):
            unknown.append(dict(pr, profile_status='invalid_word_identity'))
            continue
        reference = row.get('construction_ref')
        if reference is not None and (not isinstance(reference, dict)
                or type(reference.get('number')) is not int
                or not isinstance(reference.get('head'), str)
                or not re.fullmatch(r'[0-9a-f]{40}', reference['head'])):
            unknown.append(dict(pr, profile_status='invalid_construction_reference'))
            continue
        profile = row.get('profile', {})
        profile_key = fingerprint(profile)
        # Missing both identities gets its own group; identical counts never merge circuits.
        identity = word or (['construction-reference', reference] if reference else f"unknown-word-pr-{pr['number']}")
        group_key = fingerprint([identity, profile_key])
        group = groups.setdefault(group_key, {'group_id': group_key, 'word_sha256': word, 'construction_ref': reference,
                                 'grouping_basis': 'word_hash' if word else ('construction_reference' if reference else 'unknown_word'),
                                 'identity_status': 'declared identity; verify provenance before reusing circuit checks',
                                 'profile_id': profile_key, 'members': []})
        group['members'].append(dict(pr, metadata_evidence=row.get('evidence'),
                  metadata_status=row.get('evidence_status', 'unreviewed'),
                  profile_role=row.get('profile_role', 'candidate-profile; not admitted'),
                  dependencies=row.get('dependencies', []), remaining_obligations=row.get('remaining_obligations', [])))
        profiles.setdefault(profile_key, {'profile_id': profile_key, 'inputs': profile,
                                          'ceiling': get_price(profile), 'construction_groups': []})
        if group_key not in profiles[profile_key]['construction_groups']:
            profiles[profile_key]['construction_groups'].append(group_key)
    references = []
    for row in inventory.get('references', []):
        references.append(dict(row, ceiling=get_price(row['profile'])))
    return {'schema_version': 1, 'base': plan.get('base'), 'observed_at': plan.get('observed_at'),
            'live_source': plan.get('live_source'),
            'scope': 'Read-only grouping. No intake decisions changed. Same profile is not the same circuit; stale heads are not reused.',
            'construction_groups': list(groups.values()), 'profile_clusters': list(profiles.values()),
            'unclassified': unknown, 'references': references,
            'requested_numbers_not_in_plan': sorted(set(numbers)-{r['number'] for r in plan['pull_requests']}),
            'inventory_records_not_in_plan': sorted({r['number'] for r in inventory['records']}-{r['number'] for r in plan['pull_requests']}),
            'counts': {'classified_prs': sum(len(g['members']) for g in groups.values()),
                       'unclassified_prs': len(unknown), 'construction_groups': len(groups),
                       'profile_clusters': len(profiles), 'priced_distinct_profiles': len(prices)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True, help='Existing pr_intake.py plan output')
    parser.add_argument('--inventory', type=Path, default=INVENTORY)
    parser.add_argument('--overlap-cache', type=Path, help='Optional existing PR-body cache; no fetch')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--max-profiles', type=int, default=20)
    parser.add_argument('--number', type=int, action='append', default=[])
    args = parser.parse_args()
    extra, warnings = body_records(json.loads(args.overlap_cache.read_text())) if args.overlap_cache else ([], [])
    result = group_plan(json.loads(args.plan.read_text()), json.loads(args.inventory.read_text()),
                        extra, args.max_profiles, args.number)
    result['warnings'] = warnings
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result['counts']))


if __name__ == '__main__':
    main()
