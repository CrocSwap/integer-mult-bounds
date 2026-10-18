#!/usr/bin/env python3
"""Replay the pinned finite read-exchange search with two separate F2 engines."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
DOMAINS = [('two_pairs', 2, 'all'), ('connected_triples', 3, 'shared-targets')]


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def load(path):
    return json.loads(Path(path).read_text())


def validate_sources():
    source = load(HERE / 'SOURCE.json')
    for name, pins in source['inputs'].items():
        raw = (HERE / 'inputs' / name).read_bytes()
        if name.endswith('.gz'):
            # Regenerated gzip containers may differ; proof input is its payload.
            actual = hashlib.sha256(gzip.decompress(raw)).hexdigest()
            need(actual == pins['content_sha256'], 'Input payload mismatch: ' + name)
        else:
            need(hashlib.sha256(raw).hexdigest() == pins['sha256'], 'Input source mismatch: ' + name)
    return source


def domain_receipt(primary, independent):
    replay = independent['refusal_replay']
    need(primary['status'] == 'COMPLETE_FINITE_DOMAIN', 'Search did not complete')
    need(replay['status'] == 'PASS_INDEPENDENT_FINITE_REFUSAL_REPLAY', 'Independent replay did not pass')
    need(not primary['distinct_legal_profiles'] and not primary['successive_best'], 'Unexpected surviving candidate')
    need(primary['counts'] == replay['counts'], 'Engine count disagreement')
    need(primary['failure_site_sha256'] == replay['failure_site_sha256'], 'Engine failure-site disagreement')
    need(independent['exact_scalar_columns'] == 728, 'Baseline column coverage')
    need(independent['candidate_sha256'] == primary['comparison_sha256'], 'Baseline identity mismatch')
    need(independent['price']['relation'] == 'identical_profile', 'Baseline pricing mismatch')
    return {'arity': primary['arity'], 'domain': primary['domain'],
            'eligible_pairs': replay['eligible_pairs'], 'groups': len(primary['pairs_tested']),
            'counts': primary['counts'], 'failure_site_sha256': primary['failure_site_sha256'],
            'failure_witness_sha256': replay['failure_witness_sha256'],
            'exact_baseline_columns': independent['exact_scalar_columns']}


def main():
    need(sys.version_info >= (3, 11), 'Python 3.11 or newer is required')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--expected', type=Path, default=HERE / 'EXPECTED.json')
    args = ap.parse_args()
    source = validate_sources()
    expected = load(args.expected)
    observed = {'input_sha256': source['inputs']['P6K4-WORD.json.gz']['content_sha256'],
                'comparison_sha256': source['comparison_content_sha256'], 'domains': {}}
    with tempfile.TemporaryDirectory(prefix='complex-read-exchange-') as temp:
        work = Path(temp)
        word = HERE / 'inputs/P6K4-WORD.json.gz'
        recipe = HERE / 'inputs/SW4-RECIPE.json'
        def run(label, *arguments):
            command = [sys.executable, '-B', '-I']
            if not __debug__:
                command.append('-O')
            command.extend(map(str, arguments))
            result = subprocess.run(command, capture_output=True, text=True)
            need(result.returncode == 0, label + ' failed:\n' + (result.stdout + result.stderr)[-6000:])
            print('PASS ' + label, flush=True)
        for label, arity, domain in DOMAINS:
            out = work / label
            run(label + ' primary exhaustive replay', HERE / 'search.py', word,
                '--baseline-recipe', recipe, '--out', out, '--arity', arity,
                '--pair-domain', domain, '--seconds', 3600)
            independent = work / (label + '-independent.json')
            run(label + ' independent refusal replay', HERE / 'independent_check.py', word,
                '--baseline-recipe', recipe, '--search-report', out / 'SEARCH.json',
                '--replay-refusals', '--output', independent)
            observed['domains'][label] = domain_receipt(load(out / 'SEARCH.json'), load(independent))
        need(observed == expected, 'Recomputed evidence differs from EXPECTED.json')
        run('mathematical failure controls', HERE / 'test_independent.py')
    total = sum(row['counts']['coupled_total'] for row in observed['domains'].values())
    print('PASS: %d coupled partial choices rejected by both engines; exact 728-column SW4 control; no new kappa' % total)


if __name__ == '__main__':
    main()
