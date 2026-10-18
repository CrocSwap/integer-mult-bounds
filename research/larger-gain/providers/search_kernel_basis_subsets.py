#!/usr/bin/env python3
"""Exhaust the 15 nonempty protected source-exchange subsets per cold pair.

Four updates can be sourced from the first donor after donor -= pivot. Their
protected responses are then opposite. The paired remaining helper is tested
for a rank-two entrance with all legal coupled future-frame raises.
Prepared with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import defaultdict
import copy
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--exchanges', type=Path, required=True)
    parser.add_argument('--gk-dir', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    assert __debug__ and not args.out.exists()
    args.out.mkdir(parents=True)
    word = json.loads(gzip.decompress(args.word.read_bytes()))
    exchanges = json.loads(args.exchanges.read_text())
    assert exchanges['source_content_sha256'] == hashlib.sha256(gzip.decompress(args.word.read_bytes())).hexdigest()
    groups = defaultdict(list)
    for exchange in exchanges['candidates']:
        if exchange['part'] == 'B':
            groups[exchange['old_source'], exchange['new_source']].append(exchange)
    sys.path.insert(0, str(args.gk_dir.resolve()))
    import gk_word as g
    import gk_common as co
    g.V = co.V = 112
    g.DATA = co.DATA = 7168
    profile = g.profile(word)
    records = []
    script = Path(__file__).with_name('search_raised_suffix.py')
    for (pivot, donor), options in sorted(groups.items()):
        assert len(options) == 4
        for mask in range(1, 16):
            candidate = copy.deepcopy(word)
            selected = [exchange for index, exchange in enumerate(options) if mask >> index & 1]
            for exchange in selected:
                event = candidate['B'][exchange['index']]
                assert event[2] == pivot
                event[2] = donor
                event[3] *= -1
            assert g.profile(candidate) == profile
            candidate['cleanup'] = [g.inverse(event, g.FULL)
                                    for event in reversed(candidate['A'] + candidate['B'])
                                    if not 112 <= event[1] < 224]
            label = '%d-%02d' % (pivot, mask)
            raw = args.out / (label + '.json.gz')
            raw.write_bytes(g.dump(candidate))
            output = args.out / label
            command = [sys.executable, '-B', str(script), '--word', str(raw), '--gk-dir', str(args.gk_dir),
                       '--out', str(output), '--step', '1', '--rank', '2', '--pivot', str(donor)]
            result = subprocess.run(command, capture_output=True, text=True)
            (args.out / (label + '.log')).write_text(result.stdout + result.stderr)
            assert result.returncode == 0, result.stdout + result.stderr
            report = json.loads((output / 'SEARCH.json').read_text())
            records.append(dict(pivot=pivot, donor=donor, mask=mask,
                                exact_queries=report['counts']['exact_span_queries'],
                                candidates=report['candidates']))
        print('PASS', pivot, 'all15 subsets', flush=True)
    receipt = dict(status='PASS_EXACT_PROTECTED_KERNEL_BASIS_SUBSET_SCREEN',
                   source_content_sha256=exchanges['source_content_sha256'],
                   subsets=len(records), exact_queries=sum(record['exact_queries'] for record in records),
                   positive_candidates=sum(candidate['optimistic_entropy_gain'] > 0
                                           for record in records for candidate in record['candidates']),
                   records=records,
                   scope='Only the four already exact protected source exchanges per cold pair '
                         'are combined. All15 nonempty subsets per pair are tested for a paired '
                         'rank-two cold entrance. This is not an exhaustive scalar-circuit search.')
    (args.out / 'SEARCH.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({key: value for key, value in receipt.items() if key != 'records'}, indent=2))


if __name__ == '__main__':
    main()
